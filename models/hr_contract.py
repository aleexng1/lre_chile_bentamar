from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .lre_dt_tables import (
    WORKDAY_TYPE_CODES,
)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    lre_afp_code = fields.Selection([
        ('capital', 'Capital'),
        ('cuprum', 'Cuprum'),
        ('habitat', 'Habitat'),
        ('modelo', 'Modelo'),
        ('planvital', 'PlanVital'),
        ('provida', 'Provida'),
        ('uno', 'Uno'),
        ('ips', 'IPS / Ex-Cajas')
    ], string='AFP', required=False)

    lre_health_system_code = fields.Selection([
        ('fonasa', 'Fonasa'),
        ('isapre', 'Isapre'),
        ('capredena', 'Capredena/Dipreca')
    ], string='Sistema de Salud', default='fonasa')

    lre_isapre_institution = fields.Selection([
        ('banmedica', 'Banmédica'),
        ('colmena', 'Colmena Golden Cross'),
        ('consalud', 'Consalud'),
        ('cruzblanca', 'Cruz Blanca'),
        ('nuevamasvida', 'Nueva Masvida'),
        ('vidatres', 'Vida Tres'),
        ('esencial', 'Esencial'),
        ('fundacion', 'Fundación Banco Estado')
    ], string='Institución Isapre')

    lre_health_amount_type = fields.Selection([
        ('clp', 'Pesos'),
        ('uf', 'UF')
    ], string='Moneda Plan', default='clp')

    lre_health_amount = fields.Float(string='Monto Pactado', digits=(16, 4),
                                     help="Cotización pactada en Isapre (en UF o Pesos)")

    lre_termination_cause = fields.Selection([
        ('1', '1 - Art. 159 N° 1 (Mutuo Acuerdo)'),
        ('2', '2 - Art. 159 N° 2 (Renuncia del trabajador)'),
        ('3', '3 - Art. 159 N° 4 y 5 (Vencimiento del plazo / Conclusión del trabajo)'),
        ('4', '4 - Art. 160 (Despido disciplinario / Sin derecho a indemnización)'),
        ('5', '5 - Art. 161 (Necesidades de la empresa / Desahucio)'),
        ('6', '6 - Art. 163 bis (Quiebra)'),
        ('7', '7 - Art. 159 N° 3 (Muerte del trabajador)'),
        ('8', '8 - Art. 159 N° 6 (Caso fortuito o fuerza mayor)'),
        ('9', '9 - Invalidez total o parcial'),
    ], string="Causal de Término (LRE)", help="Seleccionar solo si el contrato se cancela anticipadamente. Si vence por plazo, el sistema asignará causal 3 automáticamente.")

    # ------------------------------------------------------------------
    # Campos obligatorios LRE que hasta ahora se exportaban vacíos
    # ------------------------------------------------------------------
    lre_comuna_code = fields.Char(
        string="Código comuna DT (1106)",
        size=5,
        help="Código oficial de la comuna donde se prestan los servicios. "
             "Completar solo si la comuna no puede resolverse automáticamente "
             "desde la ficha de dirección (p. ej. cuando la dirección registra "
             "una localidad como 'Pargua' en lugar de la comuna 'Calbuco').")

    lre_workday_type = fields.Selection(
        WORKDAY_TYPE_CODES,
        string="Tipo de jornada (1107)",
        default='101',
        help="Código oficial DT del tipo de jornada pactada en el contrato o "
             "en un anexo posterior.")

    lre_disability_status = fields.Selection([
        ('0', '0 - No'),
        ('1', '1 - Discapacidad certificada por la COMPIN'),
        ('2', '2 - Asignatario pensión por invalidez total'),
        ('3', '3 - Pensionado con invalidez parcial'),
    ], string="Discapacidad / Invalidez (1108)", default='0')

    lre_old_age_pensioner = fields.Boolean(
        string="Pensionado por vejez (1109)", default=False)

    lre_ips_code = fields.Char(
        string="Régimen IPS - ExINP (1142)",
        size=3,
        default='0',
        help="Código del régimen del antiguo sistema previsional. '0' si el "
             "trabajador no pertenece al IPS.")

    lre_young_worker_subsidy = fields.Boolean(
        string="Subsidio trabajador joven (1118)", default=False)

    lre_apvi = fields.Boolean(
        string="APVI - Ahorro previsional voluntario individual (1155)",
        default=False)

    lre_apvc = fields.Boolean(
        string="APVC - Ahorro previsional voluntario colectivo (1157)",
        default=False)

    lre_severance_all_events = fields.Boolean(
        string="Indemnización a todo evento Art. 164 (1131)", default=False)

    lre_severance_rate = fields.Float(
        string="Tasa indemnización a todo evento (1132)",
        digits=(5, 2),
        help="Tasa porcentual sobre la remuneración imponible (mínimo 4,11%). "
             "Solo se exporta si el pacto del Art. 164 está activo.")

    lre_afc_affiliated = fields.Selection([
        ('auto', 'Determinar según cotizaciones del período'),
        ('1', 'Sí, afiliado a la AFC'),
        ('0', 'No afiliado a la AFC'),
    ], string="Afiliación AFC (1151)", default='auto',
        help="La afiliación es obligatoria para todo trabajador contratado "
             "desde el 02-10-2002. En modo automático el valor se deriva de la "
             "existencia de cotización del trabajador (3151) o aporte del "
             "empleador (4151) en el período.")

    @api.constrains('lre_severance_all_events', 'lre_severance_rate')
    def _check_lre_severance_rate(self):
        for contract in self:
            if contract.lre_severance_all_events and contract.lre_severance_rate < 4.11:
                raise ValidationError(
                    "El pacto de indemnización a todo evento (Art. 164) exige "
                    "una tasa mínima de 4,11%.")
