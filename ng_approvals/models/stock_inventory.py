# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class Inventory(models.Model):
    _inherit = "stock.inventory"
    
    approval_id = fields.Many2one('res.users', string='Approved By', readonly=True, copy=False)
    request_by_id = fields.Many2one('res.users', string='Requested By', readonly=True, copy=False)
    reject_reason = fields.Text(readonly=True, copy=False)
    rejected_by = fields.Many2one('res.users', readonly=True, copy=False)
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('to approve', 'Send for Approval'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Approved'),
        ('done', 'Validated'),
        ('rejected', 'Rejected')],
        copy=False, index=True, readonly=True,
        default='draft')

    def action_start(self):
        inventory = super(Inventory, self).action_start()
        self.state = 'to approve'
        return inventory

    def action_inventory_manager_approve(self):
        self.state = 'awaiting_approval'
        self.request_by_id = self.env.uid
        users = self.env.ref("ng_approvals.group_inventory_manager").users
        emails = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        emails = ",".join(emails)
        self._escalate(emails)
        
    def action_approve(self):
        self.state = 'confirm'
        self.approval_id = self.env.uid
        
        if self.request_by_id:
            emails = [self.request_by_id.login.strip()]
            emails = ",".join(emails)
            self._escalate(emails, 'stock_owner_approval_template')
        
    def _escalate(self, email_to, template='stock_approval_template'):
        template = self.env['ir.model.data'].\
            get_object('ng_approvals', template)
        template.with_context(
            {
                "email_to": email_to,
                # "url": self.request_link()
            }
        ).send_mail(self.id, force_send=True)
