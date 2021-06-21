from odoo import api, fields, models

class CrmClaim(models.Model):
    _inherit = "crm.claim"

    line_id = fields.Many2many('res.partner',domain="[('partner_type', '=', 'line')]")
    is_called_back = fields.Boolean(string="Souhaitez vous être appelé ?")
    num_bus = fields.Char(string="Numéro du bus")
    categ_id = fields.Many2one(comodel_name="crm.claim.category", string="Category", domain="[('claim_type', '=', claim_type)]")

class CrmClaimCategory(models.Model):
    _inherit = "crm.claim.category"

    claim_type = fields.Many2one('crm.claim.type',string="Claim Type")