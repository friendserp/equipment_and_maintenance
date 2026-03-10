// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental Agreement Items", {
	refresh(frm, cdt, cdn) {
		// Set default for is_existing_equipment (default to 0 for new equipment)
		let row = locals[cdt][cdn];
		if (row.is_existing_equipment === undefined) {
			frappe.model.set_value(cdt, cdn, "is_existing_equipment", 0);
		}
	}
});
