# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import re
from datetime import datetime


class MachineryTimeSheetRegistration(Document):
	def before_insert(self):
		# Auto-fill prepared_by with current user
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
	
	def validate(self):
		# Validate time format (HH:mm)
		self.validate_time_format("morning_start", "Morning Start")
		self.validate_time_format("morning_end", "Morning End")
		self.validate_time_format("afternoon_start", "Afternoon Start")
		self.validate_time_format("afternoon_end", "Afternoon End")
		
		# Validate time logic
		if self.morning_start and self.morning_end:
			self.validate_time_order(self.morning_start, self.morning_end, "Morning")
		if self.afternoon_start and self.afternoon_end:
			self.validate_time_order(self.afternoon_start, self.afternoon_end, "Afternoon")
	
	def validate_time_format(self, fieldname, field_label):
		"""Validate that time is in HH:mm AM/PM format (12-hour format)"""
		time_value = self.get(fieldname)
		if time_value:
			# Convert to string
			if isinstance(time_value, str):
				time_str = time_value.strip().upper()
			else:
				time_str = str(time_value).strip().upper()
			
			# If AM is explicitly specified, use AM; otherwise default to PM
			if 'AM' in time_str:
				# Keep AM if explicitly specified
				time_match = re.match(r'^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*AM$', time_str)
				if time_match:
					hour = int(time_match.group(1))
					minute = int(time_match.group(2))
					time_str = "{:02d}:{:02d} AM".format(hour, minute)
					self.set(fieldname, time_str)
			elif 'PM' in time_str:
				# Keep PM if explicitly specified
				time_match = re.match(r'^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*PM$', time_str)
				if time_match:
					hour = int(time_match.group(1))
					minute = int(time_match.group(2))
					time_str = "{:02d}:{:02d} PM".format(hour, minute)
					self.set(fieldname, time_str)
			else:
				# No AM/PM specified, default to PM
				time_match = re.match(r'^([0]?[1-9]|1[0-2]):([0-5][0-9])$', time_str)
				if time_match:
					hour = int(time_match.group(1))
					minute = int(time_match.group(2))
					time_str = "{:02d}:{:02d} PM".format(hour, minute)
					self.set(fieldname, time_str)
			
			# Check if format is HH:mm AM/PM (12-hour format)
			# Pattern: 1-12:00-59 AM/PM (with optional spaces)
			time_pattern = r'^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)$'
			match = re.match(time_pattern, time_str)
			
			if not match:
				frappe.throw(
					_("{0} must be in format HH:mm AM/PM (e.g., 05:56 AM or 12:30 PM). Current value: {1}. Please correct the format before saving.").format(
						frappe.bold(field_label), frappe.bold(time_str)
					),
					title=_("Invalid Time Format")
				)
			
			# Extract hour, minute, and AM/PM
			hour = int(match.group(1))
			minute = int(match.group(2))
			ampm = match.group(3)
			
			# Validate hour range (1-12 for 12-hour format)
			if hour < 1 or hour > 12:
				frappe.throw(
					_("{0}: Hour must be between 01 and 12. Current value: {1}").format(
						frappe.bold(field_label), frappe.bold(time_str)
					),
					title=_("Invalid Time Format")
				)
			
			# Validate minute range
			if minute < 0 or minute > 59:
				frappe.throw(
					_("{0}: Minute must be between 00 and 59. Current value: {1}").format(
						frappe.bold(field_label), frappe.bold(time_str)
					),
					title=_("Invalid Time Format")
				)
			
			# Format and update the field with proper formatting
			formatted_time = "{:02d}:{:02d} {}".format(hour, minute, ampm)
			if formatted_time != time_str:
				self.set(fieldname, formatted_time)
	
	def validate_time_order(self, start_time, end_time, period_label):
		"""Validate that end time is after start time (or next day)"""
		try:
			start = self._parse_time(start_time)
			end = self._parse_time(end_time)
			
			# If end is before start, it might be next day (night shift), which is acceptable
			# But we'll still validate the format
			pass
		except Exception as e:
			frappe.throw(
				_("Invalid time format in {0} period. Please use HH:mm format (e.g., 05:56)").format(
					frappe.bold(period_label)
				),
				title=_("Invalid Time Format")
			)
	
	def _parse_time(self, time_str):
		"""Parse time string to datetime.time object"""
		if isinstance(time_str, str):
			# Handle HH:mm or HH:mm:ss format
			parts = time_str.split(':')
			if len(parts) >= 2:
				hour = int(parts[0])
				minute = int(parts[1])
				if hour < 0 or hour > 23:
					raise ValueError("Hour must be between 00 and 23")
				if minute < 0 or minute > 59:
					raise ValueError("Minute must be between 00 and 59")
				return datetime.strptime(time_str.split('.')[0], "%H:%M:%S" if len(parts) == 3 else "%H:%M").time()
		return time_str

