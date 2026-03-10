# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BatteryRequestItem(Document):
	pass

def filter_battery_items(doctype, txt, searchfield, start, page_len, filters):
	"""Filter items for Battery Request - only show Spare Parts > General Purpose > Battery items"""
	conditions = [
		"item_group = 'Spare Parts'",
		"custom_subcategory = 'General Purpose'",
		"item_name LIKE 'Battery%'"
	]
	
	if txt:
		conditions.append(f"(name LIKE {frappe.db.escape('%' + txt + '%')} OR item_name LIKE {frappe.db.escape('%' + txt + '%')})")
	
	query = f"""
		SELECT name, item_name, item_group, custom_subcategory
		FROM `tabItem`
		WHERE {' AND '.join(conditions)}
		LIMIT {start}, {page_len}
	"""
	
	return frappe.db.sql(query, as_dict=False)
