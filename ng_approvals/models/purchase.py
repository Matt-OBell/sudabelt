from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import UserError, Warning, ValidationError
from urllib.parse import urljoin, urlencode
import base64


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    first_approve_by = fields.Many2one(
        'res.users', string='Internal Control Approved By', readonly=True, copy=False)
    second_manager_approve_by = fields.Many2one(
        'res.users', string='Process Manager Approved By', readonly=True, copy=False)
    rejected_by = fields.Many2one('res.users', readonly=True, copy=False)
    reject_reason = fields.Text(readonly=True, copy=False)
    is_record_owner = fields.Boolean(
        readonly=1, compute='_compute_record_owner', copy=False, store=False, default=False)
    is_my_approval = fields.Boolean(
        readonly=1, compute='_compute_approval_mode', copy=False, store=False, search="_search_field")
    order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines',
                                 states={
                                     'internal_control': [('readonly', True)],
                                     'to approve': [('readonly', True)],
                                     'cancel': [('readonly', True)],
                                     'done': [('readonly', True)],
                                     'rejected': [('readonly', True)], }, copy=True)

    READONLY_STATES = {
        'internal_control': [('readonly', True)],
        'to approve': [('readonly', True)],
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
        'rejected': [('readonly', True)],
    }

    def _compute_record_owner(self):
        if int(self.user_id) == int(self.env.uid):
            self.is_record_owner = True
        else:
            self.is_record_owner = False

    def action_reject_approval(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "ir.reject.wizard",
            "views": [[False, "form"]],
            "context": {"reject": self.id},
            "target": "new",
        }

    def action_internal_control_approval(self):
        self.state = 'internal_control'
        users = self.env.ref("ng_approvals.group_internal_control").users
        recipients = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        recipients = ",".join(recipients)
        self._escalate(recipients)

    def button_confirm(self):
        for order in self:
            if order.state not in ['internal_control']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                self.first_approve_by = self.env.uid
                users = self.env.ref("purchase.group_purchase_manager").users
                recipients = [user.partner_id.email.strip() for user in users if user.partner_id.email]
                recipients = ",".join(recipients)
                self._escalate(recipients)
                order.write({'state': 'to approve'})
        return True

    def button_approve(self, force=False):
        purchase = super(PurchaseOrder, self).button_approve(force)
        self.second_manager_approve_by = self.env.uid
        recipient = [self.user_id.login.strip()]
        recipient = ",".join(recipient)
        self._escalate(recipient, 'purchase_order_approved')
        return purchase

    def _escalate(self, email_to, template='purchase_approval_template'):
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
        fragment.update(menu_id=model_data.get_object_reference("ng_approvals", "menu_purchase_approval")[1])
        fragment.update(model="purchase.order")
        fragment.update(view_type="form")
        fragment.update(action=model_data.get_object_reference("ng_approvals", "action_purchase_approval")[1])
        fragment.update(id=self.id)
        query = {"db": self.env.cr.dbname}
        res = urljoin(base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    def _compute_approval_mode(self):
        for record in self:
            if record.state == 'internal_control' and \
                    self.env.user.has_group('ng_approvals.group_internal_control'):
                record.write({'is_my_approval': True})
            elif record.state == 'to approve' and \
                    self.env.user.has_group('purchase.group_purchase_manager'):
                record.write({'is_my_approval': True})
            else:
                record.write({'is_my_approval': False})

    def _search_field(self, operator, value):
        field_id = self.search([]).filtered(lambda x: x.is_my_approval == value)
        return [('id', operator, [x.id for x in field_id] if field_id else False)]

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('internal_control', 'Internal Control'),
        ('to approve', 'Process Manager'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

