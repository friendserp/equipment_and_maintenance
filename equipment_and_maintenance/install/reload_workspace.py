# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import frappe
from equipment_and_maintenance.dashboard_fixtures import create_number_cards

def execute():
	"""Reload workspace and create number cards"""
	
	# Create number cards first
	print("Creating number cards...")
	create_number_cards()
	frappe.db.commit()
	
	# Reload the workspace document from JSON file
	print("Reloading workspace...")
	try:
		frappe.reload_doc(
			"Equipment And Maintenance",
			"Workspace",
			"Equipment and Maintenance",
			force=True,
			reset_permissions=False
		)
		frappe.db.commit()
		print("✓ Workspace reloaded successfully!")
	except Exception as e:
		print(f"✗ Error reloading workspace: {str(e)}")
		frappe.log_error(f"Error reloading workspace: {str(e)}", "Workspace Reload Error")
	
	# Clear cache
	print("Clearing cache...")
	frappe.clear_cache()
	
	print("\n" + "="*50)
	print("Setup completed! Please refresh your browser.")
	print("="*50)
