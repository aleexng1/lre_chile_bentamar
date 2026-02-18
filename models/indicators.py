from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class EconomicIndicator(models.Model):
    _name = 'lre.economic.indicator'
    _description = 'Economic Indicators (UF, UTM, UTA, IMM)'
    _order = 'date desc'

    indicator_type = fields.Selection([
        ('uf', 'UF'),
        ('utm', 'UTM'),
        ('uta', 'UTA'),
        ('imm', 'Ingreso Mínimo')
    ], string='Indicator Type', required=True, index=True)
    
    date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount', digits=(16, 2), required=True)

    _sql_constraints = [
        ('unique_indicator_date', 'unique(indicator_type, date)', 'The indicator value must be unique for the given date and type.')
    ]

    @api.model
    def get_value(self, indicator_type, date):
        """
        Helper method to get the value of an indicator for a specific date.
        If no exact match is found, it looks for the latest value on or before the given date.
        """
        indicator = self.search([
            ('indicator_type', '=', indicator_type),
            ('date', '<=', date)
        ], limit=1, order='date desc')
        return indicator.amount if indicator else 0.0
