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
		self.calculate_analysis_items()
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
	
	def on_submit(self):
		"""Create Battery Recording Database Form when this document is submitted"""
		self.create_battery_recording_database()
	
	def calculate_analysis_items(self):
		"""Calculate actual coverage, deviation for each analysis item"""
		if self.analysis_items:
			for item in self.analysis_items:
				# Calculate actual coverage (b) = Current Reading - Fitted Reading
				if item.current_km_hour_reading and item.fitted_hr_reading:
					item.actual_coverage = item.current_km_hour_reading - item.fitted_hr_reading
				else:
					item.actual_coverage = 0
				
				# Calculate deviation (c) = b - a
				if item.actual_coverage and item.standard_life_time:
					item.deviation = item.actual_coverage - item.standard_life_time
				else:
					item.deviation = 0
	
	def create_battery_recording_database(self):
		"""Create Battery Recording Database Form with data from this form"""
		if not self.requested_items or len(self.requested_items) == 0:
			frappe.throw("Cannot create Battery Recording Database Form without requested items.")
		
		# Check if Battery Recording Database Form already exists for this equipment
		existing_brd = frappe.db.get_value("Battery Recording Database Form", {
			"plate_no": self.plate_no,
			"battery_request_form": self.name
		}, "name")
		
		if existing_brd:
			frappe.msgprint(f"Battery Recording Database Form {existing_brd} already exists for this request.")
			return
		
		# Create new Battery Recording Database Form
		brd_doc = frappe.get_doc({
			"doctype": "Battery Recording Database Form",
			"effective_date": self.request_date or frappe.utils.nowdate(),
			"issue_no": 1,  # Default issue number
			"equipment_type": self.equipment_type,
			"make": self.make,
			"model": self.model,
			"serial_no": self.serial_no,
			"plate_no": self.plate_no,
			"battery_request_form": self.name,
			"status": "Draft"
		})
		
		# Populate old battery items (consolidated from old_battery_items in request form)
		if self.old_battery_items:
			ref_counter = 1
			current_ref = None
			item_counter = 1
			
			for old_item in self.old_battery_items:
				brd_old_item = brd_doc.append("old_battery_items", {})
				
				# Set reference number based on position
				position_key = old_item.battery_position or "Default"
				if current_ref != position_key:
					current_ref = position_key
					ref_counter = len([x for x in brd_doc.old_battery_items if x.reference_no]) + 1
					item_counter = 1
				
				brd_old_item.reference_no = f"Ref-{ref_counter}"
				brd_old_item.item_no = item_counter
				item_counter += 1
				
				# Map old battery data
				brd_old_item.battery_make = old_item.battery_make
				brd_old_item.battery_position = old_item.battery_position
				brd_old_item.serial_no = old_item.serial_no
				brd_old_item.battery_voltage = old_item.battery_voltage
				brd_old_item.battery_amper = old_item.battery_amper
				brd_old_item.quantity = old_item.quantity
				brd_old_item.fitted_hr_reading = old_item.fitted_hr_reading
				brd_old_item.fitted_date = old_item.fitted_date
				brd_old_item.unit_price = old_item.unit_price
		
		# Populate new battery items (from requested_items in request form)
		if self.requested_items:
			ref_counter = 1
			current_ref = None
			item_counter = 1
			
			for req_item in self.requested_items:
				brd_new_item = brd_doc.append("new_battery_items", {})
				
				# Set reference number based on position
				position_key = req_item.requested_battery_position or "Default"
				if current_ref != position_key:
					current_ref = position_key
					ref_counter = len([x for x in brd_doc.new_battery_items if x.reference_no]) + 1
					item_counter = 1
				
				brd_new_item.reference_no = f"Ref-{ref_counter}"
				brd_new_item.item_no = item_counter
				item_counter += 1
				
				# Map new battery data (from requested battery)
				brd_new_item.battery_position = req_item.requested_battery_position
				brd_new_item.battery_voltage = req_item.requested_battery_voltage
				brd_new_item.battery_amper = req_item.requested_battery_amper
				brd_new_item.quantity = req_item.quantity or 1
		
		# Populate analysis items (from analysis_items in request form)
		if self.analysis_items:
			ref_counter = 1
			current_ref = None
			item_counter = 1
			
			for analysis_item in self.analysis_items:
				brd_analysis_item = brd_doc.append("analysis_items", {})
				
				# Set reference number based on position
				position_key = analysis_item.battery_position or "Default"
				if current_ref != position_key:
					current_ref = position_key
					ref_counter = len([x for x in brd_doc.analysis_items if x.reference_no]) + 1
					item_counter = 1
				
				brd_analysis_item.reference_no = f"Ref-{ref_counter}"
				brd_analysis_item.item_no = item_counter
				item_counter += 1
				
				# Map analysis data
				brd_analysis_item.battery_position = analysis_item.battery_position
				brd_analysis_item.battery_voltage = analysis_item.battery_voltage
				brd_analysis_item.battery_amper = analysis_item.battery_amper
				brd_analysis_item.old_fitted_hr_reading = analysis_item.fitted_hr_reading
				brd_analysis_item.standard_life_time = analysis_item.standard_life_time
				brd_analysis_item.actual_coverage = analysis_item.actual_coverage
				brd_analysis_item.deviation = analysis_item.deviation
				brd_analysis_item.reason_for_less_consumption = analysis_item.reason_for_less_consumption
				
				# Find matching old battery item for old_fitted_hr_reading
				if self.old_battery_items:
					matching_old = next((item for item in self.old_battery_items 
						if item.battery_position == analysis_item.battery_position), None)
					if matching_old:
						brd_analysis_item.old_fitted_hr_reading = matching_old.fitted_hr_reading
		
		# Insert the document
		brd_doc.insert(ignore_permissions=True)
		
		frappe.msgprint(f"Battery Recording Database Form {brd_doc.name} created successfully.")

