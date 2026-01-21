# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BatteryRecordingDatabase(Document):
	def validate(self):
		# Auto-fetch item_name if not set
		if self.item_code and not self.item_name:
			item_name = frappe.db.get_value("Item", self.item_code, "item_name")
			if item_name:
				self.item_name = item_name
		
		# Auto-fetch plate_no from equipment
		if self.current_equipment:
			plate_no = frappe.db.get_value("Equipment Master", self.current_equipment, "plate_number")
			if plate_no:
				self.current_plate_no = plate_no
		
		# Validate item code filters
		if self.item_code:
			item_group = frappe.db.get_value("Item", self.item_code, "item_group")
			custom_subcategory = frappe.db.get_value("Item", self.item_code, "custom_subcategory")
			item_name_val = frappe.db.get_value("Item", self.item_code, "item_name") or ""
			
			if item_group != "Spare Parts":
				frappe.throw(f"Item {self.item_code} must belong to 'Spare Parts' item group.")
			
			if custom_subcategory != "General Purpose":
				frappe.throw(f"Item {self.item_code} must have custom_subcategory 'General Purpose'.")
			
			if not item_name_val.startswith("Battery"):
				frappe.throw(f"Item {self.item_code} name must start with 'Battery'.")

@frappe.whitelist()
def filter_battery_items(doctype, txt, searchfield, start, page_len, filters):
	"""Filter items that belong to Spare Parts, General Purpose, and name starts with Battery"""
	return frappe.db.sql("""
		SELECT name, item_name
		FROM `tabItem`
		WHERE item_group = 'Spare Parts'
		AND custom_subcategory = 'General Purpose'
		AND (item_name LIKE %(txt)s OR name LIKE %(txt)s)
		AND item_name LIKE 'Battery%%'
		ORDER BY name
		LIMIT %(start)s, %(page_len)s
	""", {
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})