// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Work Order", {
	refresh(frm) {
		update_cost_summary(frm);
		setup_queries(frm);
	},
	

	maintenance_request_id(frm) {

		if (frm.doc.maintenance_request_id) {
			frappe.db.get_doc("Maintenance Request", frm.doc.maintenance_request_id)
				.then(doc => {
					
					let request_items_table = doc.request_items;
					if (request_items_table && request_items_table.length > 0) {
						frm.clear_table("request_items");
						request_items_table.forEach(item => {
							let row = frm.add_child("request_items");
							row.maintenance__repair_requests = item.maintenance__repair_requests;
						});
						frm.refresh_field("request_items");
					}
				});
		} else {
			frm.clear_table("request_items");
			frm.refresh_field("request_items");
		}
	},

	// Calculate total labor cost
	calculate_total_labor_cost(frm) {
		let total = 0;
		if (frm.doc.labor_cost_items) {
			frm.doc.labor_cost_items.forEach(row => {
				if (row.total_cost) {
					total += flt(row.total_cost);
				}
			});
		}
		frm.set_value("total_labor_cost", total);
		update_cost_summary(frm);
	},

	// Calculate total spare parts cost
	calculate_total_spare_parts_cost(frm) {
		let total = 0;
		if (frm.doc.spare_cost_items) {
			frm.doc.spare_cost_items.forEach(row => {
				if (row.total_cost) {
					total += flt(row.total_cost);
				}
			});
		}
		frm.set_value("total_spare_parts_cost", total);
		update_cost_summary(frm);
	},

	// Calculate total lubricants cost
	calculate_total_lubricants_cost(frm) {
		let total = 0;
		if (frm.doc.lubricant_cost_items) {
			frm.doc.lubricant_cost_items.forEach(row => {
				if (row.total_price) {
					total += flt(row.total_price);
				}
			});
		}
		frm.set_value("total_lubricants_cost", total);
		update_cost_summary(frm);
	},

	// Calculate total miscellaneous item cost
	calculate_total_miscellaneous_item_cost(frm) {
		let total = 0;
		if (frm.doc.miscellaneous_cost_items) {
			frm.doc.miscellaneous_cost_items.forEach(row => {
				if (row.total_cost) {
					total += flt(row.total_cost);
				}
			});
		}
		frm.set_value("total_miscellaneous_item_cost", total);
		update_cost_summary(frm);
	},

	// Calculate total outside repair cost
	calculate_total_outside_repair_cost(frm) {
		let total = 0;
		if (frm.doc.outside_cost_items) {
			frm.doc.outside_cost_items.forEach(row => {
				if (row.total_cost) {
					total += flt(row.total_cost);
				}
			});
		}
		// Store in a custom field or calculate on the fly
		frm.total_outside_repair_cost = total;
		update_cost_summary(frm);
	}
});

// Labor Cost Table Calculations
frappe.ui.form.on("Maintenance Labor Cost", {
	total_hrs_taken(frm, cdt, cdn) {
		calculate_labor_row_total(frm, cdt, cdn);
	},

	unit_cost(frm, cdt, cdn) {
		calculate_labor_row_total(frm, cdt, cdn);
	},

	job_started_date(frm, cdt, cdn) {
		calculate_labor_hours(frm, cdt, cdn);
	},

	job_started_hr(frm, cdt, cdn) {
		calculate_labor_hours(frm, cdt, cdn);
	},

	job_ended_date(frm, cdt, cdn) {
		calculate_labor_hours(frm, cdt, cdn);
	},

	job_ended_hr(frm, cdt, cdn) {
		calculate_labor_hours(frm, cdt, cdn);
	},

	labor_cost_items_remove(frm) {
		frm.events.calculate_total_labor_cost(frm);
	}
});

// Spare Parts Cost Table Calculations
frappe.ui.form.on("Maintenance Spare Parts Cost", {
	item_code(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.item_code) {
			// Fetch item details
			frappe.db.get_value("Item", row.item_code, ["item_name", "stock_uom"], (r) => {
				if (r) {
					row.parts_description = r.item_name;
					if (!row.unit) {
						row.unit = r.stock_uom;
					}
					frm.refresh_field("spare_cost_items");
				}
			});
		}
	},

	qty(frm, cdt, cdn) {
		calculate_spare_parts_row_total(frm, cdt, cdn);
	},

	unit_cost(frm, cdt, cdn) {
		calculate_spare_parts_row_total(frm, cdt, cdn);
	},

	spare_cost_items_remove(frm) {
		frm.events.calculate_total_spare_parts_cost(frm);
	}
});

// Lubricants Cost Table Calculations
frappe.ui.form.on("Maintenance Lubricant Cost", {
	qty(frm, cdt, cdn) {
		calculate_lubricant_row_total(frm, cdt, cdn);
	},

	unit_price(frm, cdt, cdn) {
		calculate_lubricant_row_total(frm, cdt, cdn);
	},

	lubricant_cost_items_remove(frm) {
		frm.events.calculate_total_lubricants_cost(frm);
	}
});

// Miscellaneous Item Cost Table Calculations
frappe.ui.form.on("Maintenance Miscellaneous Item Cost", {
	miscellaneous_item(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.miscellaneous_item) {
			// Fetch item details
			frappe.db.get_value("Item", row.miscellaneous_item, ["item_name", "stock_uom"], (r) => {
				if (r) {
					if (!row.uom) {
						row.uom = r.stock_uom;
					}
					frm.refresh_field("miscellaneous_cost_items");
				}
			});
		}
	},

	qty(frm, cdt, cdn) {
		calculate_miscellaneous_row_total(frm, cdt, cdn);
	},

	unit_cost(frm, cdt, cdn) {
		calculate_miscellaneous_row_total(frm, cdt, cdn);
	},

	miscellaneous_cost_items_remove(frm) {
		frm.events.calculate_total_miscellaneous_item_cost(frm);
	}
});

// Outside Repair Cost Table Calculations
frappe.ui.form.on("Maintenance Outside Repair Cost", {
	labor_cost(frm, cdt, cdn) {
		calculate_outside_repair_row_total(frm, cdt, cdn);
	},

	material_cost(frm, cdt, cdn) {
		calculate_outside_repair_row_total(frm, cdt, cdn);
	},

	outside_cost_items_remove(frm) {
		frm.events.calculate_total_outside_repair_cost(frm);
	}
});

// Setup Queries
function setup_queries(frm) {
	// Query for Item Code in Spare Parts table
	frm.set_query("item_code", "spare_cost_items", function() {
		return {
			filters: {
				is_stock_item: 1
			}
		};
	});
	
	// Query for Item Code in Miscellaneous Items table
	frm.set_query("miscellaneous_item", "miscellaneous_cost_items", function() {
		return {
			filters: {
				is_stock_item: 1
			}
		};
	});
	
	// Query for Material Request in Spare Parts table
	frm.set_query("issue_number", "spare_cost_items", function() {
		return {
			filters: {
				material_request_type: "Purchase",
				docstatus: ["<", 2]
			}
		};
	});
	
	// Query for Outside WO No in Outside Repair table
	frm.set_query("outside_wo_no", "outside_cost_items", function() {
		return {
			filters: {
				name: ["!=", frm.doc.name || ""],
				docstatus: ["<", 2]
			}
		};
	});
}

// Helper Functions

function calculate_labor_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let total_hrs = flt(row.total_hrs_taken) || 0;
	let unit_cost = flt(row.unit_cost) || 0;
	row.total_cost = total_hrs * unit_cost;
	frm.refresh_field("labor_cost_items");
	frm.events.calculate_total_labor_cost(frm);
}

function calculate_labor_hours(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.job_started_date && row.job_started_hr && row.job_ended_date && row.job_ended_hr) {
		// Combine date and time
		let start_datetime = new Date(row.job_started_date + " " + row.job_started_hr);
		let end_datetime = new Date(row.job_ended_date + " " + row.job_ended_hr);
		
		// Calculate difference in hours
		let diff_ms = end_datetime - start_datetime;
		let diff_hours = diff_ms / (1000 * 60 * 60);
		
		if (diff_hours > 0) {
			row.total_hrs_taken = diff_hours;
			frm.refresh_field("labor_cost_items");
			calculate_labor_row_total(frm, cdt, cdn);
		}
	}
}

function calculate_spare_parts_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let qty = flt(row.qty) || 0;
	let unit_cost = flt(row.unit_cost) || 0;
	row.total_cost = qty * unit_cost;
	frm.refresh_field("spare_cost_items");
	frm.events.calculate_total_spare_parts_cost(frm);
}

function calculate_lubricant_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let qty = flt(row.qty) || 0;
	let unit_price = flt(row.unit_price) || 0;
	row.total_price = qty * unit_price;
	frm.refresh_field("lubricant_cost_items");
	frm.events.calculate_total_lubricants_cost(frm);
}

function calculate_miscellaneous_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let qty = flt(row.qty) || 0;
	let unit_cost = flt(row.unit_cost) || 0;
	row.total_cost = qty * unit_cost;
	frm.refresh_field("miscellaneous_cost_items");
	frm.events.calculate_total_miscellaneous_item_cost(frm);
}

function calculate_outside_repair_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let labor_cost = flt(row.labor_cost) || 0;
	let material_cost = flt(row.material_cost) || 0;
	row.total_cost = labor_cost + material_cost;
	frm.refresh_field("outside_cost_items");
	frm.events.calculate_total_outside_repair_cost(frm);
}

function update_cost_summary(frm) {
	let total_labor = flt(frm.doc.total_labor_cost) || 0;
	let total_spare_parts = flt(frm.doc.total_spare_parts_cost) || 0;
	let total_lubricants = flt(frm.doc.total_lubricants_cost) || 0;
	let total_miscellaneous = flt(frm.doc.total_miscellaneous_item_cost) || 0;
	
	// Calculate outside repair cost
	let total_outside_repair = 0;
	if (frm.doc.outside_cost_items) {
		frm.doc.outside_cost_items.forEach(row => {
			if (row.total_cost) {
				total_outside_repair += flt(row.total_cost);
			}
		});
	}
	
	// Calculate subtotal before overhead
	let subtotal = total_labor + total_spare_parts + total_lubricants + total_miscellaneous + total_outside_repair;
	
	// Get overhead percentage (if field exists, otherwise default to 0)
	let overhead_percentage = flt(frm.doc.overhead_percentage) || 0;
	let overhead_cost = (subtotal * overhead_percentage) / 100;
	
	// Calculate grand total including overhead
	let grand_total = subtotal + overhead_cost;
	
	// Update cost_summary_items table
	frm.clear_table("cost_summary_items");
	
	// Add Labor cost Total
	let row1 = frm.add_child("cost_summary_items");
	row1.description = "Labor cost Total";
	row1.cost = total_labor;
	
	// Add Spare Parts Cost
	let row2 = frm.add_child("cost_summary_items");
	row2.description = "Spare Parts Cost";
	row2.cost = total_spare_parts;
	
	// Add Lubricants Cost
	let row3 = frm.add_child("cost_summary_items");
	row3.description = "Lubricants Cost";
	row3.cost = total_lubricants;
	
	// Add Miscellaneous Cost
	let row4 = frm.add_child("cost_summary_items");
	row4.description = "Miscellaneous Cost";
	row4.cost = total_miscellaneous;
	
	// Add Outside Repair Cost
	let row5 = frm.add_child("cost_summary_items");
	row5.description = "Outside Repair Cost";
	row5.cost = total_outside_repair;
	
	// Add Total Overhead % Charged
	let row6 = frm.add_child("cost_summary_items");
	row6.description = "Total Overhead % Charged";
	row6.cost = overhead_cost;
	
	// Add Grand Total Cost
	let row7 = frm.add_child("cost_summary_items");
	row7.description = "Grand Total Cost";
	row7.cost = grand_total;
	
	frm.refresh_field("cost_summary_items");
}
