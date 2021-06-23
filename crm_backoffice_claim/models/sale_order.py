from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    partner_line_ids = fields.Many2many('res.partner',domain="[('partner_type', '=', 'line')]")
    
class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Demande'),
        ('sent', 'Envoyée'),
        ('sale', 'Traitée'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')