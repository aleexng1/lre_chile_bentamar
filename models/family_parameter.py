from odoo import models, fields

class LreFamilyBracket(models.Model):
    _name = 'lre.family.bracket'
    _description = 'Tramos Asignación Familiar'
    
    name = fields.Char(string='Nombre', required=True, help="Ej: Tramo A")
    min_income = fields.Float(string='Renta Mínima', digits=(16, 2))
    max_income = fields.Float(string='Renta Máxima', digits=(16, 2))
    amount = fields.Float(string='Monto Carga', digits=(16, 2))
