// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Job Completion", {
	refresh(frm) {

	},

	work_order_no(frm) {
		// Auto-fill note when work order is selected
		if (frm.doc.work_order_no) {
			frappe.db.get_doc("Maintenance Work Order", frm.doc.work_order_no)
				.then(doc => {
					// Get work order number and date out
					let work_order_no = doc.name || frm.doc.work_order_no;
					let date_outsourced = "";
					
					if (doc.date_out) {
						// Format date out
						date_outsourced = frappe.datetime.str_to_user(doc.date_out);
					}
					
					// Create note template
					let note_text = `All the jobs required against job order no ${work_order_no} and date outsourced ${date_outsourced} has been satisfactory completed. Except the remark noticed below\n\n_______________________________\n\n_______________________________`;
					
					// Set the note field
					frm.set_value("note", note_text);
				})
				.catch(err => {
					console.error("Error fetching Maintenance Work Order:", err);
				});
		} else {
			// Clear note if work order is cleared
			frm.set_value("note", "");
		}
	}
});
