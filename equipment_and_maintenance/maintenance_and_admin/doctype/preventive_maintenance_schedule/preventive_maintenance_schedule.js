// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance Schedule", {
	refresh(frm) {
		// Add button to create maintenance log
		if (frm.doc.status === "Active" || frm.doc.status === "Overdue") {
			frm.add_custom_button(__("Create Maintenance Log"), function() {
				frappe.model.with_doctype("Preventive Maintenance Log", function() {
					let log = frappe.model.get_new_doc("Preventive Maintenance Log");
					log.schedule = frm.doc.name;
					log.equipment = frm.doc.equipment;
					log.equipment_code = frm.doc.equipment_code;
					log.plate_no = frm.doc.plate_no;
					log.service_date = frappe.datetime.get_today();
					log.service_hours = frm.doc.current_hours;
					log.service_kilometers = frm.doc.current_kilometers;
					
					frappe.set_route("Form", "Preventive Maintenance Log", log.name);
				});
			});
		}
		
		// Add button to check reminders
		frm.add_custom_button(__("Check Reminders"), function() {
			frappe.call({
				method: "equipment_and_maintenance.maintenance_and_admin.doctype.preventive_maintenance_schedule.preventive_maintenance_schedule.check_and_send_reminders",
				callback: function(r) {
					if (r.message) {
						frappe.msgprint(__("Reminders sent: {0}", [r.message]));
					}
				}
			});
		});
	},

	equipment(frm) {
		// Fetch current hours and kilometers from equipment
		if (frm.doc.equipment) {
			frappe.db.get_value("Equipment Master", frm.doc.equipment, 
				["equipment_code", "plate_number"], (r) => {
					if (r) {
						frm.set_value("equipment_code", r.equipment_code);
						frm.set_value("plate_no", r.plate_number);
					}
				}
			);
		}
	},

	template(frm) {
		// When template is selected, populate items will happen in Python before_save
		// For existing documents, populate immediately using server-side method
		if (frm.doc.template && frm.doc.name && (!frm.doc.schedule_items || frm.doc.schedule_items.length === 0)) {
			populate_template_items(frm);
		}
	},

	current_hours(frm) {
		frm.events.calculate_next_service(frm);
	},

	current_kilometers(frm) {
		frm.events.calculate_next_service(frm);
	},

	calculate_next_service(frm) {
		// Calculate next service due
		if (!frm.doc.current_hours && !frm.doc.current_kilometers) {
			return;
		}
		
		let next_hours = null;
		let next_km = null;
		
		const hour_intervals = [250, 500, 1000, 2000, 6000];
		const km_intervals = [2500, 5000, 10000, 30000, 60000];
		
		// Calculate next hours - find the smallest interval that hasn't been reached
		if (frm.doc.current_hours) {
			let last_hours = flt(frm.doc.last_service_hours) || 0;
			let current = flt(frm.doc.current_hours);
			
			for (let interval of hour_intervals) {
				let next_interval_value = last_hours + interval;
				if (current < next_interval_value) {
					// This is a future interval, check if it's the smallest
					if (!next_hours || next_interval_value < next_hours) {
						next_hours = next_interval_value;
					}
				}
			}
		}
		
		// Calculate next kilometers - find the smallest interval that hasn't been reached
		if (frm.doc.current_kilometers) {
			let last_km = flt(frm.doc.last_service_kilometers) || 0;
			let current = flt(frm.doc.current_kilometers);
			
			for (let interval of km_intervals) {
				let next_interval_value = last_km + interval;
				if (current < next_interval_value) {
					// This is a future interval, check if it's the smallest
					if (!next_km || next_interval_value < next_km) {
						next_km = next_interval_value;
					}
				}
			}
		}
		
		if (next_hours) {
			frm.set_value("next_service_due_hours", next_hours);
		}
		if (next_km) {
			frm.set_value("next_service_due_kilometers", next_km);
		}
	}
});

function determine_target_interval(frm) {
	// Determine which interval milestone we're targeting based on current readings
	// This finds the next upcoming interval
	
	const hour_intervals = [250, 500, 1000, 2000, 6000];
	const km_intervals = [2500, 5000, 10000, 30000, 60000];
	
	let target_hour_interval = null;
	let target_km_interval = null;
	
	// Determine target hour interval
	if (frm.doc.current_hours) {
		let last_hours = flt(frm.doc.last_service_hours) || 0;
		let current = flt(frm.doc.current_hours);
		
		// Find the smallest interval that hasn't been reached yet
		for (let interval of hour_intervals) {
			let next_interval_value = last_hours + interval;
			if (current < next_interval_value) {
				if (!target_hour_interval || next_interval_value < target_hour_interval.value) {
					target_hour_interval = {
						type: "Hours",
						value: interval,
						name: `${interval} Hours`
					};
				}
			}
		}
	}
	
	// Determine target km interval
	if (frm.doc.current_kilometers) {
		let last_km = flt(frm.doc.last_service_kilometers) || 0;
		let current = flt(frm.doc.current_kilometers);
		
		// Find the smallest interval that hasn't been reached yet
		for (let interval of km_intervals) {
			let next_interval_value = last_km + interval;
			if (current < next_interval_value) {
				if (!target_km_interval || next_interval_value < target_km_interval.value) {
					target_km_interval = {
						type: "Kilometers",
						value: interval,
						name: `${interval} KM`
					};
				}
			}
		}
	}
	
	// Return the interval that comes first (or the one that exists)
	if (target_hour_interval && target_km_interval) {
		// Compare which one comes first
		let hour_next = (frm.doc.last_service_hours || 0) + target_hour_interval.value;
		let km_next = (frm.doc.last_service_kilometers || 0) + target_km_interval.value;
		
		// Use the one that comes first, or prefer hours if equal
		if (hour_next <= km_next) {
			return target_hour_interval;
		} else {
			return target_km_interval;
		}
	}
	
	return target_hour_interval || target_km_interval;
}

function populate_template_items(frm) {
	// Use server-side method to populate and save items
	// This ensures items are saved to the database
	frappe.call({
		method: "equipment_and_maintenance.maintenance_and_admin.doctype.preventive_maintenance_schedule.preventive_maintenance_schedule.populate_from_template",
		args: {
			schedule: frm.doc.name,
			template: frm.doc.template
		},
		callback: function(r) {
			if (r.message) {
				frm.reload_doc();
			}
		}
	});
}

