// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance Template", {
	refresh(frm) {
		// Set up query for task field
		frm.set_query("task", "maintenance_tasks", function() {
			return {
				filters: {
					is_active: 1
				}
			};
		});
	}
});

frappe.ui.form.on("Preventive Maintenance Task Interval", {
	task(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.task) {
			frappe.db.get_value("Preventive Maintenance Task", row.task, 
				["task_name", "task_category"], (r) => {
					if (r) {
						row.task_name = r.task_name;
						row.task_category = r.task_category;
						frm.refresh_field("maintenance_tasks");
					}
				}
			);
		}
	}
});

function import_standard_tasks(frm) {
	// This function can be used to bulk import standard tasks
	// For now, users will add tasks manually
	frappe.msgprint(__("Please add tasks manually. Standard tasks can be created in Preventive Maintenance Task master."));
}

