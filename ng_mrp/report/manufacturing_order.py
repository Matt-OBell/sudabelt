#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mattobell (<http://mattobell.com>). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class manufacturing_order(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(manufacturing_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'get_manufacturing_order': self._get_manufacturing_order,       
        })
  
    def _get_manufacturing_order(self):
        mrp_production = self.pool.get('mrp.production')
        mrp_productions = mrp_production.browse(self.cr,self.uid,self.ids)[0]
        return mrp_productions

   

# NOTE: THIS ID MUST BE THESAME AS THE NAME DEFINED IN THE ID of the account_invoice_extend_report.xml, WITHOUT THE report_ PREFIX, attached to this name, other wise you will get an error in the mako template, when calling a python method
report_sxw.report_sxw('report.manufacturing.order.webkit', 
                      'ng_mrp.manufacturing_order', 
                      'ng_mrp/report/manufacturing_order.mako', 
                      parser=manufacturing_order)
