# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from osv import fields, osv
import datetime
from dateutil.relativedelta import relativedelta
    
class doc_required(osv.Model):
    
#    def _get_count_down(self, cr, uid, context=None):
#        res = {}
#        count = 0
#        doc_ids = self.search(cr, uid, [], context=context)
#        for id in doc_ids:
#            doc_data = self.browse(cr, uid, id, context=context)
#            days_to_collect = doc_data.days_to_collect
#            end_date = datetime.datetime.strptime(doc_data.create_date , '%Y-%m-%d %H:%M:%S')
#            start_date =  datetime.datetime.today()
#            difference_in_days = relativedelta(end_date, start_date).days
#            if days_to_collect >= difference_in_days:
#                count = days_to_collect- difference_in_days
#            else:
#                count = 0
#            self.write(cr, uid, doc_ids, {'cowndown':count}, context=context)
#        return True
    
    def _get_count_down(self, cr, uid, ids, name, args, context=None):
        res = {}
        count = 0
        for data in self.browse(cr, uid, ids, context):
            days_to_collect = data.days_to_collect
            create_date = datetime.datetime.strptime(data.create_date , '%Y-%m-%d %H:%M:%S')
            date_create = create_date.strftime('%Y-%m-%d')
            end_date = datetime.datetime.strptime(date_create , '%Y-%m-%d')
            today_date =  datetime.datetime.today()
            date_today = today_date.strftime('%Y-%m-%d')
            start_date = datetime.datetime.strptime(date_today , '%Y-%m-%d')
            difference_in_days = (start_date-end_date).days
            if days_to_collect >= difference_in_days:
                count = days_to_collect- difference_in_days
            else:
                count = 0
            res[data.id] = count
        return res
     
    
    _name="doc.required"
    
    _columns={
        'create_date':fields.datetime('Date',readonly=True),
        'doc_sale_id' : fields.many2one("sale.order", 'order'),
        'doc_id' : fields.many2one("documents.all","Document Name"),
        'document_id': fields.many2one('ir.attachment',"Document" ),
        'collected' : fields.boolean("Collected"),
        'days_to_collect': fields.integer("Days to Collect"),
        'notify_customer': fields.many2one("res.partner","Notify Customer when Collected"),
        'notify_users': fields.many2many("res.users", "part_document_rel", "part_id", 'document_id',"Notify Users When Collected"),
#        'cowndown':fields.integer("Countdown Counter", help="Remaining days for each document collection"),
        'cowndown':fields.function(_get_count_down, method=True, string="Countdown Counter", type="integer", help="Remaining days for each document collection"),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        mail_mail = self.pool.get('mail.mail')
        attachment_obj = self.pool.get('ir.attachment')
        email_template_obj = self.pool.get('email.template')
        res_partner_obj = self.pool.get('res.partner')
        res_users_obj = self.pool.get('res.users')
        if not vals.get('document_id', None):
            return super(doc_required, self).write(cr, uid, ids, vals, context=context)
        if attachment_obj.browse(cr, uid, vals.get('document_id'), context = context).datas == False:
            vals.update({'collected' : False})
            return super(doc_required, self).write(cr, uid, ids, vals, context=context)
        vals.update({'collected' : True})
        cur_rec = self.browse(cr, uid, ids, context=context)[0]
        customer = cur_rec.notify_customer
        if not customer:
            if vals.get('notify_customer', None):
                notify_cust = vals.get('notify_customer', None)
                customer = res_partner_obj.browse(cr, uid, notify_cust, context=context)
        users = cur_rec.notify_users
        send_mail_obj = self.pool.get('send.send.mail')
        if customer:
            if customer.email:
                template_id = self.pool.get('ir.model.data').get_object(cr, uid, 'sps_sale', 'upload_required_document_cutomer', context=context)
                template_values = email_template_obj.generate_email(cr, uid, template_id, cur_rec.id, context=context)
                template_values.update({'email_to': customer.email})
                msg_id = mail_mail.create(cr, uid, template_values, context=context)
                mail_mail.send(cr, uid, [msg_id], context=context)
        if users:
            for user in users:
                if user.email:
                    template_id = self.pool.get('ir.model.data').get_object(cr, uid, 'sps_sale', 'upload_required_document_user', context=context)
                    template_values = email_template_obj.generate_email(cr, uid, template_id, cur_rec.id, context=context)
                    template_values.update({'email_to': user.email})
                    msg_id = mail_mail.create(cr, uid, template_values, context=context)
                    mail_mail.send(cr, uid, [msg_id], context=context)
        return super(doc_required, self).write(cr, uid, ids, vals, context=context)

class documents_all(osv.Model):
    
    _inherit = "documents.all"
    
    _columns = {
            'days_to_collect': fields.integer("Days to Collect"),
            'finace_type': fields.boolean("Is Finance Type?")
     }
    
#class crm_lead(osv.Model):
#    
#    _inherit = "crm.lead"
#    
#    def on_change_utility_company(self, cr, uid, ids, utility_company_id, context=None):
#        values = {}
#        document_list = []
#        if utility_company_id:
#            utility_company = self.pool.get('res.partner').browse(cr, uid, utility_company_id, context=context)
#            for document in utility_company.document_ids:
#                if document.finace_type == False:
#                    document_list.append({'doc_id':document.id})
#            values = {'doc_req_ids' : document_list or False}
#        return {'value' : values}
    
class sale_order(osv.Model):
    
    _inherit= "sale.order"
    
    def _get_require_doc(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for data in self.browse(cr, uid, ids, context=context):
            document_obj = self.pool.get('documents.all')
            if not data.doc_req_ids:
                res[data.id] = True
            else:
                for doc in data.doc_req_ids:
                    if doc.doc_id.prevent == True:
                        if doc.document_id:
                            if doc.document_id.datas == False:
                                res[data.id] = False
                                break
                            else:
                                res[data.id] = True
                        else:
                            res[data.id] = False
                            break
                    else:
                        res[data.id] = True
        return res
    
    _columns={
        'doc_req_ids' : fields.one2many('doc.required', 'doc_sale_id', 'Required Documents'),
        'required_document':fields.function(_get_require_doc, store= True, method=True, type='boolean', string="Required Document Collected?", help="Checked if Yes."),
    }
    
