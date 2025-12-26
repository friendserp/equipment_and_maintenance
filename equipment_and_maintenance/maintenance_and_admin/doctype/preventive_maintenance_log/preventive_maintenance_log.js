// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance Log", {
	refresh(frm) {
		// Load tasks from schedule when schedule is selected
		if (frm.doc.schedule && !frm.doc.completed_tasks || frm.doc.completed_tasks.length === 0) {
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
	
	frappe.db.get_doc("Preventive Maintenance Schedule", frm.doc.schedule)
		.then(doc => {
			// Get current interval
			let current_hours = flt(frm.doc.service_hours) || flt(doc.current_hours);
			let current_km = flt(frm.doc.service_kilometers) || flt(doc.current_kilometers);
			
			// Determine which interval this service is for
			let interval_name = determine_interval(current_hours, current_km, doc);
			
			if (interval_name) {
				frm.set_value("interval_name", interval_name);
			}
			
			// Load tasks for this interval
			frm.clear_table("completed_tasks");
			
			if (doc.schedule_items) {
				doc.schedule_items.forEach(item => {
					if (item.interval_name === interval_name && !item.is_completed) {
						let row = frm.add_child("completed_tasks");
						row.task = item.task;
						row.task_name = item.task_name;
						row.task_category = item.task_category;
						row.is_completed = 0;
					}
				});
			}
			
			frm.refresh_field("completed_tasks");
		});
}

function determine_interval(current_hours, current_km, schedule) {
	// Determine which interval this service is for based on current readings
	const hour_intervals = [
		{name: "250 Hours", value: 250},
		{name: "500 Hours", value: 500},
		{name: "1000 Hours", value: 1000},
		{name: "2000 Hours", value: 2000},
		{name: "6000 Hours", value: 6000}
	];
	
	const km_intervals = [
		{name: "2500 KM", value: 2500},
		{name: "5000 KM", value: 5000},
		{name: "10000 KM", value: 10000},
		{name: "30000 KM", value: 30000},
		{name: "60000 KM", value: 60000}
	];
	
	let last_hours = flt(schedule.last_service_hours) || 0;
	let last_km = flt(schedule.last_service_kilometers) || 0;
	
	// Find the interval that matches
	if (current_hours) {
		for (let interval of hour_intervals) {
			if (current_hours >= last_hours + interval.value && 
				current_hours < last_hours + interval.value + 100) {
				return interval.name;
			}
		}
	}
	
	if (current_km) {
		for (let interval of km_intervals) {
			if (current_km >= last_km + interval.value && 
				current_km < last_km + interval.value + 500) {
				return interval.name;
			}
		}
	}
	
	return null;
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

