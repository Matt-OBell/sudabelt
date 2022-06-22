# -*- coding: utf-8 -*-
from odoo import http

# class NgPaymentAdviceReport(http.Controller):
#     @http.route('/ng_payment_advice_report/ng_payment_advice_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ng_payment_advice_report/ng_payment_advice_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ng_payment_advice_report.listing', {
#             'root': '/ng_payment_advice_report/ng_payment_advice_report',
#             'objects': http.request.env['ng_payment_advice_report.ng_payment_advice_report'].search([]),
#         })

#     @http.route('/ng_payment_advice_report/ng_payment_advice_report/objects/<model("ng_payment_advice_report.ng_payment_advice_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ng_payment_advice_report.object', {
#             'object': obj
#         })