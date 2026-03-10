// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment and Maintenance Setting", {
	refresh(frm) {
		// Set query filter for fuel_item in child table
		frm.set_query("fuel_item", "fuel_prices", function() {
			return {
				filters: {
					item_group: "Fuel, Oils & Lubricants",
					custom_subcategory: "Fuel"
				}
			};
		});
	}
});

