from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import ormcache

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

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_cache()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res

    @api.model
    @ormcache('indicator_type', 'str(date)')
    def get_value(self, indicator_type, date):
        """
        Cached helper to get the value of an indicator for a specific date.
        If no exact match is found, it looks for the latest value on or before the given date.
        Cache is invalidated on write/create/unlink of any indicator.
        """
        indicator = self.search([
            ('indicator_type', '=', indicator_type),
            ('date', '<=', date)
        ], limit=1, order='date desc')
        return indicator.amount if indicator else 0.0
