# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days
from datetime import datetime


class PreventiveMaintenanceSchedule(Document):
	def validate(self):
		self.calculate_next_service()
		self.update_status()
	
	def calculate_next_service(self):
		"""Calculate next service due based on intervals"""
		if not self.current_hours and not self.current_kilometers:
			return
		
		# Find the next service interval
		next_hours = None
		next_km = None
		
		# Standard intervals
		hour_intervals = [250, 500, 1000, 2000, 6000]
		km_intervals = [2500, 5000, 10000, 30000, 60000]
		
		# Calculate next hours interval
		if self.current_hours:
			last_hours = self.last_service_hours or 0
			current = self.current_hours
			
			# Find the smallest interval that hasn't been reached yet
			for interval in hour_intervals:
				next_interval_value = last_hours + interval
				if current < next_interval_value:
					# This is a future interval, check if it's the smallest
					if not next_hours or next_interval_value < next_hours:
						next_hours = next_interval_value
			
			if next_hours:
				self.next_service_due_hours = next_hours
		
		# Calculate next kilometers interval
		if self.current_kilometers:
			last_km = self.last_service_kilometers or 0
			current = self.current_kilometers
			
			# Find the smallest interval that hasn't been reached yet
			for interval in km_intervals:
				next_interval_value = last_km + interval
				if current < next_interval_value:
					# This is a future interval, check if it's the smallest
					if not next_km or next_interval_value < next_km:
						next_km = next_interval_value
			
			if next_km:
				self.next_service_due_kilometers = next_km
	
	def update_status(self):
		"""Update status based on service due"""
		if not self.next_service_due_hours and not self.next_service_due_kilometers:
			self.status = "Active"
			return
		
		hours_overdue = False
		km_overdue = False
		
		if self.next_service_due_hours and self.current_hours:
			hours_overdue = self.current_hours >= self.next_service_due_hours
		
		if self.next_service_due_kilometers and self.current_kilometers:
			km_overdue = self.current_kilometers >= self.next_service_due_kilometers
		
		if hours_overdue or km_overdue:
			self.status = "Overdue"
		else:
			self.status = "Active"
	
	def on_update(self):
		"""Create schedule items from template"""
		if self.template and not self.schedule_items:
			self.populate_schedule_items()
	
	def populate_schedule_items(self):
		"""Populate schedule items from template"""
		template = frappe.get_doc("Preventive Maintenance Template", self.template)
		
		if template.maintenance_tasks:
			for task_row in template.maintenance_tasks:
				# Create schedule items for each interval where task is required
				intervals = []
				
				if task_row.interval_250_hours:
					intervals.append({"interval": "250 Hours", "type": "Hours", "value": 250})
				if task_row.interval_500_hours:
					intervals.append({"interval": "500 Hours", "type": "Hours", "value": 500})
				if task_row.interval_1000_hours:
					intervals.append({"interval": "1000 Hours", "type": "Hours", "value": 1000})
				if task_row.interval_2000_hours:
					intervals.append({"interval": "2000 Hours", "type": "Hours", "value": 2000})
				if task_row.interval_6000_hours:
					intervals.append({"interval": "6000 Hours", "type": "Hours", "value": 6000})
				if task_row.interval_2500_km:
					intervals.append({"interval": "2500 KM", "type": "Kilometers", "value": 2500})
				if task_row.interval_5000_km:
					intervals.append({"interval": "5000 KM", "type": "Kilometers", "value": 5000})
				if task_row.interval_10000_km:
					intervals.append({"interval": "10000 KM", "type": "Kilometers", "value": 10000})
				if task_row.interval_30000_km:
					intervals.append({"interval": "30000 KM", "type": "Kilometers", "value": 30000})
				if task_row.interval_60000_km:
					intervals.append({"interval": "60000 KM", "type": "Kilometers", "value": 60000})
				
				for interval in intervals:
					row = self.append("schedule_items")
					row.task = task_row.task
					row.task_name = task_row.task_name
					row.task_category = task_row.task_category
					row.interval_name = interval["interval"]
					row.interval_type = interval["type"]
					row.interval_value = interval["value"]
					row.is_completed = 0


@frappe.whitelist()
def check_and_send_reminders():
	"""Check all schedules and send reminders for due services"""
	schedules = frappe.get_all("Preventive Maintenance Schedule", 
		filters={"send_reminders": 1, "status": ["in", ["Active", "Overdue"]]},
		fields=["name", "equipment", "equipment_code", "plate_no", 
			"next_service_due_hours", "next_service_due_kilometers", 
			"reminder_days_before", "reminder_recipients", "current_hours", "current_kilometers"])
	
	reminders_sent = 0
	
	for schedule in schedules:
		# Check if service is due or approaching
		hours_due = False
		km_due = False
		
		if schedule.next_service_due_hours and schedule.current_hours:
			hours_remaining = schedule.next_service_due_hours - schedule.current_hours
			# Estimate days based on average usage (assuming 8 hours/day)
			days_remaining = hours_remaining / 8 if hours_remaining > 0 else 0
			hours_due = days_remaining <= schedule.reminder_days_before
		
		if schedule.next_service_due_kilometers and schedule.current_kilometers:
			km_remaining = schedule.next_service_due_kilometers - schedule.current_kilometers
			# Estimate days based on average usage (assuming 100 km/day)
			days_remaining = km_remaining / 100 if km_remaining > 0 else 0
			km_due = days_remaining <= schedule.reminder_days_before
		
		if hours_due or km_due:
			send_reminder(schedule)
			reminders_sent += 1
	
	return reminders_sent


def send_reminder(schedule):
	"""Send reminder email for maintenance due"""
	recipients = []
	if schedule.reminder_recipients:
		recipients = [email.strip() for email in schedule.reminder_recipients.split(",")]
	
	if not recipients:
		# Default to system manager
		recipients = [frappe.session.user]
	
	subject = f"Preventive Maintenance Due: {schedule.equipment_code or schedule.plate_no}"
	
	message = f"""
	Preventive Maintenance is due for the following equipment:
	
	Equipment: {schedule.equipment_code or schedule.plate_no}
	Current Hours: {schedule.current_hours or 0}
	Current Kilometers: {schedule.current_kilometers or 0}
	Next Service Due (Hours): {schedule.next_service_due_hours or 'N/A'}
	Next Service Due (Kilometers): {schedule.next_service_due_kilometers or 'N/A'}
	
	Please schedule maintenance service.
	"""
	
	frappe.sendmail(
		recipients=recipients,
		subject=subject,
		message=message
	)


@frappe.whitelist()
def populate_from_template(schedule, template):
	"""Populate schedule items from template"""
	try:
		# Handle new document case
		if schedule and frappe.db.exists("Preventive Maintenance Schedule", schedule):
			schedule_doc = frappe.get_doc("Preventive Maintenance Schedule", schedule)
		else:
			# For new documents, this will be called after save
			return False
		
		template_doc = frappe.get_doc("Preventive Maintenance Template", template)
		
		# Clear existing items if any
		schedule_doc.schedule_items = []
		
		if template_doc.maintenance_tasks:
			for task_row in template_doc.maintenance_tasks:
				# Create schedule items for each interval where task is required
				intervals = []
				
				if task_row.interval_250_hours:
					intervals.append({"interval": "250 Hours", "type": "Hours", "value": 250})
				if task_row.interval_500_hours:
					intervals.append({"interval": "500 Hours", "type": "Hours", "value": 500})
				if task_row.interval_1000_hours:
					intervals.append({"interval": "1000 Hours", "type": "Hours", "value": 1000})
				if task_row.interval_2000_hours:
					intervals.append({"interval": "2000 Hours", "type": "Hours", "value": 2000})
				if task_row.interval_6000_hours:
					intervals.append({"interval": "6000 Hours", "type": "Hours", "value": 6000})
				if task_row.interval_2500_km:
					intervals.append({"interval": "2500 KM", "type": "Kilometers", "value": 2500})
				if task_row.interval_5000_km:
					intervals.append({"interval": "5000 KM", "type": "Kilometers", "value": 5000})
				if task_row.interval_10000_km:
					intervals.append({"interval": "10000 KM", "type": "Kilometers", "value": 10000})
				if task_row.interval_30000_km:
					intervals.append({"interval": "30000 KM", "type": "Kilometers", "value": 30000})
				if task_row.interval_60000_km:
					intervals.append({"interval": "60000 KM", "type": "Kilometers", "value": 60000})
				
				for interval in intervals:
					row = schedule_doc.append("schedule_items")
					row.task = task_row.task
					row.task_name = task_row.task_name
					row.task_category = task_row.task_category
					row.interval_name = interval["interval"]
					row.interval_type = interval["type"]
					row.interval_value = interval["value"]
					row.is_completed = 0
		
		schedule_doc.save()
		return True
	except Exception as e:
		frappe.log_error(f"Error populating from template: {str(e)}")
		return False

