// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental Agreement Items", {
	refresh(frm, cdt, cdn) {
		// Set default for is_existing_equipment
		let row = locals[cdt][cdn];
		if (row.is_existing_equipment === undefined) {
			frappe.model.set_value(cdt, cdn, "is_existing_equipment", 1);
		}
	},

	is_existing_equipment(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Clear fields when switching between existing and new
		if (row.is_existing_equipment) {
			frappe.model.set_value(cdt, cdn, "equipment_type", "");
		} else {
			frappe.model.set_value(cdt, cdn, "plate_number", "");
		}
	},

	plate_number(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.plate_number) {
			// Fetch equipment type from Equipment Master
			frappe.db.get_value("Equipment Master", row.plate_number, 
				["equipment_category"], (r) => {
					if (r && r.equipment_category) {
						frappe.db.get_value("Asset Category", r.equipment_category, 
							"asset_category_name", (cat) => {
								if (cat && cat.asset_category_name) {
									frappe.model.set_value(cdt, cdn, "equipment_type", cat.asset_category_name);
								}
							}
						);
					}
				}
			);
		} else {
			frappe.model.set_value(cdt, cdn, "equipment_type", "");
		}
	}
});
