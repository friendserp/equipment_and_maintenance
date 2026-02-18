# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from equipment_and_maintenance.dashboard_fixtures import create_custom_blocks

def execute():
	"""Delete existing workspace and create three new workspaces"""
	
	# Delete existing workspaces if they exist
	workspaces_to_delete = ["Equipment and Maintenance", "Equipment", "Maintenance"]
	for ws_name in workspaces_to_delete:
		if frappe.db.exists("Workspace", ws_name):
			try:
				frappe.delete_doc("Workspace", ws_name, force=1)
				frappe.db.commit()
				print(f"✓ Deleted existing workspace: {ws_name}")
			except Exception as e:
				print(f"✗ Error deleting workspace {ws_name}: {str(e)}")
	
	# Create custom HTML blocks (imported from dashboard_fixtures)
	create_custom_blocks()
	
	# Create main parent workspace first (must exist before child workspaces reference it)
	create_main_workspace()
	frappe.db.commit()
	
	# Create Equipment workspace (child workspace) - parent must exist first
	create_equipment_workspace()
	frappe.db.commit()
	
	# Create Maintenance workspace (child workspace) - parent must exist first
	create_maintenance_workspace()
	frappe.db.commit()
	
	frappe.clear_cache()
	print("\n" + "="*60)
	print("✓ All workspaces created successfully!")
	print("="*60)

def create_main_workspace():
	"""Create main Equipment and Maintenance workspace"""
	import json
	workspace = frappe.get_doc({
		"doctype": "Workspace",
		"label": "Equipment and Maintenance",
		"title": "Equipment and Maintenance",
		"module": "Equipment And Maintenance",
		"app": "equipment_and_maintenance",
		"icon": "dashboard-list",
		"public": 1,
		"sequence_id": 10.0,
		"content": json.dumps([
			{"id": "header_main", "type": "header", "data": {"text": "<span class=\"h3\"><b>Equipment & Maintenance Dashboard</b></span>", "col": 12}},
			{"id": "chart_maintenance_trend", "type": "chart", "data": {"chart_name": "Maintenance Requests Trend", "col": 6}},
			{"id": "chart_work_orders", "type": "chart", "data": {"chart_name": "Work Orders Status", "col": 6}},
			{"id": "spacer1", "type": "spacer", "data": {"col": 12}},
			{"id": "custom_block_stats", "type": "custom_block", "data": {"custom_block_name": "Quick Stats", "col": 12}},
			{"id": "spacer2", "type": "spacer", "data": {"col": 12}},
			{"id": "number_card_total_equipment", "type": "number_card", "data": {"number_card_name": "Total Equipment", "col": 4}},
			{"id": "number_card_pending_requests", "type": "number_card", "data": {"number_card_name": "Pending Maintenance Requests", "col": 4}},
			{"id": "number_card_open_work_orders", "type": "number_card", "data": {"number_card_name": "Open Work Orders", "col": 4}},
			{"id": "spacer3", "type": "spacer", "data": {"col": 12}},
			{"id": "header_dashboard", "type": "header", "data": {"text": "<span class=\"h4\"><b>Dashboards</b></span>", "col": 12}},
			{"id": "shortcut_dashboard_main", "type": "shortcut", "data": {"shortcut_name": "Equipment and Maintenance Dashboard", "col": 4}},
			{"id": "shortcut_dashboard_equipment", "type": "shortcut", "data": {"shortcut_name": "Equipment Dashboard", "col": 4}},
			{"id": "shortcut_dashboard_maintenance", "type": "shortcut", "data": {"shortcut_name": "Maintenance Dashboard", "col": 4}},
			{"id": "spacer4", "type": "spacer", "data": {"col": 12}},
			{"id": "header_modules", "type": "header", "data": {"text": "<span class=\"h4\"><b>Modules</b></span>", "col": 12}},
			{"id": "custom_block_equipment", "type": "custom_block", "data": {"custom_block_name": "Equipment Overview", "col": 6}},
			{"id": "custom_block_maintenance", "type": "custom_block", "data": {"custom_block_name": "Maintenance Overview", "col": 6}},
			{"id": "spacer5", "type": "spacer", "data": {"col": 12}},
			{"id": "card_equipment", "type": "card", "data": {"card_name": "Equipment", "col": 6}},
			{"id": "card_maintenance", "type": "card", "data": {"card_name": "Maintenance", "col": 6}}
		]),
		"charts": [
			{
				"chart_name": "Maintenance Requests Trend",
				"label": "Maintenance Requests Trend"
			},
			{
				"chart_name": "Work Orders Status",
				"label": "Work Orders Status"
			}
		],
		"number_cards": [
			{
				"label": "Total Equipment",
				"name": "Total Equipment",
				"number_card_name": "Total Equipment"
			},
			{
				"label": "Pending Maintenance Requests",
				"name": "Pending Maintenance Requests",
				"number_card_name": "Pending Maintenance Requests"
			},
			{
				"label": "Open Work Orders",
				"name": "Open Work Orders",
				"number_card_name": "Open Work Orders"
			}
		],
		"custom_blocks": [
			{
				"custom_block_name": "Quick Stats"
			},
			{
				"custom_block_name": "Equipment Overview"
			},
			{
				"custom_block_name": "Maintenance Overview"
			}
		],
		"shortcuts": [
			{
				"label": "Equipment and Maintenance Dashboard",
				"link_to": "Equipment and Maintenance",
				"shortcut_name": "Equipment and Maintenance Dashboard",
				"type": "Dashboard"
			},
			{
				"label": "Equipment Dashboard",
				"link_to": "Equipment",
				"shortcut_name": "Equipment Dashboard",
				"type": "Dashboard"
			},
			{
				"label": "Maintenance Dashboard",
				"link_to": "Maintenance",
				"shortcut_name": "Maintenance Dashboard",
				"type": "Dashboard"
			}
		],
		"links": [
			{
				"label": "Equipment",
				"type": "Card Break"
			},
			{
				"label": "Maintenance",
				"type": "Card Break"
			}
		]
	})
	workspace.insert(ignore_permissions=True)
	frappe.db.commit()
	print("✓ Created main workspace: Equipment and Maintenance")

def create_equipment_workspace():
	"""Create Equipment workspace"""
	import json
	workspace = frappe.get_doc({
		"doctype": "Workspace",
		"label": "Equipment",
		"title": "Equipment",
		"module": "Equipment And Maintenance",
		"app": "equipment_and_maintenance",
		"icon": "money-coins-1",
		"public": 1,
		"sequence_id": 11.0,
		"parent_page": "Equipment and Maintenance",
		"content": json.dumps([
			{"id": "header_main", "type": "header", "data": {"text": "<span class=\"h3\"><b>Equipment Module</b></span>", "col": 12}},
			{"id": "chart_equipment_category", "type": "chart", "data": {"chart_name": "Equipment by Category", "col": 6}},
			{"id": "chart_fuel_requests", "type": "chart", "data": {"chart_name": "Fuel Requests Trend", "col": 6}},
			{"id": "spacer0", "type": "spacer", "data": {"col": 12}},
			{"id": "custom_block_equipment_overview", "type": "custom_block", "data": {"custom_block_name": "Equipment Overview", "col": 12}},
			{"id": "spacer1", "type": "spacer", "data": {"col": 12}},
			{"id": "number_card_total_equipment", "type": "number_card", "data": {"number_card_name": "Total Equipment", "col": 6}},
			{"id": "spacer2", "type": "spacer", "data": {"col": 12}},
			{"id": "header_dashboard", "type": "header", "data": {"text": "<span class=\"h4\"><b>Dashboard</b></span>", "col": 12}},
			{"id": "shortcut_dashboard_equipment", "type": "shortcut", "data": {"shortcut_name": "Equipment Dashboard", "col": 4}},
			{"id": "spacer3", "type": "spacer", "data": {"col": 12}},
			{"id": "header_shortcuts", "type": "header", "data": {"text": "<span class=\"h4\"><b>Quick Actions</b></span>", "col": 12}},
			{"id": "shortcut_equipment_master", "type": "shortcut", "data": {"shortcut_name": "Equipment Master", "col": 3}},
			{"id": "shortcut_fuel_request", "type": "shortcut", "data": {"shortcut_name": "Fuel Request", "col": 3}},
			{"id": "shortcut_vehicle_movement", "type": "shortcut", "data": {"shortcut_name": "Vehicle Daily Movement", "col": 3}},
			{"id": "shortcut_equipment_transfer", "type": "shortcut", "data": {"shortcut_name": "Equipment Transfer Form", "col": 3}},
			{"id": "shortcut_equipment_disposal", "type": "shortcut", "data": {"shortcut_name": "Equipment Disposal Request", "col": 3}},
			{"id": "shortcut_rental_agreement", "type": "shortcut", "data": {"shortcut_name": "Rental Agreement", "col": 3}},
			{"id": "spacer4", "type": "spacer", "data": {"col": 12}},
			{"id": "header_forms", "type": "header", "data": {"text": "<span class=\"h4\"><b>Forms & Reports</b></span>", "col": 12}},
			{"id": "card_equipment_masters", "type": "card", "data": {"card_name": "Equipment Masters", "col": 6}},
			{"id": "card_battery_tyre", "type": "card", "data": {"card_name": "Battery & Tyre", "col": 6}},
			{"id": "card_equipment_forms", "type": "card", "data": {"card_name": "Equipment Forms", "col": 12}},
			{"id": "card_followup_forms", "type": "card", "data": {"card_name": "Followup Forms", "col": 6}}
		]),
		"charts": [
			{
				"chart_name": "Equipment by Category",
				"label": "Equipment by Category"
			},
			{
				"chart_name": "Fuel Requests Trend",
				"label": "Fuel Requests Trend"
			}
		],
		"number_cards": [
			{
				"label": "Total Equipment",
				"name": "Total Equipment",
				"number_card_name": "Total Equipment"
			}
		],
		"shortcuts": [
			{
				"label": "Equipment Master",
				"link_to": "Equipment Master",
				"shortcut_name": "Equipment Master",
				"type": "DocType"
			},
			{
				"label": "Fuel Request",
				"link_to": "Fuel Request",
				"shortcut_name": "Fuel Request",
				"type": "DocType"
			},
			{
				"label": "Vehicle Daily Movement",
				"link_to": "Vehicle Daily Movement",
				"shortcut_name": "Vehicle Daily Movement",
				"type": "DocType"
			},
			{
				"label": "Equipment Transfer Form",
				"link_to": "Equipment Transfer Form",
				"shortcut_name": "Equipment Transfer Form",
				"type": "DocType"
			},
			{
				"label": "Equipment Disposal Request",
				"link_to": "Equipment Disposal Request",
				"shortcut_name": "Equipment Disposal Request",
				"type": "DocType"
			},
			{
				"label": "Rental Agreement",
				"link_to": "Rental Agreement",
				"shortcut_name": "Rental Agreement",
				"type": "DocType"
			},
			{
				"label": "Equipment Dashboard",
				"link_to": "Equipment",
				"shortcut_name": "Equipment Dashboard",
				"type": "Dashboard"
			}
		],
		"links": [
			{
				"label": "Equipment Masters",
				"type": "Card Break"
			},
			{
				"label": "Equipment Master",
				"link_to": "Equipment Master",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Sub Category",
				"link_to": "Sub Category",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Asset Sub Category",
				"link_to": "Asset Sub Category",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Equipment Forms",
				"type": "Card Break"
			},
			{
				"label": "Cost Control and Registration Form",
				"link_to": "Cost Control and Registration Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Fuel Request",
				"link_to": "Fuel Request",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Accident Report Form",
				"link_to": "Accident Report Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Machinery Handover Form",
				"link_to": "Machinery Handover Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Equipment Transfer Form",
				"link_to": "Equipment Transfer Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Equipment Disposal Request",
				"link_to": "Equipment Disposal Request",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Machinery Time Sheet Registration",
				"link_to": "Machinery Time Sheet Registration",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Vehicle Daily Movement",
				"link_to": "Vehicle Daily Movement",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Rental Agreement",
				"link_to": "Rental Agreement",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Bollo Followup Form",
				"link_to": "Bollo Followup Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Insurance Followup Form",
				"link_to": "Insurance Followup Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Followup Forms",
				"type": "Card Break"
			},
			{
				"label": "Bollo Followup Form",
				"link_to": "Bollo Followup Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Insurance Followup Form",
				"link_to": "Insurance Followup Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Battery & Tyre",
				"type": "Card Break"
			},
			{
				"label": "Battery Recording Database",
				"link_to": "Battery Recording Database",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Tyre Recording Database",
				"link_to": "Tyre Recording Database",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Tyre Recording Database Form",
				"link_to": "Tyre Recording Database Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Battery Request and Analysis Form",
				"link_to": "Battery Request and Analysis Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Battery Issue and Return Report Form",
				"link_to": "Battery Issue and Return Report Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Tyre Request and Analysis Form",
				"link_to": "Tyre Request and Analysis Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Tyre Issue and Return Report Form",
				"link_to": "Tyre Issue and Return Report Form",
				"link_type": "DocType",
				"type": "Link"
			}
		],
		"custom_blocks": [
			{
				"custom_block_name": "Equipment Overview"
			}
		]
	})
	workspace.insert(ignore_permissions=True)
	frappe.db.commit()
	print("✓ Created workspace: Equipment")

def create_maintenance_workspace():
	"""Create Maintenance workspace"""
	import json
	workspace = frappe.get_doc({
		"doctype": "Workspace",
		"label": "Maintenance",
		"title": "Maintenance",
		"module": "Equipment And Maintenance",
		"app": "equipment_and_maintenance",
		"icon": "quantity-1",
		"public": 1,
		"sequence_id": 12.0,
		"parent_page": "Equipment and Maintenance",
		"content": json.dumps([
			{"id": "header_main", "type": "header", "data": {"text": "<span class=\"h3\"><b>Maintenance Module</b></span>", "col": 12}},
			{"id": "chart_maintenance_trend", "type": "chart", "data": {"chart_name": "Maintenance Requests Trend", "col": 12}},
			{"id": "spacer_charts", "type": "spacer", "data": {"col": 12}},
			{"id": "chart_work_orders", "type": "chart", "data": {"chart_name": "Work Orders Status", "col": 6}},
			{"id": "chart_completed_jobs", "type": "chart", "data": {"chart_name": "Completed Maintenance Jobs Trend", "col": 6}},
			{"id": "spacer0", "type": "spacer", "data": {"col": 12}},
			{"id": "custom_block_maintenance_overview", "type": "custom_block", "data": {"custom_block_name": "Maintenance Overview", "col": 12}},
			{"id": "spacer1", "type": "spacer", "data": {"col": 12}},
			{"id": "number_card_pending_requests", "type": "number_card", "data": {"number_card_name": "Pending Maintenance Requests", "col": 4}},
			{"id": "number_card_open_work_orders", "type": "number_card", "data": {"number_card_name": "Open Work Orders", "col": 4}},
			{"id": "number_card_completed_jobs", "type": "number_card", "data": {"number_card_name": "Completed Maintenance Jobs", "col": 4}},
			{"id": "spacer2", "type": "spacer", "data": {"col": 12}},
			{"id": "header_dashboard", "type": "header", "data": {"text": "<span class=\"h4\"><b>Dashboard</b></span>", "col": 12}},
			{"id": "shortcut_dashboard_maintenance", "type": "shortcut", "data": {"shortcut_name": "Maintenance Dashboard", "col": 4}},
			{"id": "spacer3", "type": "spacer", "data": {"col": 12}},
			{"id": "header_shortcuts", "type": "header", "data": {"text": "<span class=\"h4\"><b>Quick Actions</b></span>", "col": 12}},
			{"id": "shortcut_maintenance_request", "type": "shortcut", "data": {"shortcut_name": "Maintenance Request", "col": 3}},
			{"id": "shortcut_work_order", "type": "shortcut", "data": {"shortcut_name": "Maintenance Work Order", "col": 3}},
			{"id": "shortcut_preventive_maintenance", "type": "shortcut", "data": {"shortcut_name": "Preventive Maintenance Schedule", "col": 3}},
			{"id": "spacer4", "type": "spacer", "data": {"col": 12}},
			{"id": "card_maintenance_masters", "type": "card", "data": {"card_name": "Maintenance Masters", "col": 6}},
			{"id": "card_maintenance_forms", "type": "card", "data": {"card_name": "Maintenance Forms", "col": 6}},
			{"id": "card_settings", "type": "card", "data": {"card_name": "Settings", "col": 6}}
		]),
		"charts": [
			{
				"chart_name": "Maintenance Requests Trend",
				"label": "Maintenance Requests Trend"
			},
			{
				"chart_name": "Work Orders Status",
				"label": "Work Orders Status"
			},
			{
				"chart_name": "Completed Maintenance Jobs Trend",
				"label": "Completed Maintenance Jobs Trend"
			}
		],
		"number_cards": [
			{
				"label": "Pending Maintenance Requests",
				"name": "Pending Maintenance Requests",
				"number_card_name": "Pending Maintenance Requests"
			},
			{
				"label": "Open Work Orders",
				"name": "Open Work Orders",
				"number_card_name": "Open Work Orders"
			},
			{
				"label": "Completed Maintenance Jobs",
				"name": "Completed Maintenance Jobs",
				"number_card_name": "Completed Maintenance Jobs"
			}
		],
		"shortcuts": [
			{
				"label": "Maintenance Request",
				"link_to": "Maintenance Request",
				"shortcut_name": "Maintenance Request",
				"type": "DocType"
			},
			{
				"label": "Maintenance Work Order",
				"link_to": "Maintenance Work Order",
				"shortcut_name": "Maintenance Work Order",
				"type": "DocType"
			},
			{
				"label": "Preventive Maintenance Schedule",
				"link_to": "Preventive Maintenance Schedule",
				"shortcut_name": "Preventive Maintenance Schedule",
				"type": "DocType"
			},
			{
				"label": "Maintenance Dashboard",
				"link_to": "Maintenance",
				"shortcut_name": "Maintenance Dashboard",
				"type": "Dashboard"
			}
		],
		"links": [
			{
				"label": "Maintenance Masters",
				"type": "Card Break"
			},
			{
				"label": "Maintenance Interval",
				"link_to": "Maintenance Interval",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance Task",
				"link_to": "Preventive Maintenance Task",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance Template",
				"link_to": "Preventive Maintenance Template",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance Schedule",
				"link_to": "Preventive Maintenance Schedule",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance Plan",
				"link_to": "Preventive Maintenance Plan",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance History",
				"link_to": "Preventive Maintenance History",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance Done",
				"link_to": "Preventive Maintenance Done",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Preventive Maintenance Log",
				"link_to": "Preventive Maintenance Log",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Maintenance Forms",
				"type": "Card Break"
			},
			{
				"label": "Maintenance Request",
				"link_to": "Maintenance Request",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Maintenance Work Order",
				"link_to": "Maintenance Work Order",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Maintenance Job Completion",
				"link_to": "Maintenance Job Completion",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Cannibalization Form",
				"link_to": "Cannibalization Form",
				"link_type": "DocType",
				"type": "Link"
			},
			{
				"label": "Settings",
				"type": "Card Break"
			},
			{
				"label": "Equipment and Maintenance Setting",
				"link_to": "Equipment and Maintenance Setting",
				"link_type": "DocType",
				"type": "Link"
			}
		],
		"custom_blocks": [
			{
				"custom_block_name": "Maintenance Overview"
			}
		]
	})
	workspace.insert(ignore_permissions=True)
	frappe.db.commit()
	print("✓ Created workspace: Maintenance")
