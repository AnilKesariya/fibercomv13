from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    prepared_by_id = fields.Many2one('hr.employee', string="Prepared By")
    approved_by_id = fields.Many2one('hr.employee', string="Approved By")
    noted_by_id = fields.Many2one('hr.employee', string="Noted By")
    requested_by_id = fields.Many2one('hr.employee', string='Requested by')
    general_description = fields.Char(string='General Description')
    revision_number = fields.Char(string="Revision Number")
    
    @api.onchange('prepared_by_id','approved_by_id','requested_by_id')
    def _get_signatory_details(self):
        if not self.prepared_by:
            self.prepared_by_designation = self.prepared_by_id.job_id.name
        if not self.approved_by:
            self.approved_by_designation = self.approved_by_id.job_id.name
        if not self.requested_by:
            self.requested_by_designation = self.requested_by_id.job_id.name

    def write(self, vals):
        for key, value in vals.items():
            if key != 'state':
                field_record = self.env['ir.model.fields'].search([('name', '=', key), ('model_id.model', '=', self._name)])
                label = field_record.field_description
                old_value = getattr(self, key)
                new_value = value

                if not old_value:
                    old_value = 'Empty'
                if not new_value:
                    new_value = 'Empty'

                self.message_post(body="{0}: {1} ----> {2}".format(label, old_value, new_value))

        # vals['date_approve'] = fields.Datetime.now()
        return super(PurchaseOrder, self).write(vals)
