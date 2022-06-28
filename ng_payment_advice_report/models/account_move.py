
from odoo import models, fields, api

from num2words import num2words



def amt2words(amount, currency='USD'):
    return num2words(amount, to='currency', currency=currency).replace("dollars", "naira").replace("cents", "kobo").capitalize()



class AccountVoucher(models.Model):

    @api.depends('amount_total')
    def amount_to_text(self):
        for rec in self:
            if rec.amount_total:
                rec.amount_in_word = amt2words(rec.amount_total)
            else:
                rec.amount_in_word = None
  

    _inherit = 'account.move'


    amount_in_word=fields.Text("Amount in Word",compute=amount_to_text)
