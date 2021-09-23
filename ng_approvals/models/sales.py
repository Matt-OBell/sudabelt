from odoo import fields, api, models
from urllib.parse import urljoin, urlencode
from lxml import etree
import simplejson


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_manager_approve_by = fields.Many2one(
        'res.users', string='Sale Manager Approved by', readonly=True, copy=False)
    general_manager_approve_by = fields.Many2one(
        'res.users', string='General Manager Approved by', readonly=True, copy=False)
    finance_manager_approve_by = fields.Many2one(
        'res.users', string='Finance Manager Approved by', readonly=True, copy=False)
    reject_reason = fields.Text(readonly=True, copy=False)
    rejected_by = fields.Many2one('res.users', readonly=True, copy=False)
    is_record_owner = fields.Boolean(
        readonly=1, compute='_compute_record_owner', copy=False, store=False, default=False)
    is_my_approval = fields.Boolean(
        readonly=1, compute='_compute_approval_mode', copy=False, store=False, search="_search_field")
    partner_state_id = fields.Many2one(
        'res.country.state', related='partner_id.state_id', store=True)
    geo_zones = fields.Selection([
        ('north_central', 'North Central'),
        ('north_east', 'North East'),
        ('north_west', 'North West'),
        ('south_east', 'South East'),
        ('south_south', 'South South'),
        ('south_west', 'South West')
    ], string="Zone", required=1, default=False,
        states={
             'sales_manager': [('readonly', True)],
             'general_manager': [('readonly', True)],
             'account_manager': [('readonly', True)],
             'approved': [('readonly', True)]
         })
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={
             'sales_manager': [('readonly', True)],
             'general_manager': [('readonly', True)],
             'account_manager': [('readonly', True)],
             'approved': [('readonly', True)]
         })

    def _compute_record_owner(self):
        if int(self.user_id) == int(self.env.uid):
            self.is_record_owner = True
        else:
            self.is_record_owner = False

    def action_sales_manager_approval(self):
        self.state = "sales_manager"
        users = self.env.ref("ng_approvals.group_sale_manager").users
        emails = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        emails = ",".join(emails)
        self._escalate(emails)

    def action_general_manager_approval(self):
        self.state = "general_manager"
        self.sale_manager_approve_by = self.env.uid
        users = self.env.ref("ng_approvals.group_sale_general_manager").users
        emails = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        emails = ",".join(emails)
        self._escalate(emails)

    def action_account_manager_approval(self):
        self.state = "account_manager"
        self.general_manager_approve_by = self.env.uid
        users = self.env.ref("account.group_account_manager").users
        emails = [user.partner_id.email.strip() for user in users if user.partner_id.email]
        emails = ",".join(emails)
        self._escalate(emails)

    def action_approved(self):
        self.state = "approved"
        self.finance_manager_approve_by = self.env.uid
        emails = [self.user_id.login.strip()]
        emails = ",".join(emails)
        self._escalate(emails, 'sale_owner_approval_template')

    def action_reject(self):
        self.state = "reject"
        emails = [self.user_id.login.strip()]
        emails = ",".join(emails)
        self._escalate(emails, 'sale_rejection_template')

    def _escalate(self, email_to, template='sale_approval_template'):
        template = self.env['ir.model.data'].\
            get_object('ng_approvals', template)
        template.with_context(
            {
                "email_to": email_to,
                "url": self.request_link()
                # "products": products
            }
        ).send_mail(self.id, force_send=True)

    def request_link(self):
        fragment = {}
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        model_data = self.env["ir.model.data"]
        fragment.update(base_url=base_url)
        fragment.update(menu_id=model_data.get_object_reference("ng_approvals", "menu_sale_approval")[1])
        fragment.update(model="sale.order")
        fragment.update(view_type="form")
        fragment.update(action=model_data.get_object_reference("ng_approvals", "action_sale_approval")[1])
        fragment.update(id=self.id)
        query = {"db": self.env.cr.dbname}
        res = urljoin(base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment)))
        return res

    def _compute_approval_mode(self):
        for record in self:
            if record.state == 'sales_manager' and \
                    self.env.user.has_group('ng_approvals.group_sale_manager'):
                record.write({'is_my_approval': True})
            elif record.state == 'general_manager' and \
                    self.env.user.has_group('ng_approvals.group_sale_general_manager'):
                record.write({'is_my_approval': True})
            elif record.state == 'account_manager' and \
                    self.env.user.has_group('account.group_account_manager'):
                record.write({'is_my_approval': True})
            else:
                record.write({'is_my_approval': False})

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if context.get('turn_view_readonly'):  # Check for context value
            doc = etree.XML(res['arch'])
            if view_type == 'form':  # Applies only for form view
                for node in doc.xpath("//field"):  # All the view fields to readonly
                    node.set('readonly', '1')
                    node.set('modifiers', simplejson.dumps({"readonly": True}))

                res['arch'] = etree.tostring(doc)
        return res

    def _search_field(self, operator, value):
        field_id = self.search([]).filtered(lambda x: x.is_my_approval == value)
        return [('id', operator, [x.id for x in field_id] if field_id else False)]

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sales_manager', 'Sales Manager'),
        ('general_manager', 'General Manager'),
        ('account_manager', 'Account Manager'),
        ('approved', 'Approved'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
