# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import json
import frappe
from frappe import _
from frappe.utils import nowdate, add_months


def get_number_cards():
	"""Create number cards for Equipment and Maintenance workspace"""
	return [
		{
			"doctype": "Number Card",
			"name": "Total Equipment",
			"label": _("Total Equipment"),
			"type": "Document Type",
			"document_type": "Equipment Master",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": "Equipment And Maintenance",
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": "[]",
			"color": "#5e64ff",
		},
		{
			"doctype": "Number Card",
			"name": "Pending Maintenance Requests",
			"label": _("Pending Maintenance Requests"),
			"type": "Document Type",
			"document_type": "Maintenance Request",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": "Equipment And Maintenance",
			"show_percentage_stats": 1,
			"stats_time_interval": "Weekly",
			"filters_json": json.dumps([
				["Maintenance Request", "docstatus", "=", 0]
			]),
			"color": "#ff5858",
		},
		{
			"doctype": "Number Card",
			"name": "Open Work Orders",
			"label": _("Open Work Orders"),
			"type": "Document Type",
			"document_type": "Maintenance Work Order",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": "Equipment And Maintenance",
			"show_percentage_stats": 1,
			"stats_time_interval": "Weekly",
			"filters_json": json.dumps([
				["Maintenance Work Order", "docstatus", "=", 1]
			]),
			"dynamic_filters_json": "",
			"color": "#ffa00a",
		},
		{
			"doctype": "Number Card",
			"name": "Completed Maintenance Jobs",
			"label": _("Completed Maintenance Jobs"),
			"type": "Document Type",
			"document_type": "Maintenance Job Completion",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": "Equipment And Maintenance",
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"filters_json": json.dumps([
				["Maintenance Job Completion", "docstatus", "=", 1]
			]),
			"color": "#28a745",
		},
	]


def create_number_cards():
	"""Create number cards if they don't exist"""
	number_cards = get_number_cards()
	
	for card_data in number_cards:
		if not frappe.db.exists("Number Card", card_data["name"]):
			try:
				card = frappe.get_doc(card_data)
				card.insert(ignore_permissions=True)
				frappe.db.commit()
				frappe.log_error(f"Created number card: {card_data['name']}", "Number Card Creation")
			except Exception as e:
				frappe.log_error(f"Error creating number card {card_data['name']}: {str(e)}", "Number Card Creation Error")
		else:
			# Update existing card
			try:
				card = frappe.get_doc("Number Card", card_data["name"])
				for key, value in card_data.items():
					if key != "doctype" and key != "name":
						setattr(card, key, value)
				card.save(ignore_permissions=True)
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(f"Error updating number card {card_data['name']}: {str(e)}", "Number Card Update Error")
