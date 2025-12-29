# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FuelRequest(Document):
	def before_insert(self):
		# Auto-set requested_by if not set
		if not self.requested_by:
			self.requested_by = frappe.session.user
		
		# Auto-set date_issued to date if not set
		if not self.date_issued:
			self.date_issued = self.date
	
	def validate(self):
		# Calculate fuel efficiency (Km/Ltr) if we have previous data
		if (self.previous_fuel_consumption_liter and 
			self.previous_km_hr_reading and 
			self.current_km_hr_reading):
			
			distance_traveled = self.current_km_hr_reading - self.previous_km_hr_reading
			if distance_traveled > 0 and self.previous_fuel_consumption_liter > 0:
				self.vehicles_km_ltr = distance_traveled / self.previous_fuel_consumption_liter
		
		# Calculate current fuel cost in birr
		# Note: This requires a fuel price field or setting
		# For now, we'll calculate it in JavaScript based on previous fuel price

