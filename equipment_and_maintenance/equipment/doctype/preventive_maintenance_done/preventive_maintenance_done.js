// Copyright (c) 2026, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance Done", {
	refresh(frm) {
		// Set item_code filter for child table
		frm.set_query("item_code", "parts_used", function() {
			return {
				filters: {
					item_group: "Spare Parts"
				}
			};
		});
		// Set default date to today
		if (!frm.doc.actual_date) {
			frm.set_value("actual_date", frappe.datetime.get_today());
		}
		
		// Set default performed_by to current user
		if (!frm.doc.performed_by) {
			frm.set_value("performed_by", frappe.session.user);
		}
		
		// Submit is handled by default Frappe form
		
		// Add button to load from plan
		if (frm.doc.equipment) {
			frm.add_custom_button(__("Load from Plan"), function() {
				load_from_plan(frm);
			});
		}
	},
	
	equipment(frm) {
		if (frm.doc.equipment) {

			// Add button to load from plan
			frm.add_custom_button(__("Load from Plan"), function() {
				load_from_plan(frm);
			});
			// Fetch equipment details
			frappe.db.get_doc("Equipment Master", frm.doc.equipment)
				.then(equipment => {
					frm.set_value({
						plate_number: equipment.plate_number || "",
						equipment_code: equipment.equipment_code || "",
						make: equipment.make || "",
						model: equipment.model || ""
					});
					
					// Load current reading
					load_current_reading(frm);
				});
		}
	},
	
	plan(frm) {
		if (frm.doc.plan && frm.doc.equipment) {
			load_plan_details(frm);
		}
	},
	
	
	actual_hours_km(frm) {
		// Could add validation here
		if (frm.doc.actual_hours_km && frm.doc.planned_hours_km) {
			// Could compare and suggest if PM was done as per schedule
		}
	}
});

function load_current_reading(frm) {
	if (!frm.doc.equipment) return;
	
	frappe.call({
		method: "equipment_and_maintenance.equipment.doctype.preventive_maintenance_plan.preventive_maintenance_plan.get_equipment_current_reading",
		args: {
			equipment: frm.doc.equipment
		},
		callback: function(r) {
			if (r.message) {
				// Set actual_hours_km to current reading as default
				if (!frm.doc.actual_hours_km) {
					frm.set_value("actual_hours_km", r.message.current_hours_km || 0);
				}
			}
		}
	});
}

function load_from_plan(frm) {
	if (!frm.doc.equipment) {
		frappe.msgprint(__("Please select Equipment first"));
		return;
	}
	
	// Show dialog to select plan
	let d = new frappe.ui.Dialog({
		title: __("Select Plan"),
		fields: [
			{
				label: __("Preventive Maintenance Plan"),
				fieldname: "plan",
				fieldtype: "Link",
				options: "Preventive Maintenance Plan",
				get_query: function() {
					return {
						filters: {
							equipment: frm.doc.equipment,
							docstatus: 1
						}
					};
				}
			}
		],
		primary_action_label: __("Load"),
		primary_action(values) {
			if (values.plan) {
				frm.set_value("plan", values.plan);
				load_plan_details(frm);
				d.hide();
			}
		}
	});
	
	d.show();
}

function load_plan_details(frm) {
	if (!frm.doc.plan || !frm.doc.equipment) return;
	
	frappe.db.get_doc("Preventive Maintenance Plan", frm.doc.plan)
		.then(plan => {
			// Plan is now for one equipment, so load directly from plan
			if (plan.equipment === frm.doc.equipment) {
				frm.set_value({
					planned_week: plan.planned_week || "",
					planned_service_type: plan.planned_service_type || "",
					planned_hours_km: plan.planned_hours_km || 0
				});
				
				// Set service type from planned if not set
				if (!frm.doc.service_type && plan.planned_service_type) {
					frm.set_value("service_type", plan.planned_service_type);
				}
			} else {
				frappe.msgprint(__("Selected plan is for a different equipment"));
			}
		});
}
