from odoo import models, fields

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

    lre_afc_affiliated = fields.Selection([
        ('auto', 'Determinar según cotizaciones del período'),
        ('1', 'Sí, afiliado a la AFC'),
        ('0', 'No afiliado a la AFC'),
    ], string="Afiliación AFC (1151)", default='auto',
        help="La afiliación es obligatoria para todo trabajador contratado "
             "desde el 02-10-2002. En modo automático el valor se deriva de la "
             "existencia de cotización del trabajador (3151) o aporte del "
             "empleador (4151) en el período.")
