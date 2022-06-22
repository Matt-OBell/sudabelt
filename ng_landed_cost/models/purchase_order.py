from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    land_tran_other_journal_id = fields.Many2one('account.journal', "Journal", required=True)
    apply_cost = fields.Boolean(string='Landed Cost Apply ?', domain=[('type', '<>', 'view'), ('type', '<>', 'closed')],
                                states={'done': [('readonly', True)]}, default=True)

    land_account_id = fields.Many2one('account.account', string='Landed Cost Account',
                                      domain=[('type', '<>', 'view'), ('type', '<>', 'closed')],
                                      states={'done': [('readonly', True)]})

    landed_supplier = fields.Many2one('res.partner', string="Landed Partner")

    transport_supplier = fields.Many2one('res.partner', string="Transport Cost Partner")

    transport_account_id = fields.Many2one('account.account', string='Transportation Cost Account',
                                           domain=[('type', '<>', 'view'), ('type', '<>', 'closed')],
                                           states={'done': [('readonly', True)]})
    other_account_id = fields.Many2one('account.account', string='Other Cost Account',
                                       states={'done': [('readonly', True)]})
    land_description = fields.Char(string='Landed Cost Note', states={'done': [('readonly', True)]})
    transport_description = fields.Char(string='Transportation Cost Note', states={'done': [('readonly', True)]})
    other_description = fields.Char(string='Other Cost Note', states={'done': [('readonly', True)]})
    land_amount = fields.Float(string='Landed Cost Amount', states={'done': [('readonly', True)]})
    transport_amount = fields.Float(string='Transportation Cost Amount', states={'done': [('readonly', True)]})
    other_amount = fields.Float(string='Other Cost Amount', states={'done': [('readonly', True)]})

    @api.onchange('transport_supplier')
    def change(self):
        if self.transport_supplier:
            self.transport_account_id = self.transport_supplier.property_account_payable_id

    @api.onchange('landed_supplier')
    def changeme(self):
        if self.landed_supplier:
            self.land_account_id = self.landed_supplier.property_account_payable_id

    @api.model
    def _create_picking(self):
        """Creates the Landed Cost Parameters on Stock Picking"""
        res = super(PurchaseOrder, self)._create_picking()
        for order in self:
            if order.picking_ids:
                vals = {
                    'apply_cost': order.apply_cost,
                    'land_account_id': order.land_account_id.id,
                    'transport_account_id': order.transport_account_id.id,
                    'other_account_id': order.other_account_id.id,
                    'land_description': order.land_description,
                    'transport_description': order.transport_description,
                    'other_description': order.other_description,
                    'land_amount': order.land_amount,
                    'transport_amount': order.transport_amount,
                    'other_amount': order.other_amount,
                    'landed_supplier':order.landed_supplier.id,
                    'transport_supplier':order.transport_supplier.id,
                    'land_tran_other_journal_id':order.land_tran_other_journal_id.id
                }
                order.picking_ids.write(vals)
        return res

    @api.multi
    def action_view_picking(self):
        res = super(PurchaseOrder, self).action_view_picking()
        stock_picking_id = self.env['stock.picking'].search([('group_id', '=', self.name), ('state', '!=', 'done')])
        stock_picking_id.write({'currency_id': self.currency_id.id})
        for record in stock_picking_id:
            for stock_obj, purchase_obj in zip(record.pack_operation_product_ids, self.order_line):
                stock_obj.write({
                    'initial_price': purchase_obj.product_id.standard_price,
                    'initial_qty': purchase_obj.product_id.qty_available,
                    'current_price': purchase_obj.price_unit
                })
            return res





