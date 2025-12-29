// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Control and Registration Form", {
	refresh(frm) {
		// Set default date for new items
		if (frm.is_new()) {
			frm.set_value("prepared_by", frappe.session.user);
		}
	},

	items_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Set default date to today if not set
		if (!row.date) {
			frappe.model.set_value(cdt, cdn, "date", frappe.datetime.get_today());
		}
	}
});

// Calculate totals for each row (if needed)
frappe.ui.form.on("Cost Control Registration Item", {
	fuel_liter(frm, cdt, cdn) {
		// Auto-calculate fuel price if unit price is known
		// This can be enhanced based on business logic
	},
	
	fuel_birr(frm, cdt, cdn) {
		// Recalculate if needed
	},
	
	engine_oil_liter(frm, cdt, cdn) {
		// Auto-calculate if unit price is known
	},
	
	engine_oil_birr(frm, cdt, cdn) {
		// Recalculate if needed
	}
});

