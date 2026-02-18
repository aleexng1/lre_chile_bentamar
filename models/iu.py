from odoo import api, fields, models


class LREIUTablePeriod(models.Model):
    _name = "lre.iu_table_period"
    _description = "Tabla Impuesto Único por Año/Mes"
    _order = "year desc, month desc"
    _rec_name = "name"

    name = fields.Char("Nombre", compute="_compute_name", store=True)
    year = fields.Integer("Año", required=True)
    month = fields.Selection(
        [(str(m).zfill(2), fields.Date.to_date(f"2000-{m:02d}-01").strftime("%B").capitalize())
         for m in range(1, 13)],
        string="Mes", required=True
    )
    currency_id = fields.Many2one(
        "res.currency", string="Moneda", required=True,
        default=lambda s: s.env.company.currency_id.id
    )
    notes = fields.Text("Notas")
    line_ids = fields.One2many("lre.iu_bracket_period", "table_id", string="Tramos")

    _sql_constraints = [
        ("uniq_period", "unique(year, month)", "Ya existe una tabla IU para ese Año/Mes."),
    ]

    @api.depends("year", "month")
    def _compute_name(self):
        for r in self:
            r.name = f"IU {r.year}-{r.month}" if (r.year and r.month) else "IU (sin período)"

    # helper para futuros cálculos
    def compute_tax_amount(self, imponible_amount):
        """Impuesto = imponible * factor - rebaja"""
        self.ensure_one()
        if imponible_amount <= 0:
            return 0.0
        lines = self.line_ids.sorted(lambda l: (l.base_from_amount, l.sequence))
        for ln in lines:
            if ln.base_to_amount and imponible_amount > ln.base_to_amount:
                continue
            if imponible_amount >= ln.base_from_amount and (not ln.base_to_amount or imponible_amount <= ln.base_to_amount):
                # usar factor (proporción). Si no está, caer a rate_percent/100 para retrocompatibilidad
                factor = (ln.factor if ln.factor else (ln.rate_percent or 0.0) / 100.0)
                return max(0.0, (imponible_amount * factor) - (ln.rebate_amount or 0.0))
        return 0.0


class LREIUBracketPeriod(models.Model):
    _name = "lre.iu_bracket_period"
    _description = "Tramo IU por Año/Mes"
    _order = "sequence, base_from_amount"

    table_id = fields.Many2one("lre.iu_table_period", required=True, ondelete="cascade")
    sequence = fields.Integer("Secuencia", default=10)

    base_from_amount = fields.Monetary("Base desde", required=True, currency_field="currency_id")
    base_to_amount = fields.Monetary("Base hasta", currency_field="currency_id", help="Dejar vacío para 'sin tope'")

    # NUEVO: factor (proporción del SII: 0.04, 0.08, 0.135, 0.4, etc.)
    factor = fields.Float("Factor", digits=(16, 6), help="Proporción del SII, ej. 0.04 = 4%")

    # Dejamos rate_percent por compatibilidad (si ya lo tenías cargado)
    rate_percent = fields.Float("Tasa (%)", digits=(16, 6))

    rebate_amount = fields.Monetary("Rebaja (monto)", required=True, currency_field="currency_id", help="Monto fijo a restar")
    currency_id = fields.Many2one(related="table_id.currency_id", store=True, readonly=True)
    active = fields.Boolean(default=True)

    @api.constrains("base_from_amount", "base_to_amount", "factor", "rate_percent", "rebate_amount")
    def _check_values(self):
        for r in self:
            if r.base_from_amount < 0:
                raise ValueError("Base desde no puede ser negativa.")
            if r.base_to_amount and r.base_to_amount <= r.base_from_amount:
                raise ValueError("Base hasta debe ser mayor que Base desde.")
            if r.factor is not None and r.factor < 0:
                raise ValueError("El factor no puede ser negativo.")
            if r.rate_percent is not None and r.rate_percent < 0:
                raise ValueError("La tasa (%) no puede ser negativa.")
            if r.rebate_amount < 0:
                raise ValueError("La rebaja no puede ser negativa.")

    # Normalización: si alguien rellena solo tasa%, calculamos factor automáticamente
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("factor") and vals.get("rate_percent") is not None:
                try:
                    vals["factor"] = float(vals["rate_percent"]) / 100.0
                except (ValueError, TypeError):
                    vals["factor"] = 0.0
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "factor" not in vals and "rate_percent" in vals and vals["rate_percent"] is not None:
            try:
                vals["factor"] = float(vals["rate_percent"]) / 100.0
            except Exception:
                vals["factor"] = 0.0
        return super().write(vals)