// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machinery Time Sheet Registration", {
	refresh(frm) {
		// Auto-fill prepared_by for new documents
		if (frm.is_new()) {
			frm.set_value("prepared_by", frappe.session.user);
		}
		
		// Format time fields to HH:mm format
		format_time_fields(frm);
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
	},

	morning_start(frm) {
		format_time_field(frm, "morning_start");
		calculate_total_working_hour(frm);
	},

	morning_end(frm) {
		format_time_field(frm, "morning_end");
		calculate_total_working_hour(frm);
	},

	afternoon_start(frm) {
		format_time_field(frm, "afternoon_start");
		calculate_total_working_hour(frm);
	},

	afternoon_end(frm) {
		format_time_field(frm, "afternoon_end");
		calculate_total_working_hour(frm);
	}
});

function format_time_fields(frm) {
	// Format all time fields to HH:mm AM/PM format
	const time_fields = ["morning_start", "morning_end", "afternoon_start", "afternoon_end"];
	time_fields.forEach(field => {
		format_time_field(frm, field);
	});
}

function format_time_field(frm, fieldname) {
	if (frm.doc[fieldname]) {
		let time_value = frm.doc[fieldname];
		if (typeof time_value === 'string' && time_value.trim()) {
			// Try to format to HH:mm AM/PM (always default to PM unless AM is specified)
			let formatted = format_to_ampm(time_value);
			if (formatted && formatted !== time_value.toUpperCase()) {
				frm.set_value(fieldname, formatted);
			}
		}
	}
}

function format_to_ampm(time_str) {
	// Convert various time formats to HH:mm AM/PM
	// Always default to PM unless AM is explicitly specified
	time_str = time_str.trim().toUpperCase();
	
	// If AM is explicitly specified, use AM
	if (time_str.includes('AM')) {
		let match = time_str.match(/^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*AM$/);
		if (match) {
			let hour = parseInt(match[1]);
			let minute = parseInt(match[2]);
			return String(hour).padStart(2, '0') + ':' + String(minute).padStart(2, '0') + ' AM';
		}
	}
	
	// If PM is explicitly specified, use PM
	if (time_str.includes('PM')) {
		let match = time_str.match(/^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*PM$/);
		if (match) {
			let hour = parseInt(match[1]);
			let minute = parseInt(match[2]);
			return String(hour).padStart(2, '0') + ':' + String(minute).padStart(2, '0') + ' PM';
		}
	}
	
	// If in 24-hour format, convert to 12-hour
	let match_24 = time_str.match(/^([0-1]?[0-9]|2[0-3]):([0-5][0-9])/);
	if (match_24) {
		let hour24 = parseInt(match_24[1]);
		let minute = parseInt(match_24[2]);
		let hour12, ampm;
		
		if (hour24 === 0) {
			hour12 = 12;
			ampm = 'AM';
		} else if (hour24 === 12) {
			hour12 = 12;
			ampm = 'PM';
		} else if (hour24 < 12) {
			hour12 = hour24;
			ampm = 'AM';
		} else {
			hour12 = hour24 - 12;
			ampm = 'PM';
		}
		
		return String(hour12).padStart(2, '0') + ':' + String(minute).padStart(2, '0') + ' ' + ampm;
	}
	
	// If in HH:mm format without AM/PM, always default to PM
	let match_12 = time_str.match(/^([0]?[1-9]|1[0-2]):([0-5][0-9])$/);
	if (match_12) {
		let hour = parseInt(match_12[1]);
		let minute = parseInt(match_12[2]);
		return String(hour).padStart(2, '0') + ':' + String(minute).padStart(2, '0') + ' PM';
	}
	
	return null;
}

// Validation is now only done on save (server-side)
// Client-side only formats the time without showing errors

function calculate_total_working_hour(frm) {
	let total_hours = 0;
	
	// Calculate morning hours
	if (frm.doc.morning_start && frm.doc.morning_end) {
		let morning_hours = calculate_time_difference(frm.doc.morning_start, frm.doc.morning_end);
		if (morning_hours > 0) {
			total_hours += morning_hours;
		}
	}
	
	// Calculate afternoon hours
	if (frm.doc.afternoon_start && frm.doc.afternoon_end) {
		let afternoon_hours = calculate_time_difference(frm.doc.afternoon_start, frm.doc.afternoon_end);
		if (afternoon_hours > 0) {
			total_hours += afternoon_hours;
		}
	}
	
	frm.set_value("total_working_hour", flt(total_hours, 2));
}

function calculate_time_difference(start_time_str, end_time_str) {
	// Convert AM/PM format to 24-hour format for calculation
	let start_24 = convert_ampm_to_24hour(start_time_str);
	let end_24 = convert_ampm_to_24hour(end_time_str);
	
	if (!start_24 || !end_24) return 0;
	
	// Parse times
	let start_moment = moment(start_24, "HH:mm", true);
	let end_moment = moment(end_24, "HH:mm", true);
	
	if (!start_moment.isValid() || !end_moment.isValid()) return 0;
	
	// If end time is before start time, assume it's next day (e.g., night shift)
	if (end_moment.isBefore(start_moment)) {
		end_moment.add(1, 'day');
	}
	
	return end_moment.diff(start_moment, 'hours', true);
}

function convert_ampm_to_24hour(time_str) {
	// Convert HH:mm AM/PM to HH:mm (24-hour format)
	let match = time_str.trim().toUpperCase().match(/^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)$/);
	if (!match) return null;
	
	let hour = parseInt(match[1]);
	let minute = parseInt(match[2]);
	let ampm = match[3];
	
	// Convert to 24-hour format
	if (ampm === 'AM') {
		if (hour === 12) {
			hour = 0; // 12:xx AM becomes 00:xx
		}
	} else { // PM
		if (hour !== 12) {
			hour += 12; // 1-11 PM becomes 13-23
		}
		// 12:xx PM stays 12:xx
	}
	
	return String(hour).padStart(2, '0') + ':' + String(minute).padStart(2, '0');
}

