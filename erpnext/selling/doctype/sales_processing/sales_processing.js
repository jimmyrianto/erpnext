// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Processing', {
    onload: function(frm) {
        frm.set_value("date_from", frappe.datetime.month_start());
        frm.set_value("date_to", frappe.datetime.month_end());
    },
    button_get_data: function(frm){
        return frappe.call({
            method: "erpnext.selling.doctype.sales_processing.sales_processing.get_data",
            args: {
                date_from: frm.doc.date_from,
                date_to: frm.doc.date_to,
                company: frm.doc.company
            },
            callback: function(r, rt) {
                if (r.message.status) {
                    
                }
                // if(r.message) {
                //     frappe.run_serially([
                //         () => {
                //             if(frm.doc.payment_type == "Receive") {
                //                 frm.set_value("paid_from", r.message.party_account);
                //                 frm.set_value("paid_from_account_currency", r.message.party_account_currency);
                //                 frm.set_value("paid_from_account_balance", r.message.account_balance);
                //             } else if (frm.doc.payment_type == "Pay"){
                //                 frm.set_value("paid_to", r.message.party_account);
                //                 frm.set_value("paid_to_account_currency", r.message.party_account_currency);
                //                 frm.set_value("paid_to_account_balance", r.message.account_balance);
                //             }
                //         },
                //         () => frm.set_value("party_balance", r.message.party_balance),
                //         () => frm.set_value("party_name", r.message.party_name),
                //         () => frm.clear_table("references"),
                //         () => frm.events.hide_unhide_fields(frm),
                //         () => frm.events.set_dynamic_labels(frm),
                //         () => {
                //             frm.set_party_account_based_on_party = false;
                //             if (r.message.bank_account) {
                //                 frm.set_value("party_bank_account", r.message.bank_account);
                //             }
                //         }
                //     ]);
                // }
            }
        });
    }
});
