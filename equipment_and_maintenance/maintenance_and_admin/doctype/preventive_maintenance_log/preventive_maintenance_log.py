# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days


class PreventiveMaintenanceLog(Document):
	def validate(self):
		if self.schedule:
			self.update_schedule()
	
	def on_submit(self):
		"""Update schedule when log is submitted"""
		if self.schedule:
			self.update_schedule_after_service()
	
	def update_schedule(self):
		"""Update schedule with current service information"""
		if self.schedule:
			schedule = frappe.get_doc("Preventive Maintenance Schedule", self.schedule)
			
			# Update last service values
			if self.service_hours:
				schedule.last_service_hours = self.service_hours
			if self.service_kilometers:
				schedule.last_service_kilometers = self.service_kilometers
			
			# Update current values
			if self.service_hours:
				schedule.current_hours = self.service_hours
			if self.service_kilometers:
				schedule.current_kilometers = self.service_kilometers
			
			schedule.save()
	
	def update_schedule_after_service(self):
		"""Mark completed tasks in schedule"""
		if self.schedule and self.completed_tasks:
			schedule = frappe.get_doc("Preventive Maintenance Schedule", self.schedule)
			
			for log_task in self.completed_tasks:
				# Find matching schedule item and mark as completed
				for schedule_item in schedule.schedule_items:
					if (schedule_item.task == log_task.task and 
						schedule_item.interval_name == self.interval_name and
						not schedule_item.is_completed):
						schedule_item.is_completed = 1
						schedule_item.completed_date = self.service_date
						schedule_item.completed_by = self.technician or frappe.session.user
						schedule_item.remarks = log_task.remarks
						break
			
			# Recalculate next service
			schedule.calculate_next_service()
			schedule.save()

