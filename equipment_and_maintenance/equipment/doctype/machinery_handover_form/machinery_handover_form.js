// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machinery Handover Form", {
	refresh(frm) {
		// Populate default body parts if empty
		if (!frm.doc.body_parts || frm.doc.body_parts.length === 0) {
			populate_default_body_parts(frm);
		}
		
		// Populate default attachments if empty
		if (!frm.doc.attachments || frm.doc.attachments.length === 0) {
			populate_default_attachments(frm);
		}
	},
	
	refresh(frm) {
		// Auto-set custodian_name if not set (on creation)
		if (frm.is_new() && !frm.doc.custodian_name) {
			frm.set_value("custodian_name", frappe.session.user);
		}
		
		// Populate default body parts if empty
		if (!frm.doc.body_parts || frm.doc.body_parts.length === 0) {
			populate_default_body_parts(frm);
		}
		
		// Populate default attachments if empty
		if (!frm.doc.attachments || frm.doc.attachments.length === 0) {
			populate_default_attachments(frm);
		}
	},
	
	before_workflow_action(frm) {
		// Populate user fields BEFORE workflow action is applied
		// Return a promise to ensure values are set before workflow proceeds
		return new Promise((resolve) => {
			const action = frm.selected_workflow_action;
			
			if (!action) {
				resolve();
				return;
			}
			
			frappe.workflow.get_transitions(frm.doc).then((transitions) => {
				const transition = transitions.find(t => t.action === action);
				if (transition) {
					const next_state = transition.next_state;
					
					if (action === "Receive" && next_state === "Received") {
						if (!frm.doc.received_by) {
							frappe.db.get_value("User", frappe.session.user, "full_name").then(r => {
								if (r && r.full_name) {
									frm.set_value("received_by", frappe.session.user);
									frm.set_value("received_date", frappe.datetime.get_today());
								}
								setTimeout(() => resolve(), 100);
							}).catch(() => resolve());
						} else {
							resolve();
						}
					} else if (action === "Hand Over" && next_state === "Handed Over") {
						if (!frm.doc.handed_over_by) {
							frappe.db.get_value("User", frappe.session.user, "full_name").then(r => {
								if (r && r.full_name) {
									frm.set_value("handed_over_by", frappe.session.user);
									frm.set_value("handed_date", frappe.datetime.get_today());
								}
								setTimeout(() => resolve(), 100);
							}).catch(() => resolve());
						} else {
							resolve();
						}
					} else {
						resolve();
					}
				} else {
					resolve();
				}
			}).catch(() => resolve());
		});
	}
});

function populate_default_body_parts(frm) {
	const default_parts = [
		"Head Light Right Side",
		"Head Light Left Side",
		"Mirror Right Side",
		"Mirror Left Side",
		"Front Window Right Side",
		"Front Window Left Side",
		"Rear Window Right Side",
		"Rear Window Left Side",
		"Front Door Right Side",
		"Front Door Left Side",
		"Rear Door Right Side",
		"Rear Door Left Side",
		"Escort Tire",
		"Wind Shield",
		"Hood",
		"Front Turn Signal Right Side",
		"Front Turn Light Left side",
		"Rear Turn Signal Right Side",
		"Rear Turn Light Left side",
		"Fog Lamp Right Side",
		"Fog Lamp Left Side",
		"Bumper",
		"Front Door Handle Right Side",
		"Front Door Handle Left Side",
		"Rear Door Handle Right Side",
		"Rear Door Handle Left Side",
		"Rear View Mirror",
		"Wind Shield Wiper Right Side",
		"Wind Shield Wiper Left Side",
		"Tail Light Right Side",
		"Tail Light Left Side",
		"Front Wind Deflector Right Side",
		"Front Wind Deflector Left Side",
		"Rear Wind Deflector Right Side",
		"Rear Wind Deflector Left Side",
		"Roof Rack",
		"Antenna",
		"Bed Liner",
		"High Over Bar Right Side",
		"High Over Bar Left Side",
		"Side Step Right Side",
		"Side Step Left Side",
		"Under Guard",
		"Front Floor Mat Right Side",
		"Front Floor Mat Left Side",
		"Rear Floor Mat Right Side",
		"Rear Floor Mat Left Side",
		"Logo",
		"Front Lamp Bezel Right Side",
		"Front Lamp Bezel Left Side",
		"Rear Lamp Bezel Right Side",
		"Rear Lamp Bezel Left Side",
		"Rear Glass",
		"Hydraulic Jack",
		"Tape",
		"Cigarette Lighter",
		"Radiator Cap",
		"Engine Oil Cap",
		"Dip Stick",
		"Plate Number Light"
	];
	
	default_parts.forEach((part_name) => {
		let row = frm.add_child("body_parts");
		row.part_name = part_name;
	});
	
	frm.refresh_field("body_parts");
}

function populate_default_attachments(frm) {
	const default_attachments = [
		{ name: "Allen Keys", has_size: false },
		{ name: "Open Ended Spanners", has_size: true },
		{ name: "Box Ended Spanners", has_size: true },
		{ name: "Combination Spanners", has_size: true },
		{ name: "Wrenches", has_size: true },
		{ name: "Flat Screw Drivers", has_size: false },
		{ name: "Cross Screw Drivers", has_size: false },
		{ name: "Hammer", has_size: false },
		{ name: "Pliers", has_size: false },
		{ name: "Others", has_size: false }
	];
	
	default_attachments.forEach((item) => {
		let row = frm.add_child("attachments");
		row.part_name = item.name;
		if (item.has_size) {
			row.size_numbers = "Size Numbers";
		}
	});
	
	frm.refresh_field("attachments");
}

