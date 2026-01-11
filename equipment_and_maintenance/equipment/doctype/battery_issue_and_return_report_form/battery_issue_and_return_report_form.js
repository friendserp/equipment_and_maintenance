// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Battery Issue and Return Report Form", {
	refresh(frm) {
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
		
		// Add button to create Battery Recording Database entry
		if (!frm.is_new() && frm.doc.battery_items && frm.doc.battery_items.length > 0) {
			frm.add_custom_button(
				__("Battery Recording Database"),
				function() {
					frm.trigger("make_recording_database");
				},
				__("Create")
			);
		}
		
		// Load data from Battery Request Form if linked
		if (frm.doc.battery_request_form && (!frm.doc.battery_items || frm.doc.battery_items.length === 0)) {
			frm.trigger("load_from_request_form");
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
	
	battery_request_form(frm) {
		if (frm.doc.battery_request_form) {
			frm.trigger("load_from_request_form");
		}
	},
	
	load_from_request_form(frm) {
		if (!frm.doc.battery_request_form) return;
		
		frappe.db.get_doc("Battery Request and Analysis Form", frm.doc.battery_request_form)
			.then(doc => {
				// Copy equipment information
				// equipment_type is now Asset Category, so copy it directly
				if (doc.equipment_type) {
					frm.set_value("equipment_type", doc.equipment_type);
				}
				frm.set_value("make", doc.make);
				frm.set_value("model", doc.model);
				frm.set_value("serial_no", doc.serial_no);
				frm.set_value("plate_no", doc.plate_no);
				frm.set_value("project", doc.project);
				
				// Copy old battery details
				if (doc.battery_items && doc.battery_items.length > 0) {
					doc.battery_items.forEach(function(item) {
						let bir_item = frappe.model.add_child(frm.doc, "Battery Issue Return Item", "battery_items");
						bir_item.item_no = item.item_no;
						
						// Old battery details
						bir_item.old_battery_make = item.battery_make;
						bir_item.old_battery_position = item.battery_position;
						bir_item.old_serial_no = item.serial_no;
						bir_item.old_battery_voltage = item.battery_voltage;
						bir_item.old_battery_amper = item.battery_amper;
						bir_item.old_fitted_hr_reading = item.fitted_hr_reading;
						bir_item.old_fitted_date = item.fitted_date;
						bir_item.old_unit_price = item.unit_price;
						
						// Analysis data
						bir_item.actual_coverage = item.actual_coverage;
						bir_item.standard_life_time = item.standard_life_time;
						bir_item.deviation = item.deviation;
						bir_item.reason_for_less_consumption = item.reason_for_less_consumption;
					});
					frm.refresh_field("battery_items");
				}
			});
	},
	
	equipment_type(frm) {
		// When Equipment Master is selected, fetch plate number and other details
		if (frm.doc.equipment_type) {
			frappe.db.get_value("Equipment Master", frm.doc.equipment_type, [
				"plate_number",
				"make",
				"model",
				"serial_number",
				"location",
				"operators_name"
			]).then(r => {
				if (r) {
					if (r.plate_number) {
						frm.set_value("plate_no", r.plate_number);
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
					if (r.location) {
						frm.set_value("project", r.location);
					}
					// Set operator/driver name in battery items if not set
					if (r.operators_name && frm.doc.battery_items && frm.doc.battery_items.length > 0) {
						frm.doc.battery_items.forEach(function(item) {
							if (!item.operator_driver_name) {
								frappe.model.set_value(item.doctype, item.name, "operator_driver_name", r.operators_name);
							}
						});
						frm.refresh_field("battery_items");
					}
				}
			});
		}
	},
	
	plate_no(frm) {
		// Fetch equipment details when plate_no is selected
		if (frm.doc.plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.plate_no, [
				"name",
				"make",
				"model",
				"serial_number",
				"location",
				"operators_name",
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
					if (r.location) {
						frm.set_value("project", r.location);
					}
					// Set operator/driver name in battery items if not set
					if (r.operators_name && frm.doc.battery_items && frm.doc.battery_items.length > 0) {
						frm.doc.battery_items.forEach(function(item) {
							if (!item.operator_driver_name) {
								frappe.model.set_value(item.doctype, item.name, "operator_driver_name", r.operators_name);
							}
						});
						frm.refresh_field("battery_items");
					}
				}
			});
		}
	},
	
	make_recording_database(frm) {
		if (!frm.doc.battery_items || frm.doc.battery_items.length === 0) {
			frappe.msgprint(__("No battery items found. Please add battery items first."));
			return;
		}
		
		// Check if recording database already exists for this equipment
		frappe.db.get_value("Battery Recording Database Form", {
			"plate_no": frm.doc.plate_no
		}, "name").then(r => {
			let brd_doc;
			if (r && r.name) {
				// Open existing document
				frappe.set_route("Form", "Battery Recording Database Form", r.name);
			} else {
				// Create new document
				brd_doc = frappe.model.get_new_doc("Battery Recording Database Form");
				brd_doc.effective_date = frappe.datetime.get_today();
				brd_doc.issue_no = frm.doc.issue_no || 1;
				
				// Copy equipment information
				brd_doc.equipment_type = frm.doc.equipment_type;
				brd_doc.make = frm.doc.make;
				brd_doc.model = frm.doc.model;
				brd_doc.serial_no = frm.doc.serial_no;
				brd_doc.plate_no = frm.doc.plate_no;
				
				// Generate reference number
				let ref_no = "Ref-1";
				
				// Copy battery items
				frm.doc.battery_items.forEach(function(item, index) {
					let brd_item = frappe.model.add_child(brd_doc, "Battery Recording Item", "battery_items");
					brd_item.reference_no = ref_no;
					brd_item.item_no = index + 1;
					
					// Old battery details
					brd_item.old_battery_make = item.old_battery_make;
					brd_item.old_battery_position = item.old_battery_position;
					brd_item.old_serial_no = item.old_serial_no;
					brd_item.old_battery_voltage = item.old_battery_voltage;
					brd_item.old_battery_amper = item.old_battery_amper;
					brd_item.old_fitted_hr_reading = item.old_fitted_hr_reading;
					brd_item.old_fitted_date = item.old_fitted_date;
					brd_item.old_unit_price = item.old_unit_price;
					
					// Old battery return details
					brd_item.old_return_project = frm.doc.project;
					brd_item.old_return_store_voucher_no = frm.doc.battery_return_voucher;
					brd_item.old_return_date = frm.doc.effective_date;
					brd_item.old_return_by_operator = item.operator_driver_name || "";
					
					// New battery details
					brd_item.new_battery_make = item.new_battery_make;
					brd_item.new_battery_position = item.new_battery_position;
					brd_item.new_serial_no = item.new_serial_no;
					brd_item.new_battery_voltage = item.new_battery_voltage;
					brd_item.new_battery_amper = item.new_battery_amper;
					brd_item.new_fitted_hr_reading = item.new_fitted_hr_reading;
					brd_item.new_fitted_date = item.new_fitted_date;
					brd_item.new_unit_price = item.new_unit_price;
					
					// New battery issue details
					brd_item.new_issue_project = frm.doc.project;
					brd_item.new_issue_siv_no = frm.doc.siv_no;
					brd_item.new_issue_date = frm.doc.effective_date;
					brd_item.new_issue_by_operator = item.operator_driver_name || "";
					
					// Analysis data
					brd_item.actual_coverage = item.actual_coverage;
					brd_item.standard_life_time = item.standard_life_time;
					brd_item.deviation = item.deviation;
					brd_item.reason_for_less_consumption = item.reason_for_less_consumption;
				});
				
				// Link to Issue/Return Form
				brd_doc.battery_issue_return_form = frm.doc.name;
				
				frappe.set_route("Form", "Battery Recording Database Form", brd_doc.name);
			}
		});
	}
});

// Handle child table calculations
frappe.ui.form.on("Battery Issue Return Item", {
	new_fitted_hr_reading(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	old_fitted_hr_reading(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	standard_life_time(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	battery_items_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.item_no) {
			frappe.model.set_value(cdt, cdn, "item_no", row.idx);
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

