from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time


class Picking(models.Model):
    _inherit = 'stock.picking'

    picking_type = fields.Char(string="Purchase/Sales Type", related='picking_type_id.name')

    landed_supplier=fields.Many2one('res.partner',"Landed Supplier")
    transport_supplier=fields.Many2one('res.partner',"Transport Cost Supplier")
    land_tran_other_journal_id=fields.Many2one('account.journal', "Journal", required=True)
    apply_cost = fields.Boolean(string='Landed Cost Apply ?', states={'done': [('readonly', True)]}, default=True)
    land_account_id = fields.Many2one('account.account', string='Landed Cost Account',
                                      states={'done': [('readonly', True)]})
    transport_account_id = fields.Many2one('account.account', string='Transportation Cost Account',
                                           states={'done': [('readonly', True)]})
    other_account_id = fields.Many2one('account.account', string='Other Cost Account',
                                       states={'done': [('readonly', True)]})
    land_description = fields.Char(string='Landed Cost Note', states={'done': [('readonly', True)]})
    transport_description = fields.Char(string='Transportation Cost Note', states={'done': [('readonly', True)]})
    other_description = fields.Char(string='Other Cost Note', states={'done': [('readonly', True)]})
    land_amount = fields.Float(string='Landed Cost Amount', states={'done': [('readonly', True)]})
    transport_amount = fields.Float(string='Transportation Cost Amount', states={'done': [('readonly', True)]})
    other_amount = fields.Float(string='Other Cost Amount', states={'done': [('readonly', True)]})

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id)

    @api.multi
    def do_transfer(self):
        res = super(Picking, self).do_transfer()
        self.cal_standard_price()
        return res

    def cal_standard_price(self):
        all_landed_cost = self.land_amount + self.transport_amount + self.other_amount

        exchange_rate = (1 / self.currency_id.rate)

        total_cost = []

        if not self.currency_id:
            raise UserError(_('Please select a currency for this purchase'))

        for record in self.pack_operation_product_ids:
            if record.qty_done > 0.0:
                total_cost.append(record.current_price * record.qty_done * exchange_rate)
            else:
                total_cost.append(record.current_price * record.product_qty * exchange_rate)

        for record in self.pack_operation_product_ids:
            initial_val = record.initial_price * record.initial_qty
            if all_landed_cost > 0.0:
                if record.qty_done > 0.0:
                    current_val = record.current_price * record.qty_done * exchange_rate
                    landed_cost = (current_val / sum(total_cost)) * all_landed_cost
                    standard_price = (landed_cost + initial_val) / (record.initial_qty + record.qty_done)
                    record.product_id.write({'standard_price': standard_price})
                else:
                    current_val = record.current_price * record.product_qty * exchange_rate
                    landed_cost = (current_val / sum(total_cost)) * all_landed_cost
                    standard_price = (landed_cost + initial_val) / (record.initial_qty + record.product_qty)
                    record.product_id.write({'standard_price': standard_price})
                self.landed_cost_move()
            else:
                if record.qty_done > 0.0:
                    current_val = record.current_price * record.qty_done * exchange_rate
                    standard_price = (initial_val + current_val) / (record.initial_qty + record.qty_done)
                    record.product_id.write({'standard_price': standard_price})
                else:
                    current_val = record.current_price * record.product_qty * exchange_rate
                    standard_price = (initial_val + current_val) / (record.initial_qty + record.product_qty)
                    record.product_id.write({'standard_price': standard_price})

    def landed_cost_move(self):
        self.update_stock_move()
        move_obj = self.env['account.move']
        move_obj_line = self.env['account.move.line'].with_context(check_move_validity=False)

        landed_cost_account = ['land_account_id', 'transport_account_id', 'other_account_id']
        landed_cost = ['land_amount', 'transport_amount', 'other_amount']
        landed_supplier = ['landed_supplier', 'transport_supplier', 'partner_id']

        acc_move = move_obj.create({
            'journal_id': self.land_tran_other_journal_id.id,
            'date': time.strftime('%Y-%m-%d'),
            'ref': self.name
        })

        for record_cost, record_acc, supplier in zip(landed_cost, landed_cost_account, landed_supplier):
            if self[record_acc]:
                move_obj_line.create({
                    'account_id': self[record_acc].id,
                    'credit': self[record_cost],
                    'debit': 0.0,
                    'move_id': acc_move.id,
                    'name': self.name,
                    'partner_id': self[supplier].id if self[supplier] else '/'
                })

                move_obj_line.create({
                    'account_id': self[record_acc].id,
                    'credit': 0.0,
                    'debit': self[record_cost],
                    'move_id': acc_move.id,
                    'name': self.name,
                    'partner_id': self[supplier].id if self[supplier] else '/'
                })
        acc_move.post()

    def update_stock_move(self):
        stock_obj = self.env['stock.move'].search([('picking_id', '=', self.name)])
        for record, stock_obj in zip(self.pack_operation_product_ids, stock_obj):
            stock_obj.write({'move_average_cost': record.product_id.standard_price, 'move_cost': record.current_price})


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    initial_price = fields.Float(string="Initial Price")
    initial_qty = fields.Float(string="Initial Qty")
    current_price = fields.Float(string="Current Price")



