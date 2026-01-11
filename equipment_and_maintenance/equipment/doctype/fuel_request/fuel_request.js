// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fuel Request", {
	refresh(frm) {
		// Auto-set requested_by if not set (on creation)
		if (frm.is_new() && !frm.doc.requested_by) {
			frm.set_value("requested_by", frappe.session.user);
		}
		
		// Auto-set date_issued to date if not set
		if (frm.doc.date && !frm.doc.date_issued) {
			frm.set_value("date_issued", frm.doc.date);
		}
		
		// Set query filter for fuel_type from settings
		frm.set_query("fuel_type", function() {
			return {
				filters: {
					item_group: "Fuel, Oil & Lubricants",
					custom_subcategory: "Fuel"
				}
			};
		});
	},
	
	date(frm) {
		// Auto-set date_issued to date if not set
		if (frm.doc.date && !frm.doc.date_issued) {
			frm.set_value("date_issued", frm.doc.date);
		}
		// Refetch fuel price if fuel type is already selected
		if (frm.doc.fuel_type) {
			fetch_fuel_price(frm);
		}
	},
	
	plate_number(frm) {
		// Fetch previous fuel data from Stock Entry when plate number is selected
		if (frm.doc.plate_number) {
			fetch_previous_fuel_data(frm);
		} else {
			// Clear previous fields if plate number is cleared
			frm.set_value("previous_km_hr_reading", 0);
			frm.set_value("previous_fuel_consumption_liter", 0);
			frm.set_value("previous_fuel_consumption_birr", 0);
		}
	},
	
	fuel_type(frm) {
		// Fetch price from settings when fuel type is selected
		if (frm.doc.fuel_type) {
			fetch_fuel_price(frm);
		} else {
			frm.set_value("current_price_per_liter", 0);
			calculate_current_fuel_cost(frm);
		}
	},
	
	previous_fuel_consumption_liter(frm) {
		calculate_fuel_efficiency(frm);
	},
	
	previous_fuel_consumption_birr(frm) {
		// Previous section logic will be handled separately
	},
	
	previous_km_hr_reading(frm) {
		calculate_fuel_efficiency(frm);
	},
	
	current_km_hr_reading(frm) {
		calculate_fuel_efficiency(frm);
	},
	
	current_fuel_requested_liter(frm) {
		calculate_current_fuel_cost(frm);
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
	}
});

function calculate_fuel_efficiency(frm) {
	// Calculate Km/Ltr = (Current Reading - Previous Reading) / Previous Fuel Consumption
	if (frm.doc.previous_km_hr_reading && 
		frm.doc.current_km_hr_reading && 
		frm.doc.previous_fuel_consumption_liter) {
		
		let distance_traveled = flt(frm.doc.current_km_hr_reading) - flt(frm.doc.previous_km_hr_reading);
		
		if (distance_traveled > 0 && flt(frm.doc.previous_fuel_consumption_liter) > 0) {
			let km_per_liter = distance_traveled / flt(frm.doc.previous_fuel_consumption_liter);
			frm.set_value("vehicles_km_ltr", km_per_liter);
		} else {
			frm.set_value("vehicles_km_ltr", 0);
		}
	}
}

function fetch_fuel_price(frm) {
	// Fetch fuel price from Equipment and Maintenance Setting
	if (!frm.doc.fuel_type) return;
	
	frappe.call({
		method: "equipment_and_maintenance.equipment.doctype.fuel_request.fuel_request.get_fuel_price",
		args: {
			fuel_item: frm.doc.fuel_type,
			date: frm.doc.date || frappe.datetime.get_today()
		},
		callback: function(r) {
			if (r.message) {
				frm.set_value("current_price_per_liter", r.message);
				calculate_current_fuel_cost(frm);
			}
		}
	});
}

function fetch_previous_fuel_data(frm) {
	// Fetch previous fuel consumption data from Stock Entry
	if (!frm.doc.plate_number) return;
	
	frappe.call({
		method: "equipment_and_maintenance.equipment.doctype.fuel_request.fuel_request.get_previous_fuel_data",
		args: {
			plate_number: frm.doc.plate_number
		},
		callback: function(r) {
			if (r.message && Object.keys(r.message).length > 0) {
				// Populate previous section fields
				if (r.message.previous_km_hr_reading) {
					frm.set_value("previous_km_hr_reading", r.message.previous_km_hr_reading);
				}
				if (r.message.previous_fuel_consumption_liter) {
					frm.set_value("previous_fuel_consumption_liter", r.message.previous_fuel_consumption_liter);
				}
				if (r.message.previous_fuel_consumption_birr) {
					frm.set_value("previous_fuel_consumption_birr", r.message.previous_fuel_consumption_birr);
				}
				// Recalculate fuel efficiency if current reading is available
				if (frm.doc.current_km_hr_reading) {
					calculate_fuel_efficiency(frm);
				}
			}
		}
	});
}

function calculate_current_fuel_cost(frm) {
	// Calculate current fuel cost = quantity * price per liter
	if (frm.doc.current_fuel_requested_liter && frm.doc.current_price_per_liter) {
		let current_cost = flt(frm.doc.current_fuel_requested_liter) * flt(frm.doc.current_price_per_liter);
		frm.set_value("current_fuel_requested_birr", current_cost);
	} else {
		frm.set_value("current_fuel_requested_birr", 0);
	}
}

