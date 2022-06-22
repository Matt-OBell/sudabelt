# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mattobell (<http://www.mattobell.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name' : 'More Features on Manufacturing Process',
    'version' : '1.0',
    'depends' : ['mrp', 'account', 'stock_account'],
    'author' : 'Mattobell',
    'website' : 'http://www.mattobell.com',
    'description': '''
More Features on Manufacturing
==============================================================
- Modules to add more costs accounts on workcenters and production loss features.
- Also show total cost of workcenters, total cost of raw materials and total cost of finish products on production form.
- User can create parent workcenter and divide the cost in percentage in child workcenters accordingly to capacity and efficiency.
..
..
    ''',
    'category' : 'Manufacturing',
    'sequence': 32,
    'data' : [
        'ng_mrp_view.xml',
        'company_view.xml',
        'stock_history_view.xml',
        'bom_view.xml',
#         'report/manufacturing_order_report.xml'#todoprobuse
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


