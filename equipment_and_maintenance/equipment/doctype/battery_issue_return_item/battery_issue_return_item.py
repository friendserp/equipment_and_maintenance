# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BatteryIssueReturnItem(Document):
	pass

def filter_batteries_for_issue(doctype, txt, searchfield, start, page_len, filters):
	"""Filter batteries for Issue based on Battery Request requirements"""
	# Get Battery Request Form from parent
	parent_doc = frappe.get_doc(filters.get("parent") or "")
	if not parent_doc or not parent_doc.battery_request_form:
		return []
	
	# Get requested items from Battery Request
	requested_items = frappe.db.get_all(
		"Battery Request Item",
		filters={"parent": parent_doc.battery_request_form},
		fields=["requested_item_no", "requested_battery_voltage", "requested_battery_amper", "requested_battery_position"]
	)
	
	if not requested_items:
		return []
	
	# Build filters for Battery Recording Database
	conditions = ["battery_status = 'Available'"]
	item_codes = [item.requested_item_no for item in requested_items if item.requested_item_no]
	voltages = [item.requested_battery_voltage for item in requested_items if item.requested_battery_voltage]
	ampers = [item.requested_battery_amper for item in requested_items if item.requested_battery_amper]
	positions = [item.requested_battery_position for item in requested_items if item.requested_battery_position]
	
	if item_codes:
		conditions.append(f"item_code IN ({','.join([frappe.db.escape(code) for code in item_codes])})")
	if voltages:
		conditions.append(f"battery_voltage IN ({','.join([str(v) for v in voltages])})")
	if ampers:
		conditions.append(f"battery_amper IN ({','.join([str(a) for a in ampers])})")
	if positions:
		conditions.append(f"battery_position IN ({','.join([frappe.db.escape(p) for p in positions])})")
	
	# Search filter
	if txt:
		conditions.append(f"(name LIKE {frappe.db.escape('%' + txt + '%')} OR battery_serial_no LIKE {frappe.db.escape('%' + txt + '%')})")
	
	query = f"""
		SELECT name, battery_serial_no, item_code, battery_voltage, battery_amper, battery_position
		FROM `tabBattery Recording Database`
		WHERE {' AND '.join(conditions)}
		LIMIT {start}, {page_len}
	"""
	
	return frappe.db.sql(query, as_dict=False)

def filter_batteries_for_return(doctype, txt, searchfield, start, page_len, filters):
	"""Filter batteries for Return based on Battery Request old batteries"""
	# Get Battery Request Form from parent
	parent_doc = frappe.get_doc(filters.get("parent") or "")
	if not parent_doc or not parent_doc.battery_request_form:
		return []
	
	# Get old battery items from Battery Request
	old_battery_items = frappe.db.get_all(
		"Battery Old Item",
		filters={"parent": parent_doc.battery_request_form},
		fields=["battery_recording_database"]
	)
	
	if not old_battery_items:
		return []
	
	battery_names = [item.battery_recording_database for item in old_battery_items if item.battery_recording_database]
	
	if not battery_names:
		return []
	
	conditions = [
		"battery_status = 'Fitted'",
		f"name IN ({','.join([frappe.db.escape(name) for name in battery_names])})"
	]
	
	if txt:
		conditions.append(f"(name LIKE {frappe.db.escape('%' + txt + '%')} OR battery_serial_no LIKE {frappe.db.escape('%' + txt + '%')})")
	
	query = f"""
		SELECT name, battery_serial_no, item_code, battery_voltage, battery_amper, battery_position
		FROM `tabBattery Recording Database`
		WHERE {' AND '.join(conditions)}
		LIMIT {start}, {page_len}
	"""
	
	return frappe.db.sql(query, as_dict=False)
