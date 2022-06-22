import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    date_start = fields.Date(string="Start Date")
    date_until = fields.Date(string="Date Until")


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_id')
    def get_bom(self):
        if self.product_id:
            print self.bom_id.product_tmpl_id.name
            if self.bom_id.date_until >= time.strftime(DEFAULT_SERVER_DATE_FORMAT):
                raise UserError(_('Product Not Available'))


