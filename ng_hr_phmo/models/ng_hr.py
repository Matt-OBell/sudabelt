# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrExtended(models.Model):
    _inherit = "hr.employee"

    administrator = fields.Many2one("pension.fund", string="Pension Funds Administrator")
    administrator_id = fields.Char("PFA ID")
    health_management = fields.Many2one("health.management", string="Health Management Organization")
    management_id = fields.Char("HMO ID")

class HrConfiguration(models.TransientModel):
    _inherit= 'res.config.settings'

    administrator = fields.Char("Pension Funds Administrator")
    health_management = fields.Char("Health Management Organization")

class Health(models.Model):
    _name = "health.management"
    _description = "Health"

    name = fields.Char('Health Management Organization')
    hmo_id = fields.Char("HMO ID")
   
class Pension(models.Model):
    _name = "pension.fund"
    _description = "Pension"
   
    name = fields.Char('Pension Funds Administrator')
    pfd_id = fields.Char("PFD ID")

#   related = fields.Many2one('res.config.settings')  "school.student", string="Name", required=Tru