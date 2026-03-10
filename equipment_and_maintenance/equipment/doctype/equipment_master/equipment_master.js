// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Master", {
	refresh(frm) {
		frm.set_query("equipment_sub_category", function() {
			return {
				filters: {
					asset_category: frm.doc.equipment_category || undefined
				}
			};
		});
	},
	
	after_save(frm) {
		console.log("afater save triggerd");
		console.log("rental agreement", frm.doc.rental_agreement);
		console.log("make", frm.doc.make);
		console.log("name", frm.doc.name);

		if (frm.doc.rental_agreement && frm.doc.make && frm.doc.name) {
			console.log("linking to rental agreement");
			frappe.call({
				method: "equipment_and_maintenance.equipment.doctype.rental_agreement.rental_agreement.link_equipment_to_agreement",
				args: {
					agreement: frm.doc.rental_agreement,
					equipment_type: frm.doc.make,
					equipment_name: frm.doc.name
				},
				callback: function(r) {
					if (r.message?.success) {
						frappe.show_alert({ message: __("Linked to Rental Agreement"), indicator: "green" });
					}
				}
			});
		}
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
