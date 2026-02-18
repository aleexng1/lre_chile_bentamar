# -*- coding: utf-8 -*-
# from odoo import http


# class LreChileBentamar(http.Controller):
#     @http.route('/lre_chile_bentamar/lre_chile_bentamar', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lre_chile_bentamar/lre_chile_bentamar/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('lre_chile_bentamar.listing', {
#             'root': '/lre_chile_bentamar/lre_chile_bentamar',
#             'objects': http.request.env['lre_chile_bentamar.lre_chile_bentamar'].search([]),
#         })

#     @http.route('/lre_chile_bentamar/lre_chile_bentamar/objects/<model("lre_chile_bentamar.lre_chile_bentamar"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lre_chile_bentamar.object', {
#             'object': obj
#         })

