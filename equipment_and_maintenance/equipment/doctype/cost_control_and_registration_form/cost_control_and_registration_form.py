# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CostControlandRegistrationForm(Document):
	def validate(self):
		"""Validate the form"""
		# Auto-set prepared_by if not set
		if not self.prepared_by:
			self.prepared_by = frappe.session.user

