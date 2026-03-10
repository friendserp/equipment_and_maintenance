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

def update_tyre_request_on_mr_submit(doc, method):
	"""Update Tyre Request when Material Request is submitted"""
	tyre_request_name = None
	
	# First check if already linked via material_requisition_no field
	tyre_requests = frappe.db.get_all(
		"Tyre Request and Analysis Form",
		filters={"material_requisition_no": doc.name},
		fields=["name"]
	)
	
	if tyre_requests:
		tyre_request_name = tyre_requests[0].name
	else:
		# Check if linked via custom field (if exists)
		if hasattr(doc, 'custom_tyre_request') and doc.custom_tyre_request:
			if frappe.db.exists("Tyre Request and Analysis Form", doc.custom_tyre_request):
				tyre_request_name = doc.custom_tyre_request
		else:
			# Try to find Tyre Request that doesn't have a Material Request yet
			if doc.items and len(doc.items) > 0:
				# Get item codes from Material Request
				item_codes = [item.item_code for item in doc.items if item.item_code]
				
				if item_codes:
					# Find Tyre Requests with these items that don't have a Material Request
					tyre_requests = frappe.db.sql("""
						SELECT DISTINCT tr.name
						FROM `tabTyre Request and Analysis Form` tr
						INNER JOIN `tabTyre Request Item` tri ON tri.parent = tr.name
						WHERE tri.requested_item_no IN %s
						AND tr.docstatus = 1
						AND (tr.material_requisition_no IS NULL OR tr.material_requisition_no = '')
						ORDER BY tr.creation DESC
						LIMIT 1
					""", (item_codes,), as_dict=True)
					
					if tyre_requests:
						tyre_request_name = tyre_requests[0].name
	
	if tyre_request_name:
		# Update Tyre Request with Material Request link
		frappe.db.set_value(
			"Tyre Request and Analysis Form",
			tyre_request_name,
			"material_requisition_no",
			doc.name
		)
		
		# Update Tyre Recording Database records
		tyre_request = frappe.get_doc("Tyre Request and Analysis Form", tyre_request_name)
		for req_item in tyre_request.requested_items:
			# Note: Tyre Request doesn't create database records on submit
			# Database records are created when tyres are issued via Issue and Return form
			pass

def update_tyre_request_on_mr_cancel(doc, method):
	"""Remove Tyre Request link when Material Request is cancelled"""
	# Find Tyre Request linked to this Material Request
	tyre_requests = frappe.db.get_all(
		"Tyre Request and Analysis Form",
		filters={"material_requisition_no": doc.name},
		fields=["name"]
	)
	
	for tyre_request in tyre_requests:
		# Clear Material Request link
		frappe.db.set_value(
			"Tyre Request and Analysis Form",
			tyre_request.name,
			"material_requisition_no",
			None
		)

def update_tyre_recording_on_mr_issue(doc, method):
	"""Update Tyre Recording Database when Material Request status changes to Issued"""
	# Only process if status is Issued
	if doc.status != "Issued":
		return
	
	# Check if this Material Request is linked to a Tyre Request
	tyre_requests = frappe.db.get_all(
		"Tyre Request and Analysis Form",
		filters={"material_requisition_no": doc.name},
		fields=["name"]
	)
	
	if not tyre_requests:
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
	
	# Update Tyre Recording Database records
	for tyre_request_name in tyre_requests:
		tyre_request = frappe.get_doc("Tyre Request and Analysis Form", tyre_request_name.name)
		
		# Update Tyre Recording Database records if they exist
		# Note: Database records are created when tyres are issued, not on request submit
		for req_item in tyre_request.requested_items:
			# Check if there are any Tyre Recording Database records for these items
			tyre_dbs = frappe.db.get_all(
				"Tyre Recording Database",
				filters={"item_code": req_item.requested_item_no},
				fields=["name"]
			)
			
			for tyre_db in tyre_dbs:
				update_data = {
					"last_tyre_request": tyre_request.name,
					"last_material_request": doc.name
				}
				if stock_entries:
					update_data["last_stock_entry"] = stock_entries[0].name
				
				frappe.db.set_value("Tyre Recording Database", tyre_db.name, update_data)

def update_tyre_recording_on_stock_entry(doc, method):
	"""Update Tyre Recording Database when Stock Entry is submitted from Material Request"""
	if not doc.material_request:
		return
	
	if doc.purpose not in ["Material Issue", "Material Transfer"]:
		return
	
	# Check if this Material Request is linked to a Tyre Request
	tyre_requests = frappe.db.get_all(
		"Tyre Request and Analysis Form",
		filters={"material_requisition_no": doc.material_request},
		fields=["name"]
	)
	
	if not tyre_requests:
		return
	
	# Update Tyre Recording Database records
	for tyre_request_name in tyre_requests:
		tyre_request = frappe.get_doc("Tyre Request and Analysis Form", tyre_request_name.name)
		
		# Update Tyre Recording Database records if they exist
		for req_item in tyre_request.requested_items:
			tyre_dbs = frappe.db.get_all(
				"Tyre Recording Database",
				filters={"item_code": req_item.requested_item_no},
				fields=["name"]
			)
			
			for tyre_db in tyre_dbs:
				frappe.db.set_value("Tyre Recording Database", tyre_db.name, {
					"last_tyre_request": tyre_request.name,
					"last_material_request": doc.material_request,
					"last_stock_entry": doc.name
				})


def sync_purchase_request_status_to_source_material_requests(doc, method):
	"""Sync Purchase-type Material Request status to linked source Material Requests.

	Use case:
	- You create a Purchase Request using Material Request with items that have `custom_mr_number`
	  pointing to the original Material Requests (typically Material Issue).
	- When the Purchase Request is created (Draft) or its workflow/status changes later,
	  we want to push that PR status into the original Material Requests' `custom_mr_status` field.
	"""
	# Only handle Material Request doctype
	if doc.doctype != "Material Request":
		return

	# Only sync for Purchase-type Material Requests
	if getattr(doc, "material_request_type", None) != "Purchase":
		return

	# Determine the status we want to propagate.
	# Prefer the custom workflow-based status if present (PR Draft / PR Requested / etc.),
	# otherwise fall back to the core document status.
	pr_status = getattr(doc, "custom_mr_status", None) or getattr(doc, "status", None)
	if not pr_status:
		return

	# Collect unique source Material Requests from child items' custom_mr_number
	source_mrs = {
		getattr(item, "custom_mr_number")
		for item in (doc.items or [])
		if getattr(item, "custom_mr_number", None)
	}

	if not source_mrs:
		return

	for mr_name in source_mrs:
		if not mr_name:
			continue

		# Make sure the referenced Material Request exists
		if not frappe.db.exists("Material Request", mr_name):
			continue

		# Avoid accidental loops if someone links Purchase → Purchase
		mr_type = frappe.db.get_value("Material Request", mr_name, "material_request_type")
		if mr_type == "Purchase":
			continue

		current_status = frappe.db.get_value("Material Request", mr_name, "custom_mr_status")
		if current_status == pr_status:
			continue

		# Update without touching modified timestamp to keep the original MR history cleaner
		frappe.db.set_value(
			"Material Request",
			mr_name,
			"custom_mr_status",
			pr_status,
			update_modified=False,
		)


def sync_source_mr_status_from_purchase_order(doc, method):
	"""When Purchase Order changes, update linked Purchase MRs and their source MRs' custom status.

	This ensures that status changes like Pending → Ordered / Partially Ordered,
	which are driven by Purchase Orders, are reflected back on the original
	Material Requests referenced via `custom_mr_number`.
	"""

	# Collect distinct Material Requests linked on PO items
	material_requests = {
		getattr(item, "material_request")
		for item in (doc.items or [])
		if getattr(item, "material_request", None)
	}

	if not material_requests:
		return

	for mr_name in material_requests:
		if not mr_name:
			continue

		if not frappe.db.exists("Material Request", mr_name):
			continue

		mr_doc = frappe.get_doc("Material Request", mr_name)

		# Reuse the existing logic; this will:
		# - Ensure it's a Purchase-type MR
		# - Read its current status / custom_mr_status
		# - Push that status into all source MRs via custom_mr_number
		sync_purchase_request_status_to_source_material_requests(mr_doc, method)


def sync_source_mr_status_from_purchase_receipt(doc, method):
	"""When Purchase Receipt changes, update linked Purchase MRs and their source MRs' custom status.

	This covers transitions like Ordered → Received / Partially Received that
	are driven by Purchase Receipts.
	"""

	# Collect distinct Material Requests linked on PR items
	material_requests = {
		getattr(item, "material_request")
		for item in (doc.items or [])
		if getattr(item, "material_request", None)
	}

	if not material_requests:
		return

	for mr_name in material_requests:
		if not mr_name:
			continue

		if not frappe.db.exists("Material Request", mr_name):
			continue

		mr_doc = frappe.get_doc("Material Request", mr_name)

		# Reuse the same propagation logic from the Purchase MR
		sync_purchase_request_status_to_source_material_requests(mr_doc, method)

