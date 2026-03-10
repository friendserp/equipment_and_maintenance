// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Battery Recording Database", {
	refresh(frm) {
		// Add buttons to link to related forms
		if (!frm.is_new()) {
			if (frm.doc.last_battery_request) {
				frm.add_custom_button(
					__("Battery Request"),
					function() {
						frappe.set_route("Form", "Battery Request and Analysis Form", frm.doc.last_battery_request);
					},
					__("View")
				);
			}
			
			if (frm.doc.last_battery_return) {
				frm.add_custom_button(
					__("Battery Return"),
					function() {
						frappe.set_route("Form", "Battery Issue and Return Report Form", frm.doc.last_battery_return);
					},
					__("View")
				);
			}
		}
		
		// Add filter for item_code
		frm.set_query("item_code", function() {
			return {
				filters: {
					"item_group": "Spare Parts",
					"custom_subcategory": "General Purpose"
				},
				query: "equipment_and_maintenance.equipment.doctype.battery_recording_database.battery_recording_database.filter_battery_items"
			};
		});
		
		// Add filter for serial_no to only show serial numbers for battery items
		frm.set_query("battery_serial_no", function() {
			return {
				filters: {
					"item_group": "Spare Parts"
				}
			};
		});
	},
	
});
