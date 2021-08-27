# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def _cron_notify_scheduler_queue(self, days=183):
        config = self.env['res.config.settings']
        #if config.module_product_expiry:
        self._schedule_notification_for_expected_expiration(days)

    def _schedule_notification_for_expected_expiration(self, days):
        today = fields.Datetime.today()
        future = today + datetime.timedelta(days=days)
        domain = [
            ('expiration_date', '>', today),
            ('expiration_date', '<=', fields.Datetime.to_string(future))
        ]
        products = self.env['stock.production.lot'].search(domain, order='expiration_date asc')
        users = self.env.ref("stock.group_stock_manager").users
        emails = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        emails = ",".join(emails)
        var = []
        for product in products:
            ctx = {
                "expiration_date": fields.Date.to_string(product.expiration_date),
                "lot": product.name,
                "name": product.product_id.name,
                "days": (product.expiration_date - today).days
            }
            var.append(ctx)
        if len(var) > 0:
            self._escalate(emails, var)

    def _escalate(self, emails, products):
        template = self.env['ir.model.data'].\
            get_object('ng_expiry', 'email_template_notify_inventory_manager_mail')
        template.with_context(
            {
                "emails": emails,
                "products": products
            }
        ).send_mail(self.id, force_send=True)
