// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Transfer Form", {
	refresh(frm) {
		// Auto-fill transfer_ordered_by for new documents
		if (frm.is_new()) {
			frm.set_value("transfer_ordered_by", frappe.session.user);
		}
		
	},

	equipment_plate_no(frm) {
		// Fetch equipment details from Equipment Master
		if (frm.doc.equipment_plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.equipment_plate_no, 
				["equipment_category", "operators_name", "location"], (r) => {
					if (r) {
						// Set equipment type based on category
						if (r.equipment_category) {
							frappe.db.get_value("Asset Category", r.equipment_category, 
								"asset_category_name", (cat) => {
									if (cat && cat.asset_category_name) {
										frm.set_value("equipment_type", cat.asset_category_name);
									}
								}
							);
						}
						// Auto-fill current operator
						if (r.operators_name) {
							frm.set_value("current_operator", r.operators_name);
						}
						// Auto-fill from_project based on current location
						if (r.location) {
							frm.set_value("from_project", r.location);
						}
					}
				}
			);
		} else {
			// Clear fields if equipment is cleared
			frm.set_value("equipment_type", "");
			frm.set_value("current_operator", "");
			frm.set_value("operator_driver_name", "");
			frm.set_value("from_project", "");
		}
	},


	
	before_workflow_action(frm) {
		// Populate user fields BEFORE workflow action is applied
		// Return a promise to ensure values are set before workflow proceeds
		return new Promise((resolve) => {
			const action = frm.selected_workflow_action;
			
			if (!action) {
				resolve();
				return;
			}
			
			frappe.workflow.get_transitions(frm.doc).then((transitions) => {
				const transition = transitions.find(t => t.action === action);
				if (transition) {
					const next_state = transition.next_state;
					
					if (action === "Approve" && next_state === "Approved") {
						if (!frm.doc.approved_by) {
							frm.set_value("approved_by", frappe.session.user);
						}
					}
					
					// Wait a bit to ensure values are set before resolving
					setTimeout(() => resolve(), 100);
				} else {
					resolve();
				}
			}).catch(() => resolve());
		});
	}
});

