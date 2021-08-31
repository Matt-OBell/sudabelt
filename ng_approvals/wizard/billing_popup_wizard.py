from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseWizard(models.TransientModel):
    _name = 'billing.reject.reason.wizard'

    reason = fields.Many2one(
        'reject.reason', string='Reject Reason', required=1)

    def reject(self):
        billing_br_obj = self.env['account.move'].browse(self._context.get('active_ids'))[0]
        billing_br_obj.write(
            {
                'state': 'rejected',
                'rejected_by': self.env.uid,
                'reject_reason': self.reason.name
            }
        )
        emails = [billing_br_obj.user_id.login.strip()]
        emails = ",".join(emails)
        billing_br_obj._escalate(emails, 'billing_rejection_template')

        ctx = self.env.context.copy()
        # ctx.update({'reject_reason': reason.name})
        # sale_br_obj.with_context(ctx).escalate_order()
        return True
