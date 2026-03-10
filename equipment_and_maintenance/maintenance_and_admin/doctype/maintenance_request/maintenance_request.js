// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Request", {
	refresh(frm) {
		// Auto-set requested_by if not set (on creation)
		if (frm.is_new() && !frm.doc.requested_by) {
			frappe.db.get_value("User", frappe.session.user, "full_name").then(r => {
				if (r && r.full_name) {
					frm.set_value("requested_by", r.full_name);
					frm.set_value("date_requested", frappe.datetime.get_today());
				}
			});
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
	},
	
	before_workflow_action(frm) {
		// Populate user fields BEFORE workflow action is applied
		// Set values directly on doc object so they're included when workflow is applied
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
					
					// Get user's full name synchronously if possible, or use session user
					frappe.db.get_value("User", frappe.session.user, "full_name").then(r => {
						const user_name = (r && r.full_name) ? r.full_name : frappe.session.user;
						
						if (action === "Approve" && next_state === "Approved") {
							if (!frm.doc.approved_by) {
								// Set directly on doc object
								frm.doc.approved_by = user_name;
								frm.doc.date_approved = frappe.datetime.get_today();
								frm.refresh_field("approved_by");
								frm.refresh_field("date_approved");
							}
						} else if (action === "Receive" && next_state === "Received") {
							if (!frm.doc.received_by) {
								// Set directly on doc object
								frm.doc.received_by = user_name;
								frm.doc.date_received = frappe.datetime.get_today();
								frm.refresh_field("received_by");
								frm.refresh_field("date_received");
							}
						}
						
						// Small delay to ensure UI updates
						setTimeout(() => resolve(), 50);
					}).catch(() => {
						// Fallback: use session user directly
						if (action === "Approve" && next_state === "Approved" && !frm.doc.approved_by) {
							frm.doc.approved_by = frappe.session.user;
							frm.doc.date_approved = frappe.datetime.get_today();
						} else if (action === "Receive" && next_state === "Received" && !frm.doc.received_by) {
							frm.doc.received_by = frappe.session.user;
							frm.doc.date_received = frappe.datetime.get_today();
						}
						resolve();
					});
				} else {
					resolve();
				}
			}).catch(() => resolve());
		});
	}
});
