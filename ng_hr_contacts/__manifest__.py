# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Contacts',
    'category': 'Human Resources',
    'author': 'Mattobell',
    'website': 'http://www.mattobell.com',
    'depends': ['hr', 'ng_hr_holidays', 'ng_hr_reminder'],
    'version': '1.0',
    'description': '''
HR Employee Contact Information
===============================
- Guarantor
- Next of Kin
- Reference
    ''',
    'data': [
        'ng_hr_contacts_view.xml',
        # 'security/ir.model.access.csv',
        'cron_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False
}
