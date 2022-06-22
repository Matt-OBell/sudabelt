from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, UserError


class AccountMoveExt(models.Model):
    _inherit = "account.move"

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('fm', 'Finance Manager'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    def send_to_fm(self):
        user = self.env['res.users'].search([])
        email = ""
        for s in user:
            if s.has_group('account.group_account_manager'):
                email = s.partner_id.email
                break
        if email:
            print("<<<<<<<<email>>>>>>>>")
            print(email)
            self.hi_sending_email(email)
        self.write({'state': 'fm'})

    def validate_fm(self):
        self.action_post()

    def button_reject_fm(self):
        self.show_reset_to_draft_button = True
        self.write({'state': 'reject'})

    def set_draft(self):
        self.write({'state': 'draft'})

    def hi_sending_email(self, email):
        if self.env.user.company_id.email_send:
            if self.env.user.company_id.email_id_custom:
                template = self.env.user.company_id.email_id_custom
                template.email_to = email
                self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
                print('Email Sent')
        #     else:
        #         raise UserError("No Email Template selected for Approval Notification")
        # else:
        #     raise UserError("Send Email Not Checked in Configuration")
