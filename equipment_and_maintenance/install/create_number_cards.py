# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import frappe
from equipment_and_maintenance.dashboard_fixtures import create_number_cards

def execute():
	"""Create number cards for Equipment and Maintenance workspace"""
	create_number_cards()
	frappe.db.commit()
	print("Number cards created successfully!")
