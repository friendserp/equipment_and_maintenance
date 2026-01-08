// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental Agreement", {
	refresh(frm) {
		if (frm.doc.equipments && frm.doc.equipments.length > 0) {
			// Check if there are any new equipment items (not existing and not already created)
			let new_equipment_items = frm.doc.equipments.filter(item => 
				!item.is_existing_equipment && 
				item.equipment_type && 
				!item.equipment_created
			);
			
			if (new_equipment_items.length > 0) {
				frm.add_custom_button(__("Create Equipment Master"), function() {
					if (new_equipment_items.length === 1) {
						create_equipment_master_form(frm, new_equipment_items[0]);
					} else {
						show_create_equipment_dialog(frm, new_equipment_items);
					}
				});
			}
		}   
	}
});

function show_create_equipment_dialog(frm, new_equipment_items) {
	// Filter out items that have already been created
	let items_to_show = new_equipment_items.filter(item => !item.equipment_created);
	
	// Show dialog to select which equipment to create
	let options_list = items_to_show.map((item, idx) => {
		return `${idx}: ${item.equipment_type || `Equipment ${idx + 1}`}`;
	}).join("\n");
	
	let d = new frappe.ui.Dialog({
		title: __("Create Equipment Master"),
		fields: [
			{
				label: __("Select Equipment"),
				fieldname: "equipment_index",
				fieldtype: "Select",
				options: options_list,
				reqd: 1
			}
		],
		primary_action_label: __("Create"),
		primary_action: function() {
			let selected_value = d.get_value("equipment_index");
			let selected_idx = parseInt(selected_value.split(":")[0]);
			let selected_item = items_to_show[selected_idx];
			
			if (selected_item) {
				create_equipment_master_form(frm, selected_item);
			}
			d.hide();
		}
	});
	
	d.show();
}

function create_equipment_master_form(frm, item) {
	show_category_selection_dialog(frm, item);
}

function show_category_selection_dialog(frm, item) {
	let d = new frappe.ui.Dialog({
		title: __("Select Category and Sub-Category"),
		fields: [
			{
				label: __("Make"),
				fieldname: "equipment_type",
				fieldtype: "Data",
				default: item.equipment_type,
				read_only: 1
			},
			{
				label: __("Equipment Category"),
				fieldname: "equipment_category",
				fieldtype: "Link",
				options: "Asset Category",
				reqd: 1,
				get_query: function() {
					return {
						filters: {}
					};
				},
				onchange: function() {
					let category = d.get_value("equipment_category");
					let sub_category_field = d.get_field("equipment_sub_category");
					
					// Clear sub-category when category changes
					sub_category_field.set_value("");
					
					// Update query for sub-category field
					if (category) {
						sub_category_field.df.get_query = function() {
							return {
								filters: {
									asset_category: category
								}
							};
						};
					}
				}
			},
			{
				label: __("Equipment Sub Category"),
				fieldname: "equipment_sub_category",
				fieldtype: "Link",
				options: "Asset Sub Category",
				get_query: function() {
					let category = d.get_value("equipment_category");
					if (category) {
						return {
							filters: {
								asset_category: category
							}
						};
					}
					return {
						filters: {}
					};
				}
			}
		],
		primary_action_label: __("Create Equipment Master"),
		primary_action: function() {
			let category = d.get_value("equipment_category");
			let sub_category = d.get_value("equipment_sub_category");
			
			if (!category) {
				frappe.msgprint(__("Please select Equipment Category"));
				return;
			}
			
			d.hide();
			
			// Store linking info for Equipment Master
			frappe.route_options = {
				equipment_category: category,
				make: item.equipment_type,
				equipment_sub_category: sub_category || null,
				location: frm.doc.project,
				ownership_type: "Rental",
				rental_agreement: frm.doc.name,
				current_status: "Active",
				_rental_item_type: item.equipment_type
			};
			
			frappe.new_doc("Equipment Master");
		}
	});
	
	d.show();
}

