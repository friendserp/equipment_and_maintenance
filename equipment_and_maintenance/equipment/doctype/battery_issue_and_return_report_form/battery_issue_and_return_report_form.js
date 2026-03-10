// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Battery Issue and Return Report Form", {
	onload(frm) {
		// Ensure child table doctype is loaded
		frappe.model.with_doctype("Battery Issue Return Item", function() {
			// Child table doctype is now loaded
		});
	},
	
	refresh(frm) {
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
		
		// Add Get Items From button (standalone, not in Actions menu)
		if ((frm.is_new() || frm.doc.docstatus === 0) && frm.doc.type) {
			frm.add_custom_button(
				__("Get Items From"),
				function() {
					frm.trigger("get_items_from");
				}
			);
		}
		
		// Show/hide fields based on Type
		frm.trigger("toggle_fields_by_type");
	},
	
	type(frm) {
		frm.trigger("toggle_fields_by_type");
		if (frm.doc.type) {
			frm.clear_table("battery_items");
			frm.refresh_field("battery_items");
		}
	},
	
	toggle_fields_by_type(frm) {
		if (!frm.doc.type) return;
		
		// Show/hide fields based on Issue or Return type
		if (frm.doc.type === "Issue") {
			// For Issue: Show plate_no, hide return voucher and current_km_hr
			frm.set_df_property("plate_no", "reqd", 1);
			frm.set_df_property("battery_return_voucher", "hidden", 1);
			frm.set_df_property("current_km_hr", "hidden", 1);
			frm.set_df_property("current_km_hr", "reqd", 0);
		} else if (frm.doc.type === "Return") {
			// For Return: Show return voucher and current_km_hr, plate_no still required
			frm.set_df_property("plate_no", "reqd", 1);
			frm.set_df_property("battery_return_voucher", "hidden", 0);
			frm.set_df_property("current_km_hr", "hidden", 0);
			frm.set_df_property("current_km_hr", "reqd", 1);
		}
	},
	
	get_items_from(frm) {
		
		if (!frm.doc.type) {
			frappe.msgprint(__("Please select Type (Issue or Return) first."));
			return;
		}
		
		// First dialog: Select source and document
		let source_dialog = new frappe.ui.Dialog({
			title: __("Get Items From"),
			fields: [
				{
					fieldtype: "Select",
					fieldname: "source",
					label: __("Source"),
					options: frm.doc.type === "Issue" ? "Battery Request\nMaterial Request" : "Battery Request\nPrevious Issue",
					default: "Battery Request",
					reqd: 1
				},
				{
					fieldtype: "Link",
					fieldname: "battery_request",
					label: __("Battery Request"),
					options: "Battery Request and Analysis Form",
					depends_on: "eval:doc.source == 'Battery Request'",
					get_query: function() {
						return {
							filters: {
								"docstatus": 1
							}
						};
					}
				},
				{
					fieldtype: "Link",
					fieldname: "material_request",
					label: __("Material Request"),
					options: "Material Request",
					depends_on: "eval:doc.source == 'Material Request'",
					get_query: function() {
						return {
							filters: {
								"docstatus": 1,
								"material_request_type": "Purchase"
							}
						};
					}
				},
				{
					fieldtype: "Link",
					fieldname: "previous_issue",
					label: __("Previous Issue"),
					options: "Battery Issue and Return Report Form",
					depends_on: "eval:doc.source == 'Previous Issue'",
					get_query: function() {
						return {
							filters: {
								"docstatus": 1,
								"type": "Issue"
							}
						};
					}
				}
			],
			primary_action_label: __("Next"),
			primary_action: function(values) {
				source_dialog.hide();
				
				// Call the functions directly from frm.events
				if (values.source === "Battery Request" && values.battery_request) {
					if (frm.events && typeof frm.events.fetch_battery_request_items === 'function') {
						frm.events.fetch_battery_request_items(frm, values.battery_request);
					}
				} else if (values.source === "Material Request" && values.material_request) {
					if (frm.events && typeof frm.events.fetch_material_request_items === 'function') {
						frm.events.fetch_material_request_items(frm, values.material_request);
					}
				} else if (values.source === "Previous Issue" && values.previous_issue) {
					if (frm.events && typeof frm.events.fetch_previous_issue_items === 'function') {
						frm.events.fetch_previous_issue_items(frm, values.previous_issue);
					}
				}
			}
		});
		source_dialog.show();
	},
	
	
	fetch_battery_request_items(frm, request_name) {
		// First get the main document
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Battery Request and Analysis Form",
				name: request_name
			},
			callback: function(r) {
				
				if (r.message) {
					let doc = r.message;
					let items_to_show = [];
					
					if (frm.doc.type === "Issue") {
						// Fetch child table using server-side method to ensure all fields are included
						frappe.call({
							method: "equipment_and_maintenance.equipment.doctype.battery_issue_and_return_report_form.battery_issue_and_return_report_form.get_battery_request_items",
							args: {
								request_name: request_name
							},
							callback: function(items_res) {
								let requested_items = items_res.message || [];
								
								if (requested_items.length > 0) {
									// Build items list based on quantity - if quantity is 2 or 3, add multiple rows
									requested_items.forEach(function(req_item) {
										let quantity = req_item.quantity || 1;
										for (let i = 0; i < quantity; i++) {
											items_to_show.push({
												item_code: req_item.requested_item_no,
												voltage: req_item.requested_battery_voltage,
												amper: req_item.requested_battery_amper,
												position: req_item.requested_battery_position,
												battery_recording_database: null,
												serial_no: null
											});
										}
									});
									
									// Add items to form
									if (items_to_show.length > 0 && frm.events && typeof frm.events.add_items_to_form === 'function') {
										frm.events.add_items_to_form(frm, items_to_show, request_name, doc);
									} else {
										frappe.msgprint(__("No requested items found in this Battery Request."));
									}
								} else {
									frappe.msgprint(__("No requested items found in this Battery Request."));
								}
							}
						});
					} else if (frm.doc.type === "Return") {
						frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "Battery Old Item",
								filters: {
									"parent": request_name,
									"parenttype": "Battery Request and Analysis Form"
								},
								fields: ["battery_recording_database", "fitted_hr_reading", "fitted_date"]
							},
							callback: function(old_res) {
								if (old_res.message && old_res.message.length > 0) {
									// Fetch Battery Recording Database details for each old battery
									// Use serial_no as it's the link field to Battery Recording Database
									let promises = old_res.message.map(function(old_item) {
										// Check for serial_no first, then battery_recording_database for backward compatibility
										const battery_db_name = old_item.serial_no || old_item.battery_recording_database;
										if (!battery_db_name) {
											return Promise.resolve(null);
										}
										return frappe.call({
											method: "frappe.client.get_value",
											args: {
												doctype: "Battery Recording Database",
												fieldname: ["battery_serial_no", "item_code", "battery_voltage", "battery_amper", "battery_position"],
												filters: { name: battery_db_name }
											}
										}).then(function(brd_res) {
											if (brd_res.message) {
												return {
													serial_no: battery_db_name, // Use serial_no as the link field
													item_code: brd_res.message.item_code || '',
													voltage: brd_res.message.battery_voltage || '',
													amper: brd_res.message.battery_amper || '',
													position: brd_res.message.battery_position || '',
													fitted_hr_reading: old_item.fitted_hr_reading,
													fitted_date: old_item.fitted_date
												};
											}
											return null;
										});
									});
									Promise.all(promises).then(function(results) {
										items_to_show = results.filter(function(item) { return item !== null; });
										
										if (items_to_show.length > 0 && frm.events && typeof frm.events.add_items_to_form === 'function') {
											frm.events.add_items_to_form(frm, items_to_show, request_name, doc);
										} else {
											frappe.msgprint(__("No old batteries found in this Battery Request."));
										}
									}).catch(function(error) {
										frappe.msgprint(__("Error fetching old batteries: {0}", [error.message || error]));
									});
								} else {
									frappe.msgprint(__("No old batteries found in this Battery Request."));
								}
							}
						});
					}
				}
			}
		});
	},
	
	add_items_to_form(frm, items_list, request_name, request_doc) {
		if (!items_list || items_list.length === 0) {
			frappe.msgprint(__("No items found to add."));
			return;
		}
		
		// Set battery request form link and copy equipment info
		frm.set_value("battery_request_form", request_name);
		if (request_doc) {
			if (request_doc.plate_no) frm.set_value("plate_no", request_doc.plate_no);
			if (request_doc.equipment_type) frm.set_value("equipment_type", request_doc.equipment_type);
			if (request_doc.make) frm.set_value("make", request_doc.make);
			if (request_doc.model) frm.set_value("model", request_doc.model);
			if (request_doc.project) frm.set_value("project", request_doc.project);
		}
		
		// Clear existing items first
		if (frm.doc.battery_items && frm.doc.battery_items.length > 0) {
			frm.clear_table("battery_items");
		}
		

		items_list.forEach(function(item, index) {
			let bir_item = frm.add_child("battery_items");
			
			// Set item_code
			if (item.item_code) {
				bir_item.item_code = item.item_code;
			}
			
			// Set battery position, voltage, amper
			if (item.position) {
				bir_item.battery_position = item.position;
			}
			if (item.voltage) {
				bir_item.battery_voltage = item.voltage;
			}
			if (item.amper) {
				bir_item.battery_amper = item.amper;
			}
			
			// Set serial_no (Battery Recording Database link) - this is the primary field
			if (item.serial_no) {
				bir_item.serial_no = item.serial_no;
			}
			
			if (item.fitted_hr_reading) {
				bir_item.fitted_hr_reading = item.fitted_hr_reading;
			}
			if (item.fitted_date) {
				bir_item.fitted_date = item.fitted_date;
			}
		});
		
		frm.refresh_field("battery_items");
		
		frappe.show_alert({
			message: __("{0} items added successfully", [items_list.length]),
			indicator: 'green'
		}, 3);
	},
	
	fetch_material_request_items(frm, mr_name) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Battery Request and Analysis Form",
				fieldname: "name",
				filters: { material_requisition_no: mr_name }
			},
			callback: function(r) {
				if (r.message && r.message.name) {
					if (frm.events && typeof frm.events.fetch_battery_request_items === 'function') {
						frm.events.fetch_battery_request_items(frm, r.message.name);
					}
				} else {
					frappe.msgprint(__("No Battery Request found linked to this Material Request."));
				}
			}
		});
	},
	
	fetch_previous_issue_items(frm, issue_name) {
		if (!issue_name) {
			frappe.msgprint(__("Error: Previous Issue name is required."));
			return;
		}
		
		// Fetch the full document to get all child table fields
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Battery Issue and Return Report Form",
				name: issue_name
			},
			callback: function(issue_res) {
				if (!issue_res.message) {
					frappe.msgprint(__("Previous Issue document not found: {0}", [issue_name]));
					return;
				}
				
				const issue_doc = issue_res.message;
				
				if (!issue_doc.battery_items || issue_doc.battery_items.length === 0) {
					frappe.msgprint(__("No battery items found in Previous Issue document."));
					return;
				}
				
				let items_to_show = [];
				let promises = [];
				
				issue_doc.battery_items.forEach(function(item) {
					// Use serial_no as it's the link field to Battery Recording Database
					if (item.serial_no) {
						// Get battery details from Battery Recording Database
						promises.push(
							frappe.call({
								method: "frappe.client.get_value",
								args: {
									doctype: "Battery Recording Database",
									fieldname: ["battery_serial_no", "item_code", "battery_voltage", "battery_amper", "battery_position"],
									filters: { name: item.serial_no }
								}
							}).then(function(battery_res) {
								return {
									serial_no: item.serial_no,
									item_code: (battery_res.message && battery_res.message.item_code) || item.item_code || '',
									voltage: item.battery_voltage || (battery_res.message && battery_res.message.battery_voltage) || '',
									amper: item.battery_amper || (battery_res.message && battery_res.message.battery_amper) || '',
									position: item.battery_position || (battery_res.message && battery_res.message.battery_position) || '',
									fitted_hr_reading: item.fitted_hr_reading || '',
									fitted_date: item.fitted_date || ''
								};
							}).catch(function(error) {
								return null;
							})
						);
					}
				});
				
				if (promises.length === 0) {
					frappe.msgprint(__("No batteries found in this Previous Issue. Please ensure the previous issue has batteries with serial numbers selected."));
					return;
				}
				
				Promise.all(promises).then(function(results) {
					items_to_show = results.filter(function(item) { 
						return item !== null && item !== undefined;
					});
					
					if (items_to_show.length > 0) {
						// Copy battery_request_form from the Issue document to the Return document
						if (issue_doc.battery_request_form) {
							frm.set_value("battery_request_form", issue_doc.battery_request_form);
						}
						
						// Copy other fields from Issue document
						if (issue_doc.plate_no) frm.set_value("plate_no", issue_doc.plate_no);
						if (issue_doc.equipment_type) frm.set_value("equipment_type", issue_doc.equipment_type);
						if (issue_doc.make) frm.set_value("make", issue_doc.make);
						if (issue_doc.model) frm.set_value("model", issue_doc.model);
						if (issue_doc.project) frm.set_value("project", issue_doc.project);
						
						if (frm.events && typeof frm.events.add_items_to_form === 'function') {
							frm.events.add_items_to_form(frm, items_to_show, issue_name, issue_doc);
						} else {
							frappe.msgprint(__("Error: Could not add items to form."));
						}
					} else {
						frappe.msgprint(__("No items found in this Previous Issue after processing."));
					}
				}).catch(function(error) {
					frappe.msgprint(__("Error fetching items from Previous Issue: {0}", [error.message || error]));
				});
			}
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
	
	battery_request_form(frm) {
		if (frm.doc.battery_request_form) {
			// Fetch Material Request from Battery Request
			frappe.db.get_value("Battery Request and Analysis Form", frm.doc.battery_request_form, "material_requisition_no")
				.then(r => {
					if (r && r.material_requisition_no) {
						frm.set_value("material_request", r.material_requisition_no);
					}
				});
			// Auto-load items if type is set
			if (frm.doc.type && frm.doc.battery_request_form) {
				frm.trigger("get_items_from_request", frm.doc.battery_request_form);
			}
		}
	},
	
	current_km_hr(frm) {
		// Recalculate battery items when current_km_hr changes (for Return type)
		if (frm.doc.type === "Return" && frm.doc.current_km_hr) {
			frm.refresh_field("battery_items");
		}
	}
});

// Handle child table calculations
frappe.ui.form.on("Battery Issue Return Item", {
	battery_recording_database(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.battery_recording_database) {
			frappe.db.get_value("Battery Recording Database", row.battery_recording_database, [
				"battery_voltage",
				"battery_amper",
				"battery_position",
				"battery_serial_no",
				"fitted_hours_km",
				"fitted_date",
				"item_code"
			]).then(r => {
				if (r) {
					// Auto-populate fields (they are read-only and fetched automatically)
					// Set fitted reading for Issue type
					if (frm.doc.type === "Issue" && frm.doc.plate_no && !row.fitted_hr_reading) {
						frappe.call({
							method: "equipment_and_maintenance.equipment.doctype.battery_issue_and_return_report_form.battery_issue_and_return_report_form.get_current_equipment_reading",
							args: {
								equipment: frm.doc.plate_no
							},
							callback: function(res) {
								if (res.message !== undefined) {
									frappe.model.set_value(cdt, cdn, "fitted_hr_reading", res.message);
									frappe.model.set_value(cdt, cdn, "fitted_date", frappe.datetime.get_today());
								}
							}
						});
					}
					// For Return type, use existing fitted reading
					if (frm.doc.type === "Return" && r.fitted_hours_km && !row.fitted_hr_reading) {
						frappe.model.set_value(cdt, cdn, "fitted_hr_reading", r.fitted_hours_km);
						if (r.fitted_date) {
							frappe.model.set_value(cdt, cdn, "fitted_date", r.fitted_date);
						}
					}
				}
			});
		}
	},
	
	battery_recording_database_query(frm, cdt, cdn) {
		// Set query filter based on Type and row data
		frm.set_query("battery_recording_database", "battery_items", function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			let filters = {};
			
			if (doc.type === "Issue") {
				// For Issue: Only show Available batteries
				filters["battery_status"] = "Available";
				
				// Filter by row's item_code (required)
				if (row.item_code) {
					filters["item_code"] = row.item_code;
				} else {
					// If no item_code is set, don't show any batteries
					filters["item_code"] = "__no_item_code__";
				}
				
				// Also filter by voltage, amper, and position if they are set
				if (row.battery_voltage) {
					filters["battery_voltage"] = row.battery_voltage;
				}
				if (row.battery_amper) {
					filters["battery_amper"] = row.battery_amper;
				}
				if (row.battery_position) {
					filters["battery_position"] = row.battery_position;
				}
			} else if (doc.type === "Return") {
				// For Return: Show Fitted batteries
				filters["battery_status"] = "Fitted";
				
				// Filter by row's item_code if set
				if (row.item_code) {
					filters["item_code"] = row.item_code;
				}
				
				// If Battery Request Form is selected, filter by old batteries from request
				if (doc.battery_request_form) {
					return {
						filters: filters,
						query: "equipment_and_maintenance.equipment.doctype.battery_issue_return_item.battery_issue_return_item.filter_batteries_for_return"
					};
				}
			}
			
			return { filters: filters };
		});
	},

});


