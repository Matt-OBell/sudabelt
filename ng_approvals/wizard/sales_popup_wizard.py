# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleRejectReason(models.TransientModel):
    _name = 'sale.reject.reason.wizard'
    _description = 'Sales order reject reason wizard'

    reason = fields.Many2one('reject.reason', string='Reject Reason', required=1, domain=[('type', '=', 'sale')])

    def reject(self):
        sale_br_obj = self.env['sale.order'].browse(self._context.get('active_ids'))[0]
        sale_br_obj.write(
            {
                'state': 'rejected',
                'rejected_by': self.env.uid,
                'reject_reason': self.reason.name
            }
        )
        emails = [sale_br_obj.user_id.login.strip()]
        emails = ",".join(emails)
        sale_br_obj._escalate(emails, 'sale_rejection_template')

        ctx = self.env.context.copy()
        # ctx.update({'reject_reason': reason.name})
        # sale_br_obj.with_context(ctx).escalate_order()
        return True
