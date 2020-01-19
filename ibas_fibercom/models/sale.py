
# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class IBASSale(models.Model):
    _inherit = 'sale.order' 

    name = fields.Char(string='Order Reference', required=True, copy=False, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))

    ibas_order_type = fields.Selection([
        ('MRF', 'MRF'),
        ('SALE', 'Sale'),
    ], string='Docment Type', default='MRF')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if vals['ibas_order_type'] == "MRF":
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                        'ibas_fibercom.mrf', sequence_date=seq_date) or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('ibas_fibercom.mrf', sequence_date=seq_date) or _('New')
            else:
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                        'sale.order', sequence_date=seq_date) or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(IBASSale, self).create(vals)
        return result
    
    # def mark_approved(self):
    #     for rec in self:
    #         rec.name = rec.name.replace(' ISSUANCE','')
    #         rec.name = rec.name.replace(' APPROVED','')
    #         rec.name = rec.name.replace(' DONE','')
    #         rec.name = rec.name + " APPROVED"
    
    # def mark_issuance(self):
    #     for rec in self:
    #         rec.name = rec.name.replace('APPROVED','ISSUANCE')
            
    
    # def mark_done(self):
    #     for rec in self:
    #         rec.name = rec.name.replace('APPROVED','DONE')
    #         rec.name = rec.name.replace('ISSUANCE','DONE')
    
    # def clear_marks(self):
    #     for rec in self:
    #         rec.name = rec.name.replace(' ISSUANCE','')
    #         rec.name = rec.name.replace(' APPROVED','')
    #         rec.name = rec.name.replace(' DONE','')
