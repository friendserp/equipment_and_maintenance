// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Request and Analysis Form", {
	refresh(frm) {
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		
		frm.trigger("handle_workflow_state");
		
		if (frm.doc.docstatus === 1) {
			if (frm.doc.material_requisition_no) {
				frm.add_custom_button(
					__("Material Request"),
					function() {
						frappe.set_route("Form", "Material Request", frm.doc.material_requisition_no);
					},
					__("View")
				);
			} else {
				frm.add_custom_button(
					__("Material Request"),
					function() {
						frm.trigger("open_material_request");
					},
					__("Create")
				);
			}
		}
		
		if (frm.doc.docstatus === 1 && frm.doc.material_requisition_no && !frm.is_new()) {
			frm.add_custom_button(
				__("Tyre Issue and Return Report"),
				function() {
					frm.trigger("make_issue_return_report");
				},
				__("Create")
			);
		}
	},
	
	open_material_request(frm) {
		if (frm.doc.docstatus !== 1) {
			frappe.msgprint(__("Tyre Request must be submitted before creating Material Request."));
			return;
		}
		
		if (!frm.doc.requested_items || frm.doc.requested_items.length === 0) {
			frappe.msgprint(__("No requested items found."));
			return;
		}
		
		sessionStorage.setItem('tyre_request_for_mr', frm.doc.name);
		
		frappe.model.with_doctype("Material Request", function() {
			frappe.model.with_doctype("Material Request Item", function() {
				let new_mr = frappe.model.get_new_doc("Material Request");
				
				new_mr.material_request_type = "Material Issue";
				new_mr.transaction_date = frappe.datetime.get_today();
				new_mr.schedule_date = frappe.datetime.add_days(frappe.datetime.get_today(), 7);
				if (frm.doc.project) {
					new_mr.custom_project = frm.doc.project;
				}
				
				new_mr.items = [];
				
				frm.doc.requested_items.forEach(function(req_item) {
					let mr_item = frappe.model.add_child(new_mr, "Material Request Item", "items");
					mr_item.item_code = req_item.requested_item_no;
					mr_item.qty = req_item.quantity || 1;
					mr_item.project = frm.doc.project;
					mr_item.uom = "pcs";
					mr_item.conversion_factor = 1;
					mr_item.description = `Tyre - Size: ${req_item.requested_tyre_size || ''}, Brand: ${req_item.requested_tyre_brand || ''}, Type: ${req_item.requested_tyre_type || ''}, Position: ${req_item.requested_tyre_position || ''}`;
				});
				
				frappe.set_route("Form", "Material Request", new_mr.name);
			});
		});
	},
	
	before_workflow_action(frm) {
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
	
	handle_workflow_state(frm) {
		if (!frm.doc.workflow_state) return;
		
		if (frm.doc.workflow_state === "Checked" && !frm.doc.checked_by) {
			frm.set_value("checked_by", frappe.session.user);
			frm.set_value("checked_by_date", frappe.datetime.get_today());
		} else if (frm.doc.workflow_state === "Approved" && !frm.doc.approved_by) {
			frm.set_value("approved_by", frappe.session.user);
			frm.set_value("approved_by_date", frappe.datetime.get_today());
		}
	},
	
	material_requisition_no(frm) {
		if (frm.doc.material_requisition_no) {
			frappe.db.get_doc("Material Request", frm.doc.material_requisition_no)
				.then(mr_doc => {
					if (mr_doc && mr_doc.items && mr_doc.items.length > 0) {
						if (mr_doc.custom_project && !frm.doc.project) {
							frm.set_value("project", mr_doc.custom_project);
						}
					}
				})
				.catch(err => {
					frappe.msgprint(__("Error fetching Material Request: " + err.message));
				});
		}
	},
	
	plate_no(frm) {
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
				
				frm.trigger("load_existing_tyres");
			});
		} else {
			frm.clear_table("old_tyre_items");
			frm.clear_table("analysis_items");
			frm.refresh_field("old_tyre_items");
			frm.refresh_field("analysis_items");
		}
	},
	
	current_km_hr(frm) {
		if (frm.doc.current_km_hr && frm.doc.old_tyre_items && frm.doc.old_tyre_items.length > 0) {
			frm.save().then(() => {
				frm.reload_doc();
			});
		}
	},
	
	load_existing_tyres(frm) {
		if (!frm.doc.plate_no) return;
		
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Tyre Issue and Return Report Form",
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
					
					frappe.call({
						method: "frappe.client.get",
						args: {
							doctype: "Tyre Issue and Return Report Form",
							name: last_issue_name
						},
						callback: function(issue_doc_res) {
							if (issue_doc_res.message && issue_doc_res.message.tyre_items) {
								const tyre_items = issue_doc_res.message.tyre_items;
								
								frm.clear_table("old_tyre_items");
								
								if (tyre_items && tyre_items.length > 0) {
									let added_tyres = new Set();
									
									tyre_items.forEach(function(tyre_item) {
										if (tyre_item.serial_no && !added_tyres.has(tyre_item.serial_no)) {
											added_tyres.add(tyre_item.serial_no);
											
											let old_item = frm.add_child("old_tyre_items");
											old_item.serial_no = tyre_item.serial_no;
											old_item.fitted_km_reading = tyre_item.fitted_km_reading;
											old_item.fitted_date = tyre_item.fitted_date;
											old_item.quantity = 1;
										}
									});
									
									frm.refresh_field("old_tyre_items");
									
									if (frm.doc.old_tyre_items && frm.doc.old_tyre_items.length > 0) {
										frm.save().then(function() {
											frm.reload_doc();
										});
									}
								} else {
									frm.refresh_field("old_tyre_items");
								}
							} else {
								frm.clear_table("old_tyre_items");
								frm.refresh_field("old_tyre_items");
							}
						}
					});
				} else {
					frm.clear_table("old_tyre_items");
					frm.refresh_field("old_tyre_items");
				}
			}
		});
	},
	
	old_tyre_items(frm) {
		if (frm.doc.old_tyre_items && frm.doc.old_tyre_items.length > 0) {
			frm.save().then(() => {
				frm.reload_doc();
			});
		} else {
			frm.clear_table("analysis_items");
			frm.refresh_field("analysis_items");
		}
	},
	
	make_issue_return_report(frm) {
		if (!frm.doc.material_requisition_no) {
			frappe.msgprint(__("Please create Material Request first before creating Issue and Return document."));
			return;
		}
		
		frappe.model.with_doctype("Tyre Issue and Return Report Form", function() {
			frappe.model.with_doctype("Tyre Issue Return Item", function() {
				let tir_doc = frappe.model.get_new_doc("Tyre Issue and Return Report Form");
				tir_doc.type = "Issue";
				tir_doc.effective_date = frappe.datetime.get_today();
				tir_doc.tyre_request_form = frm.doc.name;
				tir_doc.material_request = frm.doc.material_requisition_no;
				
				tir_doc.equipment_type = frm.doc.equipment_type;
				tir_doc.make = frm.doc.make;
				tir_doc.model = frm.doc.model;
				tir_doc.serial_no = frm.doc.serial_no;
				tir_doc.plate_no = frm.doc.plate_no;
				tir_doc.project = frm.doc.project;
				
				frappe.set_route("Form", "Tyre Issue and Return Report Form", tir_doc.name);
			});
		});
	}
});
