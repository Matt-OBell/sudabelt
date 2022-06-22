"""."""
# -*- coding: utf-8 -*-

import time
from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _


class HRPaySlipRun(models.Model):
    """HRPaySlipRun."""

    _inherit = 'hr.payslip.run'

    merge_accounting = fields.Boolean(string='Merge Accounting Entries?',
                                      help='Tick if you want to merge accounting journal entries created after closing payslips.', default=True)

    def close_payslip_run(self):
        """Close payslip run."""
        payslip_batch = self.browse(self.ids)[0]
        if payslip_batch.merge_accounting:
            payslip_ids = []
            # Pass flog to process_sheet method to merge accounting.
            # ctx.update({'to_merge_accounting': True})
            for p in payslip_batch.slip_ids:
                self.env['hr.payslip'].compute_sheet()
                payslip_ids.append(p.id)
#            wf_service.trg_validate(uid, 'hr.payslip', p.id, 'hr_verify_sheet', cr)
            # Divert call to process_sheet_merge method.
            self.env['hr.payslip'].process_sheet_merge()
            self.env['hr.payslip'].write({
                'paid': True, 'state': 'done'})
            # no need to call super here.
            return self.write({'state': 'close'})
        else:  # if merge_accounting=False then call super. Normal flow.
            return super(HRPaySlipRun, self).close_payslip_run()
        return super(HRPaySlipRun, self).close_payslip_run()


class HRPaySlip(models.Model):
    """HRPaySlip."""

    _inherit = 'hr.payslip'

    # New method to handle merge accounting entries during processing sheet all togther from batch payslips.
    # This method should check if to_merge_accounting=True in context then merge all payslip journal entries else call super.
    # if only when context.get('to_merge_accounting', False)
    def process_sheet_merge(self):
        """process sheet merge."""
        context = {}
        move_pool = self.env['account.move']
        period_pool = self.pool.get('account.period')
        precision = self.env['decimal.precision'].precision_get('Payroll')
        timenow = time.strftime('%Y-%m-%d')

        # call super if merge accounting not in context. That means normal flow.
        if not context.get('to_merge_accounting', False):
            pass
            return super(HRPaySlip, self).process_sheet()
            # @process_sheet() method is no longer available in parent class.
        debit_sum = 0.0
        credit_sum = 0.0
        accounts_dict = {}  # group journal items which does not have partner on it.
        accounts_dict_partner = {}  # group journal items which have partner on it and account.

        for slip in self.browse(self.ids):
            line_ids = []
            if not slip.period_id:
                ctx = dict(context or {}, account_period_prefer_normal=True)
                search_periods = period_pool.find(slip.date_to, context=ctx)
                period_id = search_periods[0]
            else:
                period_id = slip.period_id.id

            default_partner_id = slip.employee_id.address_home_id.id
            name = _('Payslip of %s') % (slip.employee_id.name)

            for line in slip.details_by_salary_rule_category:
                with_partner = False
                partner_id_use = False
                if line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable'):
                    with_partner = True
                    partner_id_use = line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in (
                        'receivable', 'payable') and default_partner_id or False
                amt = slip.credit_note and -line.total or line.total
                if float_is_zero(amt, precision_digits=precision):
                    continue
                # IF of partner, it is not object.
                partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_dict = (0, 0, {
                        'name': line.name + ' - ' + slip.number,
                        'date': timenow,
                        'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable')) and partner_id or False,
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'debit': amt > 0.0 and amt or 0.0,
                        'credit': amt < 0.0 and -amt or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                        'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                    })

                    if not with_partner:
                        if not debit_account_id in accounts_dict:
                            accounts_dict[debit_account_id] = [debit_dict]
                        else:
                            accounts_dict[debit_account_id].append(debit_dict)
                    else:
                        if not (debit_account_id, partner_id) in accounts_dict_partner:
                            accounts_dict_partner[(debit_account_id, partner_id)] = [debit_dict]
                        else:
                            accounts_dict_partner[(debit_account_id, partner_id)].append(debit_dict)

                    debit_sum += debit_dict[2]['debit'] - debit_dict[2]['credit']

                if credit_account_id:
                    credit_dict = (0, 0, {
                        'name': line.name + ' - ' + slip.number,
                        'date': timenow,
                        'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in ('receivable', 'payable')) and partner_id or False,
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'debit': amt < 0.0 and -amt or 0.0,
                        'credit': amt > 0.0 and amt or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                        'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                    })
                    credit_sum += credit_dict[2]['credit'] - credit_dict[2]['debit']

                    if not with_partner:
                        if not credit_account_id in accounts_dict:
                            accounts_dict[credit_account_id] = [credit_dict]
                        else:
                            accounts_dict[credit_account_id].append(credit_dict)
                    else:
                        if not (credit_account_id, partner_id) in accounts_dict_partner:
                            accounts_dict_partner[(credit_account_id, partner_id)] = [credit_dict]
                        else:
                            accounts_dict_partner[(credit_account_id, partner_id)
                                                  ].append(credit_dict)

        final_list_ids = []
        if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
            acc_id = slip.journal_id.default_credit_account_id.id
            if not acc_id:
                raise UserError(_('Configuration Error! The Expense Journal "%s" has not properly configured the Credit Account!') % (
                    slip.journal_id.name))
            adjust_credit = (0, 0, {
                'name': _('Adjustment Entry'),
                'date': timenow,
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'debit': 0.0,
                'credit': debit_sum - credit_sum,
            })
            line_ids.append(adjust_credit)
            final_list_ids.append(adjust_credit)

        elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
            acc_id = slip.journal_id.default_debit_account_id.id
            if not acc_id:
                raise UserError(_('Configuration Error! The Expense Journal "%s" has not properly configured the Debit Account!') % (
                    slip.journal_id.name))
            adjust_debit = (0, 0, {
                'name': _('Adjustment Entry'),
                'date': timenow,
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'debit': credit_sum - debit_sum,
                'credit': 0.0,
            })
            line_ids.append(adjust_debit)
            final_list_ids.append(adjust_debit)

        if not slip.period_id:
            ctx = dict(context or {}, account_period_prefer_normal=True)
            search_periods = period_pool.find(slip.payslip_run_id.date_end, context=ctx)
            period_id = search_periods[0]
        else:
            period_id = slip.period_id.id
        move = {
            'narration': slip.payslip_run_id.name + '- Group Entry',
            'date': timenow,
            'ref': slip.payslip_run_id.name + '- Group Entry',
            'journal_id': slip.payslip_run_id.journal_id.id,
            'period_id': period_id,
        }
        all_line_ids = []
        all_line_ids_without = []
        for account in accounts_dict:
            debit = 0.0
            credit = 0.0
            store_data = {}
            store_data1 = {}
            for acc in accounts_dict[account]:
                #store_data = acc
                x = acc[2].copy()
                y = acc[2].copy()
                credit += acc[2]['credit']
                debit += acc[2]['debit']
            if debit > 0.0:
                new_name = x['name'].split('-')
                x['name'] = new_name and new_name[0] + '- Group Entry' or ''
                store_data = (0, 0, x)
                store_data[2]['debit'] = debit
                store_data[2]['credit'] = 0.0
                all_line_ids_without.append(store_data)
            if credit > 0.0:
                store_data1 = (0, 0, y)
                new_name = y['name'].split('-')
                y['name'] = new_name and new_name[0] + '- Group Entry' or ''
                store_data1[2]['credit'] = credit
                store_data1[2]['debit'] = 0.0
                all_line_ids_without.append(store_data1)

        for line in accounts_dict_partner:
            all_line_ids.extend(accounts_dict_partner[line])

        final_list_ids.extend(all_line_ids_without)
        final_list_ids.extend(all_line_ids)

        move.update({'line_id': final_list_ids})
        move_id = move_pool.create(move, context=context)
        self.write({'move_id': move_id, 'period_id': period_id}, context=context)
        if slip.payslip_run_id.journal_id.entry_posted:
            move_pool.post([move_id], context=context)
        self.pool.get('hr.payslip').write({'paid': True, 'state': 'done'}, context=context)
        return True  # no need to call super.
