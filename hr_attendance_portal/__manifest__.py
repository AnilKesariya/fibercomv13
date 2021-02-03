# -*- coding: utf-8 -*-
# Copyright (C) 2020 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "hr attendance professional portal check in out",

    'summary': """
        Module creates a website page for attendance portal users""",


    'author': "Shurshilov Artem",
    'website': "http://www.eurodoo.com",
    "live_test_url": "https://www.eurodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '13.0.0.0',
    "license": "OPL-1",
    'price': 40,
    'currency': 'EUR',
    'images':[
        'static/description/Attendance_website.png',
        'static/description/Attendance_website.png',
        'static/description/Attendance_website.png',
        'static/description/Attendance_website.png',
    ],

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/views.xml',

        #'views/res_config_settings_views.xml',
    ],
    'qweb': [
       # "static/src/xml/attendance.xml",
    ],
}
