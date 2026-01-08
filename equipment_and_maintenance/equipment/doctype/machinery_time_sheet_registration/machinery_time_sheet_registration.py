# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from datetime import datetime, timedelta


class MachineryTimeSheetRegistration(Document):
	def before_insert(self):
		# Auto-fill prepared_by with current user
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
	
	def validate(self):
		# Always recalculate hours for operation time
		if self.operation_time:
			for row in self.operation_time:
				if row.start_time and row.end_time:
					calculated_hours = self.calculate_hours(row.start_time, row.end_time)
					row.hours = flt(calculated_hours, 2)
				else:
					row.hours = 0
		
		# Always recalculate hours for idle time
		if self.idle_time:
			for row in self.idle_time:
				if row.start_time and row.end_time:
					calculated_hours = self.calculate_hours(row.start_time, row.end_time)
					row.hours = flt(calculated_hours, 2)
				else:
					row.hours = 0
		
		# Always recalculate hours for down time
		if self.down_time:
			for row in self.down_time:
				if row.start_time and row.end_time:
					calculated_hours = self.calculate_hours(row.start_time, row.end_time)
					row.hours = flt(calculated_hours, 2)
				else:
					row.hours = 0
		
		# Calculate total working hour
		self.calculate_total_working_hour()
	
	def calculate_hours(self, start_time, end_time):
		"""Calculate hours between start_time and end_time"""
		try:
			if isinstance(start_time, str):
				start = datetime.strptime(start_time.split('.')[0], "%H:%M:%S").time()
			else:
				start = start_time
			
			if isinstance(end_time, str):
				end = datetime.strptime(end_time.split('.')[0], "%H:%M:%S").time()
			else:
				end = end_time
			
			# Convert to datetime for calculation
			start_dt = datetime.combine(datetime.today(), start)
			end_dt = datetime.combine(datetime.today(), end)
			
			# If end is before start, assume next day
			if end_dt < start_dt:
				end_dt += timedelta(days=1)
			
			# Calculate difference in hours
			diff = end_dt - start_dt
			return diff.total_seconds() / 3600
		except Exception:
			return 0
	
	def calculate_total_working_hour(self):
		"""Calculate total working hour = Operation hours - Idle hours - Down hours"""
		total_operation = sum([flt(row.hours or 0) for row in (self.operation_time or [])])
		total_idle = sum([flt(row.hours or 0) for row in (self.idle_time or [])])
		total_down = sum([flt(row.hours or 0) for row in (self.down_time or [])])
		
		# Set individual totals
		self.total_operation_hours = flt(total_operation, 2)
		self.total_idle_hours = flt(total_idle, 2)
		self.total_down_hours = flt(total_down, 2)
		
		# Total working hour = Operation hours - Idle hours - Down hours
		self.total_working_hour = flt(total_operation - total_idle - total_down, 2)
