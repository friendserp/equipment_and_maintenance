# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today


def daily():
	"""Run daily tasks"""
	try:
		from equipment_and_maintenance.maintenance_and_admin.doctype.preventive_maintenance_schedule.preventive_maintenance_schedule import check_and_send_reminders
		reminders_sent = check_and_send_reminders()
		if reminders_sent > 0:
			frappe.logger().info(f"Sent {reminders_sent} preventive maintenance reminders")
	except Exception as e:
		frappe.log_error(f"Error sending preventive maintenance reminders: {str(e)}")
	
	try:
		update_bollo_notification_days()
		update_insurance_notification_days()
	except Exception as e:
		frappe.log_error(f"Error updating notification days: {str(e)}")
	
	try:
		update_expired_status()
	except Exception as e:
		frappe.log_error(f"Error updating expired status: {str(e)}")


def update_bollo_notification_days():
	"""Update notification days_in_advance from settings"""
	notification_days = frappe.db.get_single_value("Equipment and Maintenance Setting", "bollo_expiry_notification_days") or 7
	notification_name = "Notification for Bollo Expiry"
	
	if frappe.db.exists("Notification", notification_name):
		notification = frappe.get_doc("Notification", notification_name)
		if notification.days_in_advance != notification_days:
			notification.days_in_advance = notification_days
			notification.save(ignore_permissions=True)
			frappe.db.commit()


def update_insurance_notification_days():
	"""Update insurance notification days_in_advance from settings"""
	notification_days = frappe.db.get_single_value("Equipment and Maintenance Setting", "insurance_expiry_notification_days") or 7
	notification_name = "Notification for Insurance Expiry"
	
	if frappe.db.exists("Notification", notification_name):
		notification = frappe.get_doc("Notification", notification_name)
		if notification.days_in_advance != notification_days:
			notification.days_in_advance = notification_days
			notification.save(ignore_permissions=True)
			frappe.db.commit()


def update_expired_status():
	"""Update status to Expired for records where expiry_date has passed"""
	today_date = today()
	
	# Update Insurance Followup Form
	insurance_records = frappe.get_all(
		"Insurance Followup Form",
		filters={
			"expiry_date": ["<", today_date],
			"status": "Active"
		},
		fields=["name"]
	)
	
	for record in insurance_records:
		frappe.db.set_value("Insurance Followup Form", record.name, "status", "Expired", update_modified=False)
	
	# Update Bollo Followup Form
	bollo_records = frappe.get_all(
		"Bollo Followup Form",
		filters={
			"expiry_date": ["<", today_date],
			"status": "Active"
		},
		fields=["name"]
	)
	
	for record in bollo_records:
		frappe.db.set_value("Bollo Followup Form", record.name, "status", "Expired", update_modified=False)
	
	if insurance_records or bollo_records:
		frappe.db.commit()
		frappe.logger().info(f"Updated {len(insurance_records)} insurance and {len(bollo_records)} bollo records to Expired status")

