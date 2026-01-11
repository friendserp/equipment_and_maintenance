// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Battery Recording Database Form", {
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
			if (frm.doc.battery_request_form) {
				frm.add_custom_button(
					__("Battery Request Form"),
					function() {
						frappe.set_route("Form", "Battery Request and Analysis Form", frm.doc.battery_request_form);
					},
					__("View")
				);
			}
			
			if (frm.doc.battery_issue_return_form) {
				frm.add_custom_button(
					__("Battery Issue Return Form"),
					function() {
						frappe.set_route("Form", "Battery Issue and Return Report Form", frm.doc.battery_issue_return_form);
					},
					__("View")
				);
			}
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
					
					// Wait a bit to ensure values are set before resolving
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
	
	battery_request_form(frm) {
		if (frm.doc.battery_request_form && 
			(!frm.doc.old_battery_items || frm.doc.old_battery_items.length === 0) &&
			(!frm.doc.new_battery_items || frm.doc.new_battery_items.length === 0)) {
			frm.trigger("load_from_request_form");
		}
	},
	
	battery_issue_return_form(frm) {
		if (frm.doc.battery_issue_return_form && 
			(!frm.doc.old_battery_items || frm.doc.old_battery_items.length === 0) &&
			(!frm.doc.new_battery_items || frm.doc.new_battery_items.length === 0)) {
			frm.trigger("load_from_issue_return_form");
		}
	},
	
	load_from_request_form(frm) {
		if (!frm.doc.battery_request_form) return;
		
		frappe.db.get_doc("Battery Request and Analysis Form", frm.doc.battery_request_form)
			.then(doc => {
				// Copy equipment information
				if (doc.equipment_type) {
					frm.set_value("equipment_type", doc.equipment_type);
				}
				frm.set_value("make", doc.make);
				frm.set_value("model", doc.model);
				frm.set_value("serial_no", doc.serial_no);
				frm.set_value("plate_no", doc.plate_no);
				
				// Copy old battery items
				if (doc.old_battery_items && doc.old_battery_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.old_battery_items.forEach(function(item) {
						let brd_old_item = frappe.model.add_child(frm.doc, "Battery Recording Old Item", "old_battery_items");
						
						let position_key = item.battery_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.old_battery_items.length > 0 ? 
								Math.max(...frm.doc.old_battery_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						brd_old_item.reference_no = `Ref-${ref_counter}`;
						brd_old_item.item_no = item_counter;
						item_counter += 1;
						
						brd_old_item.battery_make = item.battery_make;
						brd_old_item.battery_position = item.battery_position;
						brd_old_item.serial_no = item.serial_no;
						brd_old_item.battery_voltage = item.battery_voltage;
						brd_old_item.battery_amper = item.battery_amper;
						brd_old_item.quantity = item.quantity;
						brd_old_item.fitted_hr_reading = item.fitted_hr_reading;
						brd_old_item.fitted_date = item.fitted_date;
						brd_old_item.unit_price = item.unit_price;
					});
					frm.refresh_field("old_battery_items");
				}
				
				// Copy new battery items (from requested items)
				if (doc.requested_items && doc.requested_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.requested_items.forEach(function(item) {
						let brd_new_item = frappe.model.add_child(frm.doc, "Battery Recording New Item", "new_battery_items");
						
						let position_key = item.requested_battery_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.new_battery_items.length > 0 ? 
								Math.max(...frm.doc.new_battery_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						brd_new_item.reference_no = `Ref-${ref_counter}`;
						brd_new_item.item_no = item_counter;
						item_counter += 1;
						
						brd_new_item.battery_position = item.requested_battery_position;
						brd_new_item.battery_voltage = item.requested_battery_voltage;
						brd_new_item.battery_amper = item.requested_battery_amper;
						brd_new_item.quantity = item.quantity || 1;
					});
					frm.refresh_field("new_battery_items");
				}
				
				// Copy analysis items
				if (doc.analysis_items && doc.analysis_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.analysis_items.forEach(function(item) {
						let brd_analysis_item = frappe.model.add_child(frm.doc, "Battery Recording Analysis Item", "analysis_items");
						
						let position_key = item.battery_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.analysis_items.length > 0 ? 
								Math.max(...frm.doc.analysis_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						brd_analysis_item.reference_no = `Ref-${ref_counter}`;
						brd_analysis_item.item_no = item_counter;
						item_counter += 1;
						
						brd_analysis_item.battery_position = item.battery_position;
						brd_analysis_item.battery_voltage = item.battery_voltage;
						brd_analysis_item.battery_amper = item.battery_amper;
						brd_analysis_item.old_fitted_hr_reading = item.fitted_hr_reading;
						brd_analysis_item.standard_life_time = item.standard_life_time;
						brd_analysis_item.actual_coverage = item.actual_coverage;
						brd_analysis_item.deviation = item.deviation;
						brd_analysis_item.reason_for_less_consumption = item.reason_for_less_consumption;
					});
					frm.refresh_field("analysis_items");
				}
			});
	},
	
	load_from_issue_return_form(frm) {
		if (!frm.doc.battery_issue_return_form) return;
		
		frappe.db.get_doc("Battery Issue and Return Report Form", frm.doc.battery_issue_return_form)
			.then(doc => {
				// Copy equipment information
				if (doc.equipment_type) {
					frm.set_value("equipment_type", doc.equipment_type);
				}
				frm.set_value("make", doc.make);
				frm.set_value("model", doc.model);
				frm.set_value("serial_no", doc.serial_no);
				frm.set_value("plate_no", doc.plate_no);
				
				// Copy old battery items
				if (doc.battery_items && doc.battery_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.battery_items.forEach(function(item) {
						let brd_old_item = frappe.model.add_child(frm.doc, "Battery Recording Old Item", "old_battery_items");
						
						let position_key = item.old_battery_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.old_battery_items.length > 0 ? 
								Math.max(...frm.doc.old_battery_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						brd_old_item.reference_no = `Ref-${ref_counter}`;
						brd_old_item.item_no = item_counter;
						item_counter += 1;
						
						brd_old_item.battery_make = item.old_battery_make;
						brd_old_item.battery_position = item.old_battery_position;
						brd_old_item.serial_no = item.old_serial_no;
						brd_old_item.battery_voltage = item.old_battery_voltage;
						brd_old_item.battery_amper = item.old_battery_amper;
						brd_old_item.quantity = 1;
						brd_old_item.fitted_hr_reading = item.old_fitted_hr_reading;
						brd_old_item.fitted_date = item.old_fitted_date;
						brd_old_item.unit_price = item.old_unit_price;
						
						// Return details
						brd_old_item.return_project = doc.project;
						brd_old_item.return_store_voucher_no = doc.battery_return_voucher;
						brd_old_item.return_date = doc.effective_date;
					});
					frm.refresh_field("old_battery_items");
				}
				
				// Copy new battery items
				if (doc.battery_items && doc.battery_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.battery_items.forEach(function(item) {
						let brd_new_item = frappe.model.add_child(frm.doc, "Battery Recording New Item", "new_battery_items");
						
						let position_key = item.new_battery_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.new_battery_items.length > 0 ? 
								Math.max(...frm.doc.new_battery_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						brd_new_item.reference_no = `Ref-${ref_counter}`;
						brd_new_item.item_no = item_counter;
						item_counter += 1;
						
						brd_new_item.battery_make = item.new_battery_make;
						brd_new_item.battery_position = item.new_battery_position;
						brd_new_item.serial_no = item.new_serial_no;
						brd_new_item.battery_voltage = item.new_battery_voltage;
						brd_new_item.battery_amper = item.new_battery_amper;
						brd_new_item.quantity = 1;
						brd_new_item.fitted_hr_reading = item.new_fitted_hr_reading;
						brd_new_item.fitted_date = item.new_fitted_date;
						brd_new_item.unit_price = item.new_unit_price;
						
						// Issue details
						brd_new_item.issue_project = doc.project;
						brd_new_item.issue_siv_no = doc.siv_no;
						brd_new_item.issue_date = doc.effective_date;
					});
					frm.refresh_field("new_battery_items");
				}
				
				// Copy analysis items
				if (doc.battery_items && doc.battery_items.length > 0) {
					let ref_counter = 1;
					let current_ref = null;
					let item_counter = 1;
					
					doc.battery_items.forEach(function(item) {
						let brd_analysis_item = frappe.model.add_child(frm.doc, "Battery Recording Analysis Item", "analysis_items");
						
						let position_key = item.new_battery_position || "Default";
						if (current_ref != position_key) {
							current_ref = position_key;
							ref_counter = frm.doc.analysis_items.length > 0 ? 
								Math.max(...frm.doc.analysis_items.map(x => parseInt(x.reference_no.replace("Ref-", "")) || 0)) + 1 : 1;
							item_counter = 1;
						}
						
						brd_analysis_item.reference_no = `Ref-${ref_counter}`;
						brd_analysis_item.item_no = item_counter;
						item_counter += 1;
						
						brd_analysis_item.battery_position = item.new_battery_position;
						brd_analysis_item.battery_voltage = item.new_battery_voltage;
						brd_analysis_item.battery_amper = item.new_battery_amper;
						brd_analysis_item.old_fitted_hr_reading = item.old_fitted_hr_reading;
						brd_analysis_item.new_fitted_hr_reading = item.new_fitted_hr_reading;
						brd_analysis_item.actual_coverage = item.actual_coverage;
						brd_analysis_item.standard_life_time = item.standard_life_time;
						brd_analysis_item.deviation = item.deviation;
						brd_analysis_item.reason_for_less_consumption = item.reason_for_less_consumption;
					});
					frm.refresh_field("analysis_items");
				}
			});
	}
});

// Handle child table calculations for Analysis Items
frappe.ui.form.on("Battery Recording Analysis Item", {
	new_fitted_hr_reading(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	old_fitted_hr_reading(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	standard_life_time(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
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

function calculate_battery_analysis(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	// Calculate actual coverage (b) = New Fitted Reading - Old Fitted Reading
	if (row.new_fitted_hr_reading && row.old_fitted_hr_reading) {
		let actual_coverage = row.new_fitted_hr_reading - row.old_fitted_hr_reading;
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

