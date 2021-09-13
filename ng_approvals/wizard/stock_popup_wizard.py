# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockRejectReason(models.TransientModel):
    _name = 'stock.reject.reason.wizard'
    _description = 'Inventory adjustment reject reason wizard'

    reason = fields.Many2one('reject.reason', string='Reject Reason', required=1, domain=[('type', '=', 'stock')])

    def reject(self):
        stock_br_obj = self.env['stock.inventory'].browse(self._context.get('active_ids'))[0]
        stock_br_obj.write(
            {
                'state': 'rejected',
                'rejected_by': self.env.uid,
                'reject_reason': self.reason.name
            }
        )
        if stock_br_obj.request_by_id:
            emails = [stock_br_obj.request_by_id.login.strip()]
            emails = ",".join(emails)
            stock_br_obj._escalate(emails, 'stock_rejection_template')

        ctx = self.env.context.copy()
        # ctx.update({'reject_reason': reason.name})
        # stock_br_obj.with_context(ctx).escalate_order()
        return True
