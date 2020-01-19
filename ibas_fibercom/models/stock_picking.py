# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class IBASStockPicking(models.Model):
    _inherit = 'stock.picking'

    subcon = fields.Many2one('res.partner', string='Subcon')
    requested_by = fields.Char(string='Requested By')
    approved_by = fields.Char(string='Approved By')
    project_code = fields.Char(string='Project Code')
    project_area = fields.Char(string='Project Area')
    