from odoo import api, models


class PayslipReport(models.AbstractModel):
    _name = 'report.ng_hr_payroll_reports.view_hr_payslip_report'
    _description = 'Payslip Report'

    def get_salaries(self, rules, employee_ids, date_from, date_to):
        
        salary_rule = []
        for rule in rules:
            salary_rule.append(rule.id)
            
        params = [employee_ids, date_from, date_to]
        # query = """SELECT hp.name, hpl.name, sum(hpl.amount), sum(hpl.total) FROM hr_payslip hp
        # INNER join hr_payslip_line hpl ON hpl.slip_id = hp.id
        # INNER JOIN hr_employee employee ON employee.id = hp.employee_id
        # WHERE hpl.salary_rule_id in (%s) AND hp.employee_id = %s
        # AND (hp.date_from >= %s) AND (hp.date_to <= %s)
        # GROUP BY ROLLUP (hp.name, hpl.name)"""

        query = """SELECT employee.name AS employee, 
        hpl.name AS "payslip_name", 
        (hpl.amount) AS amount, 
        (hpl.total) AS total 
        FROM hr_payslip hp 
        INNER JOIN hr_payslip_line hpl ON hpl.slip_id = hp.id 
        INNER JOIN hr_employee employee ON employee.id = hp.employee_id 
        WHERE hpl.salary_rule_id in """+str(tuple([key for key in salary_rule])).replace(',)', ')')+""" AND hp.employee_id = %s 
        AND (hp.date_from >= %s) 
        AND (hp.date_to <= %s) ORDER BY sequence ASC"""

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        return res

    @api.model
    def _get_report_values(self, docids, data=None):

        return {
            'doc_ids': docids,
            'doc_model': 'ng.hr.payslip.wizard',
            'docs': self.env['ng.hr.payslip.wizard'].browse(docids),
            'data': data,
            'get_salaries': self.get_salaries,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)
