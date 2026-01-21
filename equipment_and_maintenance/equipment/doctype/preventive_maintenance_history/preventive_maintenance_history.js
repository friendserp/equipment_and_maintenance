// Copyright (c) 2026, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Preventive Maintenance History", {
	refresh(frm) {
		// Set default date to today if status is Completed
		if (!frm.doc.pm_date && frm.doc.status === "Completed") {
			frm.set_value("pm_date", frappe.datetime.get_today());
		}
	},
	
	equipment(frm) {
		if (frm.doc.equipment) {
			// Fetch equipment details
			frappe.db.get_doc("Equipment Master", frm.doc.equipment)
				.then(equipment => {
					frm.set_value({
						plate_number: equipment.plate_number || "",
						equipment_code: equipment.equipment_code || "",
						make: equipment.make || "",
						model: equipment.model || ""
					});
				});
		}
	},
	
	pm_done(frm) {
		if (frm.doc.pm_done) {
			// Load details from PM Done
			frappe.db.get_doc("Preventive Maintenance Done", frm.doc.pm_done)
				.then(pm_done => {
					frm.set_value({
						equipment: pm_done.equipment,
						pm_date: pm_done.actual_date,
						service_type: pm_done.service_type,
						hours_km_after: pm_done.actual_hours_km,
						performed_by: pm_done.performed_by,
						plan: pm_done.plan,
						planned_week: pm_done.planned_week,
						planned_service_type: pm_done.planned_service_type,
						planned_hours_km: pm_done.planned_hours_km,
						pm_performed_as_per_schedule: pm_done.pm_performed_as_per_schedule,
						status: "Completed",
						remark: pm_done.remark || pm_done.completion_notes
					});
				});
		}
	}
});
