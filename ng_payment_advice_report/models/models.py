
from odoo import models, fields, api
# import inflect
from odoo.tools.amount_to_text_en import amount_to_text



class AccountVoucher(models.Model):

    @api.multi
    @api.depends('amount')
    def amount_to_text(self):
        for content in self:
            if content.amount:
                a = amount_to_text(content.amount, currency='Naira').replace('Cent', 'kobo')
                content.amount_in_word = a

    _inherit = 'account.voucher'


    amount_in_word=fields.Text("Amount in Word",compute=amount_to_text)
