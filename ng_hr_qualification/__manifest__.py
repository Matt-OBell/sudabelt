# -*- coding: utf-8 -*-

{
    'name': 'Improvements on HR Management',
    'version': '1.0',
    'depends': ['base', 'hr', 'hr_recruitment'],
    'author': 'Mattobell',
    'website': 'http://www.mattobell.com',
    'description': '''
Improvements on HR
=====================================
- Academic Qualifications
- Schools Attended
- Professional Qualification
- Degree
- Institution
- Years of Experience

    ''',
    'category': 'Human Resources',
    'sequence': 70,
    'data': [
        # 'security/hr_security.xml',
        'security/ir.model.access.csv',
        'ng_hr_qualification_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
