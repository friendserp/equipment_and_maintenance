// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Disposal Request", {
	refresh(frm) {
		// Set up date to today if not set
		if (!frm.doc.date) {
			frm.set_value("date", frappe.datetime.get_today());
		}
		
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
	},
	
	before_workflow_action(frm) {
		// Populate user and date fields BEFORE workflow action is applied
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
					const user = frappe.session.user;
					const today = frappe.datetime.get_today();
					
					if (action === "Equipment Dept Approve" && next_state === "Equipment Dept Approved") {
						if (!frm.doc.equip_dept_approved_by) {
							frm.set_value("equip_dept_approved_by", user);
							frm.set_value("equip_dept_date", today);
						}
					} else if (action === "DGM Approve" && next_state === "DGM Approved") {
						if (!frm.doc.dgm_approved_by) {
							frm.set_value("dgm_approved_by", user);
							frm.set_value("dgm_date", today);
						}
					} else if (action === "Survey Committee Approve" && next_state === "Survey Committee Approved") {
						if (!frm.doc.survey_committee_approved_by) {
							frm.set_value("survey_committee_approved_by", user);
							frm.set_value("survey_committee_date", today);
						}
					} else if (action === "General Manager Approve" && next_state === "General Manager Approved") {
						if (!frm.doc.general_manager_approved_by) {
							frm.set_value("general_manager_approved_by", user);
						}
						if (!frm.doc.approved_by) {
							frm.set_value("approved_by", user);
						}
					}
					
					// Wait a bit to ensure values are set before resolving
					setTimeout(() => resolve(), 100);
				} else {
					resolve();
				}
			}).catch(() => resolve());
		});
	},

	plate_no(frm) {
		// Auto-fill equipment details when plate_no is selected
		if (frm.doc.plate_no) {
			frappe.db.get_doc("Equipment Master", frm.doc.plate_no)
				.then((equipment) => {
					// Fetch equipment details
					frappe.db.get_value("Equipment Master", frm.doc.plate_no, [
						"equipment_category",
						"equipment_sub_category",
						"make",
						"model",
						"location",
						"yom"
					], (r) => {
						if (r) {
							// Set type from sub-category
							if (r.equipment_sub_category) {
								frappe.db.get_value("Asset Sub Category", r.equipment_sub_category, "asset_sub_category_name", (sub_cat) => {
									if (sub_cat && sub_cat.asset_sub_category_name) {
										frm.set_value("type", sub_cat.asset_sub_category_name);
									}
								});
							}

							// Set model
							if (r.model) {
								frm.set_value("model", r.model);
							}

							// Set description (make + model)
							let description = "";
							if (r.make) description += r.make;
							if (r.model) description += (description ? " " : "") + r.model;
							if (description) {
								frm.set_value("description", description);
							}

							// Set equipment location
							if (r.location) {
								frm.set_value("equipment_location", r.location);
							}

							// Calculate service year from YOM
							if (r.yom) {
								try {
									const yom = parseInt(r.yom);
									if (yom && yom > 1900 && yom <= new Date().getFullYear()) {
										const currentYear = new Date().getFullYear();
										const serviceYear = currentYear - yom;
										frm.set_value("service_year", serviceYear);
									}
								} catch (e) {
									// Ignore if YOM is not a valid year
								}
							}

							// Try to get purchase price from linked Asset
							if (equipment.asset_id) {
								frappe.db.get_value("Asset", equipment.asset_id, ["purchase_amount", "net_purchase_amount"], (asset) => {
									if (asset) {
										if (asset.purchase_amount) {
											frm.set_value("purchase_price", asset.purchase_amount);
										} else if (asset.net_purchase_amount) {
											frm.set_value("purchase_price", asset.net_purchase_amount);
										}
									}
								});
							}
						}
					});
				})
				.catch((err) => {
					console.error("Error fetching equipment:", err);
				});
		} else {
			// Clear fields if plate_no is cleared
			frm.set_value("type", "");
			frm.set_value("model", "");
			frm.set_value("description", "");
			frm.set_value("equipment_location", "");
			frm.set_value("service_year", "");
			frm.set_value("purchase_price", "");
		}
	},

	// Make reason checkboxes mutually exclusive
	reason_beyond_repair(frm) {
		if (frm.doc.reason_beyond_repair) {
			clearOtherReasons(frm, "reason_beyond_repair");
		}
	},
	reason_part_unobtainable(frm) {
		if (frm.doc.reason_part_unobtainable) {
			clearOtherReasons(frm, "reason_part_unobtainable");
		}
	},
	reason_repair_costs_unjustified(frm) {
		if (frm.doc.reason_repair_costs_unjustified) {
			clearOtherReasons(frm, "reason_repair_costs_unjustified");
		}
	},
	reason_inferior_productivity(frm) {
		if (frm.doc.reason_inferior_productivity) {
			clearOtherReasons(frm, "reason_inferior_productivity");
		}
	},
	reason_equipment_missing(frm) {
		if (frm.doc.reason_equipment_missing) {
			clearOtherReasons(frm, "reason_equipment_missing");
		}
	},
	reason_equipment_preempted(frm) {
		if (frm.doc.reason_equipment_preempted) {
			clearOtherReasons(frm, "reason_equipment_preempted");
		}
	},
	reason_equipment_surplus(frm) {
		if (frm.doc.reason_equipment_surplus) {
			clearOtherReasons(frm, "reason_equipment_surplus");
		}
	},
	reason_other(frm) {
		if (frm.doc.reason_other) {
			clearOtherReasons(frm, "reason_other");
		}
	},

	// Make disposition checkboxes mutually exclusive
	disposition_sell_as_it(frm) {
		if (frm.doc.disposition_sell_as_it) {
			clearOtherDispositions(frm, "disposition_sell_as_it");
		}
	},
	disposition_scrap(frm) {
		if (frm.doc.disposition_scrap) {
			clearOtherDispositions(frm, "disposition_scrap");
		}
	},
	disposition_cannibalize(frm) {
		if (frm.doc.disposition_cannibalize) {
			clearOtherDispositions(frm, "disposition_cannibalize");
		}
	},
	disposition_other(frm) {
		if (frm.doc.disposition_other) {
			clearOtherDispositions(frm, "disposition_other");
		}
	},

});

function clearOtherReasons(frm, currentReason) {
	const reasons = [
		"reason_beyond_repair",
		"reason_part_unobtainable",
		"reason_repair_costs_unjustified",
		"reason_inferior_productivity",
		"reason_equipment_missing",
		"reason_equipment_preempted",
		"reason_equipment_surplus",
		"reason_other"
	];

	reasons.forEach((reason) => {
		if (reason !== currentReason && frm.doc[reason]) {
			frm.set_value(reason, 0);
		}
	});
}

function clearOtherDispositions(frm, currentDisposition) {
	const dispositions = [
		"disposition_sell_as_it",
		"disposition_scrap",
		"disposition_cannibalize",
		"disposition_other"
	];

	dispositions.forEach((disposition) => {
		if (disposition !== currentDisposition && frm.doc[disposition]) {
			frm.set_value(disposition, 0);
		}
	});
}

