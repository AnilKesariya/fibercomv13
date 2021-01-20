# -*- coding: utf-8 -*-
# Copyright YEAR(2020), AUTHOR(IBAS)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Added comment for commit
from odoo import fields, models, api, _
from odoo.tools.misc import format_date
from odoo.tools import date_utils

import logging
_logger = logging.getLogger(__name__)


class IbasHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    deduct_sss = fields.Boolean(string='Deduct SSS', default=True)
    deduct_hdmf = fields.Boolean(string='Deduct HDMF', default=True)
    deduct_philhealth = fields.Boolean(string='Deduct Philhealth', default=True)
    deduct_mpl = fields.Boolean(string='Deduct MPL', default=True)
    deduct_bayanihan = fields.Boolean(string="Deduct Bayanihan", default=True)
    generate_backpay = fields.Boolean(string='Generate 13th Month Pay/BackPay')
    deduct_healthcard = fields.Boolean(string='Deduct Healthcard', default=True)
    is_deduct_sss_loans = fields.Boolean(string="Deduct SSS Loan", default=True)
    is_deduct_hdmf_loans = fields.Boolean(string="Deduct HDMF Loans", default=True)
    is_deduct_bayanihan_loans = fields.Boolean(string="Deduct Bayanihan Loans", default=True)
    is_deduct_personal_charges = fields.Boolean(string="Deduct Personal Charges", default=True)
    is_deduct_calamity_loans = fields.Boolean(string="Deduct Calamity Loans", default=True)
    is_deduct_other_loans = fields.Boolean(string="Deduct Other Loans", default=True)
    is_deduct_company_loans = fields.Boolean(string="Deduct Company Loans", default=True)

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s - %s' % (payslip_name, self.employee_id.name or '', format_date(self.env, self.date_from, date_format="MMMM y"))

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _("This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        get_worked_days = True
        if hasattr(self, 'is_imported'):
            get_worked_days = not self.is_imported
        if get_worked_days:
            self.worked_days_line_ids = self._get_new_worked_days_lines()
            self.input_line_ids = self._get_new_input_lines()

    def _get_new_input_lines(self):
        if self.struct_id.input_line_type_ids:
            input_lines = self._get_input_lines()
            input_line_ids = self.input_line_ids.browse([])
            for r in input_lines:
                input_line_ids |= input_line_ids.new(r)
            return input_line_ids
        else:
            return [(5, False, False)]

    def _get_input_lines(self):
        lines = []
        for rec in self.struct_id.input_line_type_ids:
            lines.append({
                'input_type_id': rec.id
            })
        return lines

    def _get_worked_day_lines(self):
        res = super(IbasHrPayslip, self)._get_worked_day_lines()

        new_res = []
        work_entry_type_ids = [rec['work_entry_type_id'] for rec in res]
        entry_types = self.env['hr.work.entry.type'].search(['|', ('id', 'in', work_entry_type_ids), ('is_payslip_display', '=', True)])
        entries_to_add = entry_types.filtered(lambda rec: rec.id not in work_entry_type_ids)
        for result in res:
            work_entry_type_id = result['work_entry_type_id']
            is_payslip_display = entry_types.filtered(lambda rec: rec.id == work_entry_type_id).is_payslip_display
            result['number_of_minutes'] = result['number_of_hours'] * 60

            if is_payslip_display:
                new_res.append(result)

        for entry in entries_to_add:
            new_res.append({'sequence': entry.sequence,
                            'work_entry_type_id': entry.id,
                            'number_of_days': 0,
                            'number_of_hours': 0,
                            'amount': 0,
                            })
        return new_res

    @api.model
    def create(self, vals):
        records = super(IbasHrPayslip, self).create(vals)
        for rec in records:
            partner = records.employee_id.user_partner_id
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': records.employee_id.name,
                    'email': records.employee_id.work_email,
                })
            rec.message_subscribe(partner_ids=partner.ids)
        return records

    def action_payslip_send(self):
        try:
            template_id = self.env.ref('ibas_fibercom.email_template_hr_payslip').id
        except:
            template_id = False

        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'hr.payslip',
            'active_model': 'hr.payslip',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def read(self, fields=None, load='_classic_read'):
        results = super(IbasHrPayslip, self).read(fields, load)
        if 'line_ids' in fields and self._context.get('hide_zero_amount'):
            for (res, rec) in zip(results, self):
                res['line_ids'] = self.line_ids.filtered('total').ids
        return results

    def action_payslip_done(self):
        res = super(IbasHrPayslip, self).action_payslip_done()

        for rec in self:
            for line in rec.line_ids:
                if line.code in ['SSSLOAN', 'HDMFLOAN', 'COMPANYLOAN', 'BAYAN', 'BAYANLOAN', 'PC', 'HC', 'CALLOAN', 'OTHERLOAN', 'DONATIONLOAN']:
                    rec.employee_id.loan_ids._deduct_loan_amount(rec, line)
        return res


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    number_of_minutes = fields.Float(string='Number of Minutes')

    @api.onchange('number_of_days')
    def _onchange_number_of_days(self):
        self.number_of_hours = self.number_of_days * 8

    @api.onchange('number_of_hours')
    def _onchange_number_of_hours(self):
        self.number_of_days = self.number_of_hours / 8
        self.number_of_minutes = self.number_of_hours * 60
