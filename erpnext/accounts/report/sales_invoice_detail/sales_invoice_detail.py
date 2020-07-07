# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import msgprint, _
from frappe.utils import get_first_day

import frappe

def execute(filters=None):
	# msgprint(_(filters.get("company")))
	columns = [
		_("Sales Invoice ID") + ":Data:100", 
		_("Customer ID") + ":Data:50",
		_("Customer Name") + ":Data:300",
		_("Customer Type") + ":Data:100",
		_("Sales Order ID") + ":Data:100",
		_("Invoice Date") + ":Data:100",
		_("Week") + ":Data:100",
		_("Month") + ":Data:100",
		_("Year") + ":Data:100",
		_("Currency") + ":Data:100",
		_("TOP") + ":Data:100",
		_("Qty") + ":Data:100",
		_("Price List") + ":Data:100",
		_("Discount") + ":Data:100",
		_("Amount") + ":Data:100",
		_("Type") + ":Data:100",
		_("Item ID") + ":Data:100",
		_("Item Name") + ":Data:100",
		_("Sales Person ID") + ":Data:100",
		_("Sales Person Name") + ":Data:100",
		_("Depo") + ":Data:100",
		_("Address") + ":Data:100",
		_("Beat") + ":Data:100",
		_("Pasar") + ":Data:100",
	]
	datas = []

	# get data
	si = frappe.db.get_list('Sales Invoice',
		fields=['*'],
		filters = {
			'company': filters.get("company"),
			'posting_date': ['>=', filters.get("date_from")],
			'posting_date': ['<=', filters.get("date_to")]
		}
	)
	sii = frappe.db.get_list('Sales Invoice Item',
		fields=['*'],
		filters = {
			'parent': ["in", [d.name for d in si]]
		}
	)
	sales_team = frappe.db.get_list('Sales Team',
		fields = ['*'],
		filters= {
			'parent': ["in", [d.name for d in si]]
		}
	)
	sales_person = frappe.db.get_list('Sales Person',
		fields = ['*'],
		filters = {
			'name': ['in', [d.sales_person for d in sales_team]]
		}
	)

	# process data
	for i in range(len(si)):
		for j in range(len(sii)):
			if si[i].name == sii[j].parent:
				datas.append([
					si[i].name,
					si[i].title,
					si[i].customer,
					'', #Customer Type
					sii[j].sales_order,
					si[i].posting_date,
					'', #week
					'', #month
					'', #year
					si[i].currency,
					si[i].payment_terms_template,
					sii[j].qty,
					(sii[j].price_list_rate * 1.1),
					(sii[j].discount_amount * 1.1),
					(sii[j].amount * 1.1),
					'', #type
					sii[j].item_code,
					sii[j].item_name,
					'', #salesman id
					'', #salesman_name
					si[i].company, 
					'', #address
					'', #beat
					si[i].pasar
				])
	datas.append(
		[len(si),'2','3']
	)

	# return data
	return columns, datas

