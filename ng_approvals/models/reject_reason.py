# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RejectReason(models.Model):
    _name = 'reject.reason'
    _description = 'Rejection reason'

    name = fields.Char("Reject reason")
    type = fields.Selection([
        ('sale', 'Sale'),
        ('general', 'General'),
        ('billing', 'Billing'),
        ('purchase', 'Purchase')
    ], string='Type',
        readonly=False,
        required=True,
        copy=False,
        index=True,
        track_visibility='onchange',
        default='general')
