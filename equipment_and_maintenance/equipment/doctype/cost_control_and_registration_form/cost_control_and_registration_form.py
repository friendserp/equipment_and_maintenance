# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CostControlandRegistrationForm(Document):
	def before_insert(self):
		# Auto-set prepared_by on creation
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
	
	def validate(self):
		"""Validate the form"""
		# Auto-set prepared_by if not set (for existing docs)
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		
		# Auto-populate workflow fields
		self.auto_populate_workflow_fields()
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		if self.workflow_state == "Approved":
			if not self.approved_by:
				self.approved_by = frappe.session.user

