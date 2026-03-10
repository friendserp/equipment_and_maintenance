# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TyreRecordingDatabaseForm(Document):
	def before_insert(self):
		# Auto-populate prepared_by on creation
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		if not self.prepared_by_date:
			self.prepared_by_date = frappe.utils.today()
	
	def validate(self):
		self.auto_set_reference_numbers()
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
	
	def auto_set_reference_numbers(self):
		"""Auto-set reference numbers and item numbers for all tables"""
		# Set reference numbers for old tyre items
		if self.old_tyre_items:
			self._set_ref_numbers(self.old_tyre_items)
		
		# Set reference numbers for new tyre items
		if self.new_tyre_items:
			self._set_ref_numbers(self.new_tyre_items)
		
		# Set reference numbers for analysis items
		if self.analysis_items:
			self._set_ref_numbers(self.analysis_items)
	
	def _set_ref_numbers(self, items):
		"""Helper method to set reference numbers for a list of items"""
		current_ref = None
		ref_counter = 1
		item_counter = 1
		
		for item in items:
			# If reference_no is not set, generate it
			if not item.reference_no:
				item.reference_no = f"Ref-{ref_counter}"
			
			# If this is a new reference, reset item counter
			if item.reference_no != current_ref:
				current_ref = item.reference_no
				item_counter = 1
			
			# Set item number
			if not item.item_no:
				item.item_no = item_counter
			
			item_counter += 1
	
	def calculate_analysis_items(self):
		"""Calculate actual coverage, deviation for each analysis item"""
		if self.analysis_items:
			for item in self.analysis_items:
				# Calculate actual coverage (b) = New Fitted Reading - Old Fitted Reading
				if item.new_fitted_km_reading and item.old_fitted_km_reading:
					item.actual_coverage = item.new_fitted_km_reading - item.old_fitted_km_reading
				else:
					item.actual_coverage = 0
				
				# Calculate deviation (c) = b - a
				if item.actual_coverage and item.standard_life_time:
					item.deviation = item.actual_coverage - item.standard_life_time
				else:
					item.deviation = 0

