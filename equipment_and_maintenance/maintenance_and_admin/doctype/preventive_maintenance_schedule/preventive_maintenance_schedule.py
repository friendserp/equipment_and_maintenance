# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days
from frappe import _
from datetime import datetime


class PreventiveMaintenanceSchedule(Document):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._items_populated = False
	
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
	
	def before_save(self):
		"""Populate schedule items from template before save"""
		# Prevent multiple population calls
		if self._items_populated:
			return
		
		# Only populate if template is set and we don't have items
		if self.template:
			# Check if items exist in memory
			items_in_memory = len(self.schedule_items) if self.schedule_items else 0
			
			# For new documents, populate if no items in memory
			# For existing documents, check database too
			if items_in_memory == 0:
				if not self.name:
					# New document - populate
					self.populate_schedule_items()
					self._items_populated = True
				else:
					# Existing document - check database
					items_in_db = frappe.db.count("Preventive Maintenance Schedule Item", 
						filters={"parent": self.name})
					if items_in_db == 0:
						self.populate_schedule_items()
						self._items_populated = True
	
	def populate_schedule_items(self):
		"""Populate schedule items from template - only for the target interval"""
		# Determine target interval
		target_interval = self.determine_target_interval()
		if not target_interval:
			return
		
		template = frappe.get_doc("Preventive Maintenance Template", self.template)
		
		# Get existing task names and task links to avoid duplicates
		existing_task_names = set()
		existing_task_links = set()
		
		# Check items already in memory
		if self.schedule_items:
			for item in self.schedule_items:
				if item.task_name:
					existing_task_names.add(item.task_name)
				if item.task:
					existing_task_links.add(item.task)
		
		# Also check database if document exists
		if self.name:
			try:
				db_items = frappe.db.get_all("Preventive Maintenance Schedule Item",
					filters={"parent": self.name},
					fields=["task_name", "task"])
				for item in db_items:
					if item.task_name:
						existing_task_names.add(item.task_name)
					if item.task:
						existing_task_links.add(item.task)
			except:
				pass  # Document might not be saved yet
		
		if template.maintenance_tasks:
			# Determine which interval field to check
			interval_field = None
			if target_interval["type"] == "Hours":
				interval_field = f"interval_{target_interval['value']}_hours"
			else:
				interval_field = f"interval_{target_interval['value']}_km"
			
			# Only add tasks that have this specific interval checked and don't already exist
			for task_row in template.maintenance_tasks:
				if getattr(task_row, interval_field, False):
					# Skip if task already exists (check both task_name and task link)
					if task_row.task_name in existing_task_names:
						continue
					if task_row.task in existing_task_links:
						continue
					
					# Additional check: verify not in current schedule_items
					task_exists = False
					if self.schedule_items:
						for existing_item in self.schedule_items:
							if (existing_item.task == task_row.task or 
								existing_item.task_name == task_row.task_name):
								task_exists = True
								break
					
					if task_exists:
						continue
					
					# Only append if we're sure it doesn't exist
					row = self.append("schedule_items")
					row.task = task_row.task
					row.task_name = task_row.task_name
					row.task_category = task_row.task_category
					row.interval_name = target_interval["name"]
					row.interval_type = target_interval["type"]
					row.interval_value = target_interval["value"]
					row.is_completed = 0
					
					# Add to existing sets to prevent duplicates in same operation
					existing_task_names.add(task_row.task_name)
					existing_task_links.add(task_row.task)
	
	def determine_target_interval(self):
		"""Determine which interval milestone we're targeting"""
		hour_intervals = [250, 500, 1000, 2000, 6000]
		km_intervals = [2500, 5000, 10000, 30000, 60000]
		
		target_hour_interval = None
		target_km_interval = None
		
		# Determine target hour interval
		if self.current_hours:
			last_hours = flt(self.last_service_hours) or 0
			current = flt(self.current_hours)
			
			for interval in hour_intervals:
				next_interval_value = last_hours + interval
				if current < next_interval_value:
					if not target_hour_interval or next_interval_value < (last_hours + target_hour_interval["value"]):
						target_hour_interval = {
							"type": "Hours",
							"value": interval,
							"name": f"{interval} Hours"
						}
		
		# Determine target km interval
		if self.current_kilometers:
			last_km = flt(self.last_service_kilometers) or 0
			current = flt(self.current_kilometers)
			
			for interval in km_intervals:
				next_interval_value = last_km + interval
				if current < next_interval_value:
					if not target_km_interval or next_interval_value < (last_km + target_km_interval["value"]):
						target_km_interval = {
							"type": "Kilometers",
							"value": interval,
							"name": f"{interval} KM"
						}
		
		# Return the interval that comes first
		if target_hour_interval and target_km_interval:
			hour_next = (flt(self.last_service_hours) or 0) + target_hour_interval["value"]
			km_next = (flt(self.last_service_kilometers) or 0) + target_km_interval["value"]
			
			if hour_next <= km_next:
				return target_hour_interval
			else:
				return target_km_interval
		
		return target_hour_interval or target_km_interval


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
	"""Populate schedule items from template - only for target interval"""
	try:
		if schedule and frappe.db.exists("Preventive Maintenance Schedule", schedule):
			schedule_doc = frappe.get_doc("Preventive Maintenance Schedule", schedule)
		else:
			return False
		
		# Determine target interval
		target_interval = schedule_doc.determine_target_interval()
		if not target_interval:
			return False
		
		template_doc = frappe.get_doc("Preventive Maintenance Template", template)
		
		# Get existing task names from database to avoid duplicates
		existing_task_names = set()
		db_items = frappe.db.get_all("Preventive Maintenance Schedule Item",
			filters={"parent": schedule},
			fields=["task_name"])
		for item in db_items:
			if item.task_name:
				existing_task_names.add(item.task_name)
		
		# Clear existing items in memory
		schedule_doc.schedule_items = []
		
		# Determine which interval field to check
		interval_field = None
		if target_interval["type"] == "Hours":
			interval_field = f"interval_{target_interval['value']}_hours"
		else:
			interval_field = f"interval_{target_interval['value']}_km"
		
		# Only add tasks that have this specific interval checked and don't already exist
		if template_doc.maintenance_tasks:
			for task_row in template_doc.maintenance_tasks:
				if getattr(task_row, interval_field, False):
					# Skip if task already exists
					if task_row.task_name in existing_task_names:
						continue
					
					row = schedule_doc.append("schedule_items")
					row.task = task_row.task
					row.task_name = task_row.task_name
					row.task_category = task_row.task_category
					row.interval_name = target_interval["name"]
					row.interval_type = target_interval["type"]
					row.interval_value = target_interval["value"]
					row.is_completed = 0
					
					# Add to existing set to prevent duplicates in same operation
					existing_task_names.add(task_row.task_name)
		
		schedule_doc.save(ignore_permissions=True)
		frappe.db.commit()
		return True
	except Exception as e:
		frappe.log_error(f"Error populating from template: {str(e)}")
		frappe.throw(_("Error populating schedule items: {0}").format(str(e)))
		return False

