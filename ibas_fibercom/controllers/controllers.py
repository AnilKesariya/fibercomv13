# -*- coding: utf-8 -*-
from odoo import http

# class IbasFibercom(http.Controller):
#     @http.route('/ibas_fibercom/ibas_fibercom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ibas_fibercom/ibas_fibercom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ibas_fibercom.listing', {
#             'root': '/ibas_fibercom/ibas_fibercom',
#             'objects': http.request.env['ibas_fibercom.ibas_fibercom'].search([]),
#         })

#     @http.route('/ibas_fibercom/ibas_fibercom/objects/<model("ibas_fibercom.ibas_fibercom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ibas_fibercom.object', {
#             'object': obj
#         })