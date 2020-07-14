// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('EFaktur Transaction', {
	refresh: function(frm) {
		frm.fields_dict['item'].grid.get_field('efaktur_id').get_query = function(doc, cdt, cdn) {
			return {    
				filters: {
					'is_used': 0
				}
			}
		}

		if (frm.doc.docstatus == 1) {
			frm.add_custom_button("Export Efaktur", function() {
				let get_template_url = 'erpnext.accounts.doctype.efaktur_transaction.efaktur_transaction.export_efaktur';
				open_url_post(frappe.request.url, { cmd: get_template_url, efaktur_transaction_id: frm.doc.name });
			}, "Efaktur Action");
		}
		if (frm.doc.docstatus == 0) {
			// button get item detail (sales invoice outstanding)
			frm.add_custom_button("Get Item", function() {
				frm.clear_table("item");
				refresh_field("item");
	
				return frappe.call({
					method: "button_get_item",
					doc: frm.doc,
					callback: function(r, rt) {
						r.message.forEach(function(element) {
							var c = frm.add_child("item");
							c.sales_invoice = element.sales_invoice;
							c.efaktur_date = element.efaktur_date;
						});
						refresh_field("item");
					}
				});
			}, "Efaktur Action")
	
			// button auto assign sales invoice to efaktur
			frm.add_custom_button("Auto Assign", function() {
				frappe.call({
					method: "button_auto_assign",
					doc: frm.doc,
					callback: function(r, rt) {
						frm.clear_table("item");
						r.message.forEach(function(element) {
							var c = frm.add_child("item");
							c.sales_invoice = element.sales_invoice;
							c.efaktur_id = element.efaktur_id;
							c.efaktur_date = element.efaktur_date;
						});
						refresh_field("item");
					}
				});
			}, "Efaktur Action")		
		}
	},
	onload: function(frm) {
		// frm.get_field("item").grid.cannot_add_rows = false;
		// frm.get_field("item").grid.only_sortable();
	}
});
