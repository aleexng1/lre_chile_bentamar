from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    lre_mutual_rate = fields.Float(
        string="Tasa Mutual (%)",
        digits=(5, 2),
        default=0.90,
        help="Tasa total a pagar (Base + Adicional por siniestralidad)"
    )

    lre_mutual_code = fields.Selection([
        ('101', '101 - ACHS'),
        ('102', '102 - MUSEG (Mutual de Seguridad CChC)'),
        ('105', '105 - ISL (Instituto de Seguridad Laboral)'),
        ('107', '107 - IST'),
    ], string="Código Organismo Administrador (LRE)", default='102')
