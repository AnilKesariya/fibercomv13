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
from odoo.exceptions import ValidationError
from odoo import fields, models, api


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    prepared_by = fields.Char(string="Prepared By")
    prepared_by_designation = fields.Char(
        string="Prepared By Designation", default="Logistics Assistant")
    approved_by = fields.Char(string="Approved By")
    approved_by_designation = fields.Char(
        string="Approved By Designation", default="COO")
    noted_by = fields.Char(string="Noted By")
    requested_by = fields.Char(string='Requested by')
    requested_by_designation = fields.Char(string='Requested by Designation', default='Project Manager')

    def write(self, vals):
        self.ensure_one()
        if vals.get('state') in ['done', 'purchase']:
            user = self.env.user
            if user and user.has_group('jt_fcom_sale_ext.group_fcom_purchase_engineer'):
                raise ValidationError('You are not allowed to validate RFQ!')
        return super(PurchaseOrder, self).write(vals)
