// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Invoice Detail"] = {
	"filters": [
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("company")
        },{
            "fieldname":"date_from",
            "label": __("Date From"),
            "fieldtype": "Date",
            "options": "",
            "default": frappe.datetime.month_start()
        },{
            "fieldname":"date_to",
            "label": __("Date To"),
            "fieldtype": "Date",
            "options": "",
            "default": frappe.datetime.month_end()
        },
	]
};

