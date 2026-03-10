// Copyright (c) 2026, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance Plan", {
	refresh(frm) {
		// Set default year to current year
		if (!frm.doc.planning_year) {
			frm.set_value("planning_year", new Date().getFullYear());
		}
		
		// Set default month to next month
		if (!frm.doc.planning_month) {
			const nextMonth = new Date();
			nextMonth.setMonth(nextMonth.getMonth() + 1);
			const monthNames = ["January", "February", "March", "April", "May", "June",
				"July", "August", "September", "October", "November", "December"];
			frm.set_value("planning_month", monthNames[nextMonth.getMonth()]);
		}
		
		// Add button to create Preventive Maintenance Done in Create group (only after submission)
		if (frm.doc.equipment && frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Preventive Maintenance Done"), function() {
				create_pm_done(frm);
			}, __("Create"));
			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}
		
		// Load history when form is opened (only if not submitted)
		if (frm.doc.equipment && frm.doc.docstatus === 0) {
			load_history_into_table(frm);
		}
		
		// Make history read-only and non-editable after submission
		if (frm.doc.docstatus === 1) {
			frm.set_df_property("pm_history", "read_only", 1);
			// Disable adding new rows and make grid read-only
			if (frm.fields_dict.pm_history && frm.fields_dict.pm_history.grid) {
				frm.fields_dict.pm_history.grid.wrapper.find(".grid-add-row").hide();
				frm.fields_dict.pm_history.grid.toggle_enable(false);
			}
		} else {
			frm.set_df_property("pm_history", "read_only", 0);
			if (frm.fields_dict.pm_history && frm.fields_dict.pm_history.grid) {
				frm.fields_dict.pm_history.grid.wrapper.find(".grid-add-row").show();
				frm.fields_dict.pm_history.grid.toggle_enable(true);
			}
		}
	},
	
	equipment(frm) {
		if (frm.doc.equipment) {
			// Fetch equipment details
			frappe.db.get_doc("Equipment Master", frm.doc.equipment)
				.then(equipment => {
					frm.set_value({
						plate_number: equipment.plate_number || "",
						equipment_code: equipment.equipment_code || "",
						make: equipment.make || "",
						model: equipment.model || "",
						equipment_category: equipment.equipment_category || "",
						equipment_sub_category: equipment.equipment_sub_category || "",
						department: equipment.location ? null : frm.doc.department, // Keep existing if set
						project: equipment.location || frm.doc.project || null
					});
					
					// Load current reading and PM history
					load_equipment_pm_data(frm);
					
					// Load history into table (only if not submitted)
					if (frm.doc.docstatus === 0) {
						load_history_into_table(frm);
					}
				});
		}
	},
	
	planning_month(frm) {
		// Could add validation here
	},
	
	planning_year(frm) {
		// Could add validation here
	},
	
	current_hours_km(frm) {
		// Could add validation here
	}
});

function load_equipment_pm_data(frm) {
	if (!frm.doc.equipment) return;
	
	// Get current reading
	frappe.call({
		method: "equipment_and_maintenance.equipment.doctype.preventive_maintenance_plan.preventive_maintenance_plan.get_equipment_current_reading",
		args: {
			equipment: frm.doc.equipment
		},
		callback: function(r) {
			if (r.message) {
				frm.set_value({
					current_hours_km: r.message.current_hours_km || 0,
					last_pm_date: r.message.last_pm_date || null
				});
			}
		}
	});
	
	// Get PM history
	frappe.call({
		method: "equipment_and_maintenance.equipment.doctype.preventive_maintenance_plan.preventive_maintenance_plan.get_pm_history",
		args: {
			equipment: frm.doc.equipment
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				// Set last PM details from most recent history
				let last_pm = r.message[0];
				frm.set_value({
					last_pm_hours_km: last_pm.hours_km_after || null,
					last_pm_service_type: last_pm.service_type || null,
					last_pm_date: last_pm.pm_date || frm.doc.last_pm_date || null
				});
			}
		}
	});
}

function create_pm_done(frm) {
	if (!frm.doc.equipment) {
		frappe.msgprint(__("Please select Equipment first"));
		return;
	}
	
	frappe.model.with_doctype("Preventive Maintenance Done", function() {
		let pm_done = frappe.model.get_new_doc("Preventive Maintenance Done");
		pm_done.equipment = frm.doc.equipment;
		pm_done.plate_number = frm.doc.plate_number;
		pm_done.equipment_code = frm.doc.equipment_code;
		pm_done.make = frm.doc.make;
		pm_done.model = frm.doc.model;
		pm_done.plan = frm.doc.name;
		pm_done.planned_week = frm.doc.planned_week;
		pm_done.planned_service_type = frm.doc.planned_service_type;
		pm_done.planned_hours_km = frm.doc.planned_hours_km;
		pm_done.actual_date = frappe.datetime.get_today();
		pm_done.actual_hours_km = frm.doc.current_hours_km || 0;
		pm_done.service_type = frm.doc.planned_service_type || "";
		
		frappe.set_route("Form", "Preventive Maintenance Done", pm_done.name);
	});
}

function load_history_into_table(frm) {
	if (!frm.doc.equipment || frm.doc.docstatus === 1) return;
	
	frappe.call({
		method: "equipment_and_maintenance.equipment.doctype.preventive_maintenance_plan.preventive_maintenance_plan.get_pm_history",
		args: {
			equipment: frm.doc.equipment
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				// Clear existing history only if not submitted
				if (frm.doc.docstatus === 0) {
					frm.clear_table("pm_history");
					
					// Add history records
					r.message.forEach(function(pm_done) {
						let row = frm.add_child("pm_history");
						row.pm_done = pm_done.name;
						row.actual_date = pm_done.pm_date;
						row.service_type = pm_done.service_type;
						row.actual_hours_km = pm_done.hours_km_after;
						row.pm_performed_as_per_schedule = pm_done.pm_performed_as_per_schedule;
						row.performed_by = pm_done.performed_by;
						row.remark = pm_done.remark || pm_done.completion_notes || "";
					});
					
					frm.refresh_field("pm_history");
				}
			}
		}
	});
}
