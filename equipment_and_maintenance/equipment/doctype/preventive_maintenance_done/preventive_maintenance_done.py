# Copyright (c) 2026, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class PreventiveMaintenanceDone(Document):
	def validate(self):
		"""Validate PM Done document"""
		# Set performed_by to current user if not set
		if not self.performed_by:
			self.performed_by = frappe.session.user
		
		# Validate date
		if self.actual_date:
			actual_date = getdate(self.actual_date) if isinstance(self.actual_date, str) else self.actual_date
			if actual_date > getdate():
				frappe.throw("Actual date cannot be in the future")
	
	def on_submit(self):
		"""Update Plan when PM Done is submitted"""
		if self.plan:
			# Update plan's is_maintenance_done field
			plan = frappe.get_doc("Preventive Maintenance Plan", self.plan)
			plan.is_maintenance_done = "Yes"
			plan.save(ignore_permissions=True)
	
	def get_previous_reading(self):
		"""Get previous hours/km reading from latest PM Done or History"""
		# Try to get from latest PM Done (excluding current)
		filters = {
			"equipment": self.equipment,
			"docstatus": 1
		}
		if self.name:
			filters["name"] = ["!=", self.name]
		
		latest_done_list = frappe.db.get_all(
			"Preventive Maintenance Done",
			filters=filters,
			fields=["actual_hours_km"],
			order_by="actual_date DESC, creation DESC",
			limit=1
		)
		
		if latest_done_list and latest_done_list[0]:
			return latest_done_list[0].get("actual_hours_km") or 0
		
		return 0





@frappe.whitelist()
def get_planned_pm_for_equipment(equipment, month=None, year=None):
	"""Get planned PM for equipment from active plans"""
	filters = {
		"equipment": equipment,
		"docstatus": 1
	}
	
	if month:
		filters["planning_month"] = month
	if year:
		filters["planning_year"] = year
	
	# This would need to query plan items
	# For now, return empty - can be enhanced later
	return []
