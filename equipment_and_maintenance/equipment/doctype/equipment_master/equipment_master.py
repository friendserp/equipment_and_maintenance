# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document


class EquipmentMaster(Document):
	def autoname(self):
		"""Generate equipment code based on category and sub category codes"""
		if not self.equipment_category or not self.equipment_sub_category:
			frappe.throw("Equipment Category and Equipment Sub Category are required to generate Equipment Code")
		
		# Get category code
		category_code = frappe.db.get_value("Asset Category", self.equipment_category, "custom_asset_category_code")
		if not category_code:
			# If no code, use the name (sanitized)
			category_code = frappe.scrub(self.equipment_category)
		
		# Get sub category code
		sub_category_code = frappe.db.get_value("Asset Sub Category", self.equipment_sub_category, "code")
		if not sub_category_code:
			# If no code, use the name (sanitized)
			sub_category_code = frappe.scrub(self.equipment_sub_category)
		
		# Create prefix: Maint{category_code}{sub_category_code}-
		prefix = f"{category_code}{sub_category_code}-"
		
		# Find the highest existing number for this prefix
		# This ensures sequential numbering: highest + 1
		conditions = ["equipment_code LIKE %s"]
		values = [f"{prefix}%"]
		
		# Exclude current document if it exists (for updates)
		if self.name:
			conditions.append("name != %s")
			values.append(self.name)
		
		# Get all existing codes for this prefix
		existing_codes = frappe.db.sql(f"""
			SELECT equipment_code 
			FROM `tabEquipment Master`
			WHERE {' AND '.join(conditions)}
			ORDER BY equipment_code DESC
		""", tuple(values), as_dict=True)
		
		# Extract the highest number from existing codes
		next_number = 1
		max_number = 0
		for code_row in existing_codes:
			if code_row.equipment_code:
				# Extract number from code like "HMCR-0001" or "CATSUB-0001"
				match = re.search(r'-(\d+)$', code_row.equipment_code)
				if match:
					num = int(match.group(1))
					if num > max_number:
						max_number = num
		
		# Next number is highest + 1
		if max_number > 0:
			next_number = max_number + 1
		
		# Format the number with leading zeros (4 digits)
		formatted_number = f"{next_number:04d}"
		
		# Set the equipment code
		self.equipment_code = f"{prefix}{formatted_number}"
		self.name = self.equipment_code
