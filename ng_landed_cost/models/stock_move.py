from odoo import models, fields


class stock_move(models.Model):
    _inherit = 'stock.move'

    move_average_cost = fields.Float(string="Move Average Cost", default=0.00)

    move_cost = fields.Float(string="Move Cost", default=0.00)
