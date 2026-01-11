# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentDisposalRequest(Document):
	def before_insert(self):
		"""Set prepared_by to current user"""
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
	
	def validate(self):
		self.auto_populate_workflow_fields()
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user and date fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		user = frappe.session.user
		today = frappe.utils.today()
		
		if self.workflow_state == "Equipment Dept Approved":
			if not self.equip_dept_approved_by:
				self.equip_dept_approved_by = user
				self.equip_dept_date = today
		elif self.workflow_state == "DGM Approved":
			if not self.dgm_approved_by:
				self.dgm_approved_by = user
				self.dgm_date = today
		elif self.workflow_state == "Survey Committee Approved":
			if not self.survey_committee_approved_by:
				self.survey_committee_approved_by = user
				self.survey_committee_date = today
		elif self.workflow_state == "General Manager Approved":
			if not self.general_manager_approved_by:
				self.general_manager_approved_by = user
			if not self.approved_by:
				self.approved_by = user
	
	def before_cancel(self):
		"""Set workflow state to Cancelled before cancelling"""
		self.workflow_state = "Cancelled"

