# -*- coding: utf-8 -*-

{
    'name': 'Payslips Merge Accounting',
    'version': '1.0',
    "author": "Mattobell",
    "website": "http://www.mattobell.com",
    'description': '''

This module merge accounting entries created from batch payroll. You will find checkbox on batch payroll form.

- Important Note: This module is not compitible with ng_hr_payroll_contract module.
- It will only merge the accounting entries if it will not find partner linked on it. => Partner can be set on contribution register or for receivable/payable accounts.

''',
    'data': [
        'payroll_view.xml',
    ],
    'depends': ['ng_hr_payroll'],
    'installable': True,
    'category': 'Human Resources',
    'auto_install': False
}
