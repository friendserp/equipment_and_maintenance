// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance Log", {
	refresh(frm) {
		// Load tasks from schedule when schedule is selected
		if (frm.doc.schedule) {
			frm.add_custom_button(__("Load Tasks from Schedule"), function() {
				load_tasks_from_schedule(frm);
			});
		}
	},

	schedule(frm) {
		// Auto-fill equipment and details from schedule
		if (frm.doc.schedule) {
			frappe.db.get_doc("Preventive Maintenance Schedule", frm.doc.schedule)
				.then(doc => {
					frm.set_value("equipment", doc.equipment);
					frm.set_value("equipment_code", doc.equipment_code);
					frm.set_value("plate_no", doc.plate_no);
					frm.set_value("service_hours", doc.current_hours);
					frm.set_value("service_kilometers", doc.current_kilometers);
					
					// Load tasks
					load_tasks_from_schedule(frm);
				});
		}
	},

	service_hours(frm) {
		calculate_next_service(frm);
	},

	service_kilometers(frm) {
		calculate_next_service(frm);
	}
});

function load_tasks_from_schedule(frm) {
	if (!frm.doc.schedule) {
		frappe.msgprint(__("Please select a Maintenance Schedule first"));
		return;
	}
	
	// Fetch schedule document
	frappe.db.get_doc("Preventive Maintenance Schedule", frm.doc.schedule)
		.then(schedule_doc => {
			// Get current readings
			let current_hours = flt(frm.doc.service_hours) || flt(schedule_doc.current_hours);
			let current_km = flt(frm.doc.service_kilometers) || flt(schedule_doc.current_kilometers);
			let last_hours = flt(schedule_doc.last_service_hours) || 0;
			let last_km = flt(schedule_doc.last_service_kilometers) || 0;
			
			// Determine which interval this service is for
			let target_interval = determine_target_interval_for_log(current_hours, current_km, last_hours, last_km);
			
			if (!target_interval) {
				frappe.msgprint({
					title: __("No Interval Found"),
					message: __("Could not determine the service interval. Please check current hours/kilometers and last service readings."),
					indicator: "orange"
				});
				return;
			}
			
			// Set interval name
			frm.set_value("interval_name", target_interval.name);
			
			// Fetch schedule items using server-side method
			frappe.call({
				method: "equipment_and_maintenance.maintenance_and_admin.doctype.preventive_maintenance_log.preventive_maintenance_log.get_schedule_items_for_interval",
				args: {
					schedule: frm.doc.schedule,
					interval_name: target_interval.name
				},
				callback: function(r) {
					if (r.message) {
						let items = r.message;
						
						if (!items || items.length === 0) {
							frappe.msgprint({
								title: __("No Tasks Found"),
								message: __("No incomplete tasks found for interval {0}. All tasks may already be completed.", [target_interval.name]),
								indicator: "blue"
							});
							return;
						}
						
						// Clear existing tasks
						frm.clear_table("completed_tasks");
						
						// Add tasks
						items.forEach(item => {
							let row = frm.add_child("completed_tasks");
							row.task = item.task;
							row.task_name = item.task_name;
							row.task_category = item.task_category;
							row.is_completed = 0;
						});
						
						frm.refresh_field("completed_tasks");
						
						frappe.show_progress(__("Loading Tasks"), items.length, items.length);
						frappe.msgprint({
							title: __("Tasks Loaded"),
							message: __("Loaded {0} task(s) for interval {1}", [items.length, target_interval.name]),
							indicator: "green"
						});
					}
				}
			});
		})
		.catch(err => {
			frappe.msgprint({
				title: __("Error"),
				message: __("Error loading tasks: {0}", [err.message || err]),
				indicator: "red"
			});
		});
}

function determine_target_interval_for_log(current_hours, current_km, last_hours, last_km) {
	// Determine which interval milestone we're targeting based on current readings
	// This finds the next upcoming interval (same logic as schedule)
	
	const hour_intervals = [250, 500, 1000, 2000, 6000];
	const km_intervals = [2500, 5000, 10000, 30000, 60000];
	
	let target_hour_interval = null;
	let target_km_interval = null;
	
	// Determine target hour interval
	if (current_hours) {
		// Find the smallest interval that hasn't been reached yet
		for (let interval of hour_intervals) {
			let next_interval_value = last_hours + interval;
			if (current_hours < next_interval_value) {
				if (!target_hour_interval || next_interval_value < (last_hours + target_hour_interval.value)) {
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
	if (current_km) {
		// Find the smallest interval that hasn't been reached yet
		for (let interval of km_intervals) {
			let next_interval_value = last_km + interval;
			if (current_km < next_interval_value) {
				if (!target_km_interval || next_interval_value < (last_km + target_km_interval.value)) {
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
		let hour_next = last_hours + target_hour_interval.value;
		let km_next = last_km + target_km_interval.value;
		
		// Use the one that comes first, or prefer hours if equal
		if (hour_next <= km_next) {
			return target_hour_interval;
		} else {
			return target_km_interval;
		}
	}
	
	return target_hour_interval || target_km_interval;
}

function calculate_next_service(frm) {
	if (!frm.doc.service_hours && !frm.doc.service_kilometers) {
		return;
	}
	
	const hour_intervals = [250, 500, 1000, 2000, 6000];
	const km_intervals = [2500, 5000, 10000, 30000, 60000];
	
	let next_hours = null;
	let next_km = null;
	
	if (frm.doc.service_hours) {
		let current = flt(frm.doc.service_hours);
		for (let interval of hour_intervals) {
			if (current < interval) {
				next_hours = interval;
				break;
			}
		}
	}
	
	if (frm.doc.service_kilometers) {
		let current = flt(frm.doc.service_kilometers);
		for (let interval of km_intervals) {
			if (current < interval) {
				next_km = interval;
				break;
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

