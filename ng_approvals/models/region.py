from odoo import fields, api, models


class Region(models.Model):
    _name = 'res.region'
    _description = 'Regions'

    name = fields.Char()
    country = fields.Many2one('res.country')
