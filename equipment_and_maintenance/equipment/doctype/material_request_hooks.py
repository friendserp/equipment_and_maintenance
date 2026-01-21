# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe

def update_battery_recording_on_mr_issue(doc, method):
	"""Update Battery Recording Database when Material Request status changes to Issued"""
	# Only process if status is Issued
	if doc.status != "Issued":
		return
	
	# Check if this Material Request is linked to a Battery Request
	battery_requests = frappe.db.get_all(
		"Battery Request and Analysis Form",
		filters={"material_requisition_no": doc.name},
		fields=["name"]
	)
	
	if not battery_requests:
		return
	
	# Get Stock Entries created from this Material Request
	stock_entries = frappe.db.get_all(
		"Stock Entry",
		filters={
			"material_request": doc.name,
			"docstatus": 1,
			"purpose": ["in", ["Material Issue", "Material Transfer"]]
		},
		fields=["name"],
		order_by="creation desc",
		limit=1
	)
	
	# Update Battery Recording Database records
	for battery_request_name in battery_requests:
		battery_request = frappe.get_doc("Battery Request and Analysis Form", battery_request_name.name)
		
		# Update Battery Recording Database records
		for req_item in battery_request.requested_items:
			if req_item.battery_recording_database:
				update_data = {
					"last_battery_request": battery_request.name,
					"last_material_request": doc.name
				}
				if stock_entries:
					update_data["last_stock_entry"] = stock_entries[0].name
				
				frappe.db.set_value("Battery Recording Database", req_item.battery_recording_database, update_data)

def update_battery_recording_on_stock_entry(doc, method):
	"""Update Battery Recording Database when Stock Entry is submitted from Material Request"""
	if not doc.material_request:
		return
	
	if doc.purpose not in ["Material Issue", "Material Transfer"]:
		return
	
	# Check if this Material Request is linked to a Battery Request
	battery_requests = frappe.db.get_all(
		"Battery Request and Analysis Form",
		filters={"material_requisition_no": doc.material_request},
		fields=["name"]
	)
	
	if not battery_requests:
		return
	
	# Update Battery Recording Database records
	for battery_request_name in battery_requests:
		battery_request = frappe.get_doc("Battery Request and Analysis Form", battery_request_name.name)
		
		# Update Battery Recording Database records
		for req_item in battery_request.requested_items:
			if req_item.battery_recording_database:
				frappe.db.set_value("Battery Recording Database", req_item.battery_recording_database, {
					"last_battery_request": battery_request.name,
					"last_material_request": doc.material_request,
					"last_stock_entry": doc.name
				})

def update_battery_request_on_mr_submit(doc, method):
	"""Update Battery Request when Material Request is submitted"""
	battery_request_name = None
	
	# First check if already linked via material_requisition_no field
	battery_requests = frappe.db.get_all(
		"Battery Request and Analysis Form",
		filters={"material_requisition_no": doc.name},
		fields=["name"]
	)
	
	if battery_requests:
		battery_request_name = battery_requests[0].name
	else:
		# Check if linked via custom field (if exists)
		if hasattr(doc, 'custom_battery_request') and doc.custom_battery_request:
			if frappe.db.exists("Battery Request and Analysis Form", doc.custom_battery_request):
				battery_request_name = doc.custom_battery_request
		else:
			# Try to find Battery Request that doesn't have a Material Request yet
			# This handles the case where Material Request was created from Battery Request
			# We'll search for Battery Requests that match the items in this Material Request
			if doc.items and len(doc.items) > 0:
				# Get item codes from Material Request
				item_codes = [item.item_code for item in doc.items if item.item_code]
				
				if item_codes:
					# Find Battery Requests with these items that don't have a Material Request
					battery_requests = frappe.db.sql("""
						SELECT DISTINCT br.name
						FROM `tabBattery Request and Analysis Form` br
						INNER JOIN `tabBattery Request Item` bri ON bri.parent = br.name
						WHERE bri.requested_item_no IN %s
						AND br.docstatus = 1
						AND (br.material_requisition_no IS NULL OR br.material_requisition_no = '')
						ORDER BY br.creation DESC
						LIMIT 1
					""", (item_codes,), as_dict=True)
					
					if battery_requests:
						battery_request_name = battery_requests[0].name
	
	if battery_request_name:
		# Update Battery Request with Material Request link
		frappe.db.set_value(
			"Battery Request and Analysis Form",
			battery_request_name,
			"material_requisition_no",
			doc.name
		)
		
		# Update Battery Recording Database records
		battery_request = frappe.get_doc("Battery Request and Analysis Form", battery_request_name)
		for req_item in battery_request.requested_items:
			if req_item.battery_recording_database:
				frappe.db.set_value("Battery Recording Database", req_item.battery_recording_database, {
					"last_battery_request": battery_request_name,
					"last_material_request": doc.name
				})

def update_battery_request_on_mr_cancel(doc, method):
	"""Remove Battery Request link when Material Request is cancelled"""
	# Find Battery Request linked to this Material Request
	battery_requests = frappe.db.get_all(
		"Battery Request and Analysis Form",
		filters={"material_requisition_no": doc.name},
		fields=["name"]
	)
	
	for battery_request in battery_requests:
		# Clear Material Request link
		frappe.db.set_value(
			"Battery Request and Analysis Form",
			battery_request.name,
			"material_requisition_no",
			None
		)

@frappe.whitelist()
def update_battery_recording_on_mr_link(battery_request_name, material_request_name):
	"""Update Battery Recording Database when Material Request is linked to Battery Request"""
	if not battery_request_name or not material_request_name:
		return
	
	if not frappe.db.exists("Battery Request and Analysis Form", battery_request_name):
		return
	
	if not frappe.db.exists("Material Request", material_request_name):
		return
	
	# Update Battery Recording Database records
	battery_request = frappe.get_doc("Battery Request and Analysis Form", battery_request_name)
	for req_item in battery_request.requested_items:
		if req_item.battery_recording_database:
			frappe.db.set_value("Battery Recording Database", req_item.battery_recording_database, {
				"last_battery_request": battery_request_name,
				"last_material_request": material_request_name
			})
