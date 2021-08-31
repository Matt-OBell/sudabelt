from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseWizard(models.TransientModel):
    _name = 'purchase.reject.reason.wizard'

    reason = fields.Many2one(
        'reject.reason', string='Reject Reason', required=1)

    def reject(self):
        purchase_br_obj = self.env['purchase.order'].browse(self._context.get('active_ids'))[0]
        purchase_br_obj.write(
            {
                'state': 'rejected',
                'rejected_by': self.env.uid,
                'reject_reason': self.reason.name
            }
        )
        emails = [purchase_br_obj.user_id.login.strip()]
        emails = ",".join(emails)
        purchase_br_obj._escalate(emails, 'purchase_rejection_template')

        ctx = self.env.context.copy()
        # ctx.update({'reject_reason': reason.name})
        # sale_br_obj.with_context(ctx).escalate_order()
        return True
