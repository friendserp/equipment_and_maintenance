# Copyright (c) 2026, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DailyFuelAnalysis(Document):
	pass

@frappe.whitelist()
def get_last_fuel_entry(plate_no):
	query = """
		SELECT
			child.current_km, child.filled_amount
		FROM
			`tabDaily Fuel Analysis Item` child
		JOIN
			`tabDaily Fuel Analysis` parent ON child.parent = parent.name
		WHERE
			child.plate_no = %s
			AND parent.docstatus = 1
		ORDER BY
			parent.date DESC, parent.creation DESC
		LIMIT 1
	"""
	
	result = frappe.db.sql(query, plate_no, as_dict=True)
	if result:
		return result[0]
	return None

