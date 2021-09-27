from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.ng_hr_payroll_reports.hr_payroll_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, payslips):
        # salary_rule_totals = []
        for payslip in payslips:
            report_name = payslip.name
            rule_count = 0
            employee_count = 7
            # One sheet by payslip
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format(
                {'bold': True, 'font_size': 10, 'font_name': 'Helvetica'})
            header = workbook.add_format(
                {'font_size': 30, 'bold': True, 'font_name': 'Times New Roman'})
            row2 = workbook.add_format(
                {'font_size': 10, 'align': 'vcenter', 'font_name': 'Helvetica'})
            date_format = workbook.add_format(
                {'num_format': 'd mmmm yyyy', 'font_family': 'Helvetica', 'font_size': 10})
            money_format = workbook.add_format(
                {'num_format': payslip.currency_id.symbol + '#,##0.00', 'font_name': 'Helvetica'})
            
            sheet.set_row(0, 50)
            sheet.merge_range(0, 5, 0, 8, "Payroll Register", header)
            sheet.write(2, 4, "From", bold)
            sheet.write_datetime(2, 5, payslip.date_from, date_format)
            sheet.write(2, 6, "To", bold)
            sheet.write_datetime(2, 7, payslip.date_to, date_format)

            for employee in payslip.employee_ids:
                total = 0
                salary_count = 1
                salaries = self._get_salaries(employee.id, payslip)
                print(salaries)
                if employee_count == 7:
                    sheet.write(5, 0, "Name", bold)

                sheet.write(employee_count, 0, employee.name, row2)
                for salary in salaries:
                    if employee_count == 7:
                        sheet.write(5, salary_count, salary['payslip_name'], bold)

                    # rule_name = salary['payslip_name']
                    # salary_rule_totals[rule_name] = salary_rule_totals[rule_name] + salary['total']
                    sheet.write(employee_count, salary_count, salary['total'], money_format)
                    total = total + salary['total']
                    salary_count = salary_count + 1
                    rule_count = rule_count + 1

                if employee_count == 7:
                    sheet.write(5, salary_count, "Total", bold)
                    sheet.set_column(0, salary_count + 1, 12)

                sheet.write(employee_count, salary_count, total, money_format)
                employee_count = employee_count + 1

            # Quick fix since this is my last day. I didn't have time to write this better
            _LETTER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            for count in range(0, rule_count):
                sheet.write_formula(
                    employee_count + 1, count + 1, '=SUM(' + _LETTER[count + 1] + '8:' + _LETTER[count + 1] + str(employee_count) + ')'
                )

    def _get_salaries(self, employee_id, payslip):

        salary_rule = []

        for rule in payslip.rules:
            salary_rule.append(rule.id)

        params = [employee_id, payslip.date_from, payslip.date_to]

        query = """SELECT employee.name AS employee, 
        hpl.name AS "payslip_name", 
        (hpl.amount) AS amount, 
        (hpl.total) AS total 
        FROM hr_employee employee 
        RIGHT JOIN hr_payslip hp ON hp.employee_id = employee.id  
        RIGHT JOIN hr_payslip_line hpl ON hpl.slip_id = hp.id 
        WHERE hpl.salary_rule_id IN """ + str(tuple([key for key in salary_rule])).replace(',)', ')') + """
        AND hp.employee_id = %s
        AND (hp.date_from >= %s) 
        AND (hp.date_to <= %s) ORDER BY sequence ASC"""
        # print(query)

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        return res
