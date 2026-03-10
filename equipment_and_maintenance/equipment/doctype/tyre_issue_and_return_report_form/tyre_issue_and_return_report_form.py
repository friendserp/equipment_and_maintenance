# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class TyreIssueandReturnReportForm(Document):
	def before_insert(self):
		# Auto-populate prepared_by on creation
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		if not self.prepared_by_date:
			self.prepared_by_date = frappe.utils.today()
	
	def validate(self):
		self.calculate_tyre_items()
		self.auto_populate_workflow_fields()
		self.validate_tyre_recording_database()
	
	def validate_tyre_recording_database(self):
		"""Validate that serial_no (Tyre Recording Database) is set for all items before submission"""
		if self.tyre_items:
			for item in self.tyre_items:
				if not item.serial_no:
					item_code = item.item_code or "N/A"
					position = item.tyre_position or ""
					size = item.tyre_size or ""
					brand = item.tyre_brand or ""
					frappe.throw(_("Tyre Serial No (Tyre Recording Database) is required for item {0} (Row {1}). Please select a tyre from the database. Item: {2}, Position: {3}, Size: {4}, Brand: {5}").format(
						item_code, item.idx, item_code, position, size, brand))
	
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
	
	def calculate_tyre_items(self):
		"""Calculate actual coverage, deviation for each tyre item based on Tyre Recording Database"""
		if self.type == "Return" and self.current_km_hr:
			current_reading = self.current_km_hr
		else:
			current_reading = self.get_current_equipment_reading()
		
		for item in self.tyre_items:
			if not item.serial_no:
				continue
			
			# Fetch from Tyre Recording Database using serial_no
			trd = frappe.get_doc("Tyre Recording Database", item.serial_no)
			
			# Auto-populate fields from Tyre Recording Database
			if not item.tyre_brand:
				item.tyre_brand = trd.tyre_brand
			if not item.tyre_position:
				item.tyre_position = trd.tyre_position
			if not item.tyre_size:
				item.tyre_size = trd.tyre_size
			if not item.tyre_type:
				item.tyre_type = trd.tyre_type
			
			# For Issue type: Set fitted reading and date
			if self.type == "Issue":
				if not item.fitted_km_reading:
					item.fitted_km_reading = current_reading
				if not item.fitted_date:
					item.fitted_date = self.effective_date or frappe.utils.today()
			
			# For Return type: Calculate analysis from old fitted reading
			if self.type == "Return" and trd.fitted_hours_km:
				old_fitted_reading = trd.fitted_hours_km
				if self.current_km_hr:
					current_reading_for_calc = self.current_km_hr
				else:
					current_reading_for_calc = current_reading or item.fitted_km_reading
				
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
			
			# Item code should be set from the request or tyre database
			if not item.item_code and item.serial_no:
				item.item_code = trd.item_code
	
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
		"""Get standard life time for tyre"""
		if item.serial_no:
			item_code = frappe.db.get_value("Tyre Recording Database", item.serial_no, "item_code")
			if item_code:
				try:
					item_meta = frappe.get_meta("Item")
					field_names = [f.fieldname for f in item_meta.fields]
					
					if "standard_life_time" in field_names:
						standard_life = frappe.db.get_value("Item", item_code, "standard_life_time")
						return standard_life or 0
					elif "custom_standard_life_time" in field_names:
						standard_life = frappe.db.get_value("Item", item_code, "custom_standard_life_time")
						return standard_life or 0
				except Exception as e:
					frappe.log_error(f"Error getting standard_life_time for item {item_code}: {str(e)}", "Tyre Standard Life Time")
					pass
		return 0
	
	def on_submit(self):
		"""Update Tyre Recording Database records when Issue/Return is submitted"""
		current_reading = self.get_current_equipment_reading()
		
		if not self.tyre_items:
			return
		
		for item in self.tyre_items:
			if not item.serial_no:
				frappe.throw(_("Tyre Serial No (Tyre Recording Database) is required for all items. Please select a tyre for item {0} (Row {1})").format(
					item.item_code or "N/A", item.idx))
				continue
			
			if self.type == "Issue":
				if not self.plate_no:
					frappe.throw(_("Plate No is required to submit an Issue"))
				
				trd = frappe.get_doc("Tyre Recording Database", item.serial_no)
				trd.tyre_status = "Fitted"
				trd.current_equipment = self.plate_no
				trd.fitted_date = item.fitted_date or self.effective_date or frappe.utils.today()
				trd.fitted_hours_km = item.fitted_km_reading or current_reading or 0
				if self.tyre_request_form:
					trd.last_tyre_request = self.tyre_request_form
				trd.save(ignore_permissions=True)
				frappe.db.commit()
			
			elif self.type == "Return":
				trd = frappe.get_doc("Tyre Recording Database", item.serial_no)
				trd.tyre_status = "Returned"
				trd.current_equipment = None
				trd.fitted_date = None
				trd.fitted_hours_km = None
				trd.last_tyre_return = self.name
				trd.save(ignore_permissions=True)
				frappe.db.commit()
	
	def on_cancel(self):
		"""Reverse Tyre Recording Database updates when Issue/Return is cancelled"""
		if not self.tyre_items:
			return
		
		for item in self.tyre_items:
			if not item.serial_no:
				continue
			
			if self.type == "Issue":
				trd = frappe.get_doc("Tyre Recording Database", item.serial_no)
				trd.tyre_status = "Available"
				trd.current_equipment = None
				trd.fitted_date = None
				trd.fitted_hours_km = None
				trd.save(ignore_permissions=True)
				frappe.db.commit()
			
			elif self.type == "Return":
				trd = frappe.get_doc("Tyre Recording Database", item.serial_no)
				trd.tyre_status = "Fitted"
				trd.save(ignore_permissions=True)
				frappe.db.commit()

@frappe.whitelist()
def get_current_equipment_reading(equipment):
	"""Get current hours/km reading for the equipment (whitelisted for JS)"""
	if not equipment:
		return 0
	
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
def get_tyre_request_items(request_name):
	"""Get Tyre Request Items with all fields"""
	if not request_name:
		return []
	
	items = frappe.get_all(
		"Tyre Request Item",
		filters={
			"parent": request_name,
			"parenttype": "Tyre Request and Analysis Form"
		},
		fields=["name", "requested_item_no", "requested_tyre_size", "requested_tyre_brand", "requested_tyre_type", "requested_tyre_position", "quantity"],
		order_by="idx"
	)
	
	return items
