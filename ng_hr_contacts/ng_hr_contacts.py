# -*- coding: utf-8 -*-

from datetime import datetime
#from dateutil.relativedelta import relativedelta

from datetime import timedelta

from odoo import models, fields, api, _

import re
import time

DATETIME_FORMAT = "%Y-%m-%d"


class Guarantor(models.Model):
    _name = 'guarantor'

    name = fields.Char(string='First Name', required=True)
    lname = fields.Char(string='Last Name', required=False)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              string='Gender', required=False)
    marital = fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower',
                                                                               'Widower'), ('divorced', 'Divorced')], string='Marital Status', required=False)
    home = fields.Text(string='Home Address', required=False)
    office = fields.Text(string='Office Address', required=False)
    email = fields.Char(string='Email')
    tel1 = fields.Char(string='Telephone Number 1', required=False)
    tel2 = fields.Char(string='Telephone Number 2', required=False)
    rel = fields.Char(string='Relationship with Employee', required=False)
    status = fields.Selection([('e', 'Employed'), ('s', ' Self Employed'),
                               ('u', 'Unemployed')], string='Work Status', required=False)
    state = fields.Selection(selection=[
        ('not_verify', 'Not Verified'),
        ('verify', 'Verified'),
        ('declined', 'Declined')],
        string='Status', readonly=False, required=True, default='not_verify')
    employer = fields.Char(string='Employer')
    notes = fields.Text(string='Notes')
    emp_id = fields.Many2one('hr.employee', string='Employee')

    @api.multi
    @api.constrains('email')
    def _check_email(self):
        email_re = re.compile(r"""
        ([a-zA-Z][\w\.-]*[a-zA-Z0-9]     # username part
        @                                # mandatory @ sign
        [a-zA-Z0-9][\w\.-]*              # domain must start with a letter
         \.
         [a-z]{2,3}                      # TLD
        )
        """, re.VERBOSE)
        if self.email:
            if not email_re.match(self.email):
                raise Warning(_('Warning'), _('Please enter valid email address'))
        return True


class nextofkin(models.Model):
    _name = 'nextofkin'

    name = fields.Char(string='First Name', required=True)
    lname = fields.Char(string='Last Name', required=False)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender', required=False)
    marital = fields.Selection([('single', 'Single'), ('married', 'Married'),
                                ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status', required=False)
    home = fields.Text(string='Home Address', required=False)
    office = fields.Text(string='Office Address', required=False)
    email = fields.Char(string='Email')
    tel1 = fields.Char(string='Telephone Number 1', required=False)
    tel2 = fields.Char(string='Telephone Number 2', required=False)
    rel = fields.Char(string='Relationship with Employee', required=False)
    status = fields.Selection([('e', 'Employed'), ('s', ' Self Employed'),
                               ('u', 'Unemployed')], 'Status', required=False)
    employer = fields.Char(string='Employer')
    notes = fields.Text(string='Notes')
    emp_id = fields.Many2one('hr.employee', string='Employee')

    @api.multi
    @api.constrains('email')
    def _check_email(self):
        email_re = re.compile(r"""
        ([a-zA-Z][\w\.-]*[a-zA-Z0-9]     # username part
        @                                # mandatory @ sign
        [a-zA-Z0-9][\w\.-]*              # domain must start with a letter
         \.
         [a-z]{2,3}                      # TLD
        )
        """, re.VERBOSE)
        if self.email:
            if not email_re.match(self.email):
                raise Warning(_('Warning'), _('Please enter valid email address'))
        return True


class ref(models.Model):
    _name = 'refs'

    name = fields.Char(string='First Name', required=True)
    lname = fields.Char(string='Last Name', required=False)
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female')], string='Gender', required=False)
    marital = fields.Selection(selection=[('single', 'Single'), ('married', 'Married'), (
        'widower', 'Widower'), ('divorced', 'Divorced')], string='Marital Status', required=False)
    home = fields.Text(string='Home Address', required=False)
    office = fields.Text(string='Office Address', required=False)
    email = fields.Char(string='Email')
    tel1 = fields.Char(string='Telephone Number 1', required=False)
    tel2 = fields.Char(string='Telephone Number 2', required=False)
    rel = fields.Char(string='Relationship with Employee', required=False)
    status = fields.Selection(selection=[(
        'e', 'Employed'), ('s', ' Self Employed'), ('u', 'Unemployed')], string='Work Status', required=False)
    state = fields.Selection(selection=[
        ('not_verify', 'Not Verified'),
        ('verify', 'Verified')],
        string='Status', default='not_verify', readonly=True)
    user = fields.Many2one('res.users', string='Verified By', required=False, readonly=True)
    employer = fields.Char('Employer')
    notes = fields.Text('Notes')
    emp_id = fields.Many2one('hr.employee', string='Employee')

    @api.multi
    def verify(self):
        return self.write({'state': 'verify', 'user': self._uid})

    @api.multi
    def notverify(self):
        return self.write({'state': 'not_verify', 'user': self._uid})

    @api.multi
    @api.constrains('email')
    def _check_email(self):
        email_re = re.compile(r"""
        ([a-zA-Z][\w\.-]*[a-zA-Z0-9]     # username part
        @                                # mandatory @ sign
        [a-zA-Z0-9][\w\.-]*              # domain must start with a letter
         \.
         [a-z]{2,3}                      # TLD
        )
        """, re.VERBOSE)
        if self.email:
            if not email_re.match(self.email):
                raise Warning(_('Warning'), ('Please enter a valid email address'))
        return True


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    @api.multi
    def onchange_no_periods(self, join_date, no_periods):
        if not join_date:
            return {'value': {
                'confirm_date': False,
            }}

        confirm_date = datetime.strptime(join_date, '%Y-%m-%d') + timedelta(days=no_periods)
        return {'value': {
            'confirm_date': confirm_date.strftime('%Y-%m-%d'),
        }}

    @api.model
    def run_confirmation(self, employee_ids=False):
        ctx = self._context.copy()
        date_today = time.strftime('%Y-%m-%d')

        if not employee_ids:
            employee_ids = self.search([])

        for emp in employee_ids:
            if not emp.confirm_date:
                continue
            if emp.company_id:
                emp_company = emp.company_id
            else:
                emp_company = self.env.user.company_id
            hr_template = emp_company.email_template_id_confirmation  # .id
#            emp_template = emp_company.emp_email_template_id.id
            days1 = emp_company.hr_remind_days_confirmation
            birthday = emp.confirm_date

            cur_day = date_today.split('-')
            c1 = cur_day[1]
            c2 = cur_day[2]

            # send reminder to hr before one day logic..
            dt_check = datetime.strptime(birthday, '%Y-%m-%d') - timedelta(days=days1)
            pre_bdate = dt_check.strftime('%Y-%m-%d')
            emp_bday1 = pre_bdate.split('-')
            e11 = emp_bday1[1]
            e22 = emp_bday1[2]
            if e11 == c1 and e22 == c2:
                hr_template.with_context(ctx).send_mail(emp.id)
        return True

    ref_ids = fields.One2many('refs', 'emp_id', string='References')
    gua_ids = fields.One2many('guarantor', 'emp_id', string='Guarantors')
    kin_ids = fields.One2many('nextofkin', 'emp_id', string='Next of Kin')
    no_periods = fields.Float(string='Probation Period')
    confirm_date = fields.Date(string='Confirmation Date')  # , fnct_inv=_set_minimum_planned_date


class Company(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    @api.model
    def _get_hr_reminder(self):
        ids = self.env['mail.template'].search(
            [('name', '=', 'HR Confirmation Reminder Template')], limit=1)
        return ids

    hr_remind_days_confirmation = fields.Integer(
        string='Confirmation Reminder Days', help='Please specify number of days to send email reminder to HR Department for employee confirmation date.', default=1)
    email_template_id_confirmation = fields.Many2one(
        'mail.template', string='Confirmation Email Template', help='Reminder to HR Department email template.', default=_get_hr_reminder)
