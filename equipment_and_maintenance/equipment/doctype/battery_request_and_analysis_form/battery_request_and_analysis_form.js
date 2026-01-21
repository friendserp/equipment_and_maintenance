// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Battery Request and Analysis Form", {
	refresh(frm) {
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
		
		// Add Material Request button for submitted requests
		if (frm.doc.docstatus === 1) {
			if (frm.doc.material_requisition_no) {
				// Show link to existing Material Request
				frm.add_custom_button(
					__("Material Request"),
					function() {
						frappe.set_route("Form", "Material Request", frm.doc.material_requisition_no);
					},
					__("View")
				);
			} else {
				// Open new Material Request with pre-filled data
				frm.add_custom_button(
					__("Material Request"),
					function() {
						frm.trigger("open_material_request");
					},
					__("Create")
				);
			}
		}
		
		// Add Battery Issue and Return Report button only if Material Request is created
		if (frm.doc.docstatus === 1 && frm.doc.material_requisition_no && !frm.is_new()) {
			frm.add_custom_button(
				__("Battery Issue and Return Report"),
				function() {
					frm.trigger("make_issue_return_report");
				},
				__("Create")
			);
		}
		
	},
	
	open_material_request(frm) {
		if (frm.doc.docstatus !== 1) {
			frappe.msgprint(__("Battery Request must be submitted before creating Material Request."));
			return;
		}
		
		if (!frm.doc.requested_items || frm.doc.requested_items.length === 0) {
			frappe.msgprint(__("No requested items found."));
			return;
		}
		
		// Store Battery Request name in sessionStorage for linking
		sessionStorage.setItem('battery_request_for_mr', frm.doc.name);
		
		// Load both Material Request and Material Request Item doctypes
		frappe.model.with_doctype("Material Request", function() {
			frappe.model.with_doctype("Material Request Item", function() {
				let new_mr = frappe.model.get_new_doc("Material Request");
				
				// Set header fields
				new_mr.material_request_type = "Material Issue";
				new_mr.transaction_date = frappe.datetime.get_today();
				new_mr.schedule_date = frappe.datetime.add_days(frappe.datetime.get_today(), 7);
				if (frm.doc.project) {
					new_mr.custom_project = frm.doc.project;
				}
				
				// Clear default items
				new_mr.items = [];
				
				// Add battery items
				frm.doc.requested_items.forEach(function(req_item) {
					let mr_item = frappe.model.add_child(new_mr, "Material Request Item", "items");
					mr_item.item_code = req_item.requested_item_no;
					mr_item.qty = req_item.quantity || 1;
					mr_item.project = frm.doc.project;
					mr_item.uom = "pcs";
					mr_item.conversion_factor = 1;
					mr_item.description = `Battery - Voltage: ${req_item.requested_battery_voltage || ''}, Amper: ${req_item.requested_battery_amper || ''}, Position: ${req_item.requested_battery_position || ''}`;
				});
				
				// Open the form
				frappe.set_route("Form", "Material Request", new_mr.name);
			});
		});
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
					
					// Populate fields based on the action being taken
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
	
	material_requisition_no(frm) {
		// When Material Request is selected, fetch items and populate requested_items table
		if (frm.doc.material_requisition_no) {
			frm.trigger("fetch_mr_items");
		} else {
			// Clear all tables if MR is cleared
			frm.clear_table("requested_items");
			frm.clear_table("old_battery_items");
			frm.clear_table("analysis_items");
			frm.refresh_field("requested_items");
			frm.refresh_field("old_battery_items");
			frm.refresh_field("analysis_items");
		}
	},
	
	
	fetch_mr_items(frm) {
		if (!frm.doc.material_requisition_no) return;
		
		// Fetch Material Request document
		frappe.db.get_doc("Material Request", frm.doc.material_requisition_no)
			.then(mr_doc => {
				if (!mr_doc || !mr_doc.items || mr_doc.items.length === 0) {
					frappe.msgprint(__("No items found in Material Request."));
					return;
				}
				
				// Fetch project from MR if available
				if (mr_doc.custom_project && !frm.doc.project) {
					frm.set_value("project", mr_doc.custom_project);
				}
				
				// Clear existing items
				frm.clear_table("requested_items");
				frm.clear_table("old_battery_items");
				frm.clear_table("analysis_items");
				
				// Populate requested_items from MR items
				mr_doc.items.forEach(function(mr_item, index) {
					let requested_item = frm.add_child("requested_items");
					
					// Set requested item details from MR
					requested_item.requested_item_no = mr_item.item_code;
					requested_item.quantity = mr_item.qty || 1;
					
					// Parse description if it contains battery details
					if (mr_item.description) {
						let desc = mr_item.description;
						// Try to extract voltage, amper, position from description
						let voltage_match = desc.match(/Voltage:\s*([0-9.]+)/i);
						let amper_match = desc.match(/Amper:\s*([0-9.]+)/i);
						let position_match = desc.match(/Position:\s*(Left|Right)/i);
						
						if (voltage_match) {
							requested_item.requested_battery_voltage = parseFloat(voltage_match[1]);
						}
						if (amper_match) {
							requested_item.requested_battery_amper = parseFloat(amper_match[1]);
						}
						if (position_match) {
							requested_item.requested_battery_position = position_match[1];
						}
					}
				});
				
				frm.refresh_field("requested_items");
				
				console.log("=== MR ITEMS FETCHED ===");
				console.log("Material Request:", frm.doc.material_requisition_no);
				console.log("Plate No:", frm.doc.plate_no);
				console.log("Requested Items Count:", frm.doc.requested_items ? frm.doc.requested_items.length : 0);
				
			})
			.catch(err => {
				frappe.msgprint(__("Error fetching Material Request: " + err.message));
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
				"equipment_category"
			]).then(r => {
				if (r) {
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
				}
				
				// Load existing batteries from Battery Recording Database into old_battery_items
				frm.trigger("load_existing_batteries");
			});
				} else {
			// Clear old batteries and analysis if equipment is cleared
			frm.clear_table("old_battery_items");
			frm.clear_table("analysis_items");
			frm.refresh_field("old_battery_items");
			frm.refresh_field("analysis_items");
		}
	},
	
	current_km_hr(frm) {
		// Recalculate analysis when current_km_hr changes
		if (frm.doc.current_km_hr && frm.doc.old_battery_items && frm.doc.old_battery_items.length > 0) {
			frm.save().then(() => {
				frm.reload_doc();
			});
		}
	},
	
	load_existing_batteries(frm) {
		if (!frm.doc.plate_no) return;
		
		// Fetch the last Issue document for this equipment
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Battery Issue and Return Report Form",
				filters: {
					"plate_no": frm.doc.plate_no,
					"type": "Issue",
					"docstatus": 1
				},
				fields: ["name", "effective_date"],
				order_by: "effective_date DESC, creation DESC",
				limit: 1
			},
			callback: function(issue_res) {
				if (issue_res.message && issue_res.message.length > 0) {
					const last_issue_name = issue_res.message[0].name;
					
					// Fetch the full Issue document to get battery items
					frappe.call({
						method: "frappe.client.get",
						args: {
							doctype: "Battery Issue and Return Report Form",
							name: last_issue_name
						},
						callback: function(issue_doc_res) {
							if (issue_doc_res.message && issue_doc_res.message.battery_items) {
								const battery_items = issue_doc_res.message.battery_items;
								
								// Clear old battery items table
								frm.clear_table("old_battery_items");
								
								if (battery_items && battery_items.length > 0) {
									// Track added battery_recording_database to avoid duplicates
									let added_batteries = new Set();
									
									// Populate old_battery_items table with batteries from last Issue
									// serial_no in Battery Issue Return Item is a Link to Battery Recording Database
									battery_items.forEach(function(battery_item) {
										if (battery_item.serial_no && !added_batteries.has(battery_item.serial_no)) {
											added_batteries.add(battery_item.serial_no);
											
											let old_item = frm.add_child("old_battery_items");
											// serial_no is the Battery Recording Database name
											old_item.battery_recording_database = battery_item.serial_no;
											// Other fields will be fetched via fetch_from in Battery Old Item
											old_item.battery_position = battery_item.battery_position || '';
											old_item.battery_voltage = battery_item.battery_voltage || '';
											old_item.battery_amper = battery_item.battery_amper || '';
											old_item.fitted_date = battery_item.fitted_date || '';
											old_item.fitted_hr_reading = battery_item.fitted_hr_reading || '';
											old_item.quantity = 1;
										}
									});
									
									frm.refresh_field("old_battery_items");
									
									// Trigger analysis calculation after loading old batteries
									if (frm.doc.old_battery_items && frm.doc.old_battery_items.length > 0) {
										// Save and reload to trigger Python calculation
										frm.save().then(function() {
											frm.reload_doc();
										});
									}
								} else {
									frm.refresh_field("old_battery_items");
								}
							} else {
								frm.clear_table("old_battery_items");
								frm.refresh_field("old_battery_items");
							}
						}
					});
				} else {
					// No previous Issue found, clear old batteries
					frm.clear_table("old_battery_items");
					frm.refresh_field("old_battery_items");
				}
			}
		});
	},
	
	old_battery_items(frm) {
		// When old batteries are selected, calculate analysis
		if (frm.doc.old_battery_items && frm.doc.old_battery_items.length > 0) {
			// Trigger save to recalculate analysis items in Python
			frm.save().then(() => {
				frm.reload_doc();
			});
		} else {
			// Clear analysis if old batteries are cleared
			frm.clear_table("analysis_items");
			frm.refresh_field("analysis_items");
		}
	},
	
	calculate_analysis_from_database_batteries(frm) {
		// Trigger validation to recalculate analysis items
		frm.save().then(() => {
			frm.reload_doc();
		});
	},
	
	make_issue_return_report(frm) {
		if (!frm.doc.material_requisition_no) {
			frappe.msgprint(__("Please create Material Request first before creating Issue and Return document."));
			return;
		}
		
		// Load both parent and child doctypes before creating
		frappe.model.with_doctype("Battery Issue and Return Report Form", function() {
			frappe.model.with_doctype("Battery Issue Return Item", function() {
				let bir_doc = frappe.model.get_new_doc("Battery Issue and Return Report Form");
				bir_doc.type = "Issue";
				bir_doc.effective_date = frappe.datetime.get_today();
				bir_doc.battery_request_form = frm.doc.name;
				bir_doc.material_request = frm.doc.material_requisition_no;
				
				// Copy equipment information
				bir_doc.equipment_type = frm.doc.equipment_type;
				bir_doc.make = frm.doc.make;
				bir_doc.model = frm.doc.model;
				bir_doc.serial_no = frm.doc.serial_no;
				bir_doc.plate_no = frm.doc.plate_no;
				bir_doc.project = frm.doc.project;
				
				// Open the form - user will use "Get Items From" button to populate items
				frappe.set_route("Form", "Battery Issue and Return Report Form", bir_doc.name);
			});
		});
	}
});


// Handle Battery Recording Database filter in Battery Request Item
frappe.ui.form.on("Battery Request Item", {
	battery_recording_database(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.battery_recording_database) return;
		
		// Set query to filter Battery Recording Database by equipment
		frm.set_query("battery_recording_database", "requested_items", function(doc, cdt, cdn) {
			let filters = {
				"battery_status": "Available"
			};
			if (doc.plate_no) {
				// Allow batteries that are available OR fitted to this equipment
				// This will be handled by the query function
			}
			return {
				filters: filters,
				query: "equipment_and_maintenance.equipment.doctype.battery_request_item.battery_request_item.filter_available_batteries"
			};
		});
	}
});

// Handle child table calculations for Analysis Items
frappe.ui.form.on("Battery Analysis Item", {
	current_km_hour_reading(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	fitted_hr_reading(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
	standard_life_time(frm, cdt, cdn) {
		calculate_battery_analysis(frm, cdt, cdn);
	},
	
});

function calculate_battery_analysis(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	// Calculate actual coverage (b) = Current Reading - Fitted Reading
	if (row.current_km_hour_reading && row.fitted_hr_reading) {
		let actual_coverage = row.current_km_hour_reading - row.fitted_hr_reading;
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


