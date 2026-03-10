# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BatteryRequestandAnalysisForm(Document):
	def before_insert(self):
		# Auto-populate prepared_by on creation
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		if not self.prepared_by_date:
			self.prepared_by_date = frappe.utils.today()
	
	def validate(self):
		self.remove_duplicate_old_batteries()
		self.calculate_analysis_items()
		self.auto_populate_workflow_fields()
	
	def remove_duplicate_old_batteries(self):
		"""Remove duplicate battery_recording_database entries from old_battery_items"""
		if not self.old_battery_items:
			return
		
		seen = set()
		to_remove = []
		
		for idx, item in enumerate(self.old_battery_items):
			if item.battery_recording_database:
				if item.battery_recording_database in seen:
					to_remove.append(idx)
				else:
					seen.add(item.battery_recording_database)
		
		# Remove duplicates in reverse order to maintain indices
		for idx in reversed(to_remove):
			self.remove(self.old_battery_items[idx])
	
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
	
	def on_submit(self):
		# Do not create database records on submit
		# Database records will be created when batteries are issued via Issue and Return form
		pass
	
	def calculate_analysis_items(self):
		"""Calculate actual coverage, deviation for each analysis item based on old battery items"""
		if not self.plate_no:
			return
		
		# Get current reading - use current_km_hr if set, otherwise get from equipment
		if self.current_km_hr:
			current_reading = self.current_km_hr
		else:
			current_reading = self.get_current_equipment_reading()
		
		# Clear and rebuild analysis items from old battery items
		if self.old_battery_items:
			self.analysis_items = []
			
			for old_item in self.old_battery_items:
				# Get fitted reading from old battery item
				fitted_reading = old_item.fitted_hr_reading
				battery_position = old_item.battery_position
				
				# Create analysis item
				analysis_item = self.append("analysis_items", {})
				analysis_item.battery_position = battery_position
				analysis_item.battery_voltage = old_item.battery_voltage
				analysis_item.battery_amper = old_item.battery_amper
				analysis_item.fitted_hr_reading = fitted_reading
				analysis_item.current_km_hour_reading = current_reading
				
				# Calculate actual coverage (b) = Current Reading - Fitted Reading
				if current_reading and fitted_reading:
					analysis_item.actual_coverage = current_reading - fitted_reading
				else:
					analysis_item.actual_coverage = 0
				
				# Get standard life time from item if available
				# Try to get item_code from Battery Recording Database if linked
				item_code = None
				if hasattr(old_item, 'battery_recording_database') and old_item.battery_recording_database:
					item_code = frappe.db.get_value("Battery Recording Database", old_item.battery_recording_database, "item_code")
				
				if item_code:
					standard_life_time = self.get_standard_life_time(item_code)
					analysis_item.standard_life_time = standard_life_time
					
					# Calculate deviation (c) = b - a
					if analysis_item.actual_coverage and standard_life_time:
						analysis_item.deviation = analysis_item.actual_coverage - standard_life_time
					else:
						analysis_item.deviation = 0
				else:
					analysis_item.standard_life_time = 0
					analysis_item.deviation = 0
	
	def get_current_equipment_reading(self):
		"""Get current hours/km reading for the equipment"""
		if not self.plate_no:
			return 0
		
		# Try to get from latest PM Done
		latest_pm = frappe.db.get_all(
			"Preventive Maintenance Done",
			filters={"equipment": self.plate_no, "docstatus": 1},
			fields=["actual_hours_km"],
			order_by="actual_date DESC",
			limit=1
		)
		
		if latest_pm and latest_pm[0].get("actual_hours_km"):
			return latest_pm[0].actual_hours_km
		
		return 0
	
	def get_standard_life_time(self, item_code):
		"""Get standard life time for battery item"""
		if not item_code:
			return 0
		
		# Try to get standard_life_time field (check if it exists first)
		try:
			# Check if field exists in Item meta
			item_meta = frappe.get_meta("Item")
			field_names = [f.fieldname for f in item_meta.fields]
			
			# Try standard_life_time first, then custom_standard_life_time
			if "standard_life_time" in field_names:
				standard_life = frappe.db.get_value("Item", item_code, "standard_life_time")
				return standard_life or 0
			elif "custom_standard_life_time" in field_names:
				standard_life = frappe.db.get_value("Item", item_code, "custom_standard_life_time")
				return standard_life or 0
		except Exception as e:
			# If field doesn't exist or any error, return 0
			frappe.log_error(f"Error getting standard_life_time for item {item_code}: {str(e)}", "Battery Standard Life Time")
			pass
		return 0
	
