# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    requested_by = fields.Char(string="Requested by")
    approved_by = fields.Char(string="Approved by")

    def _compute_group_engineer(self):
        for order in self:
            order.group_engineer = False
            user = self.env.user
            if user and user.has_group('jt_fcom_sale_ext.group_fcom_sale_engineer'):
                order.group_engineer = True

    group_engineer = fields.Boolean(string='Is Engineer?', compute="_compute_group_engineer")

    @api.onchange('ibas_order_type')
    def _onchange_document_type(self):
        self._compute_group_engineer()

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        user = self.env.user
        if user and user.has_group('jt_fcom_sale_ext.group_fcom_sale_engineer'):
            res['ibas_order_type'] = 'MRF'
        return res

    def _compute_is_admin(self):
        for order in self:
            order.is_admin = False
            user = self.env.user
            if user and (user.has_group('base.group_system') or user.has_group('base.group_erp_manager') or user.has_group('sales_team.group_sale_manager')):
                order.is_admin = True

    is_admin = fields.Boolean(string='Is Admin', compute="_compute_is_admin")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self._compute_is_admin()

    @api.onchange('partner_shipping_id')
    def onchange_partner_shipping_id(self):
        for rec in self:
            if rec.partner_shipping_id:
                rec.analytic_account_id = rec.partner_shipping_id.analytic_account and rec.partner_shipping_id.analytic_account.id or False
                for line in rec.order_line:
                    line.analytic_tag_ids = [
                        (6, 0, rec.partner_shipping_id.analytic_tags.ids)]


class SaleOrderline(models.Model):

    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.order_id and self.order_id.partner_shipping_id:
            self.analytic_tag_ids = [
                (6, 0, self.order_id.partner_shipping_id.analytic_tags.ids)]


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    project_code = fields.Char(string='Project Code')
    project_area = fields.Char(string='Project Area')
    requested_by = fields.Char(
        related="sale_id.requested_by", string="Requested by")
    approved_by = fields.Char(
        related="sale_id.approved_by", string="Approved by")
    issued_by = fields.Char(string='Issued By')

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.partner_id and res.partner_id.project_code:
            res.project_code = res.partner_id.project_code
        if res.partner_id and res.partner_id.project_area:
            res.project_area = res.partner_id.project_area
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.project_code:
            self.project_code = self.partner_id.project_code
        if self.partner_id and self.partner_id.project_area:
            self.project_area = self.partner_id.project_area
