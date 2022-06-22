{
    "name": "Purchase Landed Costs - Sudabelt",
    "version": "1.0",
    "depends": ["purchase", "account", "stock"],
    "author": "Mattobell",
    "website": "http://www.mattobell.com",
    "description": """
            Landed Cost for Sudabelt
    """,
    "category": "Purchase Management",
    "sequence": 32,
    "data": [
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_move_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: