# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.utils.csvutils import build_csv_response
from frappe.utils.xlsxutils import build_xlsx_response
from frappe.utils import round_based_on_smallest_currency_fraction
from datetime import datetime

import frappe

class EFakturTransaction(Document):
	def validate(self):
		if not (self.company and self.date_from and self.date_to):
			frappe.throw(_('Company, From Date and To Date are Mandatory'))

		si = frappe.db.get_list('Sales Invoice', 
			fields = ['*'],
			filters = {
				'company': str(self.company),
				'posting_date': ['between', [str(self.date_from), str(self.date_to)]],
				'name': ['in', [d.sales_invoice for d in self.item]],
				'docstatus': '1'
			}
		)

		ef = frappe.db.get_list('EFaktur',
			fields = ['*'],
			filters = {
				'is_used': 0,
				'efaktur_id': ['in', [d.efaktur_id for d in self.item]]
			},
			order_by = 'efaktur_id asc'
		)

		efts = frappe.db.get_list('EFaktur Transaction Item',
			fields = ['*'],
			filters = {
				'sales_invoice': ['in', [d.sales_invoice for d in self.item]],
				'docstatus': ['in', ['0','1']],
				'parent': ['!=', self.name]
			}
		)

		eftf = frappe.db.get_list('EFaktur Transaction Item',
			fields = ['*'],
			filters = {
				'efaktur_id': ['in', [d.efaktur_id for d in self.item]],
				'docstatus': ['in', ['0','1']],
				'parent': ['!=', self.name]
			}
		)

		for i in range(len(self.item)):
			self.validate_sales_invoice(si, efts, self.item[i].sales_invoice)
			self.validate_faktur_pajak(ef, eftf, self.item[i].efaktur_id)

	def on_submit(self):
		for i in range(len(self.item)):
			frappe.db.set_value('EFaktur', self.item[i].efaktur_id, {
				'is_used': 1
			})

	def on_cancel(self):
		for i in range(len(self.item)):
			frappe.db.set_value('EFaktur', self.item[i].efaktur_id, {
				'is_used': 0
			})

	def button_get_item(self):
		if not (self.date_from and self.date_to):
			frappe.throw(_('From Date and To Date are Mandatory'))

		si = frappe.db.get_list('Sales Invoice', 
			fields = ['*'],
			filters = {
				'company': str(self.company),
				'posting_date': ['between', [str(self.date_from), str(self.date_to)]],
				'docstatus': '1',
				# 'status': 'Paid'
			}
		)

		eft = frappe.db.get_list('EFaktur Transaction Item',
			fields = ['*'],
			filters = {
				'sales_invoice': ['in', [d.name for d in si]],
				'docstatus': ['in', ['0','1']]
			}
		)
		
		columns = []
		for i in range(len(si)):
			if not self.check_eft_already_exists(eft, si[i].name):
				data = {
					"sales_invoice": si[i].name,
					"efaktur_id": "",
					"efaktur_date": si[i].posting_date
				}
				columns.append(data)

		return columns

	def button_auto_assign(self):
		if not (self.date_from and self.date_to):
			frappe.throw(_('From Date and To Date are Mandatory'))

		ef = frappe.db.get_list('EFaktur',
			fields = ['*'],
			filters = {
				'is_used': 0
			},
			order_by = 'efaktur_id asc'
		)

		columns = []
		for i in range(len(self.item)):
			data = {
				"sales_invoice": self.item[i].sales_invoice,
				"efaktur_id": ef[i].efaktur_id,
				"efaktur_date": self.item[i].efaktur_date
			}
			columns.append(data)

		return columns

	def check_eft_already_exists(self, eft, sales_invoice):
		p = False
		for x in eft:
			if x.sales_invoice == sales_invoice:
				p = True
				return p
		return p

	def validate_sales_invoice(self, si, efts, sales_invoice):
		p = False
		for x in si:
			if x.name == sales_invoice:
				p = True
		if p == False:
			frappe.throw(_("sales invoice " + sales_invoice + " tidak ditemukan"))

		p = False
		for x in efts:
			if x.sales_invoice == sales_invoice:
				frappe.throw(_("sales invoice " + sales_invoice + " sudah pernah digunakan"))

	def validate_faktur_pajak(self, ef, eftf, efaktur_id):
		p = False
		for x in ef:
			if x.efaktur_id == efaktur_id:
				p = True
		if p == False:
			frappe.throw(_("faktur pajak " + efaktur_id + " tidak ditemukan"))

		p = False
		for x in eftf:
			if x.efaktur_id == efaktur_id:
				frappe.throw(_("faktur pajak " + efaktur_id + " sudah pernah digunakan"))
	
@frappe.whitelist()
def export_efaktur(efaktur_transaction_id):
	eft = frappe.db.get_list('EFaktur Transaction Item',
			fields = ['*'],
			filters = {
				'docstatus': ['in', ['0','1']],
				'parent': ['=', efaktur_transaction_id]
			}
		)
	if (len(eft) <= 0):
		frappe.throw(_("faktur pajak " + efaktur_transaction_id + " tidak ditemukan"))

	si = frappe.db.get_list('Sales Invoice', 
			fields = ['*'],
			filters = {
				'name': ['in', [d.sales_invoice for d in eft]]
			}
		)
	if (len(si) <= 0):
		frappe.throw(_("sales invoice tidak ditemukan"))

	sii = frappe.db.get_list('Sales Invoice Item',
			fields = ['*'],
			filters = {
				'parent': ["in", [d.name for d in si]]
			}
		)

	addcust = frappe.db.get_list('Address',
			fields = ['*'],
			filters = {
				'name': ['in', [d.customer_address for d in si]]
			}
		)

	columns = []
	columns.append(
		[
			'FK','KD_JENIS_TRANSAKSI','FG_PENGGANTI','NOMOR_FAKTUR','MASA_PAJAK','TAHUN_PAJAK',
			'TANGGAL_FAKTUR','NPWP','NAMA','ALAMAT_LENGKAP','JUMLAH_DPP','JUMLAH_PPN',
			'JUMLAH_PPNBM','ID_KETERANGAN_TAMBAHAN','FG_UANG_MUKA','UANG_MUKA_DPP',
			'UANG_MUKA_PPN','UANG_MUKA_PPNBM','REFERENSI'
		]
	)
	columns.append(
		[
			'LT','NPWP','NAMA','JALAN','BLOK','NOMOR','RT','RW','KECAMATAN','KELURAHA',
			'KABUPATEN','PROPINSI','KODE_POS','NOMOR_TELEPON','','','','',''
		]
	)
	columns.append(
		[
			'OF','KODE_OBJEK','NAMA','HARGA_SATUAN','JUMLAH_BARANG','HARGA_TOTAL','DISKON','DPP',
			'PPN','TARIF_PPNBM','PPNBM','','','','','','','',''
		]
	)

	company_name = 'PT. United Family Food'
	company_address =  	'PERKANT. SUNRISE GARDEN BLOK A3 NO 1 KEDOYA UTARA KEBON JERUK \n\n' + \
						'JAKARTA,'
	for i in range(len(eft)):
		for j in range(len(si)):
			if si[j].name == eft[i].sales_invoice:
				items = []
				discount = si[j].discount_amount / si[j].total_qty
				total_dpp = 0
				total_ppn = 0
				for k in range(len(sii)):
					if sii[k].parent == si[j].name:
						amount = round_based_on_smallest_currency_fraction((sii[k].price_list_rate*sii[k].qty), 'IDR', 0)
						diskon = round_based_on_smallest_currency_fraction((sii[k].qty * (discount + sii[k].discount_amount)), 'IDR', 0)
						dpp = round_based_on_smallest_currency_fraction((amount - diskon), 'IDR', 0)
						ppn = round_based_on_smallest_currency_fraction((dpp / 10), 'IDR', 0)
						total_dpp = total_dpp + dpp
						total_ppn = total_ppn + ppn
						items.append(
							[
								'OF',str(sii[k].item_code),str(sii[k].item_name),
								str(sii[k].price_list_rate),str(sii[k].qty),str(amount),
								str(diskon),str(dpp),str(ppn),'0','0','','','','','','','',''
							]
						)
				efd = datetime.strptime(str(eft[i].efaktur_date), "%Y-%m-%d")
				efd = efd.strftime("%d/%m/%Y")
				columns.append(
					[
						'FK','01','0',str(eft[i].efaktur_id).replace('.',''),
						str(datetime.strptime(str(si[i].posting_date), "%Y-%m-%d").month),
						str(datetime.strptime(str(si[i].posting_date), "%Y-%m-%d").year),
						str(efd),'',str(si[j].customer_name),
						str(find_address_by_name(addcust, si[j].customer_address)),
						str(total_dpp),str(total_ppn),'0','','0',
						'0','0','0',str(si[j].name)
					]
				) 
				columns.append(
					[
						'FAPR',company_name,company_address,'','','','','','','','','',
						'','','','','','',''
					]
				)
				for k in range(len(items)):
					columns.append(items[k])

	build_xlsx_response(columns, 'efaktur_template')

def find_address_by_name(arr, name):
	for x in arr:
		if x.name == name:
			return x.address_line1
