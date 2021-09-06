from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    leave_validation_type = fields.Selection(selection_add=[('triple', 'Team Leader/ COO and Time Off Officer')])
#     state = fields.Selection(selection_add=[('to_approve', 'To approve')])
