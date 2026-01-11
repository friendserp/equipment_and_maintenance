# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BatteryIssueandReturnReportForm(Document):
	def before_insert(self):
		# Auto-populate prepared_by on creation
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		if not self.prepared_by_date:
			self.prepared_by_date = frappe.utils.today()
	
	def validate(self):
		self.calculate_battery_items()
		self.auto_populate_workflow_fields()
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
		
		if self.workflow_state in ["Checked", "Under Review"]:
			if not self.checked_by:
				self.checked_by = frappe.session.user
				self.checked_by_date = frappe.utils.today()
		elif self.workflow_state == "Approved":
			if not self.approved_by:
				self.approved_by = frappe.session.user
				self.approved_by_date = frappe.utils.today()
	
	def calculate_battery_items(self):
		"""Calculate actual coverage, deviation for each battery item"""
		for item in self.battery_items:
			# Calculate actual coverage (b) = New Fitted Reading - Old Fitted Reading
			if item.new_fitted_hr_reading and item.old_fitted_hr_reading:
				item.actual_coverage = item.new_fitted_hr_reading - item.old_fitted_hr_reading
			else:
				item.actual_coverage = 0
			
			# Calculate deviation (c) = b - a
			if item.actual_coverage and item.standard_life_time:
				item.deviation = item.actual_coverage - item.standard_life_time
			else:
				item.deviation = 0
			
			# Set item number if not set
			if not item.item_no:
				item.item_no = item.idx

