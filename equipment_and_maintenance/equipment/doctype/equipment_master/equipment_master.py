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
		
		# Create prefix: {category_code}{sub_category_code}-
		prefix = f"{category_code}{sub_category_code}-"
		
		# Find the highest existing number for this prefix
		conditions = ["equipment_code LIKE %s"]
		values = [f"{prefix}%"]
		
		# Exclude current document if it exists (for updates)
		if self.name:
			conditions.append("name != %s")
			values.append(self.name)
		
		# Get the highest number using SQL - ensures we see committed data
		# Use numeric ordering to get the actual highest number
		result = frappe.db.sql(f"""
			SELECT equipment_code 
			FROM `tabEquipment Master`
			WHERE {' AND '.join(conditions)}
			ORDER BY 
				CAST(SUBSTRING_INDEX(equipment_code, '-', -1) AS UNSIGNED) DESC,
				equipment_code DESC
			LIMIT 1
		""", tuple(values), as_dict=True)
		
		# Extract the highest number from existing codes
		next_number = 1
		if result and result[0].get("equipment_code"):
			match = re.search(r'-(\d+)$', result[0]["equipment_code"])
			if match:
				next_number = int(match.group(1)) + 1
		
		# Format the number with leading zeros (4 digits)
		formatted_number = f"{next_number:04d}"
		
		# Set the equipment code
		self.equipment_code = f"{prefix}{formatted_number}"
		self.name = self.equipment_code
	
	def validate(self):
		"""Validate and ensure unique equipment code"""
		# Check if equipment_code already exists (handles race conditions)
		if self.equipment_code and self.is_new():
			existing = frappe.db.get_value("Equipment Master", {"equipment_code": self.equipment_code}, "name")
			if existing:
				# Regenerate autoname if duplicate found
				self.autoname()
				# Double check after regeneration
				existing = frappe.db.get_value("Equipment Master", {"equipment_code": self.equipment_code}, "name")
				if existing:
					frappe.throw(f"Equipment code {self.equipment_code} already exists. Please try again.")
	
	def db_insert(self, *args, **kwargs):
		"""Override db_insert to handle duplicate equipment_code errors and retry"""
		max_retries = 5
		for attempt in range(max_retries):
			try:
				return super().db_insert(*args, **kwargs)
			except Exception as e:
				# If duplicate equipment_code error, regenerate and retry
				if (frappe.db.is_primary_key_violation(e) or frappe.db.is_unique_key_violation(e)) and self.is_new():
					if "equipment_code" in str(e).lower() or "duplicate" in str(e).lower() or "name" in str(e).lower():
						if attempt < max_retries - 1:
							# Regenerate equipment code with incremented number
							# Get current code and increment
							if self.equipment_code:
								match = re.search(r'-(\d+)$', self.equipment_code)
								if match:
									current_num = int(match.group(1))
									prefix = self.equipment_code[:self.equipment_code.rfind('-') + 1]
									new_num = current_num + 1
									self.equipment_code = f"{prefix}{new_num:04d}"
									self.name = self.equipment_code
								else:
									# Fallback: regenerate completely
									self.autoname()
							else:
								# Fallback: regenerate completely
								self.autoname()
							continue
				# If not a duplicate error or max retries reached, raise
				raise
		
		# If we get here, all retries failed
		frappe.throw(f"Failed to create Equipment Master after {max_retries} attempts due to duplicate equipment codes")
