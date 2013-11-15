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

from openerp.osv import osv, fields
from datetime import datetime

class insolation_incident(osv.Model):
    
#    def name_get(self, cr, user, ids, context=None):
#        if not ids:
#            return []
#        cur_rec = self.browse(cr, user, ids, context = context)[0]
#        return [(cur_rec.id,cur_rec.station_id.name)]
    
    _name = "insolation.incident.yearly"
    
#    _rec_name = "station_id"
    
    _description = "Insolation Incident Manager (Yearly)"
    
    _columns = {
        'name' : fields.char('Station Name'),
        'parent_id' : fields.many2one('insolation.incident.yearly',"Parent Station"),
        'parent_persentage': fields.float("Parent Station %"),
#        'from_zip' : fields.char('Zip (From)'),
#        'to_zip' : fields.char('Zip (To)'),
        'zip_id' : fields.many2one('city.city',"Zip"),
        'tilt_azimuth_ids': fields.one2many('tilt.azimuth','tilt_azimuth_id','Tilt & Azimuth Reading'),
    }
    
    _constraints = [
        (osv.osv._check_recursion, 'Error ! You cannot create recursive Station.', ['parent_id'])
    ]
    
    
    def compute_percentage(self, cr, uid, ids, context=None):
#        tilt_azimuth = self.pool.get("tilt.azimuth")
        for data in self.browse(cr, uid, ids, context=context):
            if data.parent_id:
                for parent_line in data.parent_id.tilt_azimuth_ids:
                    child_jan = (data.parent_persentage/100) * parent_line.jan
                    child_feb = (data.parent_persentage/100) * parent_line.feb
                    child_mar = (data.parent_persentage/100) * parent_line.mar
                    child_apr = (data.parent_persentage/100) * parent_line.apr
                    child_may = (data.parent_persentage/100) * parent_line.may
                    child_jun = (data.parent_persentage/100) * parent_line.jun
                    child_jul = (data.parent_persentage/100) * parent_line.jul
                    child_aug = (data.parent_persentage/100) * parent_line.aug
                    child_sep = (data.parent_persentage/100) * parent_line.sep
                    child_oct = (data.parent_persentage/100) * parent_line.oct
                    child_nov = (data.parent_persentage/100) * parent_line.nov
                    child_dec = (data.parent_persentage/100) * parent_line.dec
                    child_production = (data.parent_persentage/100) * parent_line.production
                    self.write(cr, uid, ids, {"tilt_azimuth_ids": [(0,0,{'tilt': parent_line.tilt.id,'azimuth':parent_line.azimuth,'jan':child_jan,'feb':child_feb,'mar':child_mar,'apr':child_apr,'may':child_may,'jun':child_jun,'jul':child_jul,'aug':child_aug,'sep':child_sep,'oct':child_oct,'nov':child_nov,'dec':child_dec, 'production':child_production})]})
    
class tilt_azimuth(osv.Model):
    """ Model for Tilt and Azimuth. """
    _name = "tilt.azimuth"
    
    _description= "Tilt and Azimuth Information."
    
    def _get_annual_avg(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for anual_avg in self.browse(cr, uid, ids, context=context):
            avg = anual_avg.jan + anual_avg.feb + anual_avg.mar + anual_avg.apr + anual_avg.may + anual_avg.jun + anual_avg.jul + anual_avg.aug + anual_avg.sep + anual_avg.oct + anual_avg.nov + anual_avg.dec
            res[anual_avg.id] =  avg
        return res
    
    
    _columns = {
        'tilt_azimuth_id': fields.many2one('insolation.incident.yearly','Tilt and Azimuth'),
        'tilt': fields.many2one('tilt.tilt','Tilt'),
        'azimuth': fields.selection(
                    [
                        ('n','[N]North'),
                        ('ne','[NE]North-East'),
                        ('e','[E]East'),
                        ('se','[SE]South-East'),
                        ('s','[S]South'),
                        ('sw','[SW]South-West'),
                        ('w','[W]West'),
                        ('nw','[NW]North-West')
                    ],'Azimuth'),
#        'month' : fields.selection(
#                    [
#                        (1,'January'),
#                        (2,'February'), 
#                        (3,'March'), 
#                        (4,'April'),
#                        (5,'May'), 
#                        (6,'June'), 
#                        (7,'July'), 
#                        (8,'August'),
#                        (9,'September'),
#                        (10,'October'),
#                        (11,'November'),
#                        (12,'December'),
#                        (13,'Production'),
#                    ],'Month'),
        'jan': fields.float('Jan'),
        'feb': fields.float('Feb'),
        'mar': fields.float('Mar'),
        'apr': fields.float('Apr'),
        'may': fields.float('May'),
        'jun': fields.float('Jun'),
        'jul': fields.float('Jul'),
        'aug': fields.float('Aug'),
        'sep': fields.float('Sep'),
        'oct': fields.float('Oct'),
        'nov': fields.float('Nov'),
        'dec': fields.float('Dec'),
        'annual_avg': fields.function(_get_annual_avg, string='Annual Average', type='float'),
        'production' : fields.float('Production (kWh/m2)')
    }
    
    _sql_constraints = [('record_uniq', 'unique(tilt_azimuth_id, tilt, azimuth)', 'Duplication found in Tilt and Azimuth Reading.')]

class station_station(osv.Model):
    
    _name = "station.station"
    
    _description = "Station Master"
    
    _columns = {
        'name' : fields.char("Name",required=True),
    }
    
class tilt_tilt(osv.Model):
    
    _name = "tilt.tilt"
    
    _rec_name = "tilt"
    
    _description = "Tilt Master"
    
    _columns = {
        'tilt' : fields.char("Name",requiered=True)
    }
    
class electricity_usage(osv.Model):
    
    _name = 'electricity.usage'
    
    _description = "Annual Electricity Usage"
    
    def onchange_month_value(self, cr, uid ,ids, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec, context=None):
        avg = (jan + feb + mar + apr + may + jun + jul + aug + sep + oct + nov + dec)/12
        return {'value':{'usage_kwh':avg}}
    
    _columns = {
        'name' : fields.integer("Year"),
        'jan' : fields.integer("January"),
        'feb' : fields.integer('February'),
        'mar' : fields.integer('March'),
        'apr' : fields.integer("April"),
        'may' : fields.integer("May"),
        'jun' : fields.integer("June"),
        'jul' : fields.integer("July"),
        'aug' : fields.integer("August"),
        'sep' : fields.integer("September"),
        'oct' : fields.integer("October"),
        'nov' : fields.integer("November"),
        'dec' : fields.integer("December"),
        'usage_kwh' : fields.integer("Usage (KWh)"),
        'lead_id' : fields.many2one("crm.lead"),
    }
    
    _defaults = {
        'name' : datetime.now().year,
        'jan' : 0,
        'feb' : 0,
        'mar' : 0,
        'apr' : 0,
        'may' : 0,
        'jun' : 0,
        'jul' : 0,
        'aug' : 0,
        'sep' : 0,
        'oct' : 0,
        'nov' : 0,
        'dec' : 0,
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: