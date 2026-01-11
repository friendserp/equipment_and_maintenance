# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TyreRequestandAnalysisForm(Document):
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
		"""Create Tyre Recording Database Form when this document is submitted"""
		self.create_tyre_recording_database()
	
	def calculate_analysis_items(self):
		"""Calculate actual coverage, deviation for each analysis item"""
		if self.analysis_items:
			for item in self.analysis_items:
				# Calculate actual coverage (b) = Current Reading - Fitted Reading
				if item.current_km_reading and item.fitted_km_reading:
					item.actual_coverage = item.current_km_reading - item.fitted_km_reading
				else:
					item.actual_coverage = 0
				
				# Calculate deviation (c) = b - a
				if item.actual_coverage and item.standard_life_time:
					item.deviation = item.actual_coverage - item.standard_life_time
				else:
					item.deviation = 0
	
	def create_tyre_recording_database(self):
		"""Create Tyre Recording Database Form with data from this form"""
		if not self.requested_items or len(self.requested_items) == 0:
			frappe.throw("Cannot create Tyre Recording Database Form without requested items.")
		
		# Check if Tyre Recording Database Form already exists for this equipment
		existing_trd = frappe.db.get_value("Tyre Recording Database Form", {
			"plate_no": self.plate_no,
			"tyre_request_form": self.name
		}, "name")
		
		if existing_trd:
			frappe.msgprint(f"Tyre Recording Database Form {existing_trd} already exists for this request.")
			return
		
		# Create new Tyre Recording Database Form
		trd_doc = frappe.get_doc({
			"doctype": "Tyre Recording Database Form",
			"effective_date": self.request_date or frappe.utils.nowdate(),
			"issue_no": 1,  # Default issue number
			"equipment_type": self.equipment_type,
			"make": self.make,
			"model": self.model,
			"serial_no": self.serial_no,
			"plate_no": self.plate_no,
			"tyre_request_form": self.name,
			"status": "Draft"
		})
		
		# Populate old tyre items (consolidated from old_tyre_items in request form)
		if self.old_tyre_items:
			ref_counter = 1
			current_ref = None
			item_counter = 1
			
			for old_item in self.old_tyre_items:
				trd_old_item = trd_doc.append("old_tyre_items", {})
				
				# Set reference number based on position
				position_key = old_item.tyre_position or "Default"
				if current_ref != position_key:
					current_ref = position_key
					ref_counter = len([x for x in trd_doc.old_tyre_items if x.reference_no]) + 1
					item_counter = 1
				
				trd_old_item.reference_no = f"Ref-{ref_counter}"
				trd_old_item.item_no = item_counter
				item_counter += 1
				
				# Map old tyre data
				trd_old_item.tyre_brand = old_item.tyre_brand
				trd_old_item.tyre_position = old_item.tyre_position
				trd_old_item.serial_no = old_item.serial_no
				trd_old_item.tyre_size = old_item.tyre_size
				trd_old_item.tyre_type = old_item.tyre_type
				trd_old_item.quantity = old_item.quantity
				trd_old_item.fitted_km_reading = old_item.fitted_km_reading
				trd_old_item.fitted_date = old_item.fitted_date
				trd_old_item.unit_price = old_item.unit_price
		
		# Populate new tyre items (from requested_items in request form)
		if self.requested_items:
			ref_counter = 1
			current_ref = None
			item_counter = 1
			
			for req_item in self.requested_items:
				trd_new_item = trd_doc.append("new_tyre_items", {})
				
				# Set reference number based on position
				position_key = req_item.requested_tyre_position or "Default"
				if current_ref != position_key:
					current_ref = position_key
					ref_counter = len([x for x in trd_doc.new_tyre_items if x.reference_no]) + 1
					item_counter = 1
				
				trd_new_item.reference_no = f"Ref-{ref_counter}"
				trd_new_item.item_no = item_counter
				item_counter += 1
				
				# Map new tyre data (from requested tyre)
				trd_new_item.tyre_position = req_item.requested_tyre_position
				trd_new_item.tyre_size = req_item.requested_tyre_size
				trd_new_item.tyre_brand = req_item.requested_tyre_brand
				trd_new_item.tyre_type = req_item.requested_tyre_type
				trd_new_item.quantity = req_item.quantity or 1
		
		# Populate analysis items (from analysis_items in request form)
		if self.analysis_items:
			ref_counter = 1
			current_ref = None
			item_counter = 1
			
			for analysis_item in self.analysis_items:
				trd_analysis_item = trd_doc.append("analysis_items", {})
				
				# Set reference number based on position
				position_key = analysis_item.tyre_position or "Default"
				if current_ref != position_key:
					current_ref = position_key
					ref_counter = len([x for x in trd_doc.analysis_items if x.reference_no]) + 1
					item_counter = 1
				
				trd_analysis_item.reference_no = f"Ref-{ref_counter}"
				trd_analysis_item.item_no = item_counter
				item_counter += 1
				
				# Map analysis data
				trd_analysis_item.tyre_position = analysis_item.tyre_position
				trd_analysis_item.tyre_size = analysis_item.tyre_size
				trd_analysis_item.tyre_brand = analysis_item.tyre_brand
				trd_analysis_item.tyre_type = analysis_item.tyre_type
				trd_analysis_item.old_fitted_km_reading = analysis_item.fitted_km_reading
				trd_analysis_item.standard_life_time = analysis_item.standard_life_time
				trd_analysis_item.actual_coverage = analysis_item.actual_coverage
				trd_analysis_item.deviation = analysis_item.deviation
				trd_analysis_item.reason_for_less_consumption = analysis_item.reason_for_less_consumption
				
				# Find matching old tyre item for old_fitted_km_reading
				if self.old_tyre_items:
					matching_old = next((item for item in self.old_tyre_items 
						if item.tyre_position == analysis_item.tyre_position), None)
					if matching_old:
						trd_analysis_item.old_fitted_km_reading = matching_old.fitted_km_reading
		
		# Insert the document
		trd_doc.insert(ignore_permissions=True)
		
		frappe.msgprint(f"Tyre Recording Database Form {trd_doc.name} created successfully.")

