# Copyright (c) 2026, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class PreventiveMaintenancePlan(Document):
	def validate(self):
		"""Validate and fetch equipment details"""
		# Validate month and year
		if self.planning_year:
			current_year = getdate().year
			if self.planning_year < current_year - 1 or self.planning_year > current_year + 5:
				frappe.throw("Planning year should be reasonable (within 1 year past to 5 years future)")
		
		# Check for duplicate plan for same equipment, month, and year
		if self.equipment and self.planning_month and self.planning_year:
			existing = frappe.db.exists(
				"Preventive Maintenance Plan",
				{
					"equipment": self.equipment,
					"planning_month": self.planning_month,
					"planning_year": self.planning_year,
					"name": ["!=", self.name]
				}
			)
			if existing:
				frappe.throw(f"A plan already exists for this equipment in {self.planning_month} {self.planning_year}")
		
		# Load history before save (only if not submitted)
		if self.equipment and self.docstatus == 0:
			load_pm_history(self)


def load_pm_history(plan):
	"""Load PM Done history into plan's history child table"""
	# Clear existing history
	plan.pm_history = []
	
	# Get all PM Done records for this equipment
	pm_done_list = frappe.db.get_all(
		"Preventive Maintenance Done",
		filters={
			"equipment": plan.equipment,
			"docstatus": 1
		},
		fields=["name", "actual_date", "service_type", "actual_hours_km", 
				"pm_performed_as_per_schedule", "performed_by", "remark", "completion_notes"],
		order_by="actual_date DESC, creation DESC"
	)
	
	# Add to history child table
	for pm_done in pm_done_list:
		plan.append("pm_history", {
			"pm_done": pm_done.name,
			"actual_date": pm_done.actual_date,
			"service_type": pm_done.service_type,
			"actual_hours_km": pm_done.actual_hours_km,
			"pm_performed_as_per_schedule": pm_done.pm_performed_as_per_schedule,
			"performed_by": pm_done.performed_by,
			"remark": pm_done.remark or pm_done.completion_notes
		})
	

@frappe.whitelist()
def get_pm_history(equipment):
	"""Get PM history for an equipment from PM Done records"""
	history = frappe.db.get_all(
		"Preventive Maintenance Done",
		filters={
			"equipment": equipment,
			"docstatus": 1
		},
		fields=["name", "actual_date as pm_date", "service_type", "actual_hours_km as hours_km_after",
				"performed_by", "plan", "pm_performed_as_per_schedule", "remark", "completion_notes"],
		order_by="actual_date DESC, creation DESC",
		limit=10
	)
	
	return history


@frappe.whitelist()
def get_equipment_current_reading(equipment):
	"""Get current hours/km reading from latest PM Done or History"""
	# Try to get from latest PM Done
	latest_done = frappe.db.get_all(
		"Preventive Maintenance Done",
		filters={"equipment": equipment, "docstatus": 1},
		fields=["actual_hours_km", "actual_date"],
		order_by="actual_date DESC",
		limit=1
	)
	
	if latest_done and latest_done[0]:
		return {
			"current_hours_km": latest_done[0].get("actual_hours_km") or 0,
			"last_pm_date": latest_done[0].get("actual_date")
		}
	
	
	return {
		"current_hours_km": 0,
		"last_pm_date": None
	}
