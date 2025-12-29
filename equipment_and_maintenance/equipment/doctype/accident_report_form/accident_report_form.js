// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accident Report Form", {
	date(frm) {
		// Auto-set signature date to form date if not set
		if (frm.doc.date && !frm.doc.signature_date) {
			frm.set_value("signature_date", frm.doc.date);
		}
	},
	
	// Accident Time - mutually exclusive
	accident_time_night(frm) {
		if (frm.doc.accident_time_night && frm.doc.accident_time_day) {
			frm.set_value("accident_time_day", 0);
		}
	},
	
	accident_time_day(frm) {
		if (frm.doc.accident_time_day && frm.doc.accident_time_night) {
			frm.set_value("accident_time_night", 0);
		}
	},
	
	// Weather Condition - mutually exclusive
	weather_rainy(frm) {
		if (frm.doc.weather_rainy) {
			if (frm.doc.weather_sunny) frm.set_value("weather_sunny", 0);
			if (frm.doc.weather_foggy) frm.set_value("weather_foggy", 0);
		}
	},
	
	weather_sunny(frm) {
		if (frm.doc.weather_sunny) {
			if (frm.doc.weather_rainy) frm.set_value("weather_rainy", 0);
			if (frm.doc.weather_foggy) frm.set_value("weather_foggy", 0);
		}
	},
	
	weather_foggy(frm) {
		if (frm.doc.weather_foggy) {
			if (frm.doc.weather_rainy) frm.set_value("weather_rainy", 0);
			if (frm.doc.weather_sunny) frm.set_value("weather_sunny", 0);
		}
	},
	
	// Accident Place - mutually exclusive
	accident_place_bush_fallow(frm) {
		if (frm.doc.accident_place_bush_fallow) {
			uncheck_other_places(frm, "accident_place_bush_fallow");
		}
	},
	
	accident_place_uphill(frm) {
		if (frm.doc.accident_place_uphill) {
			uncheck_other_places(frm, "accident_place_uphill");
		}
	},
	
	accident_place_escarp(frm) {
		if (frm.doc.accident_place_escarp) {
			uncheck_other_places(frm, "accident_place_escarp");
		}
	},
	
	accident_place_muddy(frm) {
		if (frm.doc.accident_place_muddy) {
			uncheck_other_places(frm, "accident_place_muddy");
		}
	},
	
	accident_place_dry(frm) {
		if (frm.doc.accident_place_dry) {
			uncheck_other_places(frm, "accident_place_dry");
		}
	}
});

function uncheck_other_places(frm, current_field) {
	const place_fields = [
		"accident_place_bush_fallow",
		"accident_place_uphill",
		"accident_place_escarp",
		"accident_place_muddy",
		"accident_place_dry"
	];
	
	place_fields.forEach(field => {
		if (field !== current_field && frm.doc[field]) {
			frm.set_value(field, 0);
		}
	});
}

