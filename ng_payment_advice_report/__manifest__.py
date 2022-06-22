# -*- coding: utf-8 -*-
{
    'name': "ng_payment_advice_report",
    'summary': """
        Add Payment adivce on Purchase  receipt""",
    'description': """
        Long description of module's purpose""",
    'author': "Mattobell Limited",
    'website': "http://www.mattobell.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','account_voucher','report'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}