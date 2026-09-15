# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import csv
import re
import unicodedata
from datetime import date
import calendar

class PreviredExportWizard(models.TransientModel):
    _name = 'previred.export.wizard'
    _description = 'Wizard Exportación Previred'

    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    year = fields.Integer(string='Año', required=True, default=lambda self: date.today().year)
    month = fields.Selection([
        ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
        ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
        ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ], string='Mes', required=True, default=lambda self: str(date.today().month).zfill(2))

    output_format = fields.Selection([
        ('txt', 'Oficial Previred (TXT - Sin Cabeceras)'),
        ('csv', 'Validación (CSV - Con Cabeceras)')
    ], string="Formato de Salida", default='txt', required=True)

    PREVIRED_HEADERS = [
        '01-RutTrab', '02-DV', '03-ApePat', '04-ApeMat', '05-Nombres', '06-Sexo', '07-Nacionalidad', '08-TipoPago', '09-PerDesde', '10-PerHasta',
        '11-Regimen', '12-TipoTrab', '13-DiasTrab', '14-TipoLinea', '15-CodAFP', '16-RentaImpAFP', '17-CotObligAFP', '18-SIS', '19-CtaAhorroAFP',
        '20-RentaImpSust', '21-TasaPactSalud', '22-Cot7%Salud', '23-CotAdicSalud', '24-MontoPactUF', '25-CCAF-Cred', '26-CCAF-Dent', '27-CCAF-Leas', '28-CCAF-Seg', '29-CCAF-Otr',
        '30-MontoCargas', '31-OtrosAportes', '32-Sind1', '33-Sind2', '34-ImpUnico', '35-HorasExtras', '36-FechIniCon', '37-CodMov1', '38-FechTerm', '39-CodMov2', '40-RentaTrib',
        '41-TrabPes-Trab', '42-TrabPes-Emp', '43-AporteIndem', '44-RentaImpSC(Old)', '45-SC-Trab(Old)', '46-SC-Emp(Old)', '47-TotHabImp(Old)', '48-TotHabNoImp(Old)',
        '49-CodInstAPV1', '50-MontoAPV1', '51-CodInstAPV2', '52-MontoAPV2', '53-CodInstAPVC', '54-MontoAPVC', '55-CodInstDepConv', '56-MontoDepConv',
        '57-BonoGobierno', '58-CodInstEduc', '59-BonoEscolar', '60-NivEduc', '61-CodSucursal', '62-IPS-RentaImp', '63-IPS-CotObli', '64-IPS-Desahucio', '65-IPS-Fonasa', '66-IPS-Accidente',
        '67-Bonif-DL889', '68-Gasto-Desp', '69-Ley-LeyesSoc', '70-Mutual-RentaImp', '71-Mutual-CotAcc', '72-Mutual-Sucursal', '73-Pariente-Rut', '74-Pariente-DV', '75-Pariente-Pat',
        '76-Pariente-Mat', '77-Pariente-Nom', '78-Pariente-Sex', '79-Pariente-Parent', '80-Tramo-AsigFam', '81-Nro-CargasSimples', '82-Nro-CargasMat', '83-Nro-CargasInv', '84-AsigFam-Retro',
        '85-AsigFam-Reintegro', '86-Sil-Monto', '87-Sil-Dias', '88-Ret-Judicial', '89-Ret-RutAcreedor', '90-Ret-DvAcreedor', '91-Cheque-Rest', '92-Licencia-RutMed', '93-Licencia-DvMed',
        '94-Licencia-Nro', '95-Licencia-Codigo', '96-Licencia-Dias', '97-Licencia-Fecha', '98-Subsidio-Empleo', '99-Bono-ClaseMedia',
        '100-RentaImpAFC', '101-SegCesantia-Trab', '102-SegCesantia-Emp', '103-TotalHaberesImp', '104-TotalHaberesNoImp', '105-CodSucursal-Pago'
    ]

    # Mapeos Previred
    AFP_CODES = {
        'capital': '33', 'cuprum': '03', 'habitat': '05', 
        'planvital': '29', 'provida': '23', 'modelo': '34', 
        'uno': '35', 'ips': '08'
    }

    ISAPRE_CODES = {
        'fonasa': '07',
        'banmedica': '01', 'colmena': '04', 'consalud': '09', 
        'cruzblanca': '06', 'nuevamasvida': '43', 'vidatres': '12', 
        'esencial': '44', 'fundacion': '40', 'rio_blanco': '41', 
        'chuquicamata': '37'
    }

    def _clean_rut(self, rut):
        """Limpia RUT y retorna (cuerpo, dv). Ej: ('12345678', 'K')"""
        if not rut:
            return '', ''
        rut_clean = re.sub(r'[^0-9kK]', '', str(rut)).upper()
        if len(rut_clean) < 2:
            return rut_clean, ''
        cuerpo = rut_clean[:-1]
        dv = rut_clean[-1]
        if not cuerpo.isdigit():
            return '', ''
        return cuerpo, dv

    def _split_name(self, name):
        if not name:
            return '', '', ''
        parts = name.strip().split()
        if len(parts) == 1:
            return parts[0], '', ''
        elif len(parts) == 2:
            return parts[0], parts[1], ''
        elif len(parts) == 3:
            return parts[0], parts[1], parts[2]
        else:
            return parts[-2], parts[-1], " ".join(parts[:-2])

    def _sanitize_text(self, text, max_length=0):
        """Sanitiza texto para archivos planos Previred (sistemas legacy COBOL).

        - Convierte a mayúsculas
        - Reemplaza Ñ→N, elimina tildes
        - Filtra caracteres no-ASCII y delimitadores peligrosos (;|\n\r\t)
        - Trunca al largo máximo si se especifica

        :param text: Texto de entrada
        :param max_length: Largo máximo permitido (0 = sin límite)
        :return: Texto limpio y seguro
        """
        if not text:
            return ''
        text = str(text).upper()
        # Reemplazos criticos antes de normalización
        text = text.replace('Ñ', 'N').replace('ñ', 'N')
        # Normalización Unicode (separar tildes)
        text = unicodedata.normalize('NFD', text)
        # Eliminar marcas diacríticas (tildes separadas)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        # Eliminar delimitadores y caracteres de control peligrosos
        text = re.sub(r'[;|\r\n\t\\]', '', text)
        # Filtrar solo ASCII imprimible (32-126)
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        # Truncar si hay límite
        if max_length > 0:
            text = text[:max_length]
        return text

    def action_generate_previred(self):
        last_day = calendar.monthrange(self.year, int(self.month))[1]
        date_start = date(self.year, int(self.month), 1)
        date_end = date(self.year, int(self.month), last_day)

        payslips = self.env['hr.payslip'].search([
            ('state', 'in', ['done', 'paid']),
            ('date_from', '>=', date_start),
            ('date_to', '<=', date_end),
            ('company_id', '=', self.company_id.id)
        ])

        if not payslips:
            raise UserError(_('No se encontraron liquidaciones confirmadas para el periodo seleccionado.'))

        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')

        # Escribir cabeceras si es CSV
        if self.output_format == 'csv':
            writer.writerow(self.PREVIRED_HEADERS)

        for slip in payslips:
            contract = slip.contract_id
            employee = slip.employee_id
            
            # Inicializar fila con 105 ceros (como strings para facilitar)
            row = ['0'] * 105

            # --- DATOS EMPLEADO (Cols 1-47) ---
            # Indices son col_num - 1
            
            # 1 RUT Cuerpo, 2 RUT DV
            rut_body, rut_dv = self._clean_rut(employee.identification_id)
            row[0] = rut_body
            row[1] = rut_dv

            # 3 Ap Paterno, 4 Ap Materno, 5 Nombres
            # Usando lógica simple de split sobre employee.name
            # Odoo 18 Community no tiene campos separados por defecto en hr.employee
            # Intentamos ser inteligentes:
            parts = employee.name.strip().split()
            if len(parts) >= 2:
                if len(parts) == 2:
                    row[2] = self._sanitize_text(parts[1], max_length=30)  # Ap Pat
                    row[3] = ''       # Ap Mat
                    row[4] = self._sanitize_text(parts[0], max_length=30)  # Nombres
                else:
                    # 3 o más: Nombres ApP ApM
                    row[2] = self._sanitize_text(parts[-2], max_length=30)  # Ap Pat
                    row[3] = self._sanitize_text(parts[-1], max_length=30)  # Ap Mat
                    row[4] = self._sanitize_text(" ".join(parts[:-2]), max_length=30)  # Nombres
            else:
                row[2] = self._sanitize_text(employee.name, max_length=30)  # Ap Pat (Todo)
                row[3] = ''
                row[4] = ''

            # 6 Sexo (M/F)
            row[5] = 'M' if employee.gender == 'male' else 'F' if employee.gender == 'female' else 'M'

            # 9 Tipo de Pago (1 Efectivo, 2 Cheque, 3 Deposito)
            # Por defecto 1
            row[8] = '1'

            # 10 Codigo AFP
            afp_internal = contract.lre_afp_code
            row[9] = self.AFP_CODES.get(afp_internal, '00')

            # 12 Codigo Isapre
            health_system = contract.lre_health_system_code
            if health_system == 'fonasa':
                row[11] = '07'
            elif health_system == 'isapre':
                isapre_internal = contract.lre_isapre_institution
                row[11] = self.ISAPRE_CODES.get(isapre_internal, '')
            else:
                row[11] = '00' # Ninguno

            # 15 Monto Pactado UF (Isapre)
            # Si es Isapre, buscar valor. Asumimos que está en contrato o regla.
            # Por ahora dejaremos en 0 si no hay campo específico mapeado, 
            # pero el usuario pidió mapear col 55. La col 15 es informativa.
            # Dejaremos 0 por defecto salvo que haya dato.
            row[14] = '0'

            # --- MONTOS (Cols 48-105) ---
            # Iterar reglas
            for line in slip.line_ids:
                if line.salary_rule_id.lre_previred_code:
                    col_idx = int(line.salary_rule_id.lre_previred_code) - 1
                    if 0 <= col_idx < 105:
                        # Sumar valor (convertir a int)
                        current_val = int(row[col_idx])
                        add_val = int(round(line.total))
                        row[col_idx] = str(current_val + add_val)

            # Ajustes finales de formato
            # Asegurar que todos sean strings
            row = [str(x) for x in row]
            
            writer.writerow(row)

        # Codificar
        # Previred usa TXT plano, extensión .txt o .csv
        out_data = base64.b64encode(output.getvalue().encode('latin-1', errors='replace'))
        
        ext = 'csv' if self.output_format == 'csv' else 'txt'
        filename = f'Previred_{self.year}_{self.month}.{ext}'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': out_data,
            'type': 'binary',
            'res_model': 'previred.export.wizard',
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
