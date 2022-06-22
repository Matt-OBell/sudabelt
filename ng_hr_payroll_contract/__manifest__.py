# -*- coding: utf-8 -*-
{
    'name': 'Payroll Extended on Contract',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 21,
    'summary': 'Payroll Extended on Contract',
    'description': '''
Payroll
================================
- Contract form extended with salary rules
- Configured Amounts on Contract
    ''',
    'author': 'Mattobell',
    'website': 'http://www.mattobell.com',
    'images': [
    ],
    'depends': ['ng_hr_payroll', 'hr_payroll_account'],
    'data': [
        'ng_hr_payroll_contract_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
