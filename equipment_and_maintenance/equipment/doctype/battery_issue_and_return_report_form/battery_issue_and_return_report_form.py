# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class BatteryIssueandReturnReportForm(Document):
	def before_insert(self):
		# Auto-populate prepared_by on creation
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		if not self.prepared_by_date:
			self.prepared_by_date = frappe.utils.today()
	
	def validate(self):
		self.calculate_battery_items()
		self.auto_populate_workflow_fields()
		self.validate_battery_recording_database()
	
	def validate_battery_recording_database(self):
		"""Validate that serial_no (Battery Recording Database) is set for all items before submission"""
		# Only validate if document is being saved/submitted (not during draft)
		if self.battery_items:
			for item in self.battery_items:
				# Use serial_no as it's the link field to Battery Recording Database
				if not item.serial_no:
					# Get item details for better error message
					item_code = item.item_code or "N/A"
					position = item.battery_position or ""
					voltage = item.battery_voltage or ""
					amper = item.battery_amper or ""
					frappe.throw(_("Battery Serial No (Battery Recording Database) is required for item {0} (Row {1}). Please select a battery from the database. Item: {2}, Position: {3}, Voltage: {4}V, Amper: {5}A").format(
						item_code, item.idx, item_code, position, voltage, amper))
	
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
	
	def calculate_battery_items(self):
		"""Calculate actual coverage, deviation for each battery item based on Battery Recording Database"""
		# Get current reading - use current_km_hr if set (for Return type), otherwise get from equipment
		if self.type == "Return" and self.current_km_hr:
			current_reading = self.current_km_hr
		else:
			current_reading = self.get_current_equipment_reading()
		
		for item in self.battery_items:
			# Use serial_no as it's the link field to Battery Recording Database
			if not item.serial_no:
				continue
			
			# Fetch from Battery Recording Database using serial_no
			brd = frappe.get_doc("Battery Recording Database", item.serial_no)
			
			# Auto-populate fields from Battery Recording Database
			if not item.battery_make:
				item.battery_make = brd.battery_make
			if not item.battery_position:
				item.battery_position = brd.battery_position
			if not item.serial_no:
				item.serial_no = brd.battery_serial_no
			if not item.battery_voltage:
				item.battery_voltage = brd.battery_voltage
			if not item.battery_amper:
				item.battery_amper = brd.battery_amper
			
			# For Issue type: Set fitted reading and date
			if self.type == "Issue":
				if not item.fitted_hr_reading:
					item.fitted_hr_reading = current_reading
				if not item.fitted_date:
					item.fitted_date = self.effective_date or frappe.utils.today()
			
			# For Return type: Calculate analysis from old fitted reading
			if self.type == "Return" and brd.fitted_hours_km:
				old_fitted_reading = brd.fitted_hours_km
				# Use current_km_hr from document if set, otherwise use current_reading or item's fitted reading
				if self.current_km_hr:
					current_reading_for_calc = self.current_km_hr
				else:
					current_reading_for_calc = current_reading or item.fitted_hr_reading
				
				if current_reading_for_calc and old_fitted_reading:
					item.actual_coverage = current_reading_for_calc - old_fitted_reading
				else:
					item.actual_coverage = 0
				
				# Get standard life time
				standard_life_time = self.get_standard_life_time(item)
				item.standard_life_time = standard_life_time
				
				# Calculate deviation (c) = b - a
				if item.actual_coverage and standard_life_time:
					item.deviation = item.actual_coverage - standard_life_time
				else:
					item.deviation = 0
			
			# Item code should be set from the request or battery database
			if not item.item_code and item.serial_no:
				item.item_code = brd.item_code
	
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
	
	def get_standard_life_time(self, item):
		"""Get standard life time for battery"""
		# Try to get from Battery Recording Database or Item using serial_no
		if item.serial_no:
			item_code = frappe.db.get_value("Battery Recording Database", item.serial_no, "item_code")
			if item_code:
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
	
	def on_submit(self):
		"""Update Battery Recording Database records when Issue/Return is submitted"""
		frappe.log_error(f"on_submit called for {self.name}, type: {self.type}", "Battery Issue Submit")
		current_reading = self.get_current_equipment_reading()
		
		if not self.battery_items:
			frappe.log_error(f"No battery_items found in {self.name}", "Battery Issue Submit")
			return
		
		for item in self.battery_items:
			# Check if serial_no (Battery Recording Database link) is set
			if not item.serial_no:
				frappe.log_error(f"Item {item.name} (idx: {item.idx}) has no serial_no. Item data: {item.as_dict()}", "Battery Issue Submit")
				frappe.throw(_("Battery Serial No (Battery Recording Database) is required for all items. Please select a battery for item {0} (Row {1})").format(
					item.item_code or "N/A", item.idx))
				continue
			
			frappe.log_error(f"Processing item: {item.name}, serial_no: {item.serial_no}", "Battery Issue Submit")
			
			if self.type == "Issue":
				# Verify required values exist
				if not self.plate_no:
					frappe.throw(_("Plate No is required to submit an Issue"))
				
				# Get the Battery Recording Database document using serial_no
				brd = frappe.get_doc("Battery Recording Database", item.serial_no)
				
				# Update Battery Recording Database status to Fitted
				brd.battery_status = "Fitted"
				brd.current_equipment = self.plate_no
				# current_plate_no is fetch_from current_equipment.plate_number, so it will be auto-populated
				brd.fitted_date = item.fitted_date or self.effective_date or frappe.utils.today()
				brd.fitted_hours_km = item.fitted_hr_reading or current_reading or 0
				if self.battery_request_form:
					brd.last_battery_request = self.battery_request_form
				
				frappe.log_error(f"Updating Battery Recording Database {item.serial_no} - Status: {brd.battery_status}, Equipment: {brd.current_equipment}, Date: {brd.fitted_date}, Hours: {brd.fitted_hours_km}", "Battery Issue Submit")
				brd.save(ignore_permissions=True)
				frappe.db.commit()
				
				# Verify the update worked
				updated_status = frappe.db.get_value("Battery Recording Database", item.serial_no, "battery_status")
				updated_equipment = frappe.db.get_value("Battery Recording Database", item.serial_no, "current_equipment")
				frappe.log_error(f"After update - Status: {updated_status}, Equipment: {updated_equipment}", "Battery Issue Submit")
			
			elif self.type == "Return":
				# Update Battery Recording Database status to Returned
				brd = frappe.get_doc("Battery Recording Database", item.serial_no)
				
				brd.battery_status = "Returned"
				brd.current_equipment = None
				brd.fitted_date = None
				brd.fitted_hours_km = None
				brd.last_battery_return = self.name
				
				frappe.log_error(f"Updating Battery Recording Database {item.serial_no} - Status: {brd.battery_status}", "Battery Return Submit")
				brd.save(ignore_permissions=True)
				frappe.db.commit()
	
	def on_cancel(self):
		"""Reverse Battery Recording Database updates when Issue/Return is cancelled"""
		frappe.log_error(f"on_cancel called for {self.name}, type: {self.type}", "Battery Issue Cancel")
		
		if not self.battery_items:
			frappe.log_error(f"No battery_items found in {self.name}", "Battery Issue Cancel")
			return
		
		for item in self.battery_items:
			if not item.serial_no:
				frappe.log_error(f"Item {item.name} has no serial_no", "Battery Issue Cancel")
				continue
			
			frappe.log_error(f"Processing item: {item.name}, serial_no: {item.serial_no}", "Battery Issue Cancel")
			
			if self.type == "Issue":
				# Reverse Issue: Set status back to Available and clear equipment
				brd = frappe.get_doc("Battery Recording Database", item.serial_no)
				
				brd.battery_status = "Available"
				brd.current_equipment = None
				brd.fitted_date = None
				brd.fitted_hours_km = None
				
				frappe.log_error(f"Cancelling - Updating Battery Recording Database {item.serial_no} - Status: {brd.battery_status}", "Battery Issue Cancel")
				brd.save(ignore_permissions=True)
				frappe.db.commit()
			
			elif self.type == "Return":
				# Reverse Return: Set status back to Fitted
				# The equipment info should already be there from the original Issue
				# We just need to set status back to Fitted and clear the return link
				brd = frappe.get_doc("Battery Recording Database", item.serial_no)
				
				brd.battery_status = "Fitted"
				brd.last_battery_return = None
				
				frappe.log_error(f"Cancelling - Updating Battery Recording Database {item.serial_no} - Status: {brd.battery_status}", "Battery Return Cancel")
				brd.save(ignore_permissions=True)
				frappe.db.commit()

@frappe.whitelist()
def get_current_equipment_reading(equipment):
	"""Get current hours/km reading for the equipment (whitelisted for JS)"""
	if not equipment:
		return 0
	
	# Try to get from latest PM Done
	latest_pm = frappe.db.get_all(
		"Preventive Maintenance Done",
		filters={"equipment": equipment, "docstatus": 1},
		fields=["actual_hours_km"],
		order_by="actual_date DESC",
		limit=1
	)
	
	if latest_pm and latest_pm[0].get("actual_hours_km"):
		return latest_pm[0].actual_hours_km
	
	return 0

@frappe.whitelist()
def get_battery_request_items(request_name):
	"""Get Battery Request Items with all fields"""
	if not request_name:
		return []
	
	items = frappe.get_all(
		"Battery Request Item",
		filters={
			"parent": request_name,
			"parenttype": "Battery Request and Analysis Form"
		},
		fields=["name", "requested_item_no", "requested_battery_voltage", "requested_battery_amper", "requested_battery_position", "quantity"],
		order_by="idx"
	)
	
	return items
