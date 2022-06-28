{
    'name': "ng_payment_advice_report",
    'summary': """
        Add Payment adivce on Purchase  receipt""",
    'description': """
        Long description of module's purpose""",
    'author': "Mattobell Limited",
    'website': "http://www.mattobell.com",
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',
    'depends': ['base','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/advice_report.xml',
        'views/account_move.xml',
    ],
    "license": "LGPL-3",

}