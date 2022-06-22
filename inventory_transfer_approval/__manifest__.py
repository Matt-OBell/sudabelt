{
    'name': 'Inventory Transfer Approval',
    'depends': [
                'stock',
                ],
    'category': 'Inventory',
    'summary': """This app allow you to manage transfer of inventory""",
    'description': """ One approval for transfer of inventory, 
                    validate button should only be visible to the group (advisor) """,
    'author': 'Hamza Ilyas',
    'website': 'hamza.ilyaaaas@gmail.com',
    # 'images': ['static/description/icon.png'],
    'data': [
        'views/stock_picking_ext.xml',
    ],
    'installable': True,
}
