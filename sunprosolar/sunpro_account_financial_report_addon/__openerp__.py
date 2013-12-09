# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Serpent Consulting Services (<http://serpentcs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'SunPro Financial Reports Add-on',
    'version': '0.5',
    'category': 'Generic Modules/Reporting',
    'description': """ This module ensures that Balance Sheets generated by the sunpro_account_financial_report module balance out.""",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'depends': ['base',
        'sunpro_account_financial_report',
        'report_aeroo_ooo'
    ],
    'data': [
        'wizard/financial_report_wizard_view.xml',
        'report/financial_report_view.xml',
        'account_financial_report_addon_view.xml',
        'security/sunpro_afr_addon_security.xml',
        'report/financial_aeroo_report.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: