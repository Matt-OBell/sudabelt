# -*- coding: utf-8 -*-

{
    "name": "Nigerian Payroll Reports",
    "category": "Localization",
    "" "init_xml": [],
    "author": "Mattobell",
    "website": "http://www.mattobell.com",
    "depends": ["hr", "hr_payroll", "hr_holidays", "web", "report_xlsx"],
    "version": "1.0",
    "description": """
    Nigeria Payroll Salary Rules
    Configuration of hr_payroll for Nigeria localization
    All main contributions rules for Nigeria payslip.

    Key Features

    * New payslip report
    * Employee Contracts
    * Allow to configure Basic / Gross / Net Salary
    * Employee PaySlip
    * Allowance / Deduction
    * Integrated with Holiday Management
    * Medical Allowance, Travel Allowance, Child Allowance, ...
    * Payroll Advice and Report
    * Yearly Salary by Head and Yearly Salary by Employee Report
    * Management of Increments, Overtimes, Notices, Terminal Benefits, Unions, Contract History, etc..

    Yearly salary by Employee - Report should be fix.
    -bug:report should be print each employee detail in new pag
    """,
    "active": False,
    "data": [
        "report/hr_payslip_report.xml",
        "report/report.xml",
        "wizard/hr_payslip_view.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
