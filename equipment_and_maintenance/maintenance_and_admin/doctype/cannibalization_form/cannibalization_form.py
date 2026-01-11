# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CannibalizationForm(Document):
	def before_insert(self):
		# Auto-populate request_by_name on creation
		if not self.request_by_name:
			user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
			self.request_by_name = user_full_name
		if not self.request_by_date:
			self.request_by_date = frappe.utils.today()
	
	def validate(self):
		self.auto_populate_workflow_fields()
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
		
		if self.workflow_state in ["Maintenance Approved", "Under Maintenance Review"]:
			if not self.maintenance_dept_name:
				self.maintenance_dept_name = user_full_name
				self.maintenance_dept_date = frappe.utils.today()
		elif self.workflow_state in ["Admin Approved", "Under Admin Review"]:
			if not self.admin_dept_name:
				self.admin_dept_name = user_full_name
				self.admin_dept_date = frappe.utils.today()
		elif self.workflow_state == "GM Approved":
			if not self.gm_name:
				self.gm_name = user_full_name
				self.gm_date = frappe.utils.today()

