# Copyright (c) 2026, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PreventiveMaintenanceHistory(Document):
	def validate(self):
		"""Validate PM History document"""
		# Auto-fetch equipment details if equipment is set
		if self.equipment:
			equipment = frappe.get_doc("Equipment Master", self.equipment)
			self.plate_number = equipment.plate_number or ""
			self.equipment_code = equipment.equipment_code or ""
			self.make = equipment.make or ""
			self.model = equipment.model or ""
		
		# Validate hours/km
		if self.hours_km_before and self.hours_km_after:
			if self.hours_km_after < self.hours_km_before:
				frappe.throw("Hours/Km After cannot be less than Hours/Km Before")
	
	def on_update(self):
		"""Update related documents when history is updated"""
		# Could update plan status if needed
		pass
