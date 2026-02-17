# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import frappe
import json
import os

def execute():
	"""Create or update Workspace Sidebars for Equipment and Maintenance"""
	
	# List of workspace sidebars to create
	sidebar_files = [
		"equipment_and_maintenance.json",
		"equipment.json",
		"maintenance.json"
	]
	
	current_dir = os.path.dirname(os.path.abspath(__file__))
	app_dir = os.path.dirname(current_dir)
	sidebar_dir = os.path.join(app_dir, "workspace_sidebar")
	
	for sidebar_file in sidebar_files:
		json_path = os.path.join(sidebar_dir, sidebar_file)
		
		if not os.path.exists(json_path):
			frappe.log_error(f"Workspace Sidebar JSON file not found: {json_path}", "Workspace Sidebar Creation")
			continue
		
		# Read the JSON file
		with open(json_path, 'r') as f:
			sidebar_data = json.load(f)
		
		sidebar_name = sidebar_data.get("name")
		if not sidebar_name:
			continue
		
		# Check if sidebar already exists
		if frappe.db.exists("Workspace Sidebar", sidebar_name):
			try:
				sidebar = frappe.get_doc("Workspace Sidebar", sidebar_name)
				# Update fields
				for key, value in sidebar_data.items():
					if key not in ["doctype", "name", "items"]:
						setattr(sidebar, key, value)
				
				# Clear existing items and add new ones
				sidebar.items = []
				for item_data in sidebar_data.get("items", []):
					sidebar.append("items", item_data)
				
				sidebar.save(ignore_permissions=True)
				frappe.db.commit()
				frappe.log_error(f"Updated Workspace Sidebar: {sidebar_name}", "Workspace Sidebar Update")
				print(f"✓ Updated Workspace Sidebar: {sidebar_name}")
			except Exception as e:
				frappe.log_error(f"Error updating Workspace Sidebar {sidebar_name}: {str(e)}", "Workspace Sidebar Update Error")
				print(f"✗ Error updating Workspace Sidebar {sidebar_name}: {str(e)}")
		else:
			try:
				# Create new sidebar document
				sidebar = frappe.new_doc("Workspace Sidebar")
				# Set fields from JSON data
				for key, value in sidebar_data.items():
					if key not in ["doctype", "name", "items"]:
						setattr(sidebar, key, value)
				
				# Set title explicitly (name will be auto-generated from title)
				if "title" in sidebar_data:
					sidebar.title = sidebar_data["title"]
				
				# Add items
				for item_data in sidebar_data.get("items", []):
					sidebar.append("items", item_data)
				
				sidebar.insert(ignore_permissions=True)
				frappe.db.commit()
				frappe.log_error(f"Created Workspace Sidebar: {sidebar_name}", "Workspace Sidebar Creation")
				print(f"✓ Created Workspace Sidebar: {sidebar_name}")
			except Exception as e:
				frappe.log_error(f"Error creating Workspace Sidebar {sidebar_name}: {str(e)}", "Workspace Sidebar Creation Error")
				print(f"✗ Error creating Workspace Sidebar {sidebar_name}: {str(e)}")
