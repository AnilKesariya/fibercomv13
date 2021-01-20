# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _


class Loan(models.Model):
    _name = "hr.loan"
    _description = 'Employee Loans'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    employee_id = fields.Many2one('hr.employee', string="Employee")
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    currency_id = fields.Many2one('res.currency', default=_default_currency)
    amount_total = fields.Monetary(string="Total Loan Amount")
    amount_deduct = fields.Monetary(string="Deduction Amount")
    type = fields.Selection(
        [('sss', 'SSS'),
         ('hdmf', 'HDMF'),
         ('company_loan', 'Company Loan'),
         ('bayanihan', 'Bayanihan'),
         ('bayanihan_loan', 'Bayanihan Loan'),
         ('personal_charges', 'Personal Charges'),
         ('health_card', 'Health Card'),
         ('calamity_loan', 'Pag-IBIG Calamity Loan'),
         ('other', 'Other'),
         ('donation', 'Donation')], string='Type')
    amount_total_deducted = fields.Monetary(string="Total Deducted Amount")
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('done', 'Done')], string="Status",
                             default="draft", store=True)

    def action_open(self):
        self.write({'state': 'open'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def _compute_state(self):
        if self.amount_total_deducted >= self.amount_total:
            self.state = 'done'

    def name_get(self):
        result = []
        for loan in self:
            amount_str = 0.0
            if loan.currency_id.position == 'before':
                amount_str = loan.currency_id.symbol + \
                    ' ' + str(loan.amount_total)
            if loan.currency_id.position == 'after':
                amount_str = str(loan.amount_total) + ' ' + \
                    loan.currency_id.symbol
            result.append((loan.id, "[%s] %s" %
                           (amount_str, loan.employee_id.name)))
        return result

    def _get_loan_amount(self, loan_type, payslip):
        loan_amount = 0.0
        for rec in self.filtered(lambda r: r.state == 'open' and r.date_from >= payslip.date_from and r.date_to <= payslip.date_to and r.type == loan_type):
            if rec.amount_deduct > (rec.amount_total - rec.amount_total_deducted):
                loan_amount += (rec.amount_total - rec.amount_total_deducted)
            else:
                loan_amount += rec.amount_deduct
        return loan_amount

    def _deduct_loan_amount(self, payslip, line):
        types = {
            'SSSLOAN': 'sss',
            'HDMFLOAN': 'hdmf',
            'COMPANYLOAN': 'company_loan',
            'BAYAN': 'bayanihan',
            'BAYANLOAN': 'bayanihan_loan',
            'PC': 'personal_charges',
            'HC': 'health_card',
            'CALLOAN': 'calamity_loan',
            'OTHERLOAN': 'other',
            'DONATIONLOAN': 'donation',
        }
        loan = self.filtered(lambda r: r.state == 'open' and r.date_from >= payslip.date_from and r.date_to <= payslip.date_to and r.type == types[line.code])
        if loan:
            loan.write({'amount_total_deducted': loan.amount_total_deducted + line.total})
            loan._compute_state()
