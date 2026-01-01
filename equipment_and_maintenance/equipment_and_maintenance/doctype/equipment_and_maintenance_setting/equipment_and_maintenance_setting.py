# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentandMaintenanceSetting(Document):
	def on_update(self):
		"""Update notification days_in_advance when settings are saved"""
		self.update_bollo_notification_days()
		self.update_insurance_notification_days()
	
	def update_bollo_notification_days(self):
		"""Update the bollo expiry notification days_in_advance"""
		notification_name = "Notification for Bollo Expiry"
		if frappe.db.exists("Notification", notification_name):
			notification = frappe.get_doc("Notification", notification_name)
			notification_days = self.bollo_expiry_notification_days or 7
			if notification.days_in_advance != notification_days:
				notification.days_in_advance = notification_days
				notification.save(ignore_permissions=True)
				frappe.db.commit()
	
	def update_insurance_notification_days(self):
		"""Update the insurance expiry notification days_in_advance"""
		notification_name = "Notification for Insurance Expiry"
		if frappe.db.exists("Notification", notification_name):
			notification = frappe.get_doc("Notification", notification_name)
			notification_days = self.insurance_expiry_notification_days or 7
			if notification.days_in_advance != notification_days:
				notification.days_in_advance = notification_days
				notification.save(ignore_permissions=True)
				frappe.db.commit()

