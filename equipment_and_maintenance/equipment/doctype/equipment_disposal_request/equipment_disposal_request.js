// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Disposal Request", {
	refresh(frm) {
		// Set up date to today if not set
		if (!frm.doc.date) {
			frm.set_value("date", frappe.datetime.get_today());
		}
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

	// Make approval checkboxes mutually exclusive within each section
	equip_dept_approved(frm) {
		if (frm.doc.equip_dept_approved) {
			frm.set_value("equip_dept_rejected", 0);
			if (!frm.doc.equip_dept_date) {
				frm.set_value("equip_dept_date", frappe.datetime.get_today());
			}
		}
	},
	equip_dept_rejected(frm) {
		if (frm.doc.equip_dept_rejected) {
			frm.set_value("equip_dept_approved", 0);
			frm.set_value("equip_dept_date", "");
		}
	},
	dgm_approved(frm) {
		if (frm.doc.dgm_approved) {
			frm.set_value("dgm_rejected", 0);
			if (!frm.doc.dgm_date) {
				frm.set_value("dgm_date", frappe.datetime.get_today());
			}
		}
	},
	dgm_rejected(frm) {
		if (frm.doc.dgm_rejected) {
			frm.set_value("dgm_approved", 0);
			frm.set_value("dgm_date", "");
		}
	},
	survey_committee_approved(frm) {
		if (frm.doc.survey_committee_approved) {
			frm.set_value("survey_committee_rejected", 0);
			if (!frm.doc.survey_committee_date) {
				frm.set_value("survey_committee_date", frappe.datetime.get_today());
			}
		}
	},
	survey_committee_rejected(frm) {
		if (frm.doc.survey_committee_rejected) {
			frm.set_value("survey_committee_approved", 0);
			frm.set_value("survey_committee_date", "");
		}
	},
	general_manager_approved(frm) {
		if (frm.doc.general_manager_approved) {
			frm.set_value("general_manager_rejected", 0);
		}
	},
	general_manager_rejected(frm) {
		if (frm.doc.general_manager_rejected) {
			frm.set_value("general_manager_approved", 0);
		}
	}
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

