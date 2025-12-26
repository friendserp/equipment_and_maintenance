# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MaintenanceWorkOrder(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_dates()
	
	def calculate_totals(self):
		"""Calculate all totals for cost categories"""
		# Calculate total labor cost
		total_labor = 0
		if self.labor_cost_items:
			for row in self.labor_cost_items:
				if row.total_cost:
					total_labor += flt(row.total_cost)
		self.total_labor_cost = total_labor
		
		# Calculate total spare parts cost
		total_spare_parts = 0
		if self.spare_cost_items:
			for row in self.spare_cost_items:
				if row.total_cost:
					total_spare_parts += flt(row.total_cost)
		self.total_spare_parts_cost = total_spare_parts
		
		# Calculate total lubricants cost
		total_lubricants = 0
		if self.lubricant_cost_items:
			for row in self.lubricant_cost_items:
				if row.total_price:
					total_lubricants += flt(row.total_price)
		self.total_lubricants_cost = total_lubricants
		
		# Calculate total miscellaneous item cost
		total_miscellaneous = 0
		if self.miscellaneous_cost_items:
			for row in self.miscellaneous_cost_items:
				if row.total_cost:
					total_miscellaneous += flt(row.total_cost)
		self.total_miscellaneous_item_cost = total_miscellaneous
	
	def validate_dates(self):
		"""Validate that date_out is after date_in"""
		if self.date_in and self.date_out:
			if self.date_out < self.date_in:
				frappe.throw("Date Out cannot be before Date In")
		
		# Validate labor cost dates
		if self.labor_cost_items:
			for row in self.labor_cost_items:
				if row.job_started_date and row.job_ended_date:
					if row.job_ended_date < row.job_started_date:
						frappe.throw(f"Job Ended Date cannot be before Job Started Date in row {row.idx} of Labor Cost table")
					elif row.job_started_date == row.job_ended_date and row.job_started_hr and row.job_ended_hr:
						if row.job_ended_hr < row.job_started_hr:
							frappe.throw(f"Job Ended Time cannot be before Job Started Time in row {row.idx} of Labor Cost table")
	
	def on_submit(self):
		"""Actions to perform on submit"""
		self.update_maintenance_request_status()
	
	def update_maintenance_request_status(self):
		"""Update the status of linked Maintenance Request"""
		if self.maintenance_request_id:
			# You can add logic here to update the Maintenance Request status
			# For example, mark it as completed
			pass
