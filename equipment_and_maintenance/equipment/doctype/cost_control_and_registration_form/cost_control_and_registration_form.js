// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Control and Registration Form", {
	refresh(frm) {
		// Set default date for new items
		if (frm.is_new()) {
			frm.set_value("prepared_by", frappe.session.user);
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
	},

	items_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Set default date to today if not set
		if (!row.date) {
			frappe.model.set_value(cdt, cdn, "date", frappe.datetime.get_today());
		}
	}
});

// Calculate totals for each row (if needed)
frappe.ui.form.on("Cost Control Registration Item", {
	fuel_liter(frm, cdt, cdn) {
		// Auto-calculate fuel price if unit price is known
		// This can be enhanced based on business logic
	},
	
	fuel_birr(frm, cdt, cdn) {
		// Recalculate if needed
	},
	
	engine_oil_liter(frm, cdt, cdn) {
		// Auto-calculate if unit price is known
	},
	
	engine_oil_birr(frm, cdt, cdn) {
		// Recalculate if needed
	}
});

