from odoo import models, fields

from .lre_dt_tables import CCAF_CODES, MUTUAL_CODES


class ResCompany(models.Model):
    _inherit = 'res.company'

    lre_mutual_rate = fields.Float(
        string="Tasa Mutual (%)",
        digits=(5, 2),
        default=0.90,
        help="Tasa total a pagar (Base + Adicional por siniestralidad)"
    )

    lre_mutual_code = fields.Selection(
        MUTUAL_CODES,
        string="Código Organismo Administrador Ley 16.744 (1152)",
        default='2',
        help="Código oficial DT. Ojo: NO son los códigos Previred (101/102/105/107)."
    )

    lre_ccaf_code = fields.Selection(
        CCAF_CODES,
        string="Código CCAF (1110)",
        default='0',
        help="Caja de Compensación a la que está afiliada la empresa. "
             "'0' si no está afiliada a ninguna."
    )
