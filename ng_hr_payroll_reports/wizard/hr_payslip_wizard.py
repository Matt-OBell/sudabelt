# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectCreateSalesOrderInherit(models.TransientModel):
    _name = 'ng.hr.payslip.wizard'
    _description = 'Payslip Report Wizard'

    name = fields.Char(string="Description", required=True)
    rules = fields.Many2many('hr.salary.rule', "payroll_register_rel_salary", "reg_id", "rule_id", string="Salary Rules", required=True)
    employee_ids = fields.Many2many('hr.employee', "payroll_register_rel", "payroll_year_id", "employee_id", string="Employees", required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    to_print_excel_format = fields.Boolean(string="Print as Excel", 
                                           help="Tick if you want to output of report in excel sheet")
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    
    def print_report(self):
        if not self.to_print_excel_format:
            return self.env.ref('ng_hr_payroll_reports.hr_payslip_report').\
                report_action(self)
        else:
            return self.env.ref('ng_hr_payroll_reports.hr_payslip_report_excel'). \
                report_action(self)
