# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2014 Mattobell (<http://www.mattobell.com>)
#    Copyright (C) 2010-Today odoo SA (<http://www.odoo.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging

_logger = logging.getLogger(__name__)

import time
from datetime import datetime, timedelta

from odoo import models, fields, api


class company(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    @api.model
    def _get_hr_reminder(self):
        ids = self.env['mail.template'].search(
            [('name', '=', 'HR Birthday Reminder Template')], limit=1)
        return ids

    @api.model
    def _get_emp_wish(self):
        ids = self.env['mail.template'].search(
            [('name', '=', 'HR Birthday Wish to Employee')], limit=1)
        return ids

    hr_remind_days = fields.Integer(string='Birthday Reminder Days',
                                    help='Please specify number of days to send email reminder to HR Department for employee Birthdays.', default=1)
    email_template_id = fields.Many2one('mail.template', string='Reminder Email Template',
                                        help='Reminder to HR Department email template.', default=_get_hr_reminder)
    emp_email_template_id = fields.Many2one('mail.template', string='Birthday Wish Email Template',
                                            help='Email template to send Birthday greetings to employee.', default=_get_emp_wish)
    hr_email = fields.Char(
        string='HR Email', help='This email address will be used as To address in case of Birthday Reminder to HR Department and From address as send wish to Employee.')


class employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    @api.depends('name', 'company_id.hr_email')
    def _get_email(self):
        data = self.env['res.users'].browse(self._uid)
        print "data", data
        for record in self:
            #            record.hr_email = record.company_id and record.company_id.hr_email or data.company_id.hr_email or data.user_email or ''
            record.hr_email = record.company_id and record.company_id.hr_email or data.company_id.hr_email or ''

    hr_email = fields.Char(compute='_get_email', string='Company HR Email Address', store=True)

    @api.model
    def run_birthday(self, employee_ids=False):
        ctx = self._context.copy()
        date_today = time.strftime('%Y-%m-%d')
        if not employee_ids:
            employee_ids = self.search([])

        for emp in employee_ids:
            if not emp.birthday:
                continue
            if emp.company_id:
                emp_company = emp.company_id
            else:
                emp_company = self.env.user.company_id

            hr_template = emp_company.email_template_id  # .id
            emp_template = emp_company.emp_email_template_id  # .id
            days1 = emp_company.hr_remind_days
            birthday = emp.birthday

            emp_bday = birthday.split('-')
            e1 = emp_bday[1]
            e2 = emp_bday[2]

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

            # send reminder to employee
            if e1 == c1 and e2 == c2:
                emp_template.with_context(ctx).send_mail(emp.id)
        return True
