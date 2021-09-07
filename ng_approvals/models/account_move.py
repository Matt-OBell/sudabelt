from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import UserError, Warning, ValidationError
from urllib.parse import urljoin, urlencode
import base64


class AccountMove(models.Model):
    _inherit = "account.move"

    first_manager_approve_by = fields.Many2one(
        'res.users', string='Operation Manager Approved by', readonly=True, copy=False)
    second_manager_approve_by = fields.Many2one(
        'res.users', string='COO Approved by', readonly=True, copy=False)
    finance_manager_approve_by = fields.Many2one(
        'res.users', string='Finance Manager Approved by', readonly=True, copy=False)
    rejected_by = fields.Many2one('res.users', readonly=True, copy=False)
    reject_reason = fields.Text(readonly=True, copy=False)

    def action_operation_manager_approval(self):
        self.state = 'operation_manager'
        users = self.env.ref("ng_approvals.group_operation_manager").users
        recipients = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        recipients = ",".join(recipients)
        self._escalate(recipients)

    def action_coo_approval(self):
        self.state = 'coo'
        self.first_manager_approve_by = self.env.uid
        users = self.env.ref("ng_approvals.group_coo").users
        recipients = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        recipients = ",".join(recipients)
        self._escalate(recipients)

    def action_financial_manager_approval(self):
        self.state = 'finance_manager'
        self.second_manager_approve_by = self.env.uid
        users = self.env.ref("account.group_account_manager").users
        recipients = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        recipients = ",".join(recipients)
        self._escalate(recipients)

    def action_post(self):
        if not self.state == 'finance_manager':
            self.state = 'operation_manager'
        else:
            purchase = super(AccountMove, self).action_post()
            self.finance_manager_approve_by = self.env.uid
            # recipient = [self.user_id.login.strip()]
            # recipient = ",".join(recipient)
            # self._escalate(recipient, 'billing_approved')
            return purchase
        return

    def _escalate(self, email_to, template='billing_approval_template'):
        template = self.env['ir.model.data'].\
            get_object('ng_approvals', template)
        template.with_context(
            {
                "email_to": email_to,
                "url": self.request_link()
                # "products": products
            }
        ).send_mail(self.id, force_send=True)

    def request_link(self):
        fragment = {}
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        model_data = self.env["ir.model.data"]
        fragment.update(base_url=base_url)
        fragment.update(menu_id=model_data.get_object_reference("account", "menu_action_move_in_invoice_type")[1])
        fragment.update(model="account.move")
        fragment.update(view_type="form")
        fragment.update(action=model_data.get_object_reference("account", "action_move_in_invoice_type")[1])
        fragment.update(id=self.id)
        query = {"db": self.env.cr.dbname}
        res = urljoin(base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('operation_manager', 'Operation Manager'),
        ('coo', 'COO'),
        ('finance_manager', 'Finance Manager'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
