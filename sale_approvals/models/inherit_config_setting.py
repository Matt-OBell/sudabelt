from odoo import api, fields, models, _


class ResConfigInheritModel(models.TransientModel):
    _inherit = 'res.config.settings'

    email_send = fields.Boolean('Email Send', related='company_id.email_send', readonly=False)
    email_id_custom = fields.Many2one('mail.template', domain="[('model_id.model', '=', 'stock.picking')]",
                                      related='company_id.email_id_custom', string="Email Template", readonly=False)


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    email_send = fields.Boolean('Email Send')
    email_id_custom = fields.Many2one('mail.template', string="Email Template")
