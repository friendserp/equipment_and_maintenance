// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Request", {
	refresh(frm) {
		// Link Battery Request when Material Request is created from Battery Request
		if (frm.is_new() && sessionStorage.getItem('battery_request_for_mr')) {
			let battery_request_name = sessionStorage.getItem('battery_request_for_mr');
			
			// Store in custom field if it exists, otherwise store in form variable
			if (frm.fields_dict.custom_battery_request) {
				frm.set_value("custom_battery_request", battery_request_name);
			}
			frm.battery_request_name = battery_request_name;
			
			// Clear session storage
			sessionStorage.removeItem('battery_request_for_mr');
		}
	},
	
	before_save(frm) {
		// Store Battery Request name before save so hook can access it
		if (frm.battery_request_name && !frm.doc.custom_battery_request) {
			// Try to set custom field if it exists
			if (frm.fields_dict.custom_battery_request) {
				frm.set_value("custom_battery_request", frm.battery_request_name);
			}
		}
	}
});
