// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Recording Database Form", {
	refresh(frm) {
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
		
		// Add buttons to link to related forms
		if (!frm.is_new()) {
			if (frm.doc.tyre_request_form) {
				frm.add_custom_button(
					__("Tyre Request Form"),
					function() {
						frappe.set_route("Form", "Tyre Request and Analysis Form", frm.doc.tyre_request_form);
					},
					__("View")
				);
			}
			
			if (frm.doc.tyre_issue_return_form) {
				frm.add_custom_button(
					__("Tyre Issue Return Form"),
					function() {
						frappe.set_route("Form", "Tyre Issue and Return Report Form", frm.doc.tyre_issue_return_form);
					},
					__("View")
				);
			}
		}
	},
	
	before_workflow_action(frm) {
		// Populate user fields BEFORE workflow action is applied
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
					
					if (action === "Check" && next_state === "Checked") {
						if (!frm.doc.checked_by) {
							frm.set_value("checked_by", frappe.session.user);
							frm.set_value("checked_by_date", frappe.datetime.get_today());
						}
					} else if (action === "Approve" && next_state === "Approved") {
						if (!frm.doc.approved_by) {
							frm.set_value("approved_by", frappe.session.user);
							frm.set_value("approved_by_date", frappe.datetime.get_today());
						}
					}
					
					setTimeout(() => resolve(), 100);
				} else {
					resolve();
				}
			}).catch(() => resolve());
		});
	},
	
	plate_no(frm) {
		// Fetch equipment details when plate_no is selected
		if (frm.doc.plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.plate_no, [
				"name",
				"make",
				"model",
				"serial_number",
				"equipment_category"
			]).then(r => {
				if (r) {
					// Set equipment_type to Asset Category
					if (r.equipment_category) {
						frm.set_value("equipment_type", r.equipment_category);
					}
					if (r.make) {
						frm.set_value("make", r.make);
					}
					if (r.model) {
						frm.set_value("model", r.model);
					}
					if (r.serial_number) {
						frm.set_value("serial_no", r.serial_number);
					}
				}
			});
		}
	},
	
	tyre_request_form(frm) {
		if (frm.doc.tyre_request_form && 
			(!frm.doc.old_tyre_items || frm.doc.old_tyre_items.length === 0) &&
			(!frm.doc.new_tyre_items || frm.doc.new_tyre_items.length === 0)) {
			frm.trigger("load_from_request_form");
		}
	},
	
	tyre_issue_return_form(frm) {
		if (frm.doc.tyre_issue_return_form && 
			(!frm.doc.old_tyre_items || frm.doc.old_tyre_items.length === 0) &&
			(!frm.doc.new_tyre_items || frm.doc.new_tyre_items.length === 0)) {
			frm.trigger("load_from_issue_return_form");
		}
	},
	
	load_from_request_form(frm) {
		if (!frm.doc.tyre_request_form) return;
		
		frappe.db.get_doc("Tyre Request and Analysis Form", frm.doc.tyre_request_form)
			.then(doc => {
				// Copy equipment information
				if (doc.equipment_type) {
					frm.set_value("equipment_type", doc.equipment_type);
				}
				frm.set_value("make", doc.make);
				frm.set_value("model", doc.model);
				frm.set_value("serial_no", doc.serial_no);
				frm.set_value("plate_no", doc.plate_no);
				
				// Copy old tyre items
				if (doc.old_tyre_items && doc.old_tyre_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.old_tyre_items.forEach(function(item) {
						let trd_old_item = frappe.model.add_child(frm.doc, "Tyre Recording Old Item", "old_tyre_items");
						
						let position_key = item.tyre_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.old_tyre_items.length > 0 ? 
								Math.max(...frm.doc.old_tyre_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						trd_old_item.reference_no = `Ref-${ref_counter}`;
						trd_old_item.item_no = item_counter;
						item_counter += 1;
						
						trd_old_item.tyre_brand = item.tyre_brand;
						trd_old_item.tyre_position = item.tyre_position;
						trd_old_item.serial_no = item.serial_no;
						trd_old_item.tyre_size = item.tyre_size;
						trd_old_item.tyre_type = item.tyre_type;
						trd_old_item.quantity = item.quantity;
						trd_old_item.fitted_km_reading = item.fitted_km_reading;
						trd_old_item.fitted_date = item.fitted_date;
						trd_old_item.unit_price = item.unit_price;
					});
					frm.refresh_field("old_tyre_items");
				}
				
				// Copy new tyre items (from requested items)
				if (doc.requested_items && doc.requested_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.requested_items.forEach(function(item) {
						let trd_new_item = frappe.model.add_child(frm.doc, "Tyre Recording New Item", "new_tyre_items");
						
						let position_key = item.requested_tyre_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.new_tyre_items.length > 0 ? 
								Math.max(...frm.doc.new_tyre_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						trd_new_item.reference_no = `Ref-${ref_counter}`;
						trd_new_item.item_no = item_counter;
						item_counter += 1;
						
						trd_new_item.tyre_position = item.requested_tyre_position;
						trd_new_item.tyre_size = item.requested_tyre_size;
						trd_new_item.tyre_brand = item.requested_tyre_brand;
						trd_new_item.tyre_type = item.requested_tyre_type;
						trd_new_item.quantity = item.quantity || 1;
					});
					frm.refresh_field("new_tyre_items");
				}
				
				// Copy analysis items
				if (doc.analysis_items && doc.analysis_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.analysis_items.forEach(function(item) {
						let trd_analysis_item = frappe.model.add_child(frm.doc, "Tyre Recording Analysis Item", "analysis_items");
						
						let position_key = item.tyre_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.analysis_items.length > 0 ? 
								Math.max(...frm.doc.analysis_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						trd_analysis_item.reference_no = `Ref-${ref_counter}`;
						trd_analysis_item.item_no = item_counter;
						item_counter += 1;
						
						trd_analysis_item.tyre_position = item.tyre_position;
						trd_analysis_item.tyre_size = item.tyre_size;
						trd_analysis_item.tyre_brand = item.tyre_brand;
						trd_analysis_item.tyre_type = item.tyre_type;
						trd_analysis_item.old_fitted_km_reading = item.fitted_km_reading;
						trd_analysis_item.standard_life_time = item.standard_life_time;
						trd_analysis_item.actual_coverage = item.actual_coverage;
						trd_analysis_item.deviation = item.deviation;
						trd_analysis_item.reason_for_less_consumption = item.reason_for_less_consumption;
					});
					frm.refresh_field("analysis_items");
				}
			});
	},
	
	load_from_issue_return_form(frm) {
		if (!frm.doc.tyre_issue_return_form) return;
		
		frappe.db.get_doc("Tyre Issue and Return Report Form", frm.doc.tyre_issue_return_form)
			.then(doc => {
				// Copy equipment information
				if (doc.equipment_type) {
					frm.set_value("equipment_type", doc.equipment_type);
				}
				frm.set_value("make", doc.make);
				frm.set_value("model", doc.model);
				frm.set_value("serial_no", doc.serial_no);
				frm.set_value("plate_no", doc.plate_no);
				
				// Copy old tyre items
				if (doc.tyre_items && doc.tyre_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.tyre_items.forEach(function(item) {
						let trd_old_item = frappe.model.add_child(frm.doc, "Tyre Recording Old Item", "old_tyre_items");
						
						let position_key = item.old_tyre_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.old_tyre_items.length > 0 ? 
								Math.max(...frm.doc.old_tyre_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						trd_old_item.reference_no = `Ref-${ref_counter}`;
						trd_old_item.item_no = item_counter;
						item_counter += 1;
						
						trd_old_item.tyre_brand = item.old_tyre_brand;
						trd_old_item.tyre_position = item.old_tyre_position;
						trd_old_item.serial_no = item.old_serial_no;
						trd_old_item.tyre_size = item.old_tyre_size;
						trd_old_item.tyre_type = item.old_tyre_type;
						trd_old_item.quantity = 1;
						trd_old_item.fitted_km_reading = item.old_fitted_km_reading;
						trd_old_item.fitted_date = item.old_fitted_date;
						trd_old_item.unit_price = item.old_unit_price;
						
						// Return details
						trd_old_item.return_project = doc.project;
						trd_old_item.return_store_voucher_no = doc.tyre_return_voucher;
						trd_old_item.return_date = doc.effective_date;
					});
					frm.refresh_field("old_tyre_items");
				}
				
				// Copy new tyre items
				if (doc.tyre_items && doc.tyre_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.tyre_items.forEach(function(item) {
						let trd_new_item = frappe.model.add_child(frm.doc, "Tyre Recording New Item", "new_tyre_items");
						
						let position_key = item.new_tyre_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.new_tyre_items.length > 0 ? 
								Math.max(...frm.doc.new_tyre_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						trd_new_item.reference_no = `Ref-${ref_counter}`;
						trd_new_item.item_no = item_counter;
						item_counter += 1;
						
						trd_new_item.tyre_brand = item.new_tyre_brand;
						trd_new_item.tyre_position = item.new_tyre_position;
						trd_new_item.serial_no = item.new_serial_no;
						trd_new_item.tyre_size = item.new_tyre_size;
						trd_new_item.tyre_type = item.new_tyre_type;
						trd_new_item.quantity = 1;
						trd_new_item.fitted_km_reading = item.new_fitted_km_reading;
						trd_new_item.fitted_date = item.new_fitted_date;
						trd_new_item.unit_price = item.new_unit_price;
						
						// Issue details
						trd_new_item.issue_project = doc.project;
						trd_new_item.issue_siv_no = doc.siv_no;
						trd_new_item.issue_date = doc.effective_date;
					});
					frm.refresh_field("new_tyre_items");
				}
				
				// Copy analysis items
				if (doc.tyre_items && doc.tyre_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.tyre_items.forEach(function(item) {
						let trd_analysis_item = frappe.model.add_child(frm.doc, "Tyre Recording Analysis Item", "analysis_items");
						
						let position_key = item.new_tyre_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.analysis_items.length > 0 ? 
								Math.max(...frm.doc.analysis_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						trd_analysis_item.reference_no = `Ref-${ref_counter}`;
						trd_analysis_item.item_no = item_counter;
						item_counter += 1;
						
						trd_analysis_item.tyre_position = item.new_tyre_position;
						trd_analysis_item.tyre_size = item.new_tyre_size;
						trd_analysis_item.tyre_brand = item.new_tyre_brand;
						trd_analysis_item.tyre_type = item.new_tyre_type;
						trd_analysis_item.old_fitted_km_reading = item.old_fitted_km_reading;
						trd_analysis_item.new_fitted_km_reading = item.new_fitted_km_reading;
						trd_analysis_item.actual_coverage = item.actual_coverage;
						trd_analysis_item.standard_life_time = item.standard_life_time;
						trd_analysis_item.deviation = item.deviation;
						trd_analysis_item.reason_for_less_consumption = item.reason_for_less_consumption;
					});
					frm.refresh_field("analysis_items");
				}
			});
	}
});

// Handle child table calculations for Analysis Items
frappe.ui.form.on("Tyre Recording Analysis Item", {
	new_fitted_km_reading(frm, cdt, cdn) {
		calculate_tyre_analysis(frm, cdt, cdn);
	},
	
	old_fitted_km_reading(frm, cdt, cdn) {
		calculate_tyre_analysis(frm, cdt, cdn);
	},
	
	standard_life_time(frm, cdt, cdn) {
		calculate_tyre_analysis(frm, cdt, cdn);
	},
	
	analysis_items_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Auto-set reference number if not set
		if (!row.reference_no) {
			// Get the last reference number or start with Ref-1
			let existing_refs = [];
			if (frm.doc.analysis_items && frm.doc.analysis_items.length > 0) {
				frm.doc.analysis_items.forEach(item => {
					if (item.reference_no && !existing_refs.includes(item.reference_no)) {
						existing_refs.push(item.reference_no);
					}
				});
			}
			let ref_no = `Ref-${existing_refs.length + 1}`;
			frappe.model.set_value(cdt, cdn, "reference_no", ref_no);
		}
		
		// Auto-set item number
		if (!row.item_no) {
			// Count items with same reference number
			let same_ref_items = frm.doc.analysis_items.filter(item => 
				item.reference_no === row.reference_no && item.name !== row.name
			);
			frappe.model.set_value(cdt, cdn, "item_no", same_ref_items.length + 1);
		}
	}
});

function calculate_tyre_analysis(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	// Calculate actual coverage (b) = New Fitted Reading - Old Fitted Reading
	if (row.new_fitted_km_reading && row.old_fitted_km_reading) {
		let actual_coverage = row.new_fitted_km_reading - row.old_fitted_km_reading;
		frappe.model.set_value(cdt, cdn, "actual_coverage", actual_coverage);
		
		// Calculate deviation (c) = b - a
		if (row.standard_life_time) {
			let deviation = actual_coverage - row.standard_life_time;
			frappe.model.set_value(cdt, cdn, "deviation", deviation);
		}
	} else {
		frappe.model.set_value(cdt, cdn, "actual_coverage", 0);
		frappe.model.set_value(cdt, cdn, "deviation", 0);
	}
}
