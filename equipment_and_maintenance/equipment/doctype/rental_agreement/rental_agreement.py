# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class RentalAgreement(Document):
	pass


@frappe.whitelist()
def get_category_for_equipment_type(equipment_type):
	"""Get Asset Category and Sub Category for equipment type"""
	try:
		if not equipment_type:
			return {"category": None, "sub_category": None}
		
		# Try exact match first
		categories = frappe.get_all("Asset Category", 
			filters={"asset_category_name": equipment_type},
			fields=["name", "asset_category_name"],
			limit=1
		)
		
		# If no exact match, try partial match
		if not categories:
			categories = frappe.get_all("Asset Category", 
				filters={"asset_category_name": ["like", f"%{equipment_type}%"]},
				fields=["name", "asset_category_name"],
				limit=1
			)
		
		category = None
		sub_category = None
		
		if categories:
			category = categories[0].name
			
			# Get first sub-category for this category
			sub_categories = frappe.get_all("Asset Sub Category",
				filters={"parent": category},
				fields=["name"],
				limit=1
			)
			
			if sub_categories:
				sub_category = sub_categories[0].name
		
		return {"category": category, "sub_category": sub_category}
		
	except Exception as e:
		frappe.log_error(f"Error getting category for equipment type: {str(e)}")
		return {"category": None, "sub_category": None}


@frappe.whitelist()
def link_equipment_to_agreement(agreement, equipment_type, equipment_name):
	"""Link created Equipment Master to Rental Agreement item"""
	try:
		agreement_doc = frappe.get_doc("Rental Agreement", agreement)
		
		# Find the item by equipment_type that hasn't been created yet
		found = False
		for item in agreement_doc.equipments:
			# Check if this is the matching item (not existing equipment, matches type, not already created)
			if (item.equipment_type == equipment_type and 
				not getattr(item, 'is_existing_equipment', False) and 
				not getattr(item, 'equipment_created', False)):
				item.equipment_created = 1
				item.created_equipment_id = equipment_name
				found = True
				break
		
		if found:
			agreement_doc.save(ignore_permissions=True)
			frappe.db.commit()
			return {"success": True}
		else:
			# Try to find any item with matching equipment_type for debugging
			matching_items = [item for item in agreement_doc.equipments if item.equipment_type == equipment_type]
			error_msg = f"Could not find matching equipment item with type '{equipment_type}' that hasn't been created yet"
			if matching_items:
				error_msg += f". Found {len(matching_items)} item(s) with this type, but they may already be created or marked as existing."
			return {"success": False, "error": error_msg}
		
	except Exception as e:
		frappe.log_error(f"Error linking equipment to agreement: {str(e)}")
		return {"success": False, "error": str(e)}
