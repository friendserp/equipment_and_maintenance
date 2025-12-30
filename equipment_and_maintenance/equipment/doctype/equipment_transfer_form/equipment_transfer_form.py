# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import re


class EquipmentTransferForm(Document):
	def before_insert(self):
		# Auto-fill transfer_ordered_by with current user
		if not self.transfer_ordered_by:
			self.transfer_ordered_by = frappe.session.user
	
	def validate(self):
		# Validate departure time format if provided
		if self.departure_time:
			self.validate_time_format()
	
	def validate_time_format(self):
		"""Validate that departure time is in HH:mm AM/PM format"""
		time_str = self.departure_time.strip().upper()
		
		# If AM is explicitly specified, use AM; otherwise default to PM
		if 'AM' in time_str:
			time_match = re.match(r'^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*AM$', time_str)
			if time_match:
				hour = int(time_match.group(1))
				minute = int(time_match.group(2))
				time_str = "{:02d}:{:02d} AM".format(hour, minute)
				self.departure_time = time_str
		elif 'PM' in time_str:
			time_match = re.match(r'^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*PM$', time_str)
			if time_match:
				hour = int(time_match.group(1))
				minute = int(time_match.group(2))
				time_str = "{:02d}:{:02d} PM".format(hour, minute)
				self.departure_time = time_str
		else:
			# No AM/PM specified, default to PM
			time_match = re.match(r'^([0]?[1-9]|1[0-2]):([0-5][0-9])$', time_str)
			if time_match:
				hour = int(time_match.group(1))
				minute = int(time_match.group(2))
				time_str = "{:02d}:{:02d} PM".format(hour, minute)
				self.departure_time = time_str
		
		# Validate final format
		time_pattern = r'^([0]?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)$'
		if not re.match(time_pattern, time_str):
			frappe.throw(
				_("Departure Time must be in format HH:mm AM/PM (e.g., 05:56 AM or 12:30 PM). Current value: {0}").format(
					frappe.bold(time_str)
				),
				title=_("Invalid Time Format")
			)

