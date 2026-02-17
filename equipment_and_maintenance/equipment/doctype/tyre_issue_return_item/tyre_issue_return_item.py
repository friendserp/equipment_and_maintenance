# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TyreIssueReturnItem(Document):
	pass

def filter_tyres_for_return(doctype, txt, searchfield, start, page_len, filters):
	"""Filter tyres for Return based on Tyre Request old tyres"""
	parent_doc = frappe.get_doc(filters.get("parent") or "")
	if not parent_doc or not parent_doc.tyre_request_form:
		return []
	
	old_tyre_items = frappe.db.get_all(
		"Tyre Old Item",
		filters={"parent": parent_doc.tyre_request_form},
		fields=["serial_no"]
	)
	
	if not old_tyre_items:
		return []
	
	tyre_names = [item.serial_no for item in old_tyre_items if item.serial_no]
	
	if not tyre_names:
		return []
	
	conditions = [
		"tyre_status = 'Fitted'",
		f"name IN ({','.join([frappe.db.escape(name) for name in tyre_names])})"
	]
	
	if txt:
		conditions.append(f"(name LIKE {frappe.db.escape('%' + txt + '%')} OR tyre_serial_no LIKE {frappe.db.escape('%' + txt + '%')})")
	
	query = f"""
		SELECT name, tyre_serial_no, item_code, tyre_size, tyre_brand, tyre_type, tyre_position
		FROM `tabTyre Recording Database`
		WHERE {' AND '.join(conditions)}
		LIMIT {start}, {page_len}
	"""
	
	return frappe.db.sql(query, as_dict=False)
