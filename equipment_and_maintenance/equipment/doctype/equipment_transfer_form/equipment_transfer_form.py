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
		# Auto-populate workflow fields
		self.auto_populate_workflow_fields()
		

		
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		if self.workflow_state == "Approved":
			if not self.approved_by:
				self.approved_by = frappe.session.user
	
	def before_submit(self):
		"""Ensure from_project and current_operator are set from Equipment Master before submitting"""
		if not self.equipment_plate_no:
			return
		
		# Get current Equipment Master values and ensure they're stored in from_project and current_operator
		equipment = frappe.get_doc("Equipment Master", self.equipment_plate_no)
		
		# Store current values if not already set (these represent the "previous" values before transfer)
		if not self.from_project and equipment.location:
			self.from_project = equipment.location
		
		if not self.current_operator and equipment.operators_name:
			self.current_operator = equipment.operators_name
	
	def on_submit(self):
		"""Update Equipment Master when transfer is submitted"""
		if not self.equipment_plate_no:
			return
		
		# Get current Equipment Master
		equipment = frappe.get_doc("Equipment Master", self.equipment_plate_no)
		
		# Update project (always update)
		if self.receiving_project:
			equipment.location = self.receiving_project
		
		# Update operator if different from current operator in Equipment Master
		current_operator = equipment.operators_name
		operator_updated = False
		if self.operator_driver_name and self.operator_driver_name != current_operator:
			equipment.operators_name = self.operator_driver_name
			operator_updated = True
		
		# Save Equipment Master
		equipment.save(ignore_permissions=True)
		
		# Show appropriate message
		if operator_updated:
			frappe.msgprint(
				_("Equipment Master updated: Project set to {0}, Operator updated to {1}").format(
					frappe.bold(self.receiving_project),
					frappe.bold(self.operator_driver_name)
				),
				indicator="green",
				alert=True
			)
		else:
			frappe.msgprint(
				_("Equipment Master updated: Project set to {0}").format(
					frappe.bold(self.receiving_project)
				),
				indicator="green",
				alert=True
			)
	
	def before_cancel(self):
		"""Set workflow state to Cancelled before cancelling"""
		self.workflow_state = "Cancelled"
	
	def on_cancel(self):
		"""Revert Equipment Master changes when transfer is cancelled"""
		if not self.equipment_plate_no:
			return
		
		# Revert to previous values (stored in from_project and current_operator)
		equipment = frappe.get_doc("Equipment Master", self.equipment_plate_no)
		
		if self.from_project:
			equipment.location = self.from_project
		
		if self.current_operator:
			equipment.operators_name = self.current_operator
		
		# Save Equipment Master
		equipment.save(ignore_permissions=True)
		frappe.msgprint(
			_("Equipment Master reverted to previous values"),
			indicator="blue",
			alert=True
		)
	
	def on_trash(self):
		"""Revert Equipment Master changes when transfer is deleted"""
		# Only revert if document was submitted (has previous values stored in from_project and current_operator)
		if self.docstatus == 1 and self.equipment_plate_no:
			equipment = frappe.get_doc("Equipment Master", self.equipment_plate_no)
			
			if self.from_project:
				equipment.location = self.from_project
			
			if self.current_operator:
				equipment.operators_name = self.current_operator
			
			# Save Equipment Master
			equipment.save(ignore_permissions=True)
			frappe.msgprint(
				_("Equipment Master reverted to previous values"),
				indicator="blue",
				alert=True
			)

