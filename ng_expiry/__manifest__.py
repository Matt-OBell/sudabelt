# -*- coding: utf-8 -*-

# Created on 2019-08-03
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Odoo12在线用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/12.0/zh_CN/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.sunpop.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/

##############################################################################
#    Copyright (C) 2009-TODAY Sunpop.cn Ltd. https://www.sunpop.cn
#    Author: Ivan Deng，300883@qq.com
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#    See <http://www.gnu.org/licenses/>.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

{
    "name": "Email notification for expired products within six months",
    "version": "14.0.0.1",
    "author": "Mattobell",
    "category": "Base",
    "website": "https://www.mattobell.net",
    "license": "LGPL-3",
    "sequence": 1,
    "depends": ["product_expiry",],
    "summary": """ """,
    "data": [
        "data/email_template.xml",
        "data/ir_cron_data.xml",
    ],
    "demo": [],
    "test": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
