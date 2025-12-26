# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe


def daily():
	"""Run daily tasks - check and send preventive maintenance reminders"""
	try:
		from equipment_and_maintenance.maintenance_and_admin.doctype.preventive_maintenance_schedule.preventive_maintenance_schedule import check_and_send_reminders
		reminders_sent = check_and_send_reminders()
		if reminders_sent > 0:
			frappe.logger().info(f"Sent {reminders_sent} preventive maintenance reminders")
	except Exception as e:
		frappe.log_error(f"Error sending preventive maintenance reminders: {str(e)}")

