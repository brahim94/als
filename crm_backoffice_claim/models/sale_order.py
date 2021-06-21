from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    partner_line_ids = fields.Many2many('res.partner',domain="[('partner_type', '=', 'line')]")