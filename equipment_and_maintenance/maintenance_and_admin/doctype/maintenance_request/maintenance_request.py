# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MaintenanceRequest(Document):
	def before_insert(self):
		# Auto-populate requested_by on creation
		if not self.requested_by:
			user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
			self.requested_by = user_full_name
		if not self.date_requested:
			self.date_requested = frappe.utils.today()
	
	def validate(self):
		# Auto-populate user fields based on workflow state
		self.auto_populate_workflow_fields()
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		# Get current user's full name
		user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
		
		# Populate fields based on workflow state
		if self.workflow_state == "Approved":
			if not self.approved_by:
				self.approved_by = user_full_name
				self.date_approved = frappe.utils.today()
		elif self.workflow_state == "Received":
			if not self.received_by:
				self.received_by = user_full_name
				self.date_received = frappe.utils.today()
