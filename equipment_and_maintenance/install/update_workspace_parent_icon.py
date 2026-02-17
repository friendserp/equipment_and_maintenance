# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import frappe

def execute():
	"""Update Equipment and Maintenance workspaces with parent_page and icon"""
	
	# Update Equipment workspace
	if frappe.db.exists("Workspace", "Equipment"):
		eq = frappe.get_doc("Workspace", "Equipment")
		eq.parent_page = "Equipment and Maintenance"
		eq.icon = "tool"
		eq.save(ignore_permissions=True)
		frappe.db.commit()
		print("✓ Updated Equipment workspace: parent_page='Equipment and Maintenance', icon='tool'")
	
	# Update Maintenance workspace
	if frappe.db.exists("Workspace", "Maintenance"):
		mnt = frappe.get_doc("Workspace", "Maintenance")
		mnt.parent_page = "Equipment and Maintenance"
		mnt.icon = "wrench"
		mnt.save(ignore_permissions=True)
		frappe.db.commit()
		print("✓ Updated Maintenance workspace: parent_page='Equipment and Maintenance', icon='wrench'")
	
	frappe.clear_cache()
	print("✓ Cache cleared")
