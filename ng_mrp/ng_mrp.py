# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mattobell (<http://www.mattobell.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

# import datetime
import time
from odoo import tools

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
# from odoo.osv import osv, orm
from odoo.exceptions import UserError
from odoo import netsvc
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pick_production = fields.Many2one('mrp.production', 'Production', select=True)


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    production_id1 = fields.Many2one('mrp.production', 'Production', select=True)


class mrp_routing(models.Model):
    _inherit = 'mrp.routing'
    writeoff_account_id = fields.Many2one('account.account', string='Write Off Account')
    journal_id = fields.Many2one('account.journal', string='Account Journal')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')#todoprobuse, domain=[('type', '!=', 'view')],
    total_cost_wc = fields.Float(string='Total Workcenter Cost', )
    raw_cost = fields.Float(string='Total Raw Material Cost')
    total_cost = fields.Float(string='Total Cost', readonly=True)
    total_cost_unit = fields.Float(string='Cost per Unit', readonly=True)
    move_loss_ids = fields.One2many('stock.move', 'production_id1', string='Product Off (Product Gain/Loss)', states={'done':[('readonly', False)]}, copy=False)
    wip_amount = fields.Float(string='WIP Amount')

    @api.multi
    def next_stage(self):
        self.state = 'submitted'

    @api.v7
#    def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        
        move_pool = self.pool.get('account.move')  
        period_pool = self.pool.get('account.period')
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)
        wf_service = netsvc.LocalService("workflow")
        wip_amount = production.wip_amount
#         period_id = period_pool.find(cr, uid, production.date_planned, context=context)[0]
        timenow = time.strftime('%Y-%m-%d')

        currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        currency_obj = self.pool.get('res.currency')
        currency = currency_obj.browse(cr, uid, currency_id, context=context)
        
        res = super(MrpProduction, self).action_produce(cr, uid, production_id, production_qty, production_mode, wiz=wiz, context=context)

        if production_mode == 'consume_produce':
            move = {
                'narration': production.name + ' / Finished Product: ' + production.product_id.name,
                'date': production.date_planned,
                'ref': production.name,
                'journal_id': production.routing_id.journal_id.id,
#                 'period_id': period_id,
            }
            t = 0.0
            total = 0.0
            moves = []
            total_credit = 0.0
            for i in production.product_lines:#row matrial entry.
                t = i.product_qty * i.product_id.standard_price
                print i.product_id
                print i.product_id.name,":::::::::::::::"
                total += currency_obj.round(cr, uid, currency, t)
                if not i.product_id.property_stock_production.valuation_out_account_id:
                    raise Warning(_('Error !'),_('Please define stock valuation account (incoming/outgoing) on production location defined on row material used'))
                credit_line = (0, 0, {
                        'name': production.name + ' / ' + i.product_id.name ,
                        'date': production.date_planned,
    #                        'partner_id': partner_id,
                        'account_id': i.product_id.property_stock_production.valuation_out_account_id.id,
                        'journal_id':  production.routing_id.journal_id.id,
#                         'period_id': period_id,
                        'debit': 0.0,
                        'credit': currency_obj.round(cr, uid, currency, t),
                    })
                moves.append(credit_line)
            
            total_credit += total
            for p in production.workcenter_lines:
                overhead_costs = p.workcenter_id.labor_cost + p.workcenter_id.electric_cost + p.workcenter_id.consumables_cost + p.workcenter_id.rent_cost + p.workcenter_id.other_cost
                credit_line = (0, 0, {
                        'name': production.name + ' / ' + p.workcenter_id.name,
                        'date': production.date_planned,
    #                        'partner_id': partner_id,
                        'account_id': p.workcenter_id.wip_account_id.id,
                        'journal_id':  production.routing_id.journal_id.id,
#                         'period_id': period_id,
                        'debit': 0.0,
                        'credit': currency_obj.round(cr, uid, currency, overhead_costs*production.product_qty),
                    })
                moves.append(credit_line)
                total_credit += currency_obj.round(cr, uid, currency, overhead_costs*production.product_qty)
#            credit_line = (0, 0, {
#                    'name': production.name,
#                    'date': production.date_planned,
##                        'partner_id': partner_id,
#                    'account_id': production.workcenter_lines[0].workcenter_id.wip_account_id.id,
#                    'journal_id':  production.routing_id.journal_id.id,
#                    'period_id': period_id,
#                    'debit': 0.0,
#                    'credit': wip_amount,
#                })

            if not production.product_id.categ_id.property_stock_valuation_account_id:
                raise Warning(_('Error !'),_('Please define Stock Valuation Account on Product category of finish product.'))
            product_account = production.product_id.categ_id.property_stock_valuation_account_id.id
            print "============================="
            print wip_amount, total
            print wip_amount+total
            print "============================="
            print "Total credit", total_credit
            print "currency_obj.round(cr, uid, currency, total_credit)",currency_obj.round(cr, uid, currency, total_credit)
            print "currency_obj.round(cr, uid, currency, wip_amount+total)",currency_obj.round(cr, uid, currency, wip_amount+total)
            debit_line = (0, 0, {
                    'name': production.name + ' / ' + ' Inventory Valuation of Product ' +  production.product_id.name,
                    'date': production.date_planned,
#                        'partner_id': partner_id,
                    'account_id': product_account,
                    'journal_id': production.routing_id.journal_id.id,
#                     'period_id': period_id,
#                    'debit': round(wip_amount+total),
                    'debit': currency_obj.round(cr, uid, currency, wip_amount+total),
                    'credit': 0.0,
                    'analytic_account_id': production.analytic_account_id and production.analytic_account_id.id or False
                })
            
            
            #write off entry:
            total_debit = round(wip_amount+total)
            total_credit = round(total_credit)
            d = 0.0
            c = 0.0
            print "total_credit   total_credit::::::::::::",total_credit,total_debit
            if total_credit <> total_debit:
                if total_credit > total_debit:
                   d = total_credit - total_debit
                   c = 0.0
                else:
                   c = total_debit - total_credit
                   d = 0.0
                if not production.routing_id.writeoff_account_id:
                    raise Warning(_('Error !'),_('Please define write off account on routing.'))
                l = (0, 0, {
                        'name': production.name + ' / ' + ' Write Off Entry ' +  production.product_id.name,
                        'date': production.date_planned,
    #                        'partner_id': partner_id,
                        'account_id': production.routing_id.writeoff_account_id.id,
                        'journal_id': production.routing_id.journal_id.id,
#                         'period_id': period_id,
                        'debit': d,
                        'credit': c,
#                        'analytic_account_id': production.analytic_account_id and production.analytic_account_id.id or False
                    })
                print ":::::::::l::::::::::::::::::",l
                moves.append(l)
            moves.append(debit_line)
            move.update({'line_ids': moves})
            move_id = move_pool.create(cr, uid, move, context=context)
            print ":::::::::::::move:::::::::::",move
        print "::::::::::::action_produce:::::::::res:::::::::::",res
        return res

    
#    @api.one
#    def action_produce(self, production_id, production_qty, production_mode):
#        print ":::::::::::LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
#        move_pool = self.env['account.move']  
#        period_pool = self.env['account.period']
#        production = self.browse(production_id)
#        wip_amount = production.wip_amount
#        period_id = period_pool.find(production.date_planned)[0]
#
#        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id.id
#        currency_obj = self.env['res.currency']
#        currency = currency_obj.browse(currency_id)
#        
#        super(mrp_production, self).action_produce(production_id, production_qty, production_mode)
#
#        if production_mode == 'consume_produce':
#            move = {
#                'narration': production.name + ' / Finished Product: ' + production.product_id.name,
#                'date': production.date_planned,
#                'ref': production.name,
#                'journal_id': production.routing_id.journal_id.id,
#                'period_id': period_id,
#            }
#            t = 0.0
#            total = 0.0
#            moves = []
#            total_credit = 0.0
#            for i in production.product_lines:  # row matrial entry.
#                t = i.product_qty * i.product_id.standard_price
#                total += currency_obj.round(currency, t)
#                if not i.product_id.property_stock_production.valuation_out_account_id:
#                    raise Warning( _('Please define stock valuation account (incoming/outgoing) on production location defined on row material used'))
#                credit_line = (0, 0, {
#                        'name': production.name + ' / ' + i.product_id.name ,
#                        'date': production.date_planned,
#    #                        'partner_id': partner_id,
#                        'account_id': i.product_id.property_stock_production.valuation_out_account_id.id,
#                        'journal_id':  production.routing_id.journal_id.id,
#                        'period_id': period_id,
#                        'debit': 0.0,
#                        'credit': currency_obj.round(currency, t),
#                    })
#                moves.append(credit_line)
#            
#            total_credit += total
#            for p in production.workcenter_lines:
#                overhead_costs = p.workcenter_id.labor_cost + p.workcenter_id.electric_cost + p.workcenter_id.consumables_cost + p.workcenter_id.rent_cost + p.workcenter_id.other_cost
#                credit_line = (0, 0, {
#                        'name': production.name + ' / ' + p.workcenter_id.name,
#                        'date': production.date_planned,
#    #                        'partner_id': partner_id,
#                        'account_id': p.workcenter_id.wip_account_id.id,
#                        'journal_id':  production.routing_id.journal_id.id,
#                        'period_id': period_id,
#                        'debit': 0.0,
#                        'credit': currency_obj.round(currency, overhead_costs * production.product_qty),
#                    })
#                moves.append(credit_line)
#                total_credit += currency_obj.round(currency, overhead_costs * production.product_qty)
#
#            if not production.product_id.categ_id.property_stock_valuation_account_id:
#                raise Warning( _('Please define Stock Valuation Account on Product category of finish product.'))
#            product_account = production.product_id.categ_id.property_stock_valuation_account_id.id
#            debit_line = (0, 0, {
#                'name': production.name + ' / ' + ' Inventory Valuation of Product ' + production.product_id.name,
#                'date': production.date_planned,
#                'account_id': product_account,
#                'journal_id': production.routing_id.journal_id.id,
#                'period_id': period_id,
#                'debit': currency_obj.round(currency, wip_amount + total),
#                'credit': 0.0,
#                'analytic_account_id': production.analytic_account_id and production.analytic_account_id.id or False
#            })
#            
#            # write off entry:
#            total_debit = round(wip_amount + total)
#            total_credit = round(total_credit)
#            d = 0.0
#            c = 0.0
#            if total_credit <> total_debit:
#                if total_credit > total_debit:
#                    d = total_credit - total_debit
#                    c = 0.0
#                else:
#                    c = total_debit - total_credit
#                    d = 0.0
#                if not production.routing_id.writeoff_account_id:
#                    raise Warning( _('Please define write off account on routing.'))
#                l = (0, 0, {
#                        'name': production.name + ' / ' + ' Write Off Entry ' + production.product_id.name,
#                        'date': production.date_planned,
#                        'account_id': production.routing_id.writeoff_account_id.id,
#                        'journal_id': production.routing_id.journal_id.id,
#                        'period_id': period_id,
#                        'debit': d,
#                        'credit': c,
#                    })
#                moves.append(l)
#            moves.append(debit_line)
#            move.update({'line_id': moves})
#            move_id = move_pool.create(move)
#        return True
#    
    @api.multi
    def action_ready(self):
        print ":::::::::::LLLLLLLLLLLLLLLLLLLLsssssssssssssLLLLLLLLLLLL"
#        t = 0.0
        production = self
#        for i in production.product_lines:
#            t += i.product_qty * i.product_id.standard_price
#        
        move_pool = self.env['account.move']  
#         period_pool = self.env['account.period']

        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id.id
        currency_obj = self.env['res.currency']
        currency = currency_obj.browse(currency_id)
        
        res = super(MrpProduction, self).action_ready()
        
        for production in self:
            prd_qty = production.product_qty
            flag = False
            wip_amount = 0.0
            for p in production.workcenter_lines:
                print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
#                 period_id = period_pool.find(production.date_planned)
                timenow = time.strftime('%Y-%m-%d')
                if not production.routing_id.journal_id:
                    raise Warning( _('Please define Journal on Routing.'))
                if not p.workcenter_id.wip_account_id:
                    raise Warning( _('Please define Work in Progress Account Workcenter.'))
                move = {
                    'narration': production.name + ' / Finished Product: ' + production.product_id.name,
                    'date': production.date_planned,
                    'ref': production.name,
                    'journal_id': production.routing_id.journal_id.id,
#                     'period_id': period_id.id,
                }
                if p.workcenter_id.labor_cost > 0.0 and not p.workcenter_id.labor_cost_id:
                    raise Warning( _('Please configure Labor cost account on workcenter %s.') % (p.workcenter_id.name))
                if p.workcenter_id.electric_cost > 0.0 and not p.workcenter_id.electric_cost_id:
                    raise Warning( _('Please configure Electric cost account on workcenter %s.') % (p.workcenter_id.name))
                if p.workcenter_id.consumables_cost > 0.0 and not p.workcenter_id.consumables_cost_account_id:
                    raise Warning( _('Please configure Consumable cost account on workcenter %s.') % (p.workcenter_id.name))
                if p.workcenter_id.rent_cost > 0.0 and not p.workcenter_id.rent_cost_id:
                    raise Warning( _('Please configure Rent cost account on workcenter %s.') % (p.workcenter_id.name))
                if p.workcenter_id.other_cost > 0.0 and not p.workcenter_id.other_cost_id:
                    raise Warning( _('Please configure Other cost account on workcenter %s.') % (p.workcenter_id.name))

                if not flag:  # if else does not matter..not used any more ... same entries..todo ..remove if else.
                    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&sadfdff adfdsfsdf &&&&&sdfsdf&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                    print p.workcenter_id.labor_cost , p.workcenter_id.electric_cost ,  p.workcenter_id.consumables_cost ,  p.workcenter_id.rent_cost ,  p.workcenter_id.other_cost
                    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&sadfdsfdasfdsfdsa&&&&&&&&&&&&&&&&&&&&&&&sdfsfdsf"
                    overhead_costs = p.workcenter_id.labor_cost + p.workcenter_id.electric_cost + p.workcenter_id.consumables_cost + p.workcenter_id.rent_cost + p.workcenter_id.other_cost
                    credit_line1 = False
                    credit_line2 = False
                    credit_line3 = False
                    credit_line4 = False
                    credit_line5 = False
                    if p.workcenter_id.labor_cost > 0.0:
                        print "p.workcenter_id.labor_cost:::::::prd_qty:::::::::::",p.workcenter_id.labor_cost,prd_qty
                        credit_line1 = (0, 0, {
                            'name': production.name + ' / ' + p.workcenter_id.labor_cost_account_id.name,
                            'date': production.date_planned,
                            'account_id': p.workcenter_id.labor_cost_id.id,
                            'journal_id':  production.routing_id.journal_id.id,
#                             'period_id': period_id.id,
                            'debit': 0.0,
                            'credit': currency.round(p.workcenter_id.labor_cost * prd_qty),
                            })
                    if p.workcenter_id.electric_cost > 0.0:
                        credit_line2 = (0, 0, {
                                'name': production.name + ' / ' + p.workcenter_id.electric_cost_account_id.name,
                                'date': production.date_planned,
                                'account_id': p.workcenter_id.electric_cost_id.id,
                                'journal_id':  production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': 0.0,
                                'credit': currency.round(p.workcenter_id.electric_cost * prd_qty),
                            })
                    if p.workcenter_id.consumables_cost > 0.0:
                        credit_line3 = (0, 0, {
                                'name': production.name + ' / ' + p.workcenter_id.consumables_cost_id.name,
                                'date': production.date_planned,
                                'account_id': p.workcenter_id.consumables_cost_id.id,
                                'journal_id':  production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': 0.0,
                                'credit': currency.round(p.workcenter_id.consumables_cost * prd_qty),
                            })
                    if p.workcenter_id.rent_cost > 0.0:
                        credit_line4 = (0, 0, {
                                'name': production.name + ' / ' + p.workcenter_id.rent_cost_account_id.name,
                                'date': production.date_planned,
                                'account_id':p.workcenter_id.rent_cost_id.id,
                                'journal_id':  production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': 0.0,
                                'credit': currency.round(p.workcenter_id.rent_cost * prd_qty),
                            })
                    if p.workcenter_id.other_cost > 0.0:
                        credit_line5 = (0, 0, {
                                'name': production.name + ' / ' + p.workcenter_id.other_cost_account_id.name,
                                'date': production.date_planned,
                                'account_id': p.workcenter_id.other_cost_id.id,
                                'journal_id':  production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': 0.0,
                                'credit': currency.round(p.workcenter_id.other_cost * prd_qty),
                            })
                    debit_wip = currency.round(overhead_costs * prd_qty)
                    wip_amount += currency.round(debit_wip)
                    debit_line = (0, 0, {
                            'name': production.name,
                            'date': production.date_planned,
    #                        'partner_id': partner_id,
                            'account_id': p.workcenter_id.wip_account_id.id,
                            'journal_id': production.routing_id.journal_id.id,
#                             'period_id': period_id.id,
                            'debit': currency.round(debit_wip),
                            'credit': 0.0,
                        })

                    # write off entry:
                    total_debit = debit_wip
                    total_credit = overhead_costs * prd_qty
                    d = 0.0
                    c = 0.0
                    l = False
                    if total_credit <> total_debit:
                        if total_credit > total_debit:
                            d = total_credit - total_debit
                            c = 0.0
                        else:
                            c = total_debit - total_credit
                            d = 0.0
                        if not production.routing_id.writeoff_account_id:
                            raise Warning( _('Please define write off account on routing.'))
                        l = (0, 0, {
                                'name': production.name + ' / ' + ' Write Off Entry ' + production.product_id.name,
                                'date': production.date_planned,
                                'account_id': production.routing_id.writeoff_account_id.id,
                                'journal_id': production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': d,
                                'credit': c,
                            })
                    
                    list_append = []
                    list_append.append(debit_line)
                    if credit_line1:
                        list_append.append(credit_line1)
                    if credit_line2:
                        list_append.append(credit_line2)
                    if credit_line3:
                        list_append.append(credit_line3)
                    if credit_line4:
                        list_append.append(credit_line4)
                    if credit_line5:
                        list_append.append(credit_line5)
                    if l:  # write off.
                        list_append.append(l)
                    move.update({'line_ids': list_append})
                    move_id = move_pool.create(move)
                    flag = True
                else:
                    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&sdfsdf&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                    print p.workcenter_id.labor_cost , p.workcenter_id.electric_cost ,  p.workcenter_id.consumables_cost ,  p.workcenter_id.rent_cost ,  p.workcenter_id.other_cost
                    overhead_costs = p.workcenter_id.labor_cost + p.workcenter_id.electric_cost + p.workcenter_id.consumables_cost + p.workcenter_id.rent_cost + p.workcenter_id.other_cost 
                    credit_line1 = False
                    credit_line2 = False
                    credit_line3 = False
                    credit_line4 = False
                    credit_line5 = False
                    if p.workcenter_id.labor_cost > 0.0:
                        credit_line1 = (0, 0, {
                                'name': production.name + ' / ' + p.workcenter_id.labor_cost_account_id.name,
                                'date': production.date_planned,
                                'account_id': p.workcenter_id.labor_cost_id.id,
                                'journal_id':  production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': 0.0,
                                'credit': currency.round(p.workcenter_id.labor_cost * prd_qty),
                            })
                    if p.workcenter_id.electric_cost > 0.0:
                        credit_line2 = (0, 0, {
                                'name': production.name + ' / ' + p.workcenter_id.electric_cost_account_id.name,
                                'date': production.date_planned,
                                'account_id': p.workcenter_id.electric_cost_id.id,
                                'journal_id':  production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': 0.0,
                                'credit': currency.round(p.workcenter_id.electric_cost * prd_qty),
                            })
                    if p.workcenter_id.consumables_cost > 0.0:
                        credit_line3 = (0, 0, {
                            'name': production.name + ' / ' + p.workcenter_id.consumables_cost_id.name,
                            'date': production.date_planned,
                            'account_id': p.workcenter_id.consumables_cost_id.id,
                            'journal_id':  production.routing_id.journal_id.id,
#                             'period_id': period_id.id,
                            'debit': 0.0,
                            'credit': currency.round(p.workcenter_id.consumables_cost * prd_qty),
                        })
                    if p.workcenter_id.rent_cost > 0.0:
                        credit_line4 = (0, 0, {
                            'name': production.name + ' / ' + p.workcenter_id.rent_cost_account_id.name,
                            'date': production.date_planned,
                            'account_id':p.workcenter_id.rent_cost_id.id,
                            'journal_id':  production.routing_id.journal_id.id,
#                             'period_id': period_id.id,
                            'debit': 0.0,
                            'credit': currency.round(p.workcenter_id.rent_cost * prd_qty),
                        })
                    if p.workcenter_id.other_cost > 0.0:
                        credit_line5 = (0, 0, {
                            'name': production.name + ' / ' + p.workcenter_id.other_cost_account_id.name,
                            'date': production.date_planned,
                            'account_id': p.workcenter_id.other_cost_id.id,
                            'journal_id':  production.routing_id.journal_id.id,
#                             'period_id': period_id.id,
                            'debit': 0.0,
                            'credit': currency.round(p.workcenter_id.other_cost * prd_qty),
                        })
                    debit_wip = currency.round(overhead_costs * prd_qty)
                    wip_amount += currency.round(debit_wip)
                    debit_line = (0, 0, {
                        'name': production.name,
                        'date': production.date_planned,
                        'account_id': p.workcenter_id.wip_account_id.id,
                        'journal_id': production.routing_id.journal_id.id,
#                         'period_id': period_id.id,
                        'debit': currency.round(debit_wip),
                        'credit': 0.0,
                    })
                    # write off entry:
                    total_debit = debit_wip
                    total_credit = overhead_costs * prd_qty
                    d = 0.0
                    c = 0.0
                    l = False
                    if total_credit <> total_debit:
                        if total_credit > total_debit:
                            d = total_credit - total_debit
                            c = 0.0
                        else:
                            c = total_debit - total_credit
                            d = 0.0
                        if not production.routing_id.writeoff_account_id:
                            raise Warning( _('Please define write off account on routing.'))
                        l = (0, 0, {
                                'name': production.name + ' / ' + ' Write Off Entry ' + production.product_id.name,
                                'date': production.date_planned,
                                'account_id': production.routing_id.writeoff_account_id.id,
                                'journal_id': production.routing_id.journal_id.id,
#                                 'period_id': period_id.id,
                                'debit': d,
                                'credit': c,
                            })

                    list_append = []
                    list_append.append(debit_line)
                    if credit_line1:
                        list_append.append(credit_line1)
                    if credit_line2:
                        list_append.append(credit_line2)
                    if credit_line3:
                        list_append.append(credit_line3)
                    if credit_line4:
                        list_append.append(credit_line4)
                    if credit_line5:
                        list_append.append(credit_line5)
                    if l:
                        list_append.append(l)
                    move.update({'line_ids': list_append})
                    move_id = move_pool.create(move)
                    flag = True
            
            production.write({'wip_amount': wip_amount})
        print "&&&&&&&&&&&&&&&&&&&dsf&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        return res

    @api.multi
    def button_plan(self):

        if self.bom_id.date_until >= time.strftime(DEFAULT_SERVER_DATE_FORMAT):
            raise UserError(_('Product Not Available'))

        # Manufacturing Another Entry
        create_move_entry = self.env['account.move']

        create_move_line_entry = self.env['account.move.line'].with_context(check_move_validity=False)

        get_routing = self.env['mrp.routing'].search([('name', '=', self.routing_id.name)])

        if self.routing_id.journal_id.id:
            work_center = create_move_entry.create({
                'journal_id': self.routing_id.journal_id.id,
                'company_id': self.company_id.id,
                'date': fields.Date.context_today(self)
            })
        else:
            raise Warning(_('Please set a routing journal'))

        work_in_progress = []

        for records in get_routing.operation_ids:
            if records.workcenter_id.labor_cost_id:
                create_move_line_entry.create({
                    'account_id': records.workcenter_id.labor_cost_id.id,
                    'credit': records.workcenter_id.labor_cost * self.product_qty,
                    'debit': 0.00,
                    'move_id': work_center.id or '/',
                    'date_maturity': fields.Date.context_today(self),
                    'name': self.name
                })

            work_in_progress.append(records.workcenter_id.labor_cost * self.product_qty)

            # Electric Cost Account
            if records.workcenter_id.electric_cost_id:
                create_move_line_entry.create({
                    'account_id': records.workcenter_id.electric_cost_id.id,
                    'credit': records.workcenter_id.electric_cost * self.product_qty,
                    'debit': 0.00,
                    'move_id': work_center.id or '/',
                    'date_maturity': fields.Date.context_today(self),
                    'name': self.name
                })
            work_in_progress.append(records.workcenter_id.electric_cost * self.product_qty)

            # Consumable Cost Account
            if records.workcenter_id.consumables_cost_id:
                create_move_line_entry.create({
                    'account_id': records.workcenter_id.consumables_cost_id.id,
                    'credit': records.workcenter_id.consumables_cost * self.product_qty,
                    'debit': 0.00,
                    'move_id': work_center.id or '/',
                    'date_maturity': fields.Date.context_today(self),
                    'name': self.name
                })
            work_in_progress.append(records.workcenter_id.consumables_cost * self.product_qty)

            # Rent Cost Account
            if records.workcenter_id.rent_cost_id:
                create_move_line_entry.create({
                    'account_id': records.workcenter_id.rent_cost_id.id,
                    'credit': records.workcenter_id.rent_cost * self.product_qty,
                    'debit': 0.00,
                    'move_id': work_center.id or '/',
                    'date_maturity': fields.Date.context_today(self),
                    'name': self.name
                })
            work_in_progress.append(records.workcenter_id.rent_cost * self.product_qty)

            # Other Cost Account
            if records.workcenter_id.other_cost_id:
                create_move_line_entry.create({
                    'account_id': records.workcenter_id.other_cost_id.id,
                    'credit': records.workcenter_id.other_cost * self.product_qty,
                    'debit': 0.00,
                    'move_id': work_center.id or '/',
                    'date_maturity': fields.Date.context_today(self),
                    'name': self.name
                })
            work_in_progress.append(records.workcenter_id.other_cost * self.product_qty)

        create_move_line_entry.create({
            'account_id': self.routing_id.writeoff_account_id.id,
            'credit': 0.00,
            'debit': sum(work_in_progress),
            'move_id': work_center.id or '/',
            'date_maturity': fields.Date.context_today(self),
            'name': self.name
        })
        work_center.post()
        ############################################################################################

        """ Create work orders. And probably do stuff, like things. """
        return super(MrpProduction, self).button_plan()

    @api.multi
    def button_mark_done(self):
        #################################################################################################
        create_move_entry = self.env['account.move']

        create_move_line_entry = self.env['account.move.line'].with_context(check_move_validity=False)

        show_stock_move = self.env['stock.move'].search([('group_id', '=', self.name)]).sudo()

        # ###########################################################################################
        # Updates The Total workcenter cost, total raw material, total cost and cost per unit
        #############################################################################################
        get_routing = self.env['mrp.routing'].search([('name', '=', self.routing_id.name)])

        total_cost_wc = 0.0
        for record in get_routing.operation_ids:
            total_cost_wc += record.workcenter_id.labor_cost * self.product_qty + \
                             record.workcenter_id.electric_cost * self.product_qty + \
                             record.workcenter_id.consumables_cost * self.product_qty + \
                             record.workcenter_id.rent_cost * self.product_qty + \
                             record.workcenter_id.other_cost * self.product_qty
        self.total_cost_wc = total_cost_wc

        to_consume = []
        for record in self.move_raw_ids:
            to_consume.append(
                record.product_uom_qty * record.product_id.standard_price)  # multiplies all product unit qty with the product's standard price
        self.raw_cost = sum(to_consume)  # sums together all consumed products

        self.total_cost = self.total_cost_wc + self.raw_cost  # calculates the total cost of manufacturing

        self.total_cost_unit = round((self.total_cost / self.product_qty), 3)  # calculates the cost per unit

        avg_standard_price = 0.000

        if self.product_id.standard_price > 0.000:
            avg_standard_price += ((self.product_id.standard_price * self.product_id.qty_available) + (
                self.total_cost_unit * self.product_qty)) / (self.product_qty + self.product_id.qty_available)
        else:
            avg_standard_price += self.total_cost_unit

        self.product_id.write({'standard_price': avg_standard_price})

        # ###########################################################################################
        #         Manufacturing Journal
        #############################################################################################
        for record in self.move_raw_ids:
            stock_journal = create_move_entry.create({
                'journal_id': record.product_id.categ_id.property_stock_journal.id,
                'company_id': self.company_id.id,
                'date': fields.Date.context_today(self)
            })

            create_move_line_entry.create({
                'account_id': record.product_id.categ_id.property_stock_valuation_account_id.id,
                'credit': record.product_id.standard_price * record.product_uom_qty,
                'debit': 0.00,
                'move_id': stock_journal.id or '/',
                'date_maturity': fields.Date.context_today(self),
                'name': self.name
            })

            create_move_line_entry.create({
                'account_id': self.routing_id.writeoff_account_id.id,
                'credit': 0.00,
                'debit': record.product_id.standard_price * record.product_uom_qty,
                'move_id': stock_journal.id or '/',
                'date_maturity': fields.Date.context_today(self),
                'name': self.name
            })
            stock_journal.post()

        for moves in show_stock_move:
            if moves.state == 'assigned' or 'confirmed':
                moves.action_done()
                self.product_id.write({'standard_price': avg_standard_price})

        # ###########################################################################################
        #         Last  Journal
        #############################################################################################

        values = []

        cost_values = []

        other_journal = create_move_entry.create({
                   'journal_id': self.routing_id.journal_id.id,
                   'company_id': self.company_id.id,
                   'date': fields.Date.context_today(self)
               })

        for record in self.move_raw_ids:
            create_move_line_entry.create({
                'account_id': self.routing_id.writeoff_account_id.id,
                'credit': record.product_id.standard_price * record.product_uom_qty,
                'debit': 0.00,
                'move_id': other_journal.id or '/',
                'date_maturity': fields.Date.context_today(self),
                'name': self.name
            })
            values.append(record.product_id.standard_price * record.product_uom_qty)

        for records in get_routing.operation_ids:
            if records.workcenter_id.labor_cost_id:
                cost_values.append(records.workcenter_id.labor_cost * self.product_qty)
            if records.workcenter_id.electric_cost_id:
                cost_values.append(records.workcenter_id.electric_cost * self.product_qty)
            if records.workcenter_id.consumables_cost_id:
                cost_values.append(records.workcenter_id.consumables_cost * self.product_qty)
            if records.workcenter_id.rent_cost_id:
                cost_values.append(records.workcenter_id.rent_cost * self.product_qty)
            if records.workcenter_id.other_cost_id:
                cost_values.append(records.workcenter_id.other_cost * self.product_qty)
        cost_total = sum(cost_values)

        create_move_line_entry.create({
            'account_id': self.product_id.categ_id.property_stock_valuation_account_id.id,
            'credit': 0.00,
            'debit': sum(values) + cost_total,
            'move_id': other_journal.id or '/',
            'date_maturity': fields.Date.context_today(self),
            'name': self.name
        })

        create_move_line_entry.create({
            'account_id': self.routing_id.writeoff_account_id.id,
            'credit': sum(cost_values),
            'debit': 0.00,
            'move_id': other_journal.id or '/',
            'date_maturity': fields.Date.context_today(self),
            'name': self.name
        })
        other_journal.post()

        # ###########################################################################################
        #         Moves For Gain/Loss Product
        #############################################################################################

        for lossgain in self.move_loss_ids:
            stock_product = self.env['stock.move'].search([('product_id', '=', lossgain.product_id.name), ('state', '=', 'draft')])
            for record in stock_product:
                record.name = self.name
                record.origin = self.name
                record.action_done()

        # ###########################################################################################
        #         Calculates all move cost and average cost
        #############################################################################################

        stock_movement = self.env['stock.move'].search([('origin', '=', self.name), ('product_id', '=', self.product_id.name)])
        # stock_movement.move_cost = self.product_id.standard_price
        for record in stock_movement:
            record.move_cost = self.total_cost_unit
            record.move_average_cost = avg_standard_price

        for record in self.move_raw_ids:
            stock_movement = self.env['stock.move'].search([('origin', '=', self.name), ('product_id', '=', record.product_id.name)])
            stock_movement.move_cost = record.product_id.standard_price
            # stock_movement.move_cost = self.total_cost_unit
        return self.write({'state': 'done'})

    @api.multi
    def _generate_moves(self):
        pass

    @api.multi
    def generate_materials(self):
        for production in self:
            production._generate_finished_moves()
            factor = production.product_uom_id._compute_quantity(production.product_qty,
                                                                 production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor,
                                                    picking_type=production.bom_id.picking_type_id)
            production._generate_raw_moves(lines)
            # Check for all draft moves whether they are mto or not
            production._adjust_procure_method()
            production.move_raw_ids.action_confirm()
        self.state = 'confirmed'
        return True

class mrp_wline_account(models.Model):
    _name = 'mrp.workcenter.line.account'

    workcenter_line_id = fields.Many2one('mrp.workcenter.line', string='Workcenter Line')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Account', required=True)
    percentage = fields.Float('Percentage', required=True)


class mrp_wline(models.Model):
    _name = 'mrp.workcenter.line'
    
    @api.multi
    def onchange_wc(self, workcenter_id):
        if workcenter_id:
            prod = self.env['mrp.workcenter'].browse(workcenter_id)
            return {'value': {
                              'labor_cost_account_id': prod.labor_cost_account_id.id,
                              'electric_cost_account_id': prod.electric_cost_account_id.id,
                              'consumables_cost_account_id': prod.consumables_cost_account_id.id,
                              'rent_cost_account_id': prod.rent_cost_account_id.id,
                              'other_cost_account_id': prod.other_cost_account_id.id,
                              'costs_hour_account_id': prod.costs_hour_account_id.id,
                              'costs_cycle_account_id': prod.costs_cycle_account_id.id,
                              }}
        return {}

    #'workcenter_lines': fields.one2many('mrp.workcenter.line.account', 'workcenter_line_id', 'Distribution Work Centers Accounts'),
    workcenter_id = fields.Many2one('mrp.workcenter', string='Child Workcenter', required=True, domain=[('type', '=', 'normal')],)
    workcenter_id_main = fields.Many2one('mrp.workcenter', string='Workcenter', required=True)

    labor_cost = fields.Float(string='Labor Cost Percentage', help="Specify Labor Cost of Work Center.")
    labor_cost1 = fields.Float(string='Labor Cost', help="Specify Labor Cost of Work Center.", readonly=True)
    labor_cost_account_id = fields.Many2one('account.analytic.account', 'Labor Cost Analytic Account',
        help="Fill this only if you want automatic analytic accounting entries on production orders for Labor Cost.")

    electric_cost = fields.Float(string='Rates Of Electricity Cost Percentage', help="Specify Rates Of Electricity of Work Center.")
    electric_cost1 = fields.Float(string='Rates Of Electricity Cost', help="Specify Rates Of Electricity of Work Center.", readonly=True)
    electric_cost_account_id = fields.Many2one('account.analytic.account', string='Electricity Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Electricity Cost.")

    consumables_cost = fields.Float(string='Rates Of Consumables Cost Percentage', help="Specify Rates Of Consumables of Work Center.")
    consumables_cost1 = fields.Float(string='Rates Of Consumables Cost', help="Specify Rates Of Consumables of Work Center.", readonly=True)
    consumables_cost_account_id = fields.Many2one('account.analytic.account', string='Consumables Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Consumables Cost.")

    rent_cost = fields.Float(string='Rates Of Rent Cost Percentage', help="Specify Rates Of Rent of Work Center.")
    rent_cost1 = fields.Float(string='Rates Of Rent Cost', help="Specify Rates Of Rent of Work Center.", readonly=True)
    rent_cost_account_id = fields.Many2one('account.analytic.account', string='Rent Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Rent Cost.")

    other_cost = fields.Float(string='Rates Of Other Overheads Percentage', help="Specify Rates Of Other Overheads of Work Center.")
    other_cost1 = fields.Float(string='Rates Of Other Overheads', help="Specify Rates Of Other Overheads of Work Center.", readonly=True)
    other_cost_account_id = fields.Many2one('account.analytic.account', string='Other Overheads Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Other Overheads Cost.")
    
    costs_hour = fields.Float(string='Cost per hour Percentage', help="Specify Cost of Work Center per hour.")
    costs_hour1 = fields.Float(string='Cost per hour', help="Specify Cost of Work Center per hour.", readonly=True)
    costs_hour_account_id = fields.Many2one('account.analytic.account', string='Hour Account', help="Fill this only if you want automatic analytic accounting entries on production orders.")

    costs_cycle = fields.Float(string='Cost per cycle Percentage', help="Specify Cost of Work Center per cycle.")
    costs_cycle1 = fields.Float(string='Cost per cycle', help="Specify Cost of Work Center per cycle.", readonly=True)
    costs_cycle_account_id = fields.Many2one('account.analytic.account', string='Cycle Account', help="Fill this only if you want automatic analytic accounting entries on production orders.")
        
class mrp_workcenter(models.Model):
#    _inherit = 'mrp.workcenter'
    _name = 'mrp.workcenter'
    _inherit = ['mrp.workcenter', 'mail.thread']
    
    @api.multi
    @api.depends('child_parent_ids' , 'parent_id')
    def _get_child_ids(self):
        result = {}
        for record in self:
            if record.child_parent_ids:
                self.child_id = [x.id for x in record.child_parent_ids]
            else:
                self.child_id = []
        return result

    @api.one
    @api.constrains('parent_id')
    def _check_recursion(self, parent=None):
        """
        Verifies that there is no loop in a hierarchical structure of records,
        by following the parent relationship using the **parent** field until a loop
        is detected or until a top-level record is found.

        :param cr: database cursor
        :param uid: current user id
        :param ids: list of ids of records to check
        :param parent: optional parent field name (default: ``self._parent_name = parent_id``)
        :return: **True** if the operation can proceed safely, or **False** if an infinite loop is detected.
        """
        if not parent:
            parent = 'parent_id'
        self._table = 'mrp_workcenter'

        # must ignore 'active' flag, ir.rules, etc. => direct SQL query
        query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % (parent, self._table)
        for id in self.ids:
            current_id = id
            while current_id is not None:
                self._cr.execute(query, (current_id,))
                result = self._cr.fetchone()
                current_id = result[0] if result else None
                if current_id == id:
                    raise Warning(_('Error!'), _('You cannot create recursive workcenter.'))
        return True
#    
#    @api.one
#    @api.constrains('parent_id')
#    def _check_recursion(self):
#        level = 100
#        print self.ids
#        while len(self.ids):
#            self._cr.execute('select distinct parent_id from mrp_workcenter where id IN %s', (tuple(self.ids),))
#            ids = filter(None, map(lambda x:x[0], self._cr.fetchall()))
#            print "::::::::::::",ids,level
#            if not level:
#                raise Warning(_('Error!'), _('You cannot create recursive workcenter.'))
#            level -= 1
#        return True

    parent_id = fields.Many2one('mrp.workcenter', string='Parent Workcenter', ondelete='cascade', domain=[('type', '=', 'view')])
    child_parent_ids = fields.One2many('mrp.workcenter', 'parent_id', string='Childrens')
    child_id = fields.Many2many("mrp.workcenter", compute='_get_child_ids', string="Child Workcenters")
    type = fields.Selection(selection=[
                ('view', 'View'),
                ('normal', 'Normal'),
                ], string='Type', required=True, default='normal')
    workcenter_ids = fields.One2many('mrp.workcenter.line', 'workcenter_id_main', string='Child Work Centers Accounts')
    
    
    labor_cost = fields.Float(string='Labor Cost', help="Specify Labor Cost of Work Center.")
    labor_cost_account_id = fields.Many2one('account.analytic.account', string='Labor Cost Analytic Account',
        help="Fill this only if you want automatic analytic accounting entries on production orders for Labor Cost.")

    electric_cost = fields.Float('Rates Of Electricity Cost', help="Specify Rates Of Electricity of Work Center.")
    electric_cost_account_id = fields.Many2one('account.analytic.account', 'Electricity Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Electricity Cost.")

    consumables_cost = fields.Float(string='Rates Of Consumables Cost', help="Specify Rates Of Consumables of Work Center.")
    consumables_cost_account_id = fields.Many2one('account.analytic.account', string='Consumables Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Consumables Cost.")

    rent_cost = fields.Float(string='Rates Of Rent Cost', help="Specify Rates Of Rent of Work Center.")
    rent_cost_account_id = fields.Many2one('account.analytic.account', string='Rent Cost Analytic Account',
        help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Rent Cost.")

    other_cost = fields.Float(string='Rates Of Other Overheads', help="Specify Rates Of Other Overheads of Work Center.")
    other_cost_account_id = fields.Many2one('account.analytic.account', string='Other Overheads Cost Analytic Account', help="Fill this only if you want automatic analytic accounting entries on production orders for Rates Of Other Overheads Cost.")


    labor_cost_id = fields.Many2one('account.account', string='Labor Cost Account')#todoprobuse domain=[('type', '<>', 'view'), ('type', '<>', 'closed')]
    electric_cost_id = fields.Many2one('account.account', string='Electricity Cost Account')#todoprobuse
    consumables_cost_id = fields.Many2one('account.account', string='Consumables Cost Account')#todoprobuse
    rent_cost_id = fields.Many2one('account.account', string='Rent Cost Account')#todoprobuse
    other_cost_id = fields.Many2one('account.account', string='Other Overheads Cost Account')#todoprobuse

    costs_cycle_account_id = fields.Many2one('account.analytic.account', string='Cycle Analytic Account',
                                                help="Fill this only if you want automatic analytic accounting entries on production orders.")
    costs_hour_account_id = fields.Many2one('account.analytic.account', string='Hour Analytic Account',
                                            help="Fill this only if you want automatic analytic accounting entries on production orders.")

    state = fields.Selection(selection=[
                    ('draft', 'New'),
                    ('computed', 'Computed')], string='Status', default='draft', readonly=True,)

    wip_account_id = fields.Many2one('account.account', string='Work in Progress Account')#todoprobuse

    time_efficiency = fields.Float(string="Time Efficiency")

    capacity_per_cycle = fields.Char(string="Time Efficiency")

    time_cycle = fields.Float(string="Time Cycle")

    time_start = fields.Float('Time before prod.', help="Time in minutes for the setup.")

    time_stop = fields.Float('Time after prod.', help="Time in minutes for the cleaning.")
    #
    capacity = fields.Float(string='Capacity')
    #
    # costs_cycle = fields.Float(string='Costs Cycle')


    @api.multi
    def button_confirm(self):
        data = self
        if data.type == 'normal':
            raise Warning(_('Error!'), _("Cannot compute Workcenter if Workcenter type is Normal."))
        labor_cost = data.labor_cost
        electric_cost = data.electric_cost
        consumables_cost = data.consumables_cost
        rent_cost = data.rent_cost
        other_cost = data.other_cost
        # costs_hour = data.costs_hour
        # costs_cycle = data.costs_cycle
        
        l1 = 0.00
        e1 = 0.00
        c1 = 0.00
        r1 = 0.00
        o1 = 0.00
        # co1 = 0.00
        # co2 = 0.00
        
        for d in data.workcenter_ids:
            print data.labor_cost
            vals = {
                'labor_cost' : data.labor_cost * d.labor_cost / 100,
                'electric_cost':data.electric_cost * d.electric_cost / 100,
                'consumables_cost' :data.consumables_cost * d.consumables_cost / 100,
                'rent_cost' :data.rent_cost * d.rent_cost / 100,
                'other_cost' : data.other_cost * d.other_cost / 100,
                # 'costs_hour' : data.costs_hour * d.costs_hour / 100,
                # 'costs_cycle': data.costs_cycle * d.costs_cycle / 100,
            }
            vals1 = {
                'labor_cost1' : data.labor_cost * d.labor_cost / 100,
                'electric_cost1':data.electric_cost * d.electric_cost / 100,
                'consumables_cost1' :data.consumables_cost * d.consumables_cost / 100,
                'rent_cost1' :data.rent_cost * d.rent_cost / 100,
                'other_cost1' : data.other_cost * d.other_cost / 100,
                # 'costs_hour1' : data.costs_hour * d.costs_hour / 100,
                # 'costs_cycle1': data.costs_cycle * d.costs_cycle / 100,
            }
            print vals, vals1
            d.write(vals1)

            l1 += data.labor_cost * d.labor_cost / 100
            e1 += data.electric_cost * d.electric_cost / 100
            c1 += data.consumables_cost * d.consumables_cost / 100
            r1 += data.rent_cost * d.rent_cost / 100
            o1 += data.other_cost * d.other_cost / 100
            # co1 += data.costs_hour * d.costs_hour / 100
            # co2 += data.costs_cycle * d.costs_cycle / 100
            d.workcenter_id.write(vals)
        
        print "::::::::::::::::::::"
        if str(labor_cost) != str(l1):
            raise Warning(_('Error!'), _("Computation error on Labor Cost."))
        if electric_cost != e1:
            raise Warning(_('Error!'), _("Computation error on Electric Cost."))
        if consumables_cost != c1:
            raise Warning(_('Error!'), _("Computation error on Consumable Cost."))
        if rent_cost != r1:
            raise Warning(_('Error!'), _("Computation error on Rent Cost."))
        if other_cost != o1:
            raise Warning(_('Error!'), _("Computation error on Other Cost."))
        # if costs_hour != co1:
        #     raise Warning(_('Error!'), _("Computation error on Cost per hour."))
        # if costs_cycle != co2:
        #     raise Warning(_('Error!'), _("Computation error on Cost per cycle."))
        self.write({'state': 'computed'})
        return True
    
    @api.multi
    def button_draft(self):
        for data in self:
            if data.type == 'normal':
                raise Warning(_('Error!'), _("Cannot compute Workcenter if Workcenter type is Normal."))
            self.write({'state': 'draft'})
        return True


class product_product(models.Model):
    _inherit = 'product.product'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', help='This analytic account can be used in incoming shipment, internal orders, production raw material transfers, etc in stock journal accounting entry.')


class stock_quant(models.Model):
    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        res = super(stock_quant, self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context)
        print "::::ssssss::::::::::::::::::",res
        #super return this type: return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        
        
        
#        if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':  # row material
#            credit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})
#        elif move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':  # finish product
#            debit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})
#        elif move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':  # incoming shipment
#            credit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})
#        elif move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':  # incoming shipment
#            debit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})
        if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':  # row material
            res[1][2].update({'analytic_account_id': move.analytic_account_id.id})
        elif move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':  # finish product
            res[0][2].update({'analytic_account_id': move.analytic_account_id.id})
        elif move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':  # incoming shipment
            res[1][2].update({'analytic_account_id': move.analytic_account_id.id})
        elif move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':  # incoming shipment
            res[0][2].update({'analytic_account_id': move.analytic_account_id.id})
        return res

    def _account_entry_move(self, move):#old method in v7 was _create_product_valuation_moves
        """
        Accounting Valuation Entries

        quants: browse record list of Quants to create accounting valuation entries for. Unempty and all quants are supposed to have the same location id (thay already moved in)
        move: Move to use. browse record
        """
        if move.name.startswith('MO') and str(move.location_id.usage) == 'production' and  str(move.location_dest_id.usage) == 'internal':
            return False
        else:
            return super(stock_quant, self)._account_entry_move(move)
        

#below class and its methods are no more useful in v8. it is replaced by quant class methods see above class.
#************************************NOTE IMPORTANT V8******************************************
class stock_move(models.Model):

    analytic_account_id = fields.Many2one(related='product_id.analytic_account_id', string='Analytic Account', store=True, help='This analytic account can be used in incoming shipment, internal orders, production raw material transfers, etc in stock journal accounting entry.')

    move_average_cost = fields.Float(string="Move Average Cost", default=0.00)

    move_cost = fields.Float(string="Move Cost", default=0.00)

    #probuse note; below two methods are removed in v8.. so replace this stock.move class with stock.quant..see above class quant..
    def _create_account_move_line(self, move, src_account_id, dest_account_id, reference_amount, reference_currency_id):
        print ":::::::::::::::SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSsss",x
        # override this method to add analytic account.
        # stock move is for row material (credit side in that case) or finish product (debit side in that case)
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given stock move.
        """
        
        # prepare default values considering that the destination accounts have the reference_currency_id as their main currency
        #--------------------------------NOTE V8--------------------
        partner_id = (move.picking_id.partner_id and self.env['res.partner']._find_accounting_partner(move.picking_id.partner_id).id) or False
        debit_line_vals = {
            'name': move.name,
            'product_id': move.product_id and move.product_id.id or False,
            'quantity': move.product_qty,
            'ref': move.picking_id and move.picking_id.name or False,
            'date': time.strftime('%Y-%m-%d'),
            'partner_id': partner_id,
            'debit': reference_amount,
            'account_id': dest_account_id,
        }
        credit_line_vals = {
            'name': move.name,
            'product_id': move.product_id and move.product_id.id or False,
            'quantity': move.product_qty,
            'ref': move.picking_id and move.picking_id.name or False,
            'date': time.strftime('%Y-%m-%d'),
            'partner_id': partner_id,
            'credit': reference_amount,
            'account_id': src_account_id,
        }
        
        
        #PROBUSE 
        if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':  # row material #PROBUSE 
            credit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})#PROBUSE 
        elif move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':  # finish product #PROBUSE 
            debit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})#PROBUSE 
        elif move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':  # incoming shipment #PROBUSE 
            credit_line_vals.update({'analytic_account_id': move.analytic_account_id.id}) #PROBUSE 
        elif move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':  # incoming shipment #PROBUSE 
            debit_line_vals.update({'analytic_account_id': move.analytic_account_id.id})#PROBUSE 

        # if we are posting to accounts in a different currency, provide correct values in both currencies correctly
        # when compatible with the optional secondary currency on the account.
        # Financial Accounts only accept amounts in secondary currencies if there's no secondary currency on the account
        # or if it's the same as that of the secondary amount being posted.
        account_obj = self.env['account.account']
        src_acct, dest_acct = account_obj.browse([src_account_id, dest_account_id])
        src_main_currency_id = src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.company_id.currency_id.id
        cur_obj = self.env['res.currency']
        if reference_currency_id != src_main_currency_id:
            # fix credit line:
            credit_line_vals['credit'] = cur_obj.compute(reference_currency_id, src_main_currency_id, reference_amount)
            if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
                credit_line_vals.update(currency_id=reference_currency_id, amount_currency=-reference_amount)
        if reference_currency_id != dest_main_currency_id:
            # fix debit line:
            debit_line_vals['debit'] = cur_obj.compute(reference_currency_id, dest_main_currency_id, reference_amount)
            if (not dest_acct.currency_id) or dest_acct.currency_id.id == reference_currency_id:
                debit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    @api.model
    #This method is no more in v8.. so replace by stock.quant objects _account_entry_move method. please see above stock.quant.
    def _create_product_valuation_moves(self, move):
        # print "::::::::LLLLLLLLLLLLLLLLLLLL",xd
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        if move.product_id.valuation == 'real_time':  # FIXME: product valuation should perhaps be a property?
            src_company_ctx = dict(self._context, force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(self._context, force_company=move.location_dest_id.company_id.id)
            account_moves = []
            # Outgoing moves (or cross-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(move, src_company_ctx)
                # returning goods to supplier
                if move.location_dest_id.usage == 'supplier':
                    account_moves += [(journal_id, self._create_account_move_line(move, acc_valuation, acc_src, reference_amount, reference_currency_id))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(move, acc_valuation, acc_dest, reference_amount, reference_currency_id))]

            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(move, src_company_ctx)
                # goods return from customer
                if move.location_id.usage == 'customer':
                    account_moves += [(journal_id, self._create_account_move_line(move, acc_dest, acc_valuation, reference_amount, reference_currency_id))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(move, acc_src, acc_valuation, reference_amount, reference_currency_id))]

            move_obj = self.env['account.move']
            for j_id, move_lines in account_moves:
                # motobell #PROBUSE only this change in override *********************************
                if move.name.startswith('MO') and str(move.location_id.usage) == 'production' and  str(move.location_dest_id.usage) == 'internal':
                    pass
                else:
                    move_obj.create({
                     'journal_id': j_id,
                     'line_ids': move_lines,
                     'ref': move.picking_id and move.picking_id.name
                    })

    _inherit = 'stock.move'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


class StockHistory(models.Model):
    _inherit = 'stock.history'

    move_average_cost = fields.Float(string="Move Average Cost", default=0.00)

    move_cost = fields.Float(string="Move Cost", default=0.00)



