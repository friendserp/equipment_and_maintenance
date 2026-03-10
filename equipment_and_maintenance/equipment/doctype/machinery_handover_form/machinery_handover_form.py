# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MachineryHandoverForm(Document):
	def before_insert(self):
		# Auto-set custodian name if not set
		if not self.custodian_name:
			self.custodian_name = frappe.session.user
	
	def validate(self):
		self.auto_populate_workflow_fields()
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
		
		if self.workflow_state == "Received":
			if not self.received_by:
				self.received_by = frappe.session.user
				self.received_date = frappe.utils.today()
		elif self.workflow_state == "Handed Over":
			if not self.handed_over_by:
				self.handed_over_by = frappe.session.user
				self.handed_date = frappe.utils.today()

