# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mattobell (<http://www.mattobell.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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

from odoo import api, fields, models, _


class StaffTransfer(models.Model):
    _name = 'staff.transfer'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].get('name')
        vals['name'] = sequence
        return super(StaffTransfer, self).create(vals)

    name = fields.Char(string="Transfer ID", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True)
    employee_dept = fields.Many2one('hr.department', string="Employee Dept", related='employee_id.department_id')
    employee_job = fields.Many2one('hr.job', string="Employee Job", related='employee_id.job_id')
    present_branch = fields.Many2one('staff.branches', string="Present Branch")
    new_transfer_branch = fields.Many2one('staff.branches', string="New Transfer Branch")

    transfer_reasons = fields.Text(string="Transfer Reason", required=True)

    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting Approval'), ('cancel', 'Cancel'),
                              ('done', 'Done')], default='draft')

    @api.multi
    @api.onchange('employee_id')
    def onchangeemployee(self):
        if self.employee_id:
            xyz = self.env['hr.employee'].search([('name', '=', self.employee_id.name)])
            self.present_branch = xyz.employee_branch

    @api.multi
    def confirm(self):
        return self.write({'state': 'waiting'})

    @api.multi
    def button_approve(self):

        xyz = self.env['hr.employee'].search([('name', '=', self.employee_id.name)])

        xyz.employee_branch = self.new_transfer_branch

        res = super(StaffTransfer, self)
        # Send an Email
        ctx = self.env.context.copy()
        ctx.update({'employee_email': self.employee_id.work_email,
                    'employee_name': self.employee_id.name})

        employee_template = self.env.ref('ng_hr_transfer.email_template_to_employee')

        employee_template.with_context(ctx).send_mail(self.id, force_send=True)

        return res, self.write({'state': 'done'})

    @api.multi
    def button_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})


