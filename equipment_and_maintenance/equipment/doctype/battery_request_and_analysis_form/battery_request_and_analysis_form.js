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
		
		// Remove Material Request button - flow changed, MR is now selected first
		// Keep only Battery Issue and Return Report button
		if (!frm.is_new() && frm.doc.requested_items && frm.doc.requested_items.length > 0) {
			frm.add_custom_button(
				__("Battery Issue and Return Report"),
				function() {
					frm.trigger("make_issue_return_report");
				},
				__("Create")
			);
		}
		
		// Add dashboard link to Battery Recording Database Form
		if (!frm.is_new()) {
			frm.trigger("add_battery_database_link");
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
	
	add_battery_database_link(frm) {
		// Fetch Battery Recording Database Form linked to this request
		frappe.db.get_value("Battery Recording Database Form", {
			"battery_request_form": frm.doc.name
		}, "name").then(r => {
			if (r && r.name) {
				// Add link to dashboard
				if (frm.dashboard && frm.dashboard.data) {
					// Ensure transactions array exists
					if (!frm.dashboard.data.transactions) {
						frm.dashboard.data.transactions = [];
					}
					
					// Check if Battery Management group exists
					let battery_group = frm.dashboard.data.transactions.find(t => t.label === __("Battery Management"));
					if (!battery_group) {
						battery_group = {
							"label": __("Battery Management"),
							"items": []
						};
						frm.dashboard.data.transactions.push(battery_group);
					}
					
					// Add Battery Recording Database Form if not already present
					if (!battery_group.items.includes("Battery Recording Database Form")) {
						battery_group.items.push("Battery Recording Database Form");
					}
					
					// Refresh dashboard
					if (frm.dashboard.render_links) {
						frm.dashboard.render_links();
					}
				} else {
					// If dashboard is not initialized, add a custom button as fallback
					frm.add_custom_button(
						__("Battery Recording Database"),
						function() {
							frappe.set_route("Form", "Battery Recording Database Form", r.name);
						},
						__("View")
					);
				}
			}
		}).catch(err => {
			console.log("Error fetching Battery Recording Database Form:", err);
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
				
				// Fetch old battery data if BOTH Material Request AND Plate No are selected
				if (frm.doc.material_requisition_no && frm.doc.plate_no && frm.doc.requested_items && frm.doc.requested_items.length > 0) {
					console.log("Both MR and Plate No are selected, fetching old battery data...");
					fetch_and_populate_old_battery_data(frm);
				} else {
					console.log("Waiting for Plate No to be selected...");
				}
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
				
				console.log("=== PLATE NO CHANGED ===");
				console.log("Plate No:", frm.doc.plate_no);
				console.log("Material Request:", frm.doc.material_requisition_no);
				console.log("Requested Items Count:", frm.doc.requested_items ? frm.doc.requested_items.length : 0);
				
				// After equipment is set, fetch old battery data if BOTH Material Request AND requested items exist
				if (frm.doc.material_requisition_no && frm.doc.requested_items && frm.doc.requested_items.length > 0) {
					console.log("Both MR and Plate No are selected, fetching old battery data...");
					// Fetch Battery Recording Database Form once and populate all items
					fetch_and_populate_old_battery_data(frm);
				} else {
					if (!frm.doc.material_requisition_no) {
						console.log("Material Request not selected yet");
					}
					if (!frm.doc.requested_items || frm.doc.requested_items.length === 0) {
						console.log("No requested items found");
					}
				}
			});
		}
	},
	
	make_issue_return_report(frm) {
		if (!frm.doc.requested_items || frm.doc.requested_items.length === 0) {
			frappe.msgprint(__("No requested items found. Please add requested items first."));
			return;
		}
		
		if (!frm.doc.old_battery_items || frm.doc.old_battery_items.length === 0) {
			frappe.msgprint(__("No old battery items found. Please ensure plate number is selected and old battery data is loaded."));
			return;
		}
		
		let bir_doc = frappe.model.get_new_doc("Battery Issue and Return Report Form");
		bir_doc.effective_date = frappe.datetime.get_today();
		bir_doc.issue_no = 1; // Default issue number
		
		// Copy equipment information
		bir_doc.equipment_type = frm.doc.equipment_type;
		bir_doc.make = frm.doc.make;
		bir_doc.model = frm.doc.model;
		bir_doc.serial_no = frm.doc.serial_no;
		bir_doc.plate_no = frm.doc.plate_no;
		bir_doc.project = frm.doc.project;
		
		// Copy old battery details and analysis data
		// Match requested items with old battery items by position
		frm.doc.requested_items.forEach(function(requested_item) {
			let bir_item = frappe.model.add_child(bir_doc, "Battery Issue Return Item", "battery_items");
			
			// Find matching old battery item by position
			let matching_old_item = null;
			if (requested_item.requested_battery_position && frm.doc.old_battery_items) {
				matching_old_item = frm.doc.old_battery_items.find(old_item => 
					old_item.battery_position === requested_item.requested_battery_position
				);
			}
			
			// If no match, use first old battery item
			if (!matching_old_item && frm.doc.old_battery_items && frm.doc.old_battery_items.length > 0) {
				matching_old_item = frm.doc.old_battery_items[0];
			}
			
			if (matching_old_item) {
				// Old battery details
				bir_item.old_battery_make = matching_old_item.battery_make;
				bir_item.old_battery_position = matching_old_item.battery_position;
				bir_item.old_serial_no = matching_old_item.serial_no;
				bir_item.old_battery_voltage = matching_old_item.battery_voltage;
				bir_item.old_battery_amper = matching_old_item.battery_amper;
				bir_item.old_fitted_hr_reading = matching_old_item.fitted_hr_reading;
				bir_item.old_fitted_date = matching_old_item.fitted_date;
				bir_item.old_unit_price = matching_old_item.unit_price;
			}
			
			// Find matching analysis item
			let matching_analysis_item = null;
			if (requested_item.requested_battery_position && frm.doc.analysis_items) {
				matching_analysis_item = frm.doc.analysis_items.find(analysis_item => 
					analysis_item.battery_position === requested_item.requested_battery_position
				);
			}
			
			if (matching_analysis_item) {
				// Analysis data
				bir_item.actual_coverage = matching_analysis_item.actual_coverage;
				bir_item.standard_life_time = matching_analysis_item.standard_life_time;
				bir_item.deviation = matching_analysis_item.deviation;
				bir_item.reason_for_less_consumption = matching_analysis_item.reason_for_less_consumption;
			}
		});
		
		// Link back to Battery Request Form
		bir_doc.battery_request_form = frm.doc.name;
		
		frappe.set_route("Form", "Battery Issue and Return Report Form", bir_doc.name);
	}
});

// Function to fetch old battery data from Battery Recording Database Form for all items
function fetch_and_populate_old_battery_data(frm) {
	console.log("=== fetch_and_populate_old_battery_data START ===");
	console.log("Plate No:", frm.doc.plate_no);
	console.log("Material Request:", frm.doc.material_requisition_no);
	console.log("Requested Items Count:", frm.doc.requested_items ? frm.doc.requested_items.length : 0);
	
	// Fetch existing battery data from Battery Recording Database Form
	if (!frm.doc.plate_no) {
		console.log("ERROR: No plate_no found");
		return;
	}
	
	if (!frm.doc.requested_items || frm.doc.requested_items.length === 0) {
		console.log("ERROR: No requested_items found");
		return;
	}
	
	console.log("Searching for Battery Recording Database Form with plate_no:", frm.doc.plate_no);
	
	// Use frappe.db.get_list (client-side API) to fetch the latest Battery Recording Database Form
	// Fetch regardless of submission status (both draft and submitted)
	frappe.db.get_list("Battery Recording Database Form", {
		filters: {
			"plate_no": frm.doc.plate_no
		},
		fields: ["name", "docstatus"],
		order_by: "creation desc",
		limit: 1
	}).then(records => {
		console.log("Found Battery Recording Database Forms:", records);
		if (records && records.length > 0) {
			console.log("Fetching Battery Recording Database Form:", records[0].name, "Status:", records[0].docstatus);
			// Fetch the latest Battery Recording Database Form
			return frappe.db.get_doc("Battery Recording Database Form", records[0].name);
		}
		console.log("No Battery Recording Database Form found for plate_no:", frm.doc.plate_no);
		return null;
	}).then(brd_doc => {
		if (brd_doc) {
			console.log("Battery Recording Database Form loaded:", brd_doc.name);
			console.log("New battery items in database:", brd_doc.new_battery_items ? brd_doc.new_battery_items.length : 0);
			console.log("Analysis items in database:", brd_doc.analysis_items ? brd_doc.analysis_items.length : 0);
			
			// Fetch NEW batteries from database (they become OLD for the next request)
			if (brd_doc.new_battery_items && brd_doc.new_battery_items.length > 0) {
				console.log("Consolidating and populating old battery data from NEW batteries in database...");
				// Consolidate new batteries by (Voltage, Amper, Position) and populate old_battery_items
				consolidate_and_populate_old_batteries(frm, brd_doc);
			} else {
				console.log("No new battery items found in database");
			}
			
			// Populate analysis items from database
			if (brd_doc.analysis_items && brd_doc.analysis_items.length > 0) {
				console.log("Populating analysis items from database...");
				populate_analysis_items(frm, brd_doc);
			} else {
				console.log("No analysis items found in database");
			}
			
			frm.refresh_field("old_battery_items");
			frm.refresh_field("analysis_items");
			console.log("=== fetch_and_populate_old_battery_data END (SUCCESS) ===");
		} else {
			console.log("ERROR: Battery Recording Database Form document is null");
		}
	}).catch(err => {
		console.error("ERROR in fetch_and_populate_old_battery_data:", err);
		console.log("=== fetch_and_populate_old_battery_data END (ERROR) ===");
	});
}

// Function to consolidate old batteries by (Voltage, Amper, Position) and populate old_battery_items
// Fetches NEW batteries from database (they become OLD for the next request)
function consolidate_and_populate_old_batteries(frm, brd_doc) {
	// Clear existing old battery items
	frm.clear_table("old_battery_items");
	
	// Group batteries by (voltage, amper, position)
	let battery_groups = {};
	
	// Use new_battery_items from database (these are the current batteries that become old)
	if (!brd_doc.new_battery_items || brd_doc.new_battery_items.length === 0) {
		console.log("No new_battery_items found in database");
		return;
	}
	
	brd_doc.new_battery_items.forEach(function(db_item) {
		let voltage = db_item.battery_voltage || 0;
		let amper = db_item.battery_amper || 0;
		let position = db_item.battery_position || "";
		
		// Create a unique key for grouping
		let group_key = `${voltage}_${amper}_${position}`;
		
		if (!battery_groups[group_key]) {
			battery_groups[group_key] = {
				battery_make: db_item.battery_make,
				battery_position: position,
				battery_voltage: voltage,
				battery_amper: amper,
				quantity: 0,
				serial_no: db_item.serial_no, // Keep first serial number
				fitted_hr_reading: db_item.fitted_hr_reading,
				fitted_date: db_item.fitted_date,
				unit_price: db_item.unit_price
			};
		}
		
		// Increment quantity for this group (add quantity from database item)
		battery_groups[group_key].quantity += (db_item.quantity || 1);
	});
	
	// Populate old_battery_items table with consolidated data
	Object.keys(battery_groups).forEach(function(group_key) {
		let group = battery_groups[group_key];
		let old_item = frm.add_child("old_battery_items");
		
		old_item.battery_make = group.battery_make;
		old_item.battery_position = group.battery_position;
		old_item.battery_voltage = group.battery_voltage;
		old_item.battery_amper = group.battery_amper;
		old_item.quantity = group.quantity;
		old_item.serial_no = group.serial_no;
		old_item.fitted_hr_reading = group.fitted_hr_reading;
		old_item.fitted_date = group.fitted_date;
		old_item.unit_price = group.unit_price;
		
		console.log("Added consolidated old battery:", {
			position: old_item.battery_position,
			voltage: old_item.battery_voltage,
			amper: old_item.battery_amper,
			quantity: old_item.quantity
		});
	});
}

// Function to populate analysis items from database
function populate_analysis_items(frm, brd_doc) {
	// Clear existing analysis items
	frm.clear_table("analysis_items");
	
	// Use analysis_items from database
	if (!brd_doc.analysis_items || brd_doc.analysis_items.length === 0) {
		console.log("No analysis_items found in database");
		return;
	}
	
	// Group analysis by (voltage, amper, position) similar to old batteries
	let analysis_groups = {};
	
	brd_doc.analysis_items.forEach(function(db_item) {
		let voltage = db_item.battery_voltage || 0;
		let amper = db_item.battery_amper || 0;
		let position = db_item.battery_position || "";
		
		let group_key = `${voltage}_${amper}_${position}`;
		
		if (!analysis_groups[group_key]) {
			analysis_groups[group_key] = {
				battery_position: position,
				battery_voltage: voltage,
				battery_amper: amper,
				fitted_hr_reading: db_item.old_fitted_hr_reading || db_item.new_fitted_hr_reading,
				actual_coverage: db_item.actual_coverage,
				standard_life_time: db_item.standard_life_time,
				deviation: db_item.deviation,
				reason_for_less_consumption: db_item.reason_for_less_consumption
			};
		}
	});
	
	// Populate analysis_items table
	Object.keys(analysis_groups).forEach(function(group_key) {
		let group = analysis_groups[group_key];
		let analysis_item = frm.add_child("analysis_items");
		
		analysis_item.battery_position = group.battery_position;
		analysis_item.battery_voltage = group.battery_voltage;
		analysis_item.battery_amper = group.battery_amper;
		analysis_item.fitted_hr_reading = group.fitted_hr_reading;
		analysis_item.actual_coverage = group.actual_coverage;
		analysis_item.standard_life_time = group.standard_life_time;
		analysis_item.deviation = group.deviation;
		analysis_item.reason_for_less_consumption = group.reason_for_less_consumption;
		
		console.log("Added analysis item:", {
			position: analysis_item.battery_position,
			voltage: analysis_item.battery_voltage,
			amper: analysis_item.battery_amper
		});
	});
}

// Function to fetch old battery data for a single item (kept for backward compatibility)
function fetch_old_battery_data(frm, battery_item) {
	if (!frm.doc.plate_no) return;
	
	frappe.db.get_list("Battery Recording Database Form", {
		filters: {
			"plate_no": frm.doc.plate_no
		},
		fields: ["name"],
		order_by: "creation desc",
		limit: 1
	}).then(records => {
		if (records && records.length > 0) {
			return frappe.db.get_doc("Battery Recording Database Form", records[0].name);
		}
		return null;
	}).then(brd_doc => {
		if (brd_doc) {
			populate_old_battery_data(frm, battery_item, brd_doc);
			frm.refresh_field("battery_items");
		}
	}).catch(err => {
		console.log("Could not fetch old battery data:", err);
	});
}

// Function to fetch old battery data for a single item (kept for backward compatibility but not used)
function fetch_old_battery_data(frm, battery_item) {
	if (!frm.doc.plate_no) return;
	
	frappe.db.get_list("Battery Recording Database Form", {
		filters: {
			"plate_no": frm.doc.plate_no
		},
		fields: ["name"],
		order_by: "creation desc",
		limit: 1
	}).then(records => {
		if (records && records.length > 0) {
			return frappe.db.get_doc("Battery Recording Database Form", records[0].name);
		}
		return null;
	}).then(brd_doc => {
		if (brd_doc) {
			consolidate_and_populate_old_batteries(frm, brd_doc);
			populate_analysis_items(frm, brd_doc);
			frm.refresh_field("old_battery_items");
			frm.refresh_field("analysis_items");
		}
	}).catch(err => {
		console.log("Could not fetch old battery data:", err);
	});
}

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
