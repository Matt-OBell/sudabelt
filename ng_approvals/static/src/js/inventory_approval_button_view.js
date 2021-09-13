odoo.define('ng_approvals.InventoryApprovalView', function (require) {
"use strict";

var InventoryApprovalController = require('ng_approvals.InventoryApprovalController');
var ListView = require('web.ListView');
var viewRegistry = require('web.view_registry');

var InventoryApprovalView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: InventoryApprovalController
    })
});

viewRegistry.add('inventory_approval_button', InventoryApprovalView);

});
