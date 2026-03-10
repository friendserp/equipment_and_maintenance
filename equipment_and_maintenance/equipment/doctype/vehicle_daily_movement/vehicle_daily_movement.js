// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Daily Movement", {
	refresh(frm) {
		// Any refresh logic if needed
	},

	plate_number(frm) {
		// Fetch vehicle type and driver name from Equipment Master
		if (frm.doc.plate_number) {
			frappe.db.get_value("Equipment Master", frm.doc.plate_number, 
				["equipment_category", "equipment_sub_category", "operators_name"], (r) => {
					if (r) {
						// Set vehicle type based on category/sub-category
						if (r.equipment_category) {
							frappe.db.get_value("Asset Category", r.equipment_category, 
								"asset_category_name", (cat) => {
									if (cat && cat.asset_category_name) {
										frm.set_value("vehicle_type", cat.asset_category_name);
									}
								}
							);
						}
						// Auto-fill driver name from operators_name
						if (r.operators_name) {
							frm.set_value("driver_name", r.operators_name);
						}
					}
				}
			);
		}
	},

	starting_km(frm) {
		calculate_km_difference(frm);
	},

	ending_km(frm) {
		calculate_km_difference(frm);
	}
});

function calculate_km_difference(frm) {
	if (frm.doc.starting_km && frm.doc.ending_km) {
		let difference = flt(frm.doc.ending_km) - flt(frm.doc.starting_km);
		frm.set_value("km_difference", difference);
	} else {
		frm.set_value("km_difference", 0);
	}
}
