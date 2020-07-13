# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesProcessing(Document):
	pass

@frappe.whitelist()
def get_data(date_from=None, date_to=None, company=None):
	return_value = {}
	return_value['status'] = True
	return_value['message'] = ''
	return_value['data'] = []

	

	return return_value
	