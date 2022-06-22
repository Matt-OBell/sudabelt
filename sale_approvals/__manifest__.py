{
    'name': 'Sale Approvals',
    'depends': [
                'sale', 'account'
                ],
    'category': 'Sales/Accounting',
    'summary': """This app allow you to manage Sale Order and Invoice Approvals""",
    'description': """ Sale order and invoice approvals 
                    Two levels of approvals for sale order which are as Sales Manager & Credit Control Manager.""",
    'author': 'Hamza Ilyas',
    'website': 'hamza.ilyaaaas@gmail.com',
    # 'images': ['static/description/icon.png'],
    'data': [
        'security/sale_approval_groups.xml',
        'views/sale_order_ext.xml',
        'views/account_move_ext.xml',
    ],
    'installable': True,
}
