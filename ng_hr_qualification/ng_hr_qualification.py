"""."""
# -*- coding: utf-8 -*-

import datetime

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrRecruitmentDegree(models.Model):
    """Employee Degree."""

    _inherit = 'hr.recruitment.degree'
    _description = 'Employee Degree'
    code = fields.Char(string='Code')
    note = fields.Text(string='Description')


class Subject(models.Model):
    """Employee Course."""

    _name = 'employee.subject'
    _description = 'Employee Course'

    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Description')


class Institution(models.Model):
    """Employee Institution."""

    _name = 'employee.institution'
    _description = 'Employee Institution'

    name = fields.Char(string='Name', required=True)
#        'code': fields.char('Code', size=16, required=False),
    note = fields.Text(string='Description')


class QualificationProf(models.Model):
    """Employee Prof Qualification."""

    _name = 'employee.prof.qualification'
    _description = 'Employee Prof Qualification'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    note = fields.Text(string='Description')


class Academic(models.Model):
    """Employee school attend."""

    _name = 'academic.qualification'
    _description = 'Academic'
    _order = 'date asc'
    _rec_name = 'type_id'

    type_id = fields.Many2one('hr.recruitment.degree', string='Degree', required=True)
    school_id = fields.Many2one('employee.institution', string='Institution')
    date = fields.Date(string='Date')
    emp_id = fields.Many2one('hr.employee', string='Employee', required=False)
    subject_ids = fields.Many2one('employee.subject', string='Course', required=False)
    apply_id = fields.Many2one('hr.applicant', string='Applicant', required=False)
    user = fields.Many2one('res.users', string='Verified By', required=False, readonly=True)
    state = fields.Selection(selection=[('not_verify', 'Not Verified'), ('verify',
                                                                         'Verified')], string='Status', readonly=True, default='not_verify')
    comment = fields.Text(string='Comment')

    @api.multi
    def verify(self):
        """."""
        return self.write({'state': 'verify', 'user': self._uid})

    @api.multi
    def notverify(self):
        """."""
        return self.write({'state': 'not_verify', 'user': self._uid})


class ProfQualification(models.Model):
    """Employee professional qualification."""

    _name = 'professional.qualification'
    _description = 'professional qualification'
    _rec_name = 'type_id'

    award_org = fields.Char(string='Awarding Organization')
    type_id = fields.Many2one('employee.prof.qualification', string='Qualification', required=True)
    date = fields.Date(string='Date')
    emp_id = fields.Many2one('hr.employee', string='Employee')
    apply_id = fields.Many2one('hr.applicant', string='Applicant')
    user = fields.Many2one('res.users', string='Verified By', readonly=True)
    state = fields.Selection(selection=[('not_verify', 'Not Verified'), ('verify',
                                                                         'Verified')], string='Status', readonly=True, default='not_verify')

    @api.multi
    def verify(self):
        """."""
        return self.write({'state': 'verify', 'user': self._uid})

    @api.multi
    def notverify(self):
        """."""
        return self.write({'state': 'not_verify', 'user': self._uid})


class SchoolAttend(models.Model):
    """Employee school attend."""

    _name = 'employee.school.attend'
    _description = 'Employee attend school'
    _rec_name = 'school_id'

    school_id = fields.Many2one('employee.institution', string='Institution')
    attend_id = fields.Many2one('hr.employee', string='Employee')
    apply_id = fields.Many2one('hr.applicant', string='Applicant')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')


class HrApplicant(models.Model):
    """."""

    _inherit = 'hr.applicant'
    _description = 'Applicant'

    @api.multi
    def create_employee_from_applicant(self):
        """Create an hr.employee from the hr.applicants."""
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write(
                    {'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                                           'job_id': applicant.job_id.id,
                                                           'address_home_id': address_id,
                                                           'department_id': applicant.department_id.id or False,
                                                           'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                                           'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                                           'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()

                emp_id = employee.id
                for i in applicant.act_ids:  # probuse
                    self.env['academic.qualification'].create({
                        'type_id': i.type_id.id,
                        'school_id': i.school_id.id,
                        'date': i.date,
                        'subject_ids': i.subject_ids.id,
                        'emp_id': emp_id
                    }
                    )  # probuse
                for i in applicant.school_ids:  # probuse
                    self.env['employee.school.attend'].create({
                        'school_id': i.school_id.id,
                        'start_date': i.start_date,
                        'end_date': i.end_date,
                        'attend_id': emp_id
                    }
                    )  # probuse

                for i in applicant.prf_ids:  # probuse
                    self.env['professional.qualification'].create({
                        'award_org': i.award_org,
                        'date': i.date,
                        'type_id': i.type_id.id,
                        'emp_id': emp_id
                    }
                    )  # probuse

            else:
                raise UserError(
                    _('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

    @api.one
    @api.depends('birthday')
    def _age(self):
        res = {}
        for a in self:
            if not a.birthday:
                res[a.id] = 0.0
                continue
            today = date.today()
            birthday = False
            birthday1 = datetime.datetime.strptime(a.birthday, "%Y-%m-%d")
            birthday = date(today.year, birthday1.month, birthday1.day)
            if birthday > today:
                age = today.year - birthday1.year - 1
            else:
                age = today.year - birthday1.year
            res[a.id] = age
        return res

    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female')], string='Gender')
    birthday = fields.Date(string='Date of Birth')
    age = fields.Float(compute='_age', string='Age', help='Age of applicant', store=True)
    exp = fields.Float(string='Years of Experience')
    # from core module to change string
    type_id = fields.Many2one('hr.recruitment.degree', string='Highest Degree')
    school_ids = fields.One2many('employee.school.attend', 'apply_id', string='Schools')
    act_ids = fields.One2many('academic.qualification', 'apply_id',
                              string='Academic Qualifications')
    prf_ids = fields.One2many('professional.qualification', 'apply_id',
                              string='Professional Qualifications')


class HrEmployee(models.Model):
    """."""

    _inherit = 'hr.employee'
    _description = 'Employee'

    @api.multi
    @api.depends('birthday')
    def _age(self):
        res = {}
        for a in self:
            if not a.birthday:
                res[a.id] = 0.0
                continue
            today = date.today()
            birthday = False
            birthday1 = datetime.datetime.strptime(a.birthday, "%Y-%m-%d")
            birthday = date(today.year, birthday1.month, birthday1.day)
            if birthday > today:
                age = today.year - birthday1.year - 1
            else:
                age = today.year - birthday1.year
            a.age = age

    age = fields.Float(compute='_age', string='Age', help='Age of employee', store=True)
    school_ids = fields.One2many('employee.school.attend', 'attend_id', string='Schools')
    act_ids = fields.One2many('academic.qualification', 'emp_id', string='Academic Qualifications')
    prf_ids = fields.One2many('professional.qualification', 'emp_id',
                              string='Professional Qualifications')
