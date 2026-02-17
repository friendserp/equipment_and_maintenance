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


def create_custom_blocks():
	"""Create custom HTML blocks for workspaces"""
	custom_blocks = [
		{
			"name": "Equipment Overview",
			"html": """
				<div class="equipment-overview-block">
					<div class="block-header">
						<i class="fa fa-tool text-white"></i>
						<h5 class="mb-0 text-white">Equipment Management</h5>
					</div>
					<div class="block-content">
						<p class="block-description">Track and manage all your equipment assets efficiently.</p>
						<ul class="block-features">
							<li><i class="fa fa-check-circle"></i> Equipment Master Data</li>
							<li><i class="fa fa-check-circle"></i> Fuel & Movement Tracking</li>
							<li><i class="fa fa-check-circle"></i> Battery & Tyre Management</li>
						</ul>
					</div>
				</div>
			""",
			"style": """
				.equipment-overview-block {
					border-radius: 8px;
					overflow: hidden;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					background: white;
				}
				.equipment-overview-block .block-header {
					background: linear-gradient(135deg, #0289f7 0%, #007be0 100%);
					padding: 16px 20px;
					display: flex;
					align-items: center;
					gap: 12px;
				}
				.equipment-overview-block .block-header i {
					font-size: 20px;
				}
				.equipment-overview-block .block-content {
					padding: 20px;
					background: #f8f9fa;
				}
				.equipment-overview-block .block-description {
					color: #525252;
					margin-bottom: 16px;
					font-size: 14px;
				}
				.equipment-overview-block .block-features {
					list-style: none;
					padding: 0;
					margin: 0;
				}
				.equipment-overview-block .block-features li {
					padding: 8px 0;
					color: #383838;
					font-size: 14px;
					display: flex;
					align-items: center;
					gap: 10px;
				}
				.equipment-overview-block .block-features i {
					color: #30a66d;
					font-size: 16px;
				}
			"""
		},
		{
			"name": "Maintenance Overview",
			"html": """
				<div class="maintenance-overview-block">
					<div class="block-header">
						<i class="fa fa-wrench text-white"></i>
						<h5 class="mb-0 text-white">Maintenance Operations</h5>
					</div>
					<div class="block-content">
						<p class="block-description">Streamline your maintenance workflows and schedules.</p>
						<ul class="block-features">
							<li><i class="fa fa-check-circle"></i> Preventive Maintenance</li>
							<li><i class="fa fa-check-circle"></i> Work Order Management</li>
							<li><i class="fa fa-check-circle"></i> Maintenance History</li>
						</ul>
					</div>
				</div>
			""",
			"style": """
				.maintenance-overview-block {
					border-radius: 8px;
					overflow: hidden;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					background: white;
				}
				.maintenance-overview-block .block-header {
					background: linear-gradient(135deg, #30a66d 0%, #278f5e 100%);
					padding: 16px 20px;
					display: flex;
					align-items: center;
					gap: 12px;
				}
				.maintenance-overview-block .block-header i {
					font-size: 20px;
				}
				.maintenance-overview-block .block-content {
					padding: 20px;
					background: #f8f9fa;
				}
				.maintenance-overview-block .block-description {
					color: #525252;
					margin-bottom: 16px;
					font-size: 14px;
				}
				.maintenance-overview-block .block-features {
					list-style: none;
					padding: 0;
					margin: 0;
				}
				.maintenance-overview-block .block-features li {
					padding: 8px 0;
					color: #383838;
					font-size: 14px;
					display: flex;
					align-items: center;
					gap: 10px;
				}
				.maintenance-overview-block .block-features i {
					color: #30a66d;
					font-size: 16px;
				}
			"""
		},
		{
			"name": "Quick Stats",
			"html": """
				<div class="quick-stats-block">
					<div class="stats-icon">
						<i class="fa fa-chart-line"></i>
					</div>
					<div class="stats-content">
						<h5 class="mb-2">Quick Statistics</h5>
						<p class="mb-0">Monitor your equipment and maintenance metrics at a glance.</p>
					</div>
				</div>
			""",
			"style": """
				.quick-stats-block {
					border-radius: 8px;
					background: linear-gradient(135deg, #171717 0%, #383838 100%);
					padding: 24px;
					display: flex;
					align-items: center;
					gap: 20px;
					box-shadow: 0 2px 8px rgba(0,0,0,0.15);
				}
				.quick-stats-block .stats-icon {
					width: 56px;
					height: 56px;
					border-radius: 12px;
					background: rgba(255,255,255,0.15);
					display: flex;
					align-items: center;
					justify-content: center;
					flex-shrink: 0;
				}
				.quick-stats-block .stats-icon i {
					font-size: 28px;
					color: #ffffff;
				}
				.quick-stats-block .stats-content h5 {
					color: #ffffff;
					font-weight: 600;
					margin: 0;
					font-size: 18px;
				}
				.quick-stats-block .stats-content p {
					color: rgba(255,255,255,0.8);
					margin: 0;
					font-size: 14px;
				}
			"""
		}
	]
	
	for block_data in custom_blocks:
		# Delete existing block if it exists to recreate with new styles
		if frappe.db.exists("Custom HTML Block", block_data["name"]):
			try:
				frappe.delete_doc("Custom HTML Block", block_data["name"], force=1)
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(f"Error deleting custom block {block_data['name']}: {str(e)}", "Custom Block Deletion Error")
		
		try:
			block = frappe.get_doc({
				"doctype": "Custom HTML Block",
				"name": block_data["name"],
				"html": block_data["html"],
				"style": block_data.get("style", ""),
				"private": 0
			})
			block.insert(ignore_permissions=True)
			frappe.db.commit()
			frappe.log_error(f"Created/Updated custom block: {block_data['name']}", "Custom Block Creation")
		except Exception as e:
			frappe.log_error(f"Error creating custom block {block_data['name']}: {str(e)}", "Custom Block Creation Error")
