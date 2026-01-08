// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cannibalization Form", {
	cannibalized_from_plate_no(frm) {
		// Fetch information from Equipment Master
		if (frm.doc.cannibalized_from_plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.cannibalized_from_plate_no, 
				["model", "equipment_category", "location"], (r) => {
					if (r) {
						frm.set_value("cannibalized_from_model", r.model || "");
						frm.set_value("cannibalized_from_type", r.equipment_category || "");
						frm.set_value("cannibalized_from_project", r.location || "");
					}
				}
			);
		} else {
			frm.set_value("cannibalized_from_model", "");
			frm.set_value("cannibalized_from_type", "");
			frm.set_value("cannibalized_from_project", "");
		}
	},
	
	fitted_to_plate_no(frm) {
		// Fetch information from Equipment Master
		if (frm.doc.fitted_to_plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.fitted_to_plate_no, 
				["model", "equipment_category", "location"], (r) => {
					if (r) {
						frm.set_value("fitted_to_model", r.model || "");
						frm.set_value("fitted_to_type", r.equipment_category || "");
						frm.set_value("fitted_to_project", r.location || "");
					}
				}
			);
		} else {
			frm.set_value("fitted_to_model", "");
			frm.set_value("fitted_to_type", "");
			frm.set_value("fitted_to_project", "");
		}
	},
	
	purchase_requisition_no(frm) {
		// Auto-fill date from Material Request
		if (frm.doc.purchase_requisition_no) {
			frappe.db.get_value("Material Request", frm.doc.purchase_requisition_no, 
				["transaction_date"], (r) => {
					if (r && r.transaction_date) {
						frm.set_value("purchase_requisition_date", r.transaction_date);
					}
				}
			);
		} else {
			frm.set_value("purchase_requisition_date", "");
		}
	},
	
	refresh(frm) {
		// Set query filter for Material Request - only show those with purpose = "Purchase"
		frm.set_query("purchase_requisition_no", function() {
			return {
				filters: {
					"material_request_type": "Purchase"
				}
			};
		});
		
		// Add button to create Maintenance Request
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Maintenance Request"),
				function() {
					frm.trigger("make_maintenance_request");
				},
				__("Create")
			);
		}
	},
	
	make_maintenance_request: function(frm) {
		// Check if cannibalized_from_plate_no is available
		if (!frm.doc.cannibalized_from_plate_no) {
			frappe.msgprint(__("Cannibalized From Plate No is required to create Maintenance Request."));
			return;
		}
		
		// Check if there are cannibalized parts to add
		if (!frm.doc.cannibalized_parts || frm.doc.cannibalized_parts.length === 0) {
			frappe.msgprint(__("No cannibalized parts found. Please add cannibalized parts first."));
			return;
		}
		
		// Get Equipment Master details for type_of_equipment mapping
		frappe.db.get_value("Equipment Master", frm.doc.cannibalized_from_plate_no, 
			["equipment_category", "location"], (r) => {
				// Create new Maintenance Request document
				let mr_doc = frappe.model.get_new_doc("Maintenance Request");
				
				// Map plate number
				mr_doc.plate_no = frm.doc.cannibalized_from_plate_no;
				
				// Map project/location
				if (frm.doc.cannibalized_from_project) {
					mr_doc.project = frm.doc.cannibalized_from_project;
				} else if (r && r.location) {
					mr_doc.project = r.location;
				}
				
				// Map type of equipment (Asset Category)
				if (r && r.equipment_category) {
					mr_doc.type_of_equipment = r.equipment_category;
				}
				
				// Map date
				mr_doc.date = frappe.datetime.get_today();
				
				// Map requested_by and date_requested
				if (frm.doc.request_by_name) {
					mr_doc.requested_by = frm.doc.request_by_name;
				}
				if (frm.doc.request_by_date) {
					mr_doc.date_requested = frm.doc.request_by_date;
				} else {
					mr_doc.date_requested = frappe.datetime.get_today();
				}
				
				// Add items from cannibalized_parts table
				frm.doc.cannibalized_parts.forEach(function(cannibalized_part) {
					let item_row = frappe.model.add_child(mr_doc, "Maintenance Request Items", "request_items");
					
					// Build description from cannibalized part details
					let description_parts = [];
					
					if (cannibalized_part.description) {
						description_parts.push(`Item: ${cannibalized_part.description}`);
					}
					if (cannibalized_part.part_number) {
						description_parts.push(`Part No: ${cannibalized_part.part_number}`);
					}
					if (cannibalized_part.qty) {
						description_parts.push(`Qty: ${cannibalized_part.qty}`);
					}
					if (cannibalized_part.unit) {
						description_parts.push(`Unit: ${cannibalized_part.unit}`);
					}
					if (cannibalized_part.remark) {
						description_parts.push(`Remark: ${cannibalized_part.remark}`);
					}
					
					// Combine all parts into maintenance/repair request text
					item_row.maintenance__repair_requests = description_parts.join(" | ");
				});
				
				// Open the form
				frappe.set_route("Form", "Maintenance Request", mr_doc.name);
			}
		);
	}
});

