# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
    
    def _get_count_down(self, cr, uid, ids, name, args, context=None):
        res = {}
        count = 0
        for data in self.browse(cr, uid, ids, context):
            days_to_collect = data.days_to_collect
            for data in self.browse(cr, uid, ids, context=context):
                end_date = datetime.datetime.strptime(data.create_date , '%Y-%m-%d %H:%M:%S')
                start_date =  datetime.datetime.today()
                difference_in_days = relativedelta(end_date, start_date).days
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
#        'doc_ids': fields.one2many('ir.attachment','document_id1',"Document" ),
        'collected' : fields.boolean("Collected"),
        'days_to_collect': fields.integer("Days to Collect"),
        'notify_customer': fields.many2one("res.partner","Notify Customer when Collected"),
        'notify_users': fields.many2many("res.users", "part_document_rel", "part_id", 'document_id',"Notify Users When Collected"),
        'cowndown':fields.function(_get_count_down, method=True, store=True, string="Countdown Counter", type="integer", help="Remaining days for each document collection"),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('document_id', None):
            return super(doc_required, self).write(cr, uid, ids, vals, context=context)
        vals.update({'collected' : True})
        cur_rec = self.browse(cr, uid, ids, context=context)[0]
        customer = cur_rec.notify_customer
        users = cur_rec.notify_users
        send_mail_obj = self.pool.get('send.send.mail')
        obj_mail_server = self.pool.get('ir.mail_server')
        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
        if not mail_server_ids:
            raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids)[0]
        email_from = mail_server_record.smtp_user
        if not email_from:
            raise osv.except_osv(_('Mail Error'), _('No mail found for smtp user!'))
        if customer:
            if customer.email:
                NO_REC_MSG = ''
                SUB_LINE = 'Notification for Document Upload.'
                MSG_BODY = 'Hello ' + customer.name + ',<br/><br/>' + ' Your Document named ' + cur_rec.doc_id.name + '.<br/><br/> Have been successfully Uploaded.<br/><br/> Thank You.'
                send_mail_obj.send(cr, uid, NO_REC_MSG, SUB_LINE, MSG_BODY, customer.email, context=context)
                
        if users:
            for user in users:
                if user.email:
                    NO_REC_MSG1 = ''
                    SUB_LINE1 = 'Notification for Document Upload.'
                    MSG_BODY1 = 'Hello ' + user.name +',<br/>' +  ' The Document named ' + cur_rec.doc_id.name + '.<br/><br/> Have been successfully Uploaded.<br/><br/> Thank You.'
                    send_mail_obj.send(cr, uid, NO_REC_MSG1, SUB_LINE1, MSG_BODY1, user.email, context=context)
        return super(doc_required, self).write(cr, uid, ids, vals, context=context)

#class ir_attachment(osv.Model):
#    
#    _inherit = "ir.attachment"
#    
#    _columns ={
#            'document_id1': fields.many2one("doc.required","Document")
#    }
    
class documents_all(osv.Model):
    
    _inherit = "documents.all"
    
    _columns = {
            'days_to_collect': fields.integer("Days to Collect"),
            'finace_type': fields.boolean("Is Finance Type?")
     }
    
class crm_lead(osv.Model):
    
    _inherit = "crm.lead"
    
    def on_change_utility_company(self, cr, uid, ids, utility_company_id, context=None):
        values = {}
        document_list = []
        if utility_company_id:
            utility_company = self.pool.get('res.partner').browse(cr, uid, utility_company_id, context=context)
            for document in utility_company.document_ids:
                if document.finace_type == False:
                    document_list.append({'doc_id':document.id})
            values = {'doc_req_ids' : document_list or False}
        return {'value' : values}
    
class sale_order(osv.Model):
    
    _inherit= "sale.order"
    
    def _get_require_doc(self, cr, uid, ids, name, args, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            for doc in data.doc_req_ids:
                if doc.document_id:
                    if doc.document_id.datas == False:
                        res[data.id] = False
                    else:
                        res[data.id] = True
                else:
                    res[data.id] = False
        return res
    
    _columns={
        'doc_req_ids' : fields.one2many('doc.required', 'doc_sale_id', 'Required Documents'),
        'required_document':fields.function(_get_require_doc, method=True, type='boolean', string="Required Document Collected?", help="Checked if Yes."),
    }
    
    def create(self, cr, uid, vals, context=None):
        res = super(sale_order, self).create(cr, uid, vals, context=context)
        docs = []
        crm_obj = self.pool.get('crm.lead')
        doc_required_obj = self.pool.get('doc.required')
        if vals.get('partner_id'):
            crm_ids = crm_obj.search(cr, uid, [('partner_id','=', vals.get('partner_id'))], context=context)
            crm_id = crm_ids[0]
            crm_data = crm_obj.browse(cr, uid, crm_id, context=context)
            if crm_data.utility_company_id:
                if crm_data.utility_company_id.document_ids:
                    req_doc = crm_data.utility_company_id.document_ids
                    if req_doc is None:
                        req_doc= []
                    for rec in req_doc:
                        rec_id = rec.id
                        if rec.finace_type == True:
                            doc_created = doc_required_obj.create(cr, uid, {'doc_id' : rec.id, 'days_to_collect': rec.days_to_collect}, context=context)
                            docs.append(doc_created)
                    self.write(cr, uid, res, {'doc_req_ids': [(6,0,docs)]})
        return res
        
    
    
#class finance_documents_all(osv.Model):
#    """ Model for document information """
#    _name = "finance.documents.all"
#    _description = "Finance Documents Information."
#    
#    _columns = {
#         'name': fields.char('Document Name'),
#         'code': fields.char('Code'),
#     }
#    
#    _sql_constraints = [
#        ('code_uniq', 'unique (code)', 'The code of the Document must be unique !')
#    ]
    