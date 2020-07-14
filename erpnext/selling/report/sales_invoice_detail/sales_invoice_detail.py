# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import msgprint, _
from frappe.utils import get_first_day, round_based_on_smallest_currency_fraction
from datetime import datetime
from math import ceil

import frappe

def execute(filters=None):
	# msgprint(_(filters.get("company")))
	columns = [
		_("Sales Invoice ID") + ":Data:200", 
		_("Customer ID") + ":Data:300",
		_("Customer Name") + ":Data:300",
		_("Customer Type") + ":Data:200",
		_("Sales Order ID") + ":Data:200",
		_("Invoice Date") + ":Data:100",
		_("Week") + ":Data:50",
		_("Month") + ":Data:50",
		_("Year") + ":Data:50",
		_("Currency") + ":Data:50",
		_("TOP") + ":Data:50",
		_("Qty") + ":Data:50",
		_("Price List") + ":Data:100",
		_("Discount") + ":Data:100",
		_("Amount") + ":Data:100",
		_("Type") + ":Data:100",
		_("Item ID") + ":Data:100",
		_("Item Name") + ":Data:300",
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
			'company': str(filters.get("company")),
			'posting_date': ['between', [str(filters.get("date_from")), str(filters.get("date_to"))]]
#			'posting_date': ['<', str(filters.get("date_to"))]
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
	customer = frappe.db.get_list('Customer',
		fields = ['*'],
		filters = {
			'name': ['in', [d.customer for d in si]]
		}
	)
	dynamic_link = frappe.db.get_list('Dynamic Link',
		fields = ['*'],
		filters = {
			'link_doctype': 'Customer',
			'parenttype': 'Address',
			'link_name': ['in', [d.customer for d in si]]
		}
	)
	address = frappe.db.get_list('Address',
		fields = ['*'],
		filters = {
			'name': ['in', [d.parent for d in dynamic_link]]
		}
	)

	# process data
	for i in range(len(si)):
		discount = si[i].discount_amount / si[i].total_qty
		for j in range(len(sii)):
			if si[i].name == sii[j].parent:
				price_list = round_based_on_smallest_currency_fraction((sii[j].price_list_rate * 1.1), 'IDR', 0)
				diskon = round_based_on_smallest_currency_fraction(((discount + sii[j].discount_amount) * 1.1), 'IDR', 0)
				amount = round_based_on_smallest_currency_fraction(((price_list - diskon)*sii[j].qty), 'IDR', 0)
				data = [
					si[i].name,
					si[i].title,
					si[i].customer,
					find_customer_channel_by_name(customer, si[i].customer), #Customer Type channel customer
					sii[j].sales_order,
					si[i].posting_date,
					week_of_month(si[i].posting_date), #week
					datetime.strptime(str(si[i].posting_date), "%Y-%m-%d").month, #month
					datetime.strptime(str(si[i].posting_date), "%Y-%m-%d").year, #year
					si[i].currency,
					si[i].payment_terms_template,
					sii[j].qty,
					price_list,
					diskon,
					amount,
					# round_based_on_smallest_currency_fraction((sii[j].price_list_rate * 1.1), 'IDR', 0),
					# round_based_on_smallest_currency_fraction((sii[j].discount_amount * 1.1), 'IDR', 0),
					# round_based_on_smallest_currency_fraction((sii[j].amount * 1.1), 'IDR', 0),
					'', #type
					sii[j].item_code,
					sii[j].item_name,
					find_sales_team_by_parent(sales_team, si[i].name),
					'', #salesman_name
					si[i].company, 
					find_address_country_by_name(
						address,
						find_dynamiclink_parent_by_linkname(dynamic_link, si[i].customer)
					),
					find_address_city_by_name(
						address,
						find_dynamiclink_parent_by_linkname(dynamic_link, si[i].customer)
					),
					si[i].pasar
				]

				#get type
				if int(sii[j].qty) > 0:
					data[15] = 'Sales'
				else:
					data[15] = 'Return'

				data[19] = find_sales_person_by_name(
								sales_person,
								data[18]
				)

				datas.append(data)

#	datas.append([len(si)])

	# return data
	return columns, datas

def find_sales_team_by_parent(arr, parent):
	for x in arr:
		if x.parent == parent:
			return x.sales_person

def find_sales_person_by_name(arr, name):
	for x in arr:
		if x.name == name:
			return x.sales_person_name

def find_customer_channel_by_name(arr, name):
	for x in arr:
		if x.name == name:
			return x.channel

def find_dynamiclink_parent_by_linkname(arr, linkname):
	for x in arr:
		if x.link_name == linkname:
			return x.parent

def find_address_country_by_name(arr, name):
	for x in arr:
		if x.name == name:
			return x.address_line1

def find_address_city_by_name(arr, name):
	for x in arr:
		if x.name == name:
			return x.city

def week_of_month(dt):
	first_day = dt.replace(day=1)
	dom = dt.day
	adjusted_dom = dom + first_day.weekday()
	return int(ceil(adjusted_dom/7.0))


