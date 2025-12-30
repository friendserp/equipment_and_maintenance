// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Transfer Form", {
	refresh(frm) {
		// Auto-fill transfer_ordered_by for new documents
		if (frm.is_new()) {
			frm.set_value("transfer_ordered_by", frappe.session.user);
		}
		
		// Format departure time if present
		if (frm.doc.departure_time) {
			format_time_field(frm, "departure_time");
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
						// Auto-fill operator/driver name
						if (r.operators_name) {
							frm.set_value("operator_driver_name", r.operators_name);
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
			frm.set_value("operator_driver_name", "");
		}
	},

	departure_time(frm) {
		format_time_field(frm, "departure_time");
	}
});

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

