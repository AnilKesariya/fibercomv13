# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import time
import xlrd

from collections import OrderedDict
from datetime import datetime

from odoo import api, fields, models


class PayslipImport(models.TransientModel):
    _name = 'payslip.import'
    _description = 'Payslip Import'

    file = fields.Binary('File', required=True)
    date_from = fields.Date(string='Date From', required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Date To', required=True, default=datetime.now())
    struct_id = fields.Many2one('hr.payroll.structure', string='Structure', required=True)

    def get_data(self, keys, sheet):
        for i in range(1, sheet.nrows):
            row = (c.value for c in sheet.row(i))
            yield OrderedDict(zip(keys, row))

    def payslip_import(self):
        xlDecoded = base64.b64decode(self.file)
        xlsx = xlrd.open_workbook(file_contents=xlDecoded)
        sheet = xlsx.sheet_by_index(0)
        keys = [c.value for c in sheet.row(0)]
        data = self.get_data(keys, sheet)
        HR_PAYSLIP = self.env['hr.payslip']
        workdays_code = self.env['hr.work.entry.type'].search_read([('name', 'in', keys)], ['name', 'code'])
        input_line_ids = self.env['hr.payslip.input.type'].search_read([('name', 'in', keys)], ['name'])
        workdays_code_dict = {}
        input_line_dict = {}
        values = []
        for code in workdays_code:
            workdays_code_dict[code['name']] = code['id']
        for input_line in input_line_ids:
            input_line_dict[input_line['name']] = input_line['id']
        for rec in data:
            employee = self.env['hr.employee'].search([('name', '=', rec['Employees'])])
            if employee:
                worked_days_entries = []
                other_input_entries = []
                for key, value in rec.items():
                    if key == 'Employees':
                        continue
                    if workdays_code_dict.get(key):
                        worked_days_entries.append((0, 0, {
                            'work_entry_type_id': workdays_code_dict.get(key),
                            'number_of_days': value,
                            'number_of_hours': value*8,
                            'contract_id': employee.contract_id.id
                        }))
                    elif input_line_dict.get(key, False) in self.struct_id.input_line_type_ids.ids:
                        other_input_entries.append((0, 0, {
                            'input_type_id': input_line_dict[key],
                            'amount': value or 0
                        }))
                values.append({
                    'name': employee.name,
                    'employee_id': employee.id,
                    'worked_days_line_ids': worked_days_entries,
                    'input_line_ids': other_input_entries,
                    'contract_id': employee.contract_id.id,
                    'struct_id': self.struct_id.id,
                    'is_imported': True,
                    'date_to': self.date_to,
                    'date_from': self.date_from,
                    'deduct_sss': rec.get('Deduct SSS', True),
                    'deduct_hdmf': rec.get('Deduct HDMF', True),
                    'deduct_philhealth': rec.get('Deduct Philhealth', True),
                    'deduct_mpl': rec.get('Deduct MPL', True),
                    'deduct_bayanihan': rec.get('Deduct Bayanihan', True),
                    'generate_backpay': rec.get('Generate 13th Month Pay/BackPay', True),
                    'deduct_healthcard': rec.get('Deduct Healthcard', True),
                    'is_deduct_sss_loans': rec.get('Deduct SSS Loan', True),
                    'is_deduct_hdmf_loans': rec.get('Deduct HDMF Loans', True),
                    'is_deduct_bayanihan_loans': rec.get('Deduct Bayanihan Loans', True),
                    'is_deduct_personal_charges': rec.get('Deduct Personal Charges', True),
                    'is_deduct_calamity_loans': rec.get('Deduct Calamity Loans', True),
                    'is_deduct_other_loans': rec.get('Deduct Other Loans', True),
                    'is_deduct_company_loans': rec.get('Deduct Company Loans', True),
                })
        records = HR_PAYSLIP.create(values)
        for rec in records:
            rec._onchange_employee()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def action_import_payslip(self):
        view_id = self.env.ref('payslip_import.view_payslip_import_form').id
        return {
            'name': 'Import Payslips',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }
