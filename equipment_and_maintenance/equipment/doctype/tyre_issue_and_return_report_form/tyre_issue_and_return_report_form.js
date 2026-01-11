// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Issue and Return Report Form", {
	refresh(frm) {
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
		
		// Add button to create Tyre Recording Database entry
		if (!frm.is_new() && frm.doc.tyre_items && frm.doc.tyre_items.length > 0) {
			frm.add_custom_button(
				__("Tyre Recording Database"),
				function() {
					frm.trigger("make_recording_database");
				},
				__("Create")
			);
		}
		
		// Load data from Tyre Request Form if linked
		if (frm.doc.tyre_request_form && (!frm.doc.tyre_items || frm.doc.tyre_items.length === 0)) {
			frm.trigger("load_from_request_form");
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
	
	tyre_request_form(frm) {
		if (frm.doc.tyre_request_form) {
			frm.trigger("load_from_request_form");
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
				frm.set_value("project", doc.project);
				
				// Copy old tyre details from old_tyre_items
				if (doc.old_tyre_items && doc.old_tyre_items.length > 0) {
					doc.old_tyre_items.forEach(function(item, index) {
						let tir_item = frappe.model.add_child(frm.doc, "Tyre Issue Return Item", "tyre_items");
						tir_item.item_no = index + 1;
						
						// Old tyre details
						tir_item.old_tyre_brand = item.tyre_brand;
						tir_item.old_tyre_position = item.tyre_position;
						tir_item.old_serial_no = item.serial_no;
						tir_item.old_tyre_size = item.tyre_size;
						tir_item.old_tyre_type = item.tyre_type;
						tir_item.old_fitted_km_reading = item.fitted_km_reading;
						tir_item.old_fitted_date = item.fitted_date;
						tir_item.old_unit_price = item.unit_price;
						
						// Analysis data from analysis_items
						if (doc.analysis_items && doc.analysis_items.length > index) {
							let analysis_item = doc.analysis_items[index];
							tir_item.actual_coverage = analysis_item.actual_coverage;
							tir_item.standard_life_time = analysis_item.standard_life_time;
							tir_item.deviation = analysis_item.deviation;
							tir_item.reason_for_less_consumption = analysis_item.reason_for_less_consumption;
						}
					});
					frm.refresh_field("tyre_items");
				}
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
					// Set operator/driver name in tyre items if not set
					if (r.operators_name && frm.doc.tyre_items && frm.doc.tyre_items.length > 0) {
						frm.doc.tyre_items.forEach(function(item) {
							if (!item.operator_driver_name) {
								frappe.model.set_value(item.doctype, item.name, "operator_driver_name", r.operators_name);
							}
						});
						frm.refresh_field("tyre_items");
					}
				}
			});
		}
	},
	
	make_recording_database(frm) {
		if (!frm.doc.tyre_items || frm.doc.tyre_items.length === 0) {
			frappe.msgprint(__("No tyre items found. Please add tyre items first."));
			return;
		}
		
		// Check if recording database already exists for this equipment
		frappe.db.get_value("Tyre Recording Database Form", {
			"plate_no": frm.doc.plate_no
		}, "name").then(r => {
			let trd_doc;
			if (r && r.name) {
				// Open existing document
				frappe.set_route("Form", "Tyre Recording Database Form", r.name);
			} else {
				// Create new document
				trd_doc = frappe.model.get_new_doc("Tyre Recording Database Form");
				trd_doc.effective_date = frappe.datetime.get_today();
				trd_doc.issue_no = frm.doc.issue_no || 1;
				
				// Copy equipment information
				trd_doc.equipment_type = frm.doc.equipment_type;
				trd_doc.make = frm.doc.make;
				trd_doc.model = frm.doc.model;
				trd_doc.serial_no = frm.doc.serial_no;
				trd_doc.plate_no = frm.doc.plate_no;
				
				// Generate reference number
				let ref_no = "Ref-1";
				
				// Copy tyre items
				frm.doc.tyre_items.forEach(function(item, index) {
					// Old tyre item
					let trd_old_item = frappe.model.add_child(trd_doc, "Tyre Recording Old Item", "old_tyre_items");
					trd_old_item.reference_no = ref_no;
					trd_old_item.item_no = index + 1;
					
					trd_old_item.tyre_brand = item.old_tyre_brand;
					trd_old_item.tyre_position = item.old_tyre_position;
					trd_old_item.serial_no = item.old_serial_no;
					trd_old_item.tyre_size = item.old_tyre_size;
					trd_old_item.tyre_type = item.old_tyre_type;
					trd_old_item.fitted_km_reading = item.old_fitted_km_reading;
					trd_old_item.fitted_date = item.old_fitted_date;
					trd_old_item.unit_price = item.old_unit_price;
					
					// Old tyre return details
					trd_old_item.return_project = frm.doc.project;
					trd_old_item.return_store_voucher_no = frm.doc.tyre_return_voucher;
					trd_old_item.return_date = frm.doc.effective_date;
					trd_old_item.return_by_operator = item.operator_driver_name || "";
					
					// New tyre item
					let trd_new_item = frappe.model.add_child(trd_doc, "Tyre Recording New Item", "new_tyre_items");
					trd_new_item.reference_no = ref_no;
					trd_new_item.item_no = index + 1;
					
					trd_new_item.tyre_brand = item.new_tyre_brand;
					trd_new_item.tyre_position = item.new_tyre_position;
					trd_new_item.serial_no = item.new_serial_no;
					trd_new_item.tyre_size = item.new_tyre_size;
					trd_new_item.tyre_type = item.new_tyre_type;
					trd_new_item.fitted_km_reading = item.new_fitted_km_reading;
					trd_new_item.fitted_date = item.new_fitted_date;
					trd_new_item.unit_price = item.new_unit_price;
					
					// New tyre issue details
					trd_new_item.issue_project = frm.doc.project;
					trd_new_item.issue_siv_no = frm.doc.siv_no;
					trd_new_item.issue_date = frm.doc.effective_date;
					trd_new_item.issue_by_operator = item.operator_driver_name || "";
					
					// Analysis item
					let trd_analysis_item = frappe.model.add_child(trd_doc, "Tyre Recording Analysis Item", "analysis_items");
					trd_analysis_item.reference_no = ref_no;
					trd_analysis_item.item_no = index + 1;
					
					trd_analysis_item.tyre_position = item.old_tyre_position;
					trd_analysis_item.tyre_size = item.old_tyre_size;
					trd_analysis_item.tyre_brand = item.old_tyre_brand;
					trd_analysis_item.tyre_type = item.old_tyre_type;
					trd_analysis_item.old_fitted_km_reading = item.old_fitted_km_reading;
					trd_analysis_item.new_fitted_km_reading = item.new_fitted_km_reading;
					trd_analysis_item.actual_coverage = item.actual_coverage;
					trd_analysis_item.standard_life_time = item.standard_life_time;
					trd_analysis_item.deviation = item.deviation;
					trd_analysis_item.reason_for_less_consumption = item.reason_for_less_consumption;
				});
				
				// Link to Issue/Return Form
				trd_doc.tyre_issue_return_form = frm.doc.name;
				
				frappe.set_route("Form", "Tyre Recording Database Form", trd_doc.name);
			}
		});
	}
});

// Handle child table calculations
frappe.ui.form.on("Tyre Issue Return Item", {
	new_fitted_km_reading(frm, cdt, cdn) {
		calculate_tyre_analysis(frm, cdt, cdn);
	},
	
	old_fitted_km_reading(frm, cdt, cdn) {
		calculate_tyre_analysis(frm, cdt, cdn);
	},
	
	standard_life_time(frm, cdt, cdn) {
		calculate_tyre_analysis(frm, cdt, cdn);
	},
	
	tyre_items_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.item_no) {
			frappe.model.set_value(cdt, cdn, "item_no", row.idx);
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
