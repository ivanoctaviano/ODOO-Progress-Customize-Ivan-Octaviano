# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.osv import osv
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class new_component(models.Model):
	_name = 'new.component'
	_description = 'Component'
	
	name = fields.Char(string='Nama Komponen', required=True)
	waktu = fields.Integer(string='Waktu Pengerjaan', required=True)
	
class new_item(models.Model):
	_name = 'new.item'
	_description = 'Item'
	
	name = fields.Char(string='Nama Item', required=True)
	tanggal_pengerjaan = fields.Date('Tanggal Pengerjaan', required=True)
	expectation_date = fields.Date(compute='expect_day', string='Ekspektasi Tanggal Selesai')
	real_date = fields.Date('Realisasi Tanggal Selesai')
	component_ids = fields.One2many('item.line','item_id')
	total_percentage = fields.Integer(compute='total_persen')
	
	@api.multi
	def expect_day(self):
		for record in self:
			if record.tanggal_pengerjaan and record.component_ids:
				hari = 0
				for comp in record.component_ids:
					hari += comp.component_id.waktu
				record.expectation_date = datetime.strptime(record.tanggal_pengerjaan,'%Y-%m-%d') + relativedelta(days=hari)
			else:
				record.expectation_date = False
				
	@api.multi
	def total_persen(self):
		for record in self:
			if record.component_ids:
				total = 0
				for comp in record.component_ids:
					total += comp.percentage
				record.total_percentage = total
			else:
				record.total_percentage = 0
				
	@api.model
	def create(self, vals):
		res = super(new_item, self).create(vals)
		if not res.component_ids:
			raise ValidationError(_('Komponen yang dibutuhkan belum dipilih'))
		if res.total_percentage > 100:
			raise ValidationError(_('Jumlah persentase seluruh komponen tidak boleh melebihi 100%'))
		return res
		
	@api.multi
	def write(self, vals):
		res = super(new_item, self).write(vals)
		for record in self:
			if not record.component_ids:
				raise ValidationError(_('Komponen yang dibutuhkan belum dipilih'))
			if record.total_percentage > 100:
				raise ValidationError(_('Jumlah persentase seluruh komponen tidak boleh melebihi 100%'))
		return res
	
class item_line(models.Model):
	_name = 'item.line'
	_description = 'Item Line'
	
	item_id = fields.Many2one('new.item')
	component_id = fields.Many2one('new.component', string='Nama Komponen', required=True)
	percentage = fields.Integer(string='Bobot Persentase', required=True)
