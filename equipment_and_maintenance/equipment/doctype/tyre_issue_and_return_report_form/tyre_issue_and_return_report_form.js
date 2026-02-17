// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tyre Issue and Return Report Form", {
	onload(frm) {
		frappe.model.with_doctype("Tyre Issue Return Item", function() {});
	},

	refresh(frm) {
		if (frm.is_new() && !frm.doc.prepared_by) {
			frm.set_value("prepared_by", frappe.session.user);
			frm.set_value("prepared_by_date", frappe.datetime.get_today());
		}
		frm.trigger("handle_workflow_state");

		if ((frm.is_new() || frm.doc.docstatus === 0) && frm.doc.type) {
			frm.add_custom_button(__("Get Items From"), function() {
				frm.trigger("get_items_from");
			});
		}
		frm.trigger("toggle_fields_by_type");
	},

	type(frm) {
		frm.trigger("toggle_fields_by_type");
		if (frm.doc.type) {
			frm.clear_table("tyre_items");
			frm.refresh_field("tyre_items");
		}
	},

	toggle_fields_by_type(frm) {
		if (!frm.doc.type) return;

		if (frm.doc.type === "Issue") {
			frm.set_df_property("plate_no", "reqd", 1);
			frm.set_df_property("tyre_return_voucher", "hidden", 1);
			frm.set_df_property("current_km_hr", "hidden", 1);
			frm.set_df_property("current_km_hr", "reqd", 0);
		} else if (frm.doc.type === "Return") {
			frm.set_df_property("plate_no", "reqd", 0);
			frm.set_df_property("tyre_return_voucher", "hidden", 0);
			frm.set_df_property("current_km_hr", "hidden", 0);
			frm.set_df_property("current_km_hr", "reqd", 1);
		}
	},

	get_items_from(frm) {
		if (!frm.doc.type) {
			frappe.msgprint(__("Please select Type (Issue or Return) first."));
			return;
		}

		let source_dialog = new frappe.ui.Dialog({
			title: __("Get Items From"),
			fields: [
				{
					fieldtype: "Select",
					fieldname: "source",
					label: __("Get Items From"),
					options: frm.doc.type === "Issue" ? "Tyre Request\nMaterial Request" : "Tyre Request\nPrevious Issue",
					default: "Tyre Request",
					reqd: 1
				},
				{
					fieldtype: "Link",
					fieldname: "tyre_request",
					label: __("Tyre Request"),
					options: "Tyre Request and Analysis Form",
					depends_on: "eval:doc.source == 'Tyre Request'",
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
								"docstatus": 1
							}
						};
					}
				},
				{
					fieldtype: "Link",
					fieldname: "previous_issue",
					label: __("Previous Issue"),
					options: "Tyre Issue and Return Report Form",
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
			primary_action_label: __("Get Items"),
			primary_action: function(values) {
				source_dialog.hide();
				if (values.source === "Tyre Request" && values.tyre_request) {
					if (frm.events && typeof frm.events.fetch_tyre_request_items === 'function') {
						frm.events.fetch_tyre_request_items(frm, values.tyre_request);
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

	fetch_tyre_request_items(frm, request_name) {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Tyre Request and Analysis Form",
				name: request_name
			},
			callback: function(r) {
				if (r.message) {
					let doc = r.message;
					let items_to_show = [];

					if (frm.doc.type === "Issue") {
						frappe.call({
							method: "equipment_and_maintenance.equipment.doctype.tyre_issue_and_return_report_form.tyre_issue_and_return_report_form.get_tyre_request_items",
							args: {
								request_name: request_name
							},
							callback: function(items_res) {
								let requested_items = items_res.message || [];

								if (requested_items.length > 0) {
									requested_items.forEach(function(req_item) {
										let quantity = req_item.quantity || 1;
										for (let i = 0; i < quantity; i++) {
											items_to_show.push({
												item_code: req_item.requested_item_no,
												size: req_item.requested_tyre_size,
												brand: req_item.requested_tyre_brand,
												type: req_item.requested_tyre_type,
												position: req_item.requested_tyre_position,
												serial_no: null
											});
										}
									});

									if (items_to_show.length > 0) {
										if (frm.events && typeof frm.events.add_items_to_form === 'function') {
											frm.events.add_items_to_form(frm, items_to_show, request_name, doc);
										}
									} else {
										frappe.msgprint(__("No requested items found in this Tyre Request."));
									}
								} else {
									frappe.msgprint(__("No requested items found in this Tyre Request."));
								}
							}
						});
					} else if (frm.doc.type === "Return") {
						frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "Tyre Old Item",
								filters: {
									"parent": request_name,
									"parenttype": "Tyre Request and Analysis Form"
								},
								fields: ["serial_no", "fitted_km_reading", "fitted_date"]
							},
							callback: function(old_res) {
								if (old_res.message && old_res.message.length > 0) {
									let promises = old_res.message.map(function(old_item) {
										const tyre_db_name = old_item.serial_no;
										if (!tyre_db_name) {
											return Promise.resolve(null);
										}
										return frappe.call({
											method: "frappe.client.get_value",
											args: {
												doctype: "Tyre Recording Database",
												fieldname: ["tyre_serial_no", "item_code", "tyre_size", "tyre_brand", "tyre_type", "tyre_position"],
												filters: { name: tyre_db_name }
											}
										}).then(function(trd_res) {
											if (trd_res.message) {
												return {
													serial_no: tyre_db_name,
													item_code: trd_res.message.item_code || '',
													size: trd_res.message.tyre_size || '',
													brand: trd_res.message.tyre_brand || '',
													type: trd_res.message.tyre_type || '',
													position: trd_res.message.tyre_position || '',
													fitted_km_reading: old_item.fitted_km_reading,
													fitted_date: old_item.fitted_date
												};
											}
											return null;
										});
									});
									Promise.all(promises).then(function(results) {
										items_to_show = results.filter(function(item) { return item !== null; });

										if (items_to_show.length > 0) {
											if (frm.events && typeof frm.events.add_items_to_form === 'function') {
												frm.events.add_items_to_form(frm, items_to_show, request_name, doc);
											}
										} else {
											frappe.msgprint(__("No old tyres found in this Tyre Request."));
										}
									}).catch(function(error) {
										frappe.msgprint(__("Error fetching old tyres: {0}", [error.message || error]));
									});
								} else {
									frappe.msgprint(__("No old tyres found in this Tyre Request."));
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

		frm.set_value("tyre_request_form", request_name);
		if (request_doc) {
			if (request_doc.plate_no) frm.set_value("plate_no", request_doc.plate_no);
			if (request_doc.equipment_type) frm.set_value("equipment_type", request_doc.equipment_type);
			if (request_doc.make) frm.set_value("make", request_doc.make);
			if (request_doc.model) frm.set_value("model", request_doc.model);
			if (request_doc.project) frm.set_value("project", request_doc.project);
		}

		if (frm.doc.tyre_items && frm.doc.tyre_items.length > 0) {
			frm.clear_table("tyre_items");
		}

		items_list.forEach(function(item) {
			let tir_item = frm.add_child("tyre_items");
			if (item.item_code) {
				tir_item.item_code = item.item_code;
			}
			if (item.position) {
				tir_item.tyre_position = item.position;
			}
			if (item.size) {
				tir_item.tyre_size = item.size;
			}
			if (item.brand) {
				tir_item.tyre_brand = item.brand;
			}
			if (item.type) {
				tir_item.tyre_type = item.type;
			}
			if (item.serial_no) {
				tir_item.serial_no = item.serial_no;
			}
			if (item.fitted_km_reading) {
				tir_item.fitted_km_reading = item.fitted_km_reading;
			}
			if (item.fitted_date) {
				tir_item.fitted_date = item.fitted_date;
			}
		});

		frm.refresh_field("tyre_items");
		frappe.show_alert({
			message: __("{0} items added successfully", [items_list.length]),
			indicator: 'green'
		}, 3);
	},

	fetch_material_request_items(frm, mr_name) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Tyre Request and Analysis Form",
				fieldname: "name",
				filters: { material_requisition_no: mr_name }
			},
			callback: function(r) {
				if (r.message && r.message.name) {
					if (frm.events && typeof frm.events.fetch_tyre_request_items === 'function') {
						frm.events.fetch_tyre_request_items(frm, r.message.name);
					}
				} else {
					frappe.msgprint(__("No Tyre Request found linked to this Material Request."));
				}
			}
		});
	},

	fetch_previous_issue_items(frm, issue_name) {
		if (!issue_name) {
			frappe.msgprint(__("Error: Previous Issue name is required."));
			return;
		}

		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Tyre Issue and Return Report Form",
				name: issue_name
			},
			callback: function(issue_res) {
				if (!issue_res.message) {
					frappe.msgprint(__("Previous Issue document not found: {0}", [issue_name]));
					return;
				}

				const issue_doc = issue_res.message;

				if (!issue_doc.tyre_items || issue_doc.tyre_items.length === 0) {
					frappe.msgprint(__("No tyre items found in Previous Issue document."));
					return;
				}

				let items_to_show = [];
				let promises = [];

				issue_doc.tyre_items.forEach(function(item) {
					if (item.serial_no) {
						promises.push(
							frappe.call({
								method: "frappe.client.get_value",
								args: {
									doctype: "Tyre Recording Database",
									fieldname: ["tyre_serial_no", "item_code", "tyre_size", "tyre_brand", "tyre_type", "tyre_position"],
									filters: { name: item.serial_no }
								}
							}).then(function(tyre_res) {
								if (tyre_res.message) {
									return {
										serial_no: item.serial_no,
										item_code: (tyre_res.message && tyre_res.message.item_code) || item.item_code || '',
										size: item.tyre_size || (tyre_res.message && tyre_res.message.tyre_size) || '',
										brand: item.tyre_brand || (tyre_res.message && tyre_res.message.tyre_brand) || '',
										type: item.tyre_type || (tyre_res.message && tyre_res.message.tyre_type) || '',
										position: item.tyre_position || (tyre_res.message && tyre_res.message.tyre_position) || '',
										fitted_km_reading: item.fitted_km_reading || '',
										fitted_date: item.fitted_date || ''
									};
								}
								return null;
							}).catch(function() {
								return null;
							})
						);
					}
				});

				if (promises.length === 0) {
					frappe.msgprint(__("No tyres found in this Previous Issue. Please ensure the previous issue has tyres with serial numbers selected."));
					return;
				}

				Promise.all(promises).then(function(results) {
					items_to_show = results.filter(function(item) { return item !== null && item !== undefined; });

					if (items_to_show.length > 0) {
						if (issue_doc.tyre_request_form) {
							frm.set_value("tyre_request_form", issue_doc.tyre_request_form);
						}
						if (issue_doc.plate_no) {
							frm.set_value("plate_no", issue_doc.plate_no);
						}
						if (issue_doc.equipment_type) {
							frm.set_value("equipment_type", issue_doc.equipment_type);
						}
						if (issue_doc.make) {
							frm.set_value("make", issue_doc.make);
						}
						if (issue_doc.model) {
							frm.set_value("model", issue_doc.model);
						}
						if (issue_doc.project) {
							frm.set_value("project", issue_doc.project);
						}

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

	current_km_hr(frm) {
		if (frm.doc.type === "Return") {
			frm.trigger("calculate_tyre_items");
		}
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

	equipment_type(frm) {
		if (frm.doc.equipment_type) {
			frappe.db.get_value("Equipment Master", frm.doc.equipment_type, [
				"plate_number",
				"make",
				"model",
				"serial_number",
				"location"
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
				}
			});
		}
	},

	plate_no(frm) {
		if (frm.doc.plate_no) {
			frappe.db.get_value("Equipment Master", frm.doc.plate_no, [
				"equipment_category",
				"make",
				"model",
				"serial_number",
				"location"
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
		}
	},

	tyre_request_form(frm) {
		if (frm.doc.tyre_request_form) {
			frappe.db.get_value("Tyre Request and Analysis Form", frm.doc.tyre_request_form, [
				"plate_no",
				"equipment_type",
				"make",
				"model",
				"serial_no",
				"project"
			]).then(r => {
				if (r) {
					if (r.plate_no && !frm.doc.plate_no) {
						frm.set_value("plate_no", r.plate_no);
					}
					if (r.equipment_type && !frm.doc.equipment_type) {
						frm.set_value("equipment_type", r.equipment_type);
					}
					if (r.make && !frm.doc.make) {
						frm.set_value("make", r.make);
					}
					if (r.model && !frm.doc.model) {
						frm.set_value("model", r.model);
					}
					if (r.serial_no && !frm.doc.serial_no) {
						frm.set_value("serial_no", r.serial_no);
					}
					if (r.project && !frm.doc.project) {
						frm.set_value("project", r.project);
					}
				}
			});
		}
	},
});

frappe.ui.form.on("Tyre Issue Return Item", {
	serial_no(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.serial_no) {
			frappe.db.get_value("Tyre Recording Database", row.serial_no, [
				"tyre_size",
				"tyre_brand",
				"tyre_type",
				"tyre_position",
				"fitted_hours_km",
				"fitted_date",
				"item_code"
			]).then(r => {
				if (r) {
					if (frm.doc.type === "Issue" && frm.doc.plate_no && !row.fitted_km_reading) {
						frappe.call({
							method: "equipment_and_maintenance.equipment.doctype.tyre_issue_and_return_report_form.tyre_issue_and_return_report_form.get_current_equipment_reading",
							args: {
								equipment: frm.doc.plate_no
							},
							callback: function(res) {
								if (res.message !== undefined) {
									frappe.model.set_value(cdt, cdn, "fitted_km_reading", res.message);
									frappe.model.set_value(cdt, cdn, "fitted_date", frappe.datetime.get_today());
								}
							}
						});
					}
					if (frm.doc.type === "Return" && r.fitted_hours_km && !row.fitted_km_reading) {
						frappe.model.set_value(cdt, cdn, "fitted_km_reading", r.fitted_hours_km);
						if (r.fitted_date) {
							frappe.model.set_value(cdt, cdn, "fitted_date", r.fitted_date);
						}
					}
				}
			});
		}
	},
	
	serial_no_query(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		let filters = {};
		
		if (frm.doc.type === "Issue") {
			filters["tyre_status"] = "Available";
			
			if (row.item_code) {
				filters["item_code"] = row.item_code;
			} else {
				filters["item_code"] = "__no_item_code__";
			}
			
			if (row.tyre_size) {
				filters["tyre_size"] = row.tyre_size;
			}
			if (row.tyre_brand) {
				filters["tyre_brand"] = row.tyre_brand;
			}
			if (row.tyre_type) {
				filters["tyre_type"] = row.tyre_type;
			}
			if (row.tyre_position) {
				filters["tyre_position"] = row.tyre_position;
			}
		} else if (frm.doc.type === "Return") {
			filters["tyre_status"] = "Fitted";
			
			if (row.item_code) {
				filters["item_code"] = row.item_code;
			}
			
			if (frm.doc.tyre_request_form) {
				return {
					filters: filters,
					query: "equipment_and_maintenance.equipment.doctype.tyre_issue_return_item.tyre_issue_return_item.filter_tyres_for_return"
				};
			}
		}
		
		return { filters: filters };
	}
});
