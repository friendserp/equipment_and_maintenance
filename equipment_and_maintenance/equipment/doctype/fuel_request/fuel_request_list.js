// Copyright (c) 2025, Equipment and Maintenance and contributors
// For license information, please see license.txt

frappe.listview_settings["Fuel Request"] = {
	add_fields: ["status", "fuel_type", "plate_number", "project", "current_fuel_requested_liter", "current_fuel_requested_birr"],
	get_indicator: function (doc) {
		const status_colors = {
			"Pending": "orange",
			"Distributed": "green",
		};
		const status = doc.status || "Pending";
		const color = status_colors[status] || "gray";
		
		return [__(status), color, `status,=,${status}`];
	},
};

