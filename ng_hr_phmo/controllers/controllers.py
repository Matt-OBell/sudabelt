# -*- coding: utf-8 -*-
# from odoo import http


# class NgHrPhmo(http.Controller):
#     @http.route('/ng_hr_phmo/ng_hr_phmo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ng_hr_phmo/ng_hr_phmo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ng_hr_phmo.listing', {
#             'root': '/ng_hr_phmo/ng_hr_phmo',
#             'objects': http.request.env['ng_hr_phmo.ng_hr_phmo'].search([]),
#         })

#     @http.route('/ng_hr_phmo/ng_hr_phmo/objects/<model("ng_hr_phmo.ng_hr_phmo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ng_hr_phmo.object', {
#             'object': obj
#         })
