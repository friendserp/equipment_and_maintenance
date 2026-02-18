frappe.ui.form.on("Material Request", {
	refresh(frm) {
		update_mr_status_indicator(frm);
	},

	custom_mr_status(frm) {
		update_mr_status_indicator(frm);
	},
});

function update_mr_status_indicator(frm) {
	const status = frm.doc.custom_mr_status || frm.doc.status;
	if (!status) return;

	const color_map = {
		// PR workflow statuses
		"PR Draft": "orange",
		"PR Requested": "orange",
		"PR Checked": "blue",
		"PR Approved": "green",

		// System statuses
		Draft: "grey",
		Pending: "orange",
		"Partially Ordered": "orange",
		Ordered: "blue",
		"Partially Received": "orange",
		Received: "green",
		Cancelled: "red",
	};

	const color = color_map[status] || "blue";

	frm.dashboard.set_headline(
		__(
			"MR Status: <span class='indicator {0}'>{1}</span>",
			[color, status]
		)
	);
}

