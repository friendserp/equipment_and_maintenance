// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cannibalization Form", {
	cannibalized_from_plate_no(frm) {
		// Fetch information from Equipment Master
		if (frm.doc.cannibalized_from_plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.cannibalized_from_plate_no, 
				["model", "equipment_category", "location"], (r) => {
					if (r) {
						frm.set_value("cannibalized_from_model", r.model || "");
						frm.set_value("cannibalized_from_type", r.equipment_category || "");
						frm.set_value("cannibalized_from_project", r.location || "");
					}
				}
			);
		} else {
			frm.set_value("cannibalized_from_model", "");
			frm.set_value("cannibalized_from_type", "");
			frm.set_value("cannibalized_from_project", "");
		}
	},
	
	fitted_to_plate_no(frm) {
		// Fetch information from Equipment Master
		if (frm.doc.fitted_to_plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.fitted_to_plate_no, 
				["model", "equipment_category", "location"], (r) => {
					if (r) {
						frm.set_value("fitted_to_model", r.model || "");
						frm.set_value("fitted_to_type", r.equipment_category || "");
						frm.set_value("fitted_to_project", r.location || "");
					}
				}
			);
		} else {
			frm.set_value("fitted_to_model", "");
			frm.set_value("fitted_to_type", "");
			frm.set_value("fitted_to_project", "");
		}
	},
	
	purchase_requisition_no(frm) {
		// Auto-fill date from Material Request
		if (frm.doc.purchase_requisition_no) {
			frappe.db.get_value("Material Request", frm.doc.purchase_requisition_no, 
				["transaction_date"], (r) => {
					if (r && r.transaction_date) {
						frm.set_value("purchase_requisition_date", r.transaction_date);
					}
				}
			);
		} else {
			frm.set_value("purchase_requisition_date", "");
		}
	},
	
	refresh(frm) {
		// Set query filter for Material Request - only show those with purpose = "Purchase"
		frm.set_query("purchase_requisition_no", function() {
			return {
				filters: {
					"material_request_type": "Purchase"
				}
			};
		});
	}
});

