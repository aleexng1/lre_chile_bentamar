from odoo import models, fields, api
from odoo.tools import ormcache

class LreAfpParameter(models.Model):
    _name = 'lre.afp.parameter'
    _description = 'Parámetros de AFP (Tasas y Comisiones)'
    
    name = fields.Char(string='Nombre', required=True)
    code = fields.Selection([
        ('capital', 'Capital'),
        ('cuprum', 'Cuprum'),
        ('habitat', 'Habitat'),
        ('modelo', 'Modelo'),
        ('planvital', 'PlanVital'),
        ('provida', 'Provida'),
        ('uno', 'Uno')
    ], string='Código', required=True)
    
    rate_employee = fields.Float(string='Tasa Trabajador (%)', digits=(5, 2), 
                               help="Ej: 11.27 (10% obligatorio + 1.27% comisión)")
    rate_sis = fields.Float(string='Tasa SIS (%)', digits=(5, 2), help="Ej: 1.49")
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'El código de AFP debe ser único.')
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
    @ormcache('afp_code')
    def get_rates(self, afp_code):
        """
        Retorna las tasas cacheadas de la AFP dado su código.
        Cache se invalida al crear/escribir/eliminar parámetros AFP.
        :param afp_code: Código de la AFP (str o similar)
        :return: dict {'employee': float, 'sis': float}
        """
        if not afp_code:
            return {'employee': 0.0, 'sis': 0.0}
            
        # Conversión robusta: string y minúsculas
        code_normalized = str(afp_code).lower()
        
        afp = self.search([('code', '=', code_normalized)], limit=1)
        if afp:
            return {
                'employee': afp.rate_employee,
                'sis': afp.rate_sis
            }
        return {'employee': 0.0, 'sis': 0.0}
