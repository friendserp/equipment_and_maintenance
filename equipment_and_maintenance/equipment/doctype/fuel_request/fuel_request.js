// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fuel Request", {
	refresh(frm) {
		// Auto-set requested_by if not set
		if (!frm.doc.requested_by) {
			frm.set_value("requested_by", frappe.session.user);
		}
		
		// Auto-set date_issued to date if not set
		if (frm.doc.date && !frm.doc.date_issued) {
			frm.set_value("date_issued", frm.doc.date);
		}
	},
	
	date(frm) {
		// Auto-set date_issued to date if not set
		if (frm.doc.date && !frm.doc.date_issued) {
			frm.set_value("date_issued", frm.doc.date);
		}
	},
	
	previous_fuel_consumption_liter(frm) {
		calculate_fuel_efficiency(frm);
		calculate_current_fuel_cost(frm);
	},
	
	previous_fuel_consumption_birr(frm) {
		calculate_current_fuel_cost(frm);
	},
	
	previous_km_hr_reading(frm) {
		calculate_fuel_efficiency(frm);
	},
	
	current_km_hr_reading(frm) {
		calculate_fuel_efficiency(frm);
	},
	
	current_fuel_requested_liter(frm) {
		calculate_current_fuel_cost(frm);
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

function calculate_current_fuel_cost(frm) {
	// Calculate current fuel cost based on previous fuel price per liter
	if (frm.doc.current_fuel_requested_liter && 
		frm.doc.previous_fuel_consumption_liter && 
		frm.doc.previous_fuel_consumption_birr) {
		
		let price_per_liter = flt(frm.doc.previous_fuel_consumption_birr) / flt(frm.doc.previous_fuel_consumption_liter);
		let current_cost = flt(frm.doc.current_fuel_requested_liter) * price_per_liter;
		frm.set_value("current_fuel_requested_birr", current_cost);
	} else if (frm.doc.current_fuel_requested_liter) {
		// If no previous data, set to 0
		frm.set_value("current_fuel_requested_birr", 0);
	}
}

