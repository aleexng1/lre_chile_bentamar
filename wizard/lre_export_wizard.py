# -*- coding: utf-8 -*-
import base64
import calendar
import csv
import io
import logging
import re
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from ..models.lre_dt_tables import (
    AFP_CODES,
    COMUNA_CODES,
    HEALTH_CODES,
    REGION_CODES,
    normalize_name,
)

_logger = logging.getLogger(__name__)

class LreExportWizard(models.TransientModel):
    _name = 'lre.export.wizard'
    _description = 'Wizard Exportación LRE'

    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    year = fields.Integer(string='Año', required=True, default=lambda self: date.today().year)
    month = fields.Selection([
        ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
        ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
        ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ], string='Mes', required=True, default=lambda self: str(date.today().month).zfill(2))
    
    report_type = fields.Selection([
        ('official', 'Oficial DT (147 Columnas)'),
        ('summarized', 'Resumido (Solo columnas con datos)')
    ], string="Tipo de Reporte", default='official', required=True)

    # Definición de Columnas LRE (147 Columnas Oficiales)
    LRE_COLUMNS = [
        ('1101', 'Rut trabajador(1101)'), ('1102', 'Fecha inicio contrato(1102)'), ('1103', 'Fecha término de contrato(1103)'), ('1104', 'Causal término de contrato(1104)'), ('1105', 'Región prestación de servicios(1105)'), ('1106', 'Comuna prestación de servicios(1106)'), ('1170', 'Tipo impuesto a la renta(1170)'), ('1146', 'Técnico extranjero exención cot. previsionales(1146)'), ('1107', 'Código tipo de jornada(1107)'), ('1108', 'Persona con Discapacidad - Pensionado por Invalidez(1108)'), ('1109', 'Pensionado por vejez(1109)'),
        ('1141', 'AFP(1141)'), ('1142', 'IPS (ExINP)(1142)'), ('1143', 'FONASA - ISAPRE(1143)'), ('1151', 'AFC(1151)'), ('1110', 'CCAF(1110)'), ('1152', 'Org. administrador ley 16.744(1152)'),
        ('1111', 'Nro cargas familiares legales autorizadas(1111)'), ('1112', 'Nro de cargas familiares maternales(1112)'), ('1113', 'Nro de cargas familiares invalidez(1113)'), ('1114', 'Tramo asignación familiar(1114)'),
        ('1171', 'Rut org sindical 1(1171)'), ('1172', 'Rut org sindical 2(1172)'), ('1173', 'Rut org sindical 3(1173)'), ('1174', 'Rut org sindical 4(1174)'), ('1175', 'Rut org sindical 5(1175)'), ('1176', 'Rut org sindical 6(1176)'), ('1177', 'Rut org sindical 7(1177)'), ('1178', 'Rut org sindical 8(1178)'), ('1179', 'Rut org sindical 9(1179)'), ('1180', 'Rut org sindical 10(1180)'),
        ('1115', 'Nro días trabajados en el mes(1115)'), ('1116', 'Nro días de licencia médica en el mes(1116)'), ('1117', 'Nro días de vacaciones en el mes(1117)'), ('1118', 'Subsidio trabajador joven(1118)'), ('1154', 'Puesto Trabajo Pesado(1154)'), ('1155', 'APVI(1155)'), ('1157', 'APVC(1157)'), ('1131', 'Indemnización a todo evento(1131)'), ('1132', 'Tasa indemnización a todo evento(1132)'),
        ('2101', 'Sueldo(2101)'), ('2102', 'Sobresueldo(2102)'), ('2103', 'Comisiones(2103)'), ('2104', 'Semana corrida(2104)'), ('2105', 'Participación(2105)'), ('2106', 'Gratificación(2106)'), ('2107', 'Recargo 30% día domingo(2107)'), ('2108', 'Remun. variable pagada en vacaciones(2108)'), ('2109', 'Remun. variable pagada en clausura(2109)'), ('2110', 'Aguinaldo(2110)'), ('2111', 'Bonos u otras remun. fijas mensuales(2111)'), ('2112', 'Tratos(2112)'), ('2113', 'Bonos u otras remun. variables mensuales o superiores a un mes(2113)'), ('2114', 'Ejercicio opción no pactada en contrato(2114)'), ('2115', 'Beneficios en especie constitutivos de remun(2115)'),
        ('2116', 'Remuneraciones bimestrales(2116)'), ('2117', 'Remuneraciones trimestrales(2117)'), ('2118', 'Remuneraciones cuatrimestral(2118)'), ('2119', 'Remuneraciones semestrales(2119)'), ('2120', 'Remuneraciones anuales(2120)'), ('2121', 'Participación anual(2121)'), ('2122', 'Gratificación anual(2122)'), ('2123', 'Otras remuneraciones superiores a un mes(2123)'), ('2124', 'Pago por horas de trabajo sindical(2124)'), ('2161', 'Sueldo empresarial (2161)'),
        ('2201', 'Subsidio por incapacidad laboral por licencia médica(2201)'), ('2202', 'Beca de estudio(2202)'), ('2203', 'Gratificaciones de zona(2203)'), ('2204', 'Otros ingresos no constitutivos de renta(2204)'),
        ('2301', 'Colación(2301)'), ('2302', 'Movilización(2302)'), ('2303', 'Viáticos(2303)'), ('2304', 'Asignación de pérdida de caja(2304)'), ('2305', 'Asignación de desgaste herramienta(2305)'), ('2311', 'Asignación familiar legal(2311)'), ('2306', 'Gastos por causa del trabajo(2306)'), ('2307', 'Gastos por cambio de residencia(2307)'), ('2308', 'Sala cuna(2308)'), ('2309', 'Asignación trabajo a distancia o teletrabajo(2309)'), ('2347', 'Depósito convenido hasta UF 900(2347)'), ('2310', 'Alojamiento por razones de trabajo(2310)'), ('2312', 'Asignación de traslación(2312)'), ('2313', 'Indemnización por feriado legal(2313)'), ('2314', 'Indemnización años de servicio(2314)'), ('2315', 'Indemnización sustitutiva del aviso previo(2315)'), ('2316', 'Indemnización fuero maternal(2316)'), ('2331', 'Pago indemnización a todo evento(2331)'), ('2417', 'Indemnizaciones voluntarias tributables(2417)'), ('2418', 'Indemnizaciones contractuales tributables(2418)'),
        ('3141', 'Cotización obligatoria previsional (AFP o IPS)(3141)'), ('3143', 'Cotización obligatoria salud 7%(3143)'), ('3144', 'Cotización voluntaria para salud(3144)'), ('3151', 'Cotización AFC - trabajador(3151)'), ('3146', 'Cotizaciones técnico extranjero para seguridad social fuera de Chile(3146)'), ('3147', 'Descuento depósito convenido hasta UF 900 anual(3147)'), ('3155', 'Cotización APVi Mod A(3155)'), ('3156', 'Cotización APVi Mod B hasta UF50(3156)'), ('3157', 'Cotización APVc Mod A(3157)'), ('3158', 'Cotización APVc Mod B hasta UF50(3158)'),
        ('3161', 'Impuesto retenido por remuneraciones(3161)'), ('3162', 'Impuesto retenido por indemnizaciones(3162)'), ('3163', 'Mayor retención de impuestos solicitada por el trabajador(3163)'), ('3164', 'Impuesto retenido por reliquidación remun. devengadas otros períodos(3164)'), ('3165', 'Diferencia impuesto reliquidación remun. devengadas en este período(3165)'), ('3166', 'Retención préstamo clase media 2020 (Ley 21.252) (3166)'), ('3167', 'Rebaja zona extrema DL 889 (3167)'),
        ('3171', 'Cuota sindical 1(3171)'), ('3172', 'Cuota sindical 2(3172)'), ('3173', 'Cuota sindical 3(3173)'), ('3174', 'Cuota sindical 4(3174)'), ('3175', 'Cuota sindical 5(3175)'), ('3176', 'Cuota sindical 6(3176)'), ('3177', 'Cuota sindical 7(3177)'), ('3178', 'Cuota sindical 8(3178)'), ('3179', 'Cuota sindical 9(3179)'), ('3180', 'Cuota sindical 10(3180)'),
        ('3110', 'Crédito social CCAF(3110)'), ('3181', 'Cuota vivienda o educación(3181)'), ('3182', 'Crédito cooperativas de ahorro(3182)'), ('3183', 'Otros descuentos autorizados y solicitados por el trabajador(3183)'), ('3154', 'Cotización adicional trabajo pesado - trabajador(3154)'), ('3184', 'Donaciones culturales y de reconstrucción(3184)'), ('3185', 'Otros descuentos(3185)'), ('3186', 'Pensiones de alimentos(3186)'), ('3187', 'Descuento mujer casada(3187)'), ('3188', 'Descuentos por anticipos y préstamos(3188)'),
        ('4151', 'AFC - Aporte empleador(4151)'), ('4152', 'Aporte empleador seguro accidentes del trabajo y Ley SANNA(4152)'), ('4131', 'Aporte empleador indemnización a todo evento(4131)'), ('4154', 'Aporte adicional trabajo pesado - empleador(4154)'), ('4155', 'Aporte empleador seguro invalidez y sobrevivencia(4155)'), ('4157', 'APVC - Aporte Empleador(4157)'),
        ('5201', 'Total haberes(5201)'), ('5210', 'Total haberes imponibles y tributables(5210)'), ('5220', 'Total haberes imponibles no tributables(5220)'), ('5230', 'Total haberes no imponibles y no tributables(5230)'), ('5240', 'Total haberes no imponibles y tributables(5240)'),
        ('5301', 'Total descuentos(5301)'), ('5361', 'Total descuentos impuestos a las remuneraciones(5361)'), ('5362', 'Total descuentos impuestos por indemnizaciones(5362)'), ('5341', 'Total descuentos por cotizaciones del trabajador(5341)'), ('5302', 'Total otros descuentos(5302)'),
        ('5410', 'Total aportes empleador(5410)'),
        ('5501', 'Total líquido(5501)'), ('5502', 'Total indemnizaciones(5502)'), ('5564', 'Total indemnizaciones tributables(5564)'), ('5565', 'Total indemnizaciones no tributables(5565)')
    ]

    # ------------------------------------------------------------------
    # Política de relleno por columna
    #
    # La DT no acepta "vacío" como sinónimo de "no aplica" en los campos
    # obligatorios: espera el entero 0. Pero tampoco acepta un 0 en los
    # campos que deben quedar en blanco cuando no aplican (fecha de término,
    # tasa Art. 164, puesto de trabajo pesado, RUT sindicales). Por eso la
    # decisión de relleno se toma por columna y no por prefijo.
    # ------------------------------------------------------------------

    # Campos obligatorios 11xx que se declaran con un código numérico (0 = "no")
    LRE_MANDATORY_FLAG_COLUMNS = frozenset({
        '1107', '1108', '1109', '1110', '1118', '1131',
        '1142', '1146', '1151', '1155', '1157',
    })

    # Campos 11xx que son conteos de días o personas: 0 es un valor válido
    LRE_MANDATORY_COUNT_COLUMNS = frozenset({
        '1111', '1112', '1113', '1115', '1116', '1117',
    })

    # Campos que DEBEN quedar en blanco cuando no aplican
    LRE_BLANK_WHEN_EMPTY_COLUMNS = frozenset({
        '1103', '1104', '1114', '1132', '1154',
        '1171', '1172', '1173', '1174', '1175',
        '1176', '1177', '1178', '1179', '1180',
    })

    # Comunas cuyo código legado INE no permite derivar la región actual
    # (Los Ríos, Ñuble y Arica y Parinacota se crearon después de esa tabla).
    LRE_REGION_OVERRIDES = (
        ('105', '14'),   # provincia de Valdivia -> Los Ríos
        ('84', '16'),    # antigua provincia de Ñuble -> Ñuble
        ('12', '15'),    # Camarones -> Arica y Parinacota
        ('13', '15'),    # Putre / General Lagos -> Arica y Parinacota
        ('151', '15'),   # Arica
    )

    def _clean_rut(self, rut):
        """Limpia y valida RUT: retorna '12345678-K' o '' si el digito
        verificador no calza (algoritmo modulo 11)."""
        if not rut:
            return ''
        rut_clean = re.sub(r'[^0-9kK]', '', str(rut)).upper()
        if len(rut_clean) < 2:
            return ''
        cuerpo = rut_clean[:-1]
        dv = rut_clean[-1]
        if not cuerpo.isdigit():
            return ''
        if not self._validate_rut_dv(cuerpo, dv):
            return ''
        return f"{cuerpo}-{dv}"

    @staticmethod
    def _validate_rut_dv(cuerpo, dv):
        """Valida el digito verificador con el algoritmo modulo 11 chileno."""
        reversed_digits = map(int, reversed(cuerpo))
        factors = [2, 3, 4, 5, 6, 7]
        s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
        remainder = 11 - (s % 11)
        if remainder == 11:
            expected = '0'
        elif remainder == 10:
            expected = 'K'
        else:
            expected = str(remainder)
        return dv == expected

    # ------------------------------------------------------------------
    # Helpers de normalización
    # ------------------------------------------------------------------
    @staticmethod
    def _as_code(value, default: str = '0') -> str:
        """Normaliza un booleano / entero / selection a su código LRE.

        Nunca devuelve cadena vacía: la DT rechaza el campo en blanco en
        todos los códigos declarativos obligatorios (1108, 1109, 1110,
        1118, 1131, 1142, 1151, 1155, 1157).
        """
        match value:
            case None | False | '':
                return default
            case True:
                return '1'
            case int() | float():
                return str(int(value))
            case str() as text if text.strip().lstrip('-').isdigit():
                return str(int(text.strip()))
            case _:
                return default

    def _get_region_code(self, partner_address, comuna_code: str | None) -> str | None:
        """Resuelve el cód 1105 desde el estado del partner o, en su defecto,
        desde el prefijo del código de comuna ya resuelto."""
        state = partner_address.state_id if partner_address else False
        if state:
            if code := REGION_CODES.get(normalize_name(state.name)):
                return code

        if not comuna_code:
            return None

        for prefix, region in self.LRE_REGION_OVERRIDES:
            if comuna_code.startswith(prefix) and len(comuna_code) == len(prefix) + 2:
                return region

        # '10102' -> '10'; '5101' -> '5'
        return comuna_code[:-3] or None

    def _get_comuna_code(self, contract, partner_address) -> str | None:
        """Resuelve el cód 1106 (código numérico oficial, no el nombre).

        Odoo no trae los códigos de comuna del SII/DT en su localización:
        ``res.country.state`` solo modela regiones y ``res.city`` no tiene
        campo de código oficial. Por eso la tabla vive en el módulo y el
        contrato ofrece un campo de sobrescritura para direcciones que
        registran una localidad en lugar de la comuna.
        """
        if override := (contract.lre_comuna_code or '').strip():
            return override

        if not partner_address:
            return None

        candidates = []
        if city_id := getattr(partner_address, 'city_id', False):
            candidates.append(city_id.name)
        if city := getattr(partner_address, 'city', False):
            candidates.append(city)

        for candidate in candidates:
            if code := COMUNA_CODES.get(normalize_name(candidate)):
                return code
        return None

    def _get_workday_code(self, contract) -> str:
        """Resuelve el cód 1107 desde el contrato.

        Si el contrato no tiene jornada declarada se infiere desde el
        calendario de trabajo (menos de 30 horas semanales = jornada parcial
        del Art. 40 bis). Cualquier fallo al leer el calendario degrada a
        jornada ordinaria en vez de dejar el campo nulo, que es lo que hoy
        rechaza la DT.
        """
        if code := contract.lre_workday_type:
            return code

        try:
            calendar_id = contract.resource_calendar_id
            hours = float(getattr(calendar_id, 'hours_per_week', 0.0) or 0.0)
        except (AttributeError, TypeError, ValueError) as exc:
            _logger.warning(
                "LRE 1107: no fue posible leer la jornada del contrato %s (%s); "
                "se exporta 101 - Ordinaria. Detalle: %s",
                contract.display_name, contract.id, exc,
            )
            return '101'

        match hours:
            case 0.0:
                return '101'
            case h if h < 30.0:
                return '201'
            case _:
                return '101'

    def _get_afc_code(self, contract, row_data) -> str:
        """Resuelve el cód 1151: 1 = afiliado a la AFC, 0 = no afiliado.

        Antes se emitía el literal '53' (un código de columna Previred, no un
        valor válido para la DT, que solo acepta 0 o 1).
        """
        match contract.lre_afc_affiliated:
            case '1' | '0' as explicit:
                return explicit
            case _:
                contributed = (row_data.get('3151') or 0) > 0 or (row_data.get('4151') or 0) > 0
                return '1' if contributed else '0'

    def _get_health_code(self, contract) -> str:
        """Resuelve el cód 1143 (FONASA = 102, isapres con su código DT).

        La columna es obligatoria, así que nunca se devuelve vacío: un contrato
        marcado como isapre pero sin institución informada degrada a FONASA y
        deja traza en el log, en vez de generar un archivo que la DT rechaza.
        """
        match contract.lre_health_system_code:
            case 'isapre':
                if code := HEALTH_CODES.get(contract.lre_isapre_institution):
                    return code
                _logger.warning(
                    "LRE 1143: el contrato %s (%s) declara isapre pero no tiene "
                    "institución informada; se exporta 102 - FONASA.",
                    contract.display_name, contract.id,
                )
                return HEALTH_CODES['fonasa']
            case _:
                # fonasa, capredena/dipreca o sin sistema declarado
                return HEALTH_CODES['fonasa']

    def _format_cell(self, col_code: str, value) -> str:
        """Aplica la política de relleno de la DT a una celda.

        Un campo obligatorio vacío es un error de formato; un campo opcional
        relleno con 0 también. La decisión se toma por columna.
        """
        if value not in ('', None, False):
            return value

        if col_code in self.LRE_BLANK_WHEN_EMPTY_COLUMNS:
            return ''
        if col_code in self.LRE_MANDATORY_FLAG_COLUMNS:
            return '0'
        if col_code in self.LRE_MANDATORY_COUNT_COLUMNS:
            return '0'
        if col_code.startswith(('2', '3', '4', '5')):
            return '0'
        return ''

    def action_generate_lre(self):
        # 1. Buscar liquidaciones
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

        output_rows = []
        validation_errors = []

        for slip in payslips:
            contract = slip.contract_id
            employee = slip.employee_id
            
            row_data = {}

            # Paso A: Reglas Salariales
            # Agrupar montos por lre_code
            for line in slip.line_ids:
                if line.salary_rule_id.lre_code:
                    code = line.salary_rule_id.lre_code
                    if code not in row_data:
                        row_data[code] = 0
                    row_data[code] += line.total
            
            # Redondear montos a enteros
            for code in row_data:
                row_data[code] = int(round(row_data[code]))

            # Paso B: Datos Fijos (Serie 1xxx)
            # 1101 RUT: Formato 12345678-K (Sin puntos, con guión)
            # Se revalida el digito verificador (modulo 11) antes de exportar:
            # un RUT mal tipeado no debe pasar en silencio.
            rut_formatted = self._clean_rut(employee.identification_id)
            if not rut_formatted:
                validation_errors.append(_(
                    "%(employee)s: el RUT '%(rut)s' no es valido (digito "
                    "verificador incorrecto) o esta vacio."
                ) % {'employee': employee.display_name, 'rut': employee.identification_id or ''})
            row_data['1101'] = rut_formatted
            
            # 1102 Fecha Inicio
            if contract.date_start:
                row_data['1102'] = contract.date_start.strftime('%d/%m/%Y')
            
            # 1103 Fecha Termino y 1104 Causal Termino
            # Validar si el contrato termina en este periodo
            term_date = ''
            term_cause = ''
            
            if contract.date_end:
                # Verificar si la fecha de término cae dentro del mes del reporte
                if date_start <= contract.date_end <= date_end:
                    term_date = contract.date_end.strftime('%d/%m/%Y')
                    
                    # Lógica de Causal (cód 1104, tabla oficial DT)
                    if contract.state == 'close':
                        # Vencido: la causal por defecto es el vencimiento del
                        # plazo convenido (6 en la tabla DT, no 3, que es el
                        # mutuo acuerdo), pero si el usuario declaró otra en el
                        # contrato ésa manda.
                        term_cause = contract.lre_termination_cause or '6'
                    elif contract.state == 'cancel':
                        term_cause = contract.lre_termination_cause or ''
                    else:
                        term_cause = ''  # open/draft: no debería tener fecha fin en el período.
            
            row_data['1103'] = term_date
            row_data['1104'] = term_cause

            # 1115 Días Trabajados (WORK100)
            work100_line = slip.worked_days_line_ids.filtered(lambda x: x.code == 'WORK100')
            dias_trabajados = sum(work100_line.mapped('number_of_days')) if work100_line else 30
            row_data['1115'] = int(dias_trabajados)

            # 1111 Cargas Familiares
            row_data['1111'] = int(employee.children or 0)

            # --- BLOQUE BLINDADO PARA DIRECCIÓN ---
            partner_address = False

            # 1. Intento: Dirección Privada Estándar (si existe el campo)
            if hasattr(employee, 'address_home_id') and employee.address_home_id:
                partner_address = employee.address_home_id

            # 2. Intento: Private Partner ID (Odoo 18 Community/Enterprise variaciones)
            if not partner_address and hasattr(employee, 'private_partner_id') and employee.private_partner_id:
                partner_address = employee.private_partner_id

            # 3. Intento: Dirección del Usuario Relacionado
            if not partner_address and employee.user_id and employee.user_id.partner_id:
                partner_address = employee.user_id.partner_id

            # 4. Intento: Dirección Laboral (Fallback)
            if not partner_address and hasattr(employee, 'address_id') and employee.address_id:
                partner_address = employee.address_id

            # --- 1106: COMUNA (código numérico oficial, no el nombre) ---
            comuna_code = self._get_comuna_code(contract, partner_address)
            if not comuna_code:
                validation_errors.append(_(
                    "%(employee)s: no fue posible determinar el código de comuna "
                    "(cód 1106). Corrija la comuna en la dirección del trabajador "
                    "o informe el código oficial en el campo 'Código comuna DT' "
                    "del contrato."
                ) % {'employee': employee.display_name})
            row_data['1106'] = comuna_code or ''

            # --- 1105: REGIÓN ---
            region_code = self._get_region_code(partner_address, comuna_code)
            if not region_code:
                validation_errors.append(_(
                    "%(employee)s: no fue posible determinar el código de región "
                    "(cód 1105)."
                ) % {'employee': employee.display_name})
            row_data['1105'] = region_code or ''

            # --- 1107: TIPO DE JORNADA ---
            row_data['1107'] = self._get_workday_code(contract)

            # --- 1108 / 1109: discapacidad y pensión de vejez ---
            row_data['1108'] = self._as_code(contract.lre_disability_status)
            row_data['1109'] = self._as_code(contract.lre_old_age_pensioner)

            # 1170 Tipo Impuesto
            row_data['1170'] = '1'  # Impuesto Único

            # 1146 Tecnico Extranjero
            row_data['1146'] = '0'

            # 1141 AFP (códigos DT, no Previred)
            row_data['1141'] = AFP_CODES.get(contract.lre_afp_code, AFP_CODES['sin_afp'])

            # 1142 IPS (ExINP): 0 = no pertenece al antiguo régimen
            row_data['1142'] = self._as_code(contract.lre_ips_code)

            # 1143 Salud
            row_data['1143'] = self._get_health_code(contract)

            # 1151 AFC: 0 / 1, nunca el literal '53'
            row_data['1151'] = self._get_afc_code(contract, row_data)

            # 1110 CCAF: atributo de la empresa, no del trabajador
            row_data['1110'] = self._as_code(contract.company_id.lre_ccaf_code)

            # 1152 Mutual (códigos DT 0/1/2/3)
            row_data['1152'] = self._as_code(contract.company_id.lre_mutual_code)

            # 1118 / 1155 / 1157 / 1131: declarativos obligatorios
            row_data['1118'] = self._as_code(contract.lre_young_worker_subsidy)
            row_data['1155'] = self._as_code(contract.lre_apvi)
            row_data['1157'] = self._as_code(contract.lre_apvc)
            row_data['1131'] = self._as_code(contract.lre_severance_all_events)

            # 1132: la tasa solo se informa si existe pacto del Art. 164
            row_data['1132'] = (
                f"{contract.lre_severance_rate:.2f}"
                if contract.lre_severance_all_events and contract.lre_severance_rate
                else ''
            )

            output_rows.append(row_data)

        # Fallar antes de generar un archivo que la DT va a rechazar
        if validation_errors:
            raise UserError(
                _("No es posible generar el LRE: faltan datos obligatorios.\n\n%s")
                % "\n".join(f"- {error}" for error in validation_errors)
            )

        # Definir columnas finales
        final_columns = self.LRE_COLUMNS # Por defecto usamos las 147

        if self.report_type == 'summarized':
            columns_with_data = []

            # Iteramos sobre cada columna definida en LRE_COLUMNS
            for col_code, col_name in self.LRE_COLUMNS:
                has_data = False
                # Revisamos si ALGUNA fila tiene datos distintos de 0 o vacío para esta columna
                for row in output_rows:
                    val = row.get(col_code)
                    # Consideramos dato si no es None, no es False, no es '' y no es 0
                    if val and str(val) != '0':
                        has_data = True
                        break

                if has_data:
                    columns_with_data.append((col_code, col_name))

            final_columns = columns_with_data

        # Generar CSV
        output = io.StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\r\n')

        # Escribir cabeceras
        headers = [col[1] for col in final_columns]
        writer.writerow(headers)

        for row_data in output_rows:
            writer.writerow([
                self._format_cell(col_code, row_data.get(col_code, ''))
                for col_code, _col_name in final_columns
            ])

        # Codificar
        out_data = base64.b64encode(output.getvalue().encode('latin-1', errors='replace'))
        filename = f'LRE_{self.year}_{self.month}.csv'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': out_data,
            'type': 'binary',
            'res_model': 'lre.export.wizard',
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
