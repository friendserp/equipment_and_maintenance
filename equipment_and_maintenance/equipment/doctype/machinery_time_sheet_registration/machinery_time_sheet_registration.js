// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machinery Time Sheet Registration", {
	refresh(frm) {
		// Auto-fill prepared_by for new documents
		if (frm.is_new()) {
			frm.set_value("prepared_by", frappe.session.user);
		}
		// Recalculate all row hours and totals
		recalculate_all_hours(frm);
		calculate_total_working_hour(frm);
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
					
					if (action === "Check" && next_state === "Checked") {
						if (!frm.doc.checked_by) {
							frm.set_value("checked_by", frappe.session.user);
						}
					} else if (action === "Approve" && next_state === "Approved") {
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
	
	onload(frm) {
		// Recalculate on load to ensure values are correct
		recalculate_all_hours(frm);
		calculate_total_working_hour(frm);
	},

	plate_number(frm) {
		// Fetch machine type and operator name from Equipment Master
		if (frm.doc.plate_number) {
			frappe.db.get_value("Equipment Master", frm.doc.plate_number, 
				["equipment_category", "operators_name"], (r) => {
					if (r) {
						// Set machine type based on category
						if (r.equipment_category) {
							frappe.db.get_value("Asset Category", r.equipment_category, 
								"asset_category_name", (cat) => {
									if (cat && cat.asset_category_name) {
										frm.set_value("machine_type", cat.asset_category_name);
									}
								}
							);
						}
						// Auto-fill operator name
						if (r.operators_name) {
							frm.set_value("operators_name", r.operators_name);
						}
					}
				}
			);
		}
	}
});

// Operation Time child table
frappe.ui.form.on("Operation Time", {
	start_time(frm, cdt, cdn) {
		calculate_row_hours(frm, cdt, cdn);
		calculate_total_working_hour(frm);
	},
	end_time(frm, cdt, cdn) {
		calculate_row_hours(frm, cdt, cdn);
		calculate_total_working_hour(frm);
	},
	operation_time_add(frm, cdt, cdn) {
		// Calculate when row is added
		setTimeout(() => {
			calculate_total_working_hour(frm);
		}, 100);
	},
	operation_time_remove(frm) {
		calculate_total_working_hour(frm);
	}
});

// Idle Time child table
frappe.ui.form.on("Idle Time", {
	start_time(frm, cdt, cdn) {
		calculate_row_hours(frm, cdt, cdn);
		calculate_total_working_hour(frm);
	},
	end_time(frm, cdt, cdn) {
		calculate_row_hours(frm, cdt, cdn);
		calculate_total_working_hour(frm);
	},
	idle_time_add(frm, cdt, cdn) {
		// Calculate when row is added
		setTimeout(() => {
			calculate_total_working_hour(frm);
		}, 100);
	},
	idle_time_remove(frm) {
		calculate_total_working_hour(frm);
	}
});

// Down Time child table
frappe.ui.form.on("Down Time", {
	start_time(frm, cdt, cdn) {
		calculate_row_hours(frm, cdt, cdn);
		calculate_total_working_hour(frm);
	},
	end_time(frm, cdt, cdn) {
		calculate_row_hours(frm, cdt, cdn);
		calculate_total_working_hour(frm);
	},
	down_time_add(frm, cdt, cdn) {
		// Calculate when row is added
		setTimeout(() => {
			calculate_total_working_hour(frm);
		}, 100);
	},
	down_time_remove(frm) {
		calculate_total_working_hour(frm);
	}
});

function calculate_row_hours(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.start_time && row.end_time) {
		// Handle both Time object and string format
		let start_str = row.start_time;
		let end_str = row.end_time;
		
		// Convert to string if it's a time object
		if (typeof start_str !== 'string') {
			start_str = moment(row.start_time).format("HH:mm:ss");
		}
		if (typeof end_str !== 'string') {
			end_str = moment(row.end_time).format("HH:mm:ss");
		}
		
		let start = moment(start_str, "HH:mm:ss");
		let end = moment(end_str, "HH:mm:ss");
		
		if (start.isValid() && end.isValid()) {
			// If end time is before start time, assume it's next day
			if (end.isBefore(start)) {
				end.add(1, 'day');
			}
			
			let hours = end.diff(start, 'hours', true);
			frappe.model.set_value(cdt, cdn, "hours", flt(hours, 2));
		} else {
			frappe.model.set_value(cdt, cdn, "hours", 0);
		}
	} else {
		frappe.model.set_value(cdt, cdn, "hours", 0);
	}
}

function recalculate_all_hours(frm) {
	// Recalculate hours for all operation time rows
	if (frm.doc.operation_time && frm.doc.operation_time.length > 0) {
		frm.doc.operation_time.forEach(function(row) {
			if (row.start_time && row.end_time) {
				calculate_row_hours(frm, "Operation Time", row.name);
			}
		});
	}
	
	// Recalculate hours for all idle time rows
	if (frm.doc.idle_time && frm.doc.idle_time.length > 0) {
		frm.doc.idle_time.forEach(function(row) {
			if (row.start_time && row.end_time) {
				calculate_row_hours(frm, "Idle Time", row.name);
			}
		});
	}
	
	// Recalculate hours for all down time rows
	if (frm.doc.down_time && frm.doc.down_time.length > 0) {
		frm.doc.down_time.forEach(function(row) {
			if (row.start_time && row.end_time) {
				calculate_row_hours(frm, "Down Time", row.name);
			}
		});
	}
}

function calculate_total_working_hour(frm) {
	let total_operation_hours = 0;
	let total_idle_hours = 0;
	let total_down_hours = 0;
	
	// Calculate total operation hours
	if (frm.doc.operation_time && frm.doc.operation_time.length > 0) {
		frm.doc.operation_time.forEach(function(row) {
			if (row.hours) {
				total_operation_hours += flt(row.hours);
			}
		});
	}
	
	// Calculate total idle hours
	if (frm.doc.idle_time && frm.doc.idle_time.length > 0) {
		frm.doc.idle_time.forEach(function(row) {
			if (row.hours) {
				total_idle_hours += flt(row.hours);
			}
		});
	}
	
	// Calculate total down hours
	if (frm.doc.down_time && frm.doc.down_time.length > 0) {
		frm.doc.down_time.forEach(function(row) {
			if (row.hours) {
				total_down_hours += flt(row.hours);
			}
		});
	}
	
	// Set individual totals
	frm.set_value("total_operation_hours", flt(total_operation_hours, 2));
	frm.set_value("total_idle_hours", flt(total_idle_hours, 2));
	frm.set_value("total_down_hours", flt(total_down_hours, 2));
	
}
