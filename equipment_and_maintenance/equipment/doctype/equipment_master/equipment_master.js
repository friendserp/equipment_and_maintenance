// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Master", {
	refresh(frm) {
		// Set up query filter for sub category based on main category
		frm.set_query("equipment_sub_category", function() {
			return {
				filters: {
					asset_category: frm.doc.equipment_category || undefined
				}
			};
		});
	},
	
	equipment_category(frm) {
		// Update query filter for sub category based on selected main category
		frm.set_query("equipment_sub_category", function() {
			let filters = {};
			if (frm.doc.equipment_category) {
				filters.asset_category = frm.doc.equipment_category;
			}
			return {
				filters: filters
			};
		});
		
		// Clear sub category if it doesn't belong to the selected main category
		if (frm.doc.equipment_category && frm.doc.equipment_sub_category) {
			frappe.db.get_value("Asset Sub Category", frm.doc.equipment_sub_category, "asset_category", (r) => {
				if (r && r.asset_category !== frm.doc.equipment_category) {
					frm.set_value("equipment_sub_category", "");
				}
			});
		}
	},
	
	equipment_sub_category(frm) {
		// Auto-fill main category when sub category is selected
		if (frm.doc.equipment_sub_category) {
			frappe.db.get_value("Asset Sub Category", frm.doc.equipment_sub_category, "asset_category", (r) => {
				if (r && r.asset_category) {
					frm.set_value("equipment_category", r.asset_category);
				}
			});
		}
	}
});
