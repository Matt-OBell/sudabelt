"""."""
# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)
import time

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class HRPayslip(models.Model):
    """."""

    _inherit = 'hr.payslip'

    @api.multi
    def process_sheet_dummy(self):
        """def process_sheet(self).

        Renamed to dummy now it will not be called.... Because in 9.0 this method has
        been changed.... And below method was just passing analytic account in move lines....
        so may be in future if requirement come we will see how to fix that.... #probusetodo.
        """
        move_pool = self.env['account.move']
        period_pool = self.env['account.period']
        timenow = time.strftime('%Y-%m-%d')
        pay = self

        if not pay.contract_id.use_analytic:
            return super(HRPayslip, self).process_sheet()

        if pay.contract_id.use_analytic and not pay.contract_id.analytic_account_id:  # probuse done
            raise UserError(_('Please configure analytic account on employee  %s with contract  %s') % (
                pay.employee_id.name, pay.contract_id.name))

        for slip in self:  # for analytic account addition... in move line so completed override wholemethod..
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            if not slip.period_id:
                ctx = dict(self._context or {}, account_period_prefer_normal=True)
                search_periods = period_pool.with_context(ctx).find(slip.date_to)
                period_id = search_periods[0]
            else:
                period_id = slip.period_id.id

            default_partner_id = slip.employee_id.address_home_id.id
            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'date': timenow,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'period_id': period_id.id,
            }
            for line in slip.details_by_salary_rule_category:
                amount = slip.credit_note and -line.total or line.total
                partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'date': timenow,
                        'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable')) and partner_id or False,
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id.id,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        #                    'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'analytic_account_id': slip.contract_id.analytic_account_id and slip.contract_id.analytic_account_id.id or False,  # probuse
                        'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                        'tax_amount': line.salary_rule_id.account_tax_id and amount or 0.0,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'date': timenow,
                        'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in ('receivable', 'payable')) and partner_id or False,
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id.id,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        #                    'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'analytic_account_id': slip.contract_id.analytic_account_id and slip.contract_id.analytic_account_id.id or False,  # probuse
                        'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                        'tax_amount': line.salary_rule_id.account_tax_id and amount or 0.0,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if debit_sum > credit_sum:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_("Configuration Error! The Expense Journal '%s' has not properly configured the Credit Account!") % (
                        slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id.id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif debit_sum < credit_sum:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise UserError(_("Configuration Error! The Expense Journal '%s' has not properly configured the Debit Account!") % (
                        slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id.id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move.update({'line_id': line_ids})
            move_id = move_pool.create(move)
            print move
            slip.write({'move_id': move_id.id, 'period_id': period_id.id})
            if slip.journal_id.entry_posted:
                move_id.post()
        return self.write({'paid': True, 'state': 'done'})


class HRSalaryRule(models.Model):
    """."""

    _inherit = 'hr.salary.rule'

    contract_id = fields.Many2one('hr.contract', string='Contract')


class HRContract(models.Model):
    """Employee contract.

    This allows to add different values in fields.
    Fields are used in salary rule computation.
    """

    _inherit = 'hr.contract'
    _description = 'HR Contract'

    basic_amount = fields.Float(string='Basic (Amount)')
    pension_company_amount = fields.Float(string='Pension Company Contribution (Amount)',)
    pension_employee_amount = fields.Float(string='Pension Employee Contribution (Amount)')
    hra_amount = fields.Float(string='House Rent Allowance (Amount)',
                              digits_compute=dp.get_precision('Payroll'))
    utility_amount = fields.Float(string='Utility (Amount)',
                                  digits_compute=dp.get_precision('Payroll'), default=True)
    meal_amount = fields.Float(string='Meal Allowance (Amount)',
                               digits_compute=dp.get_precision('Payroll'))
    entertain_amount = fields.Float(
        string='Entertainment Allowance (Amount)', digits_compute=dp.get_precision('Payroll'))
    transport_amount = fields.Float(string='Transport Allowance (Amount)',
                                    digits_compute=dp.get_precision('Payroll'))
    leave_allowance_amount = fields.Float(
        string='Leave Allowance (Amount)', digits_compute=dp.get_precision('Payroll'))
    bonus_allowance_amount = fields.Float(
        string='Bonus/Benefit to Employee (Amount)', digits_compute=dp.get_precision('Payroll'))
    ot_allowance_amount = fields.Float(
        string='Overtime Allowance (Amount)', digits_compute=dp.get_precision('Payroll'))
    nhf_allowance_amount = fields.Float(
        string='Employees NHF Contribution (Amount)', digits_compute=dp.get_precision('Payroll'))
    salary_rule_ids = fields.One2many(
        'hr.salary.rule', 'contract_id', string='Configure Salary Rules for Contract')
    use_analytic = fields.Boolean(string='Use Analytic Account',
                                  help='Check this box if you want to use below analytic account while processing employee payroll/payslips instead of using one configured on salary rules.')
