// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Request and Analysis Form", {
	refresh(frm) {
		// Auto-set prepared_by if not set (on creation)
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		// Handle workflow state changes for auto-populating user fields
		frm.trigger("handle_workflow_state");
		
		// Keep only Tyre Issue and Return Report button
		if (!frm.is_new() && frm.doc.requested_items && frm.doc.requested_items.length > 0) {
			frm.add_custom_button(
				__("Tyre Issue and Return Report"),
				function() {
					frm.trigger("make_issue_return_report");
				},
				__("Create")
			);
		}
		
		// Add dashboard link to Tyre Recording Database Form
		if (!frm.is_new()) {
			frm.trigger("add_tyre_database_link");
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
	
	add_tyre_database_link(frm) {
		// Fetch Tyre Recording Database Form linked to this request
		frappe.db.get_value("Tyre Recording Database Form", {
			"tyre_request_form": frm.doc.name
		}, "name").then(r => {
			if (r && r.name) {
				// Add link to dashboard
				if (frm.dashboard && frm.dashboard.data) {
					// Ensure transactions array exists
					if (!frm.dashboard.data.transactions) {
						frm.dashboard.data.transactions = [];
					}
					
					// Check if Tyre Management group exists
					let tyre_group = frm.dashboard.data.transactions.find(t => t.label === __("Tyre Management"));
					if (!tyre_group) {
						tyre_group = {
							"label": __("Tyre Management"),
							"items": []
						};
						frm.dashboard.data.transactions.push(tyre_group);
					}
					
					// Add Tyre Recording Database Form if not already present
					if (!tyre_group.items.includes("Tyre Recording Database Form")) {
						tyre_group.items.push("Tyre Recording Database Form");
					}
					
					// Refresh dashboard
					if (frm.dashboard.render_links) {
						frm.dashboard.render_links();
					}
				} else {
					// If dashboard is not initialized, add a custom button as fallback
					frm.add_custom_button(
						__("Tyre Recording Database"),
						function() {
							frappe.set_route("Form", "Tyre Recording Database Form", r.name);
						},
						__("View")
					);
				}
			}
		}).catch(err => {
			console.log("Error fetching Tyre Recording Database Form:", err);
		});
	},
	
	material_requisition_no(frm) {
		// When Material Request is selected, fetch items and populate requested_items table
		if (frm.doc.material_requisition_no) {
			frm.trigger("fetch_mr_items");
		} else {
			// Clear all tables if MR is cleared
			frm.clear_table("requested_items");
			frm.clear_table("old_tyre_items");
			frm.clear_table("analysis_items");
			frm.refresh_field("requested_items");
			frm.refresh_field("old_tyre_items");
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
				frm.clear_table("old_tyre_items");
				frm.clear_table("analysis_items");
				
				// Populate requested_items from MR items
				mr_doc.items.forEach(function(mr_item, index) {
					let requested_item = frm.add_child("requested_items");
					
					// Set requested item details from MR
					requested_item.requested_item_no = mr_item.item_code;
					requested_item.quantity = mr_item.qty || 1;
					
					// Parse description if it contains tyre details
					if (mr_item.description) {
						let desc = mr_item.description;
						// Try to extract size, brand, type, position from description
						let size_match = desc.match(/Size:\s*([^\n,]+)/i);
						let brand_match = desc.match(/Brand:\s*([^\n,]+)/i);
						let type_match = desc.match(/Type:\s*(Radial|Bias|Tubeless|Tube Type)/i);
						let position_match = desc.match(/Position:\s*(Front Left|Front Right|Rear Left|Rear Right|Spare|Other)/i);
						
						if (size_match) {
							requested_item.requested_tyre_size = size_match[1].trim();
						}
						if (brand_match) {
							requested_item.requested_tyre_brand = brand_match[1].trim();
						}
						if (type_match) {
							requested_item.requested_tyre_type = type_match[1];
						}
						if (position_match) {
							requested_item.requested_tyre_position = position_match[1];
						}
					}
				});
				
				frm.refresh_field("requested_items");
				
				// Fetch old tyre data if BOTH Material Request AND Plate No are selected
				if (frm.doc.material_requisition_no && frm.doc.plate_no && frm.doc.requested_items && frm.doc.requested_items.length > 0) {
					fetch_and_populate_old_tyre_data(frm);
				}
			})
			.catch(err => {
				frappe.msgprint(__("Error fetching Material Request: " + err.message));
			});
	},
	
	plate_no(frm) {
		if (frm.doc.plate_no) {
			// Fetch equipment details
			frappe.db.get_value("Equipment Master", frm.doc.plate_no, [
				"equipment_category", "make", "model", "serial_number", "location"
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
			});
			
			// Fetch old tyre data and populate analysis if Material Request is already selected
			if (frm.doc.material_requisition_no && frm.doc.requested_items && frm.doc.requested_items.length > 0) {
				fetch_and_populate_old_tyre_data(frm);
				populate_analysis_items(frm);
			}
		}
	},
	
	make_issue_return_report(frm) {
		// Create Tyre Issue and Return Report Form
		frappe.new_doc("Tyre Issue and Return Report Form", {
			effective_date: frm.doc.request_date || frappe.datetime.get_today(),
			plate_no: frm.doc.plate_no,
			equipment_type: frm.doc.equipment_type,
			make: frm.doc.make,
			model: frm.doc.model,
			serial_no: frm.doc.serial_no,
			project: frm.doc.project,
			tyre_request_form: frm.doc.name
		});
	}
});

function fetch_and_populate_old_tyre_data(frm) {
	if (!frm.doc.plate_no || !frm.doc.requested_items || frm.doc.requested_items.length === 0) {
		return;
	}
	
	console.log("=== fetch_and_populate_old_tyre_data START ===");
	console.log("Plate No:", frm.doc.plate_no);
	console.log("Material Request:", frm.doc.material_requisition_no);
	console.log("Requested Items Count:", frm.doc.requested_items ? frm.doc.requested_items.length : 0);
	
	// Find the latest Tyre Recording Database Form for this equipment
	frappe.db.get_list("Tyre Recording Database Form", {
		filters: {
			plate_no: frm.doc.plate_no
		},
		fields: ["name", "effective_date", "docstatus"],
		order_by: "effective_date desc, creation desc",
		limit: 1
	}).then(results => {
		console.log("Found Tyre Recording Database Forms:", results);
		
		if (!results || results.length === 0) {
			console.log("No Tyre Recording Database Form found for plate_no:", frm.doc.plate_no);
			// Still populate analysis items even if no old data exists
			populate_analysis_items(frm);
			return;
		}
		
		const latest_db = results[0];
		console.log("Latest Tyre Recording Database Form:", latest_db.name);
		
		// Fetch the full document to get new_tyre_items
		frappe.db.get_doc("Tyre Recording Database Form", latest_db.name)
			.then(db_doc => {
				if (!db_doc || !db_doc.new_tyre_items || db_doc.new_tyre_items.length === 0) {
					console.log("No new tyre items found in database");
					populate_analysis_items(frm);
					return;
				}
				
				// Consolidate old tyre items by Tyre Size, Tyre Brand, Tyre Type, and Tyre Position
				let consolidated_old_tyres = {};
				
				db_doc.new_tyre_items.forEach(new_item => {
					// Create a key for grouping: Size + Brand + Type + Position
					let key = `${new_item.tyre_size || ''}_${new_item.tyre_brand || ''}_${new_item.tyre_type || ''}_${new_item.tyre_position || ''}`;
					
					if (!consolidated_old_tyres[key]) {
						consolidated_old_tyres[key] = {
							tyre_size: new_item.tyre_size,
							tyre_brand: new_item.tyre_brand,
							tyre_type: new_item.tyre_type,
							tyre_position: new_item.tyre_position,
							quantity: 0,
							fitted_km_reading: new_item.fitted_km_reading,
							fitted_date: new_item.fitted_date,
							unit_price: new_item.unit_price,
							serial_no: new_item.serial_no
						};
					}
					
					consolidated_old_tyres[key].quantity += (new_item.quantity || 1);
				});
				
				// Clear old tyre items table
				frm.clear_table("old_tyre_items");
				
				// Populate old_tyre_items with consolidated data
				Object.values(consolidated_old_tyres).forEach(old_tyre => {
					let old_item = frm.add_child("old_tyre_items");
					old_item.tyre_brand = old_tyre.tyre_brand;
					old_item.tyre_size = old_tyre.tyre_size;
					old_item.tyre_type = old_tyre.tyre_type;
					old_item.tyre_position = old_tyre.tyre_position;
					old_item.quantity = old_tyre.quantity;
					old_item.fitted_km_reading = old_tyre.fitted_km_reading;
					old_item.fitted_date = old_tyre.fitted_date;
					old_item.unit_price = old_tyre.unit_price;
					old_item.serial_no = old_tyre.serial_no;
				});
				
				frm.refresh_field("old_tyre_items");
				
				// Populate analysis items
				populate_analysis_items(frm);
			})
			.catch(err => {
				console.log("ERROR: Tyre Recording Database Form document is null", err);
				populate_analysis_items(frm);
			});
	})
	.catch(err => {
		console.log("Error fetching Tyre Recording Database Form:", err);
		populate_analysis_items(frm);
	});
}

function populate_analysis_items(frm) {
	if (!frm.doc.requested_items || frm.doc.requested_items.length === 0) {
		return;
	}
	
	// Clear analysis items
	frm.clear_table("analysis_items");
	
	// Fetch analysis data from latest Tyre Recording Database Form
	frappe.db.get_list("Tyre Recording Database Form", {
		filters: {
			plate_no: frm.doc.plate_no
		},
		fields: ["name"],
		order_by: "effective_date desc, creation desc",
		limit: 1
	}).then(results => {
		if (results && results.length > 0) {
			return frappe.db.get_doc("Tyre Recording Database Form", results[0].name);
		}
		return null;
	}).then(db_doc => {
		// Populate analysis items based on requested items
		frm.doc.requested_items.forEach(requested_item => {
			let analysis_item = frm.add_child("analysis_items");
			
			analysis_item.tyre_position = requested_item.requested_tyre_position;
			analysis_item.tyre_size = requested_item.requested_tyre_size;
			analysis_item.tyre_brand = requested_item.requested_tyre_brand;
			analysis_item.tyre_type = requested_item.requested_tyre_type;
			
			// Find matching old tyre item for fitted_km_reading
			if (frm.doc.old_tyre_items && frm.doc.old_tyre_items.length > 0) {
				let matching_old = frm.doc.old_tyre_items.find(item => 
					item.tyre_position === requested_item.requested_tyre_position
				);
				if (matching_old) {
					analysis_item.fitted_km_reading = matching_old.fitted_km_reading;
				}
			}
			
			// Get current km reading from equipment or set default
			// This should be fetched from Equipment Master or entered manually
			analysis_item.current_km_reading = frm.doc.engine_hour__km_reading || 0;
			
			// Standard life time - this should be configured or fetched from settings
			analysis_item.standard_life_time = 0; // Default, should be configured
		});
		
		frm.refresh_field("analysis_items");
	});
}

