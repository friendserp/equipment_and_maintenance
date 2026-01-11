# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe

def create_workflows():
	"""Create workflows for equipment and maintenance documents"""
	
	# Create Workflow States
	states = [
		{"workflow_state_name": "Draft", "icon": "question-sign", "style": "Inverse"},
		{"workflow_state_name": "Checked", "icon": "ok-sign", "style": "Info"},
		{"workflow_state_name": "Approved", "icon": "ok", "style": "Success"},
		{"workflow_state_name": "Cancelled", "icon": "remove", "style": "Danger"},
		{"workflow_state_name": "Rejected", "icon": "remove-circle", "style": "Danger"},
		{"workflow_state_name": "Under Review", "icon": "search", "style": "Warning"},
		{"workflow_state_name": "Received", "icon": "ok-circle", "style": "Success"},
		{"workflow_state_name": "Handed Over", "icon": "ok-circle", "style": "Success"},
		{"workflow_state_name": "Equipment Dept Approved", "icon": "ok-sign", "style": "Info"},
		{"workflow_state_name": "DGM Approved", "icon": "ok-sign", "style": "Info"},
		{"workflow_state_name": "Survey Committee Approved", "icon": "ok-sign", "style": "Info"},
		{"workflow_state_name": "General Manager Approved", "icon": "ok", "style": "Success"},
		{"workflow_state_name": "Maintenance Approved", "icon": "ok-sign", "style": "Info"},
		{"workflow_state_name": "Under Maintenance Review", "icon": "search", "style": "Warning"},
		{"workflow_state_name": "Admin Approved", "icon": "ok-sign", "style": "Info"},
		{"workflow_state_name": "Under Admin Review", "icon": "search", "style": "Warning"},
		{"workflow_state_name": "GM Approved", "icon": "ok", "style": "Success"},
		{"workflow_state_name": "Collected", "icon": "ok-circle", "style": "Success"},
	]
	
	for state_data in states:
		if not frappe.db.exists("Workflow State", state_data["workflow_state_name"]):
			frappe.get_doc({
				"doctype": "Workflow State",
				**state_data
			}).insert(ignore_permissions=True)
	
	# Create Workflow Actions
	actions = [
		"Check",
		"Approve",
		"Reject",
		"Resubmit",
		"Send for Review",
		"Receive",
		"Hand Over",
		"Equipment Dept Approve",
		"DGM Approve",
		"Survey Committee Approve",
		"General Manager Approve",
		"Maintenance Approve",
		"Admin Approve",
		"GM Approve",
		"Collect",
	]
	
	for action_name in actions:
		if not frappe.db.exists("Workflow Action Master", action_name):
			frappe.get_doc({
				"doctype": "Workflow Action Master",
				"workflow_action_name": action_name
			}).insert(ignore_permissions=True)
	
	# Create Battery Request and Analysis Form Workflow
	create_battery_request_workflow()
	
	# Create Battery Recording Database Form Workflow
	create_battery_recording_workflow()
	
	# Create Battery Issue and Return Report Form Workflow
	create_battery_issue_return_workflow()
	
	# Create Equipment Disposal Request Workflow
	create_equipment_disposal_workflow()
	
	# Create Cannibalization Form Workflow
	create_cannibalization_workflow()
	
	# Create Maintenance Request Workflow
	create_maintenance_request_workflow()
	
	# Create Machinery Time Sheet Registration Workflow
	create_machinery_timesheet_workflow()
	
	# Create Fuel Request Workflow
	create_fuel_request_workflow()
	
	# Create Equipment Transfer Form Workflow
	create_equipment_transfer_workflow()
	
	# Create Cost Control and Registration Form Workflow
	create_cost_control_workflow()
	
	# Create Machinery Handover Form Workflow
	create_machinery_handover_workflow()
	
	# Create Maintenance Work Order Workflow
	create_maintenance_work_order_workflow()
	
	# Create Maintenance Job Completion Workflow
	create_maintenance_job_completion_workflow()
	
	# Create Tyre Request and Analysis Form Workflow
	create_tyre_request_workflow()
	
	# Create Tyre Issue and Return Report Form Workflow
	create_tyre_issue_return_workflow()
	
	# Create Tyre Recording Database Form Workflow
	create_tyre_recording_workflow()
	
	frappe.db.commit()
	frappe.msgprint("Workflows created successfully!")

def create_battery_request_workflow():
	"""Create workflow for Battery Request and Analysis Form"""
	# Delete existing workflow if it exists to recreate it
	if frappe.db.exists("Workflow", "Battery Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Battery Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Battery Request and Analysis Form Workflow"
	workflow.document_type = "Battery Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_battery_recording_workflow():
	"""Create workflow for Battery Recording Database Form"""
	if frappe.db.exists("Workflow", "Battery Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Battery Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Battery Recording Database Form Workflow"
	workflow.document_type = "Battery Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_battery_issue_return_workflow():
	"""Create workflow for Battery Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Battery Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Battery Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Battery Issue and Return Report Form Workflow"
	workflow.document_type = "Battery Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_equipment_disposal_workflow():
	"""Create workflow for Equipment Disposal Request"""
	if frappe.db.exists("Workflow", "Equipment Disposal Request Workflow"):
		frappe.delete_doc("Workflow", "Equipment Disposal Request Workflow", force=1, ignore_permissions=True)
		frappe.db.commit()
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Equipment Disposal Request Workflow"
	workflow.document_type = "Equipment Disposal Request"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Equipment Dept Approved",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "DGM Approved",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Survey Committee Approved",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "General Manager Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Rejected",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Cancelled",
		"doc_status": 2,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	# Transitions from Draft
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Equipment Dept Approve",
		"next_state": "Equipment Dept Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Reject",
		"next_state": "Rejected",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	# Transitions from Equipment Dept Approved
	workflow.append("transitions", {
		"state": "Equipment Dept Approved",
		"action": "DGM Approve",
		"next_state": "DGM Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Equipment Dept Approved",
		"action": "Reject",
		"next_state": "Rejected",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	# Transitions from DGM Approved
	workflow.append("transitions", {
		"state": "DGM Approved",
		"action": "Survey Committee Approve",
		"next_state": "Survey Committee Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "DGM Approved",
		"action": "Reject",
		"next_state": "Rejected",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	# Transitions from Survey Committee Approved
	workflow.append("transitions", {
		"state": "Survey Committee Approved",
		"action": "General Manager Approve",
		"next_state": "General Manager Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Survey Committee Approved",
		"action": "Reject",
		"next_state": "Rejected",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	# Transition from Rejected back to Draft
	workflow.append("transitions", {
		"state": "Rejected",
		"action": "Resubmit",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True, ignore_links=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_cannibalization_workflow():
	"""Create workflow for Cannibalization Form"""
	if frappe.db.exists("Workflow", "Cannibalization Form Workflow"):
		frappe.delete_doc("Workflow", "Cannibalization Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Cannibalization Form Workflow"
	workflow.document_type = "Cannibalization Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Under Maintenance Review",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Maintenance Approved",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Under Admin Review",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Admin Approved",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "GM Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Send for Review",
		"next_state": "Under Maintenance Review",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Under Maintenance Review",
		"action": "Maintenance Approve",
		"next_state": "Maintenance Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Maintenance Approved",
		"action": "Send for Review",
		"next_state": "Under Admin Review",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Under Admin Review",
		"action": "Admin Approve",
		"next_state": "Admin Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Admin Approved",
		"action": "GM Approve",
		"next_state": "GM Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Under Maintenance Review",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Under Admin Review",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_maintenance_request_workflow():
	"""Create workflow for Maintenance Request"""
	if frappe.db.exists("Workflow", "Maintenance Request Workflow"):
		frappe.delete_doc("Workflow", "Maintenance Request Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Maintenance Request Workflow"
	workflow.document_type = "Maintenance Request"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Received",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Approved",
		"action": "Receive",
		"next_state": "Received",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Approved",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_machinery_timesheet_workflow():
	"""Create workflow for Machinery Time Sheet Registration"""
	if frappe.db.exists("Workflow", "Machinery Time Sheet Registration Workflow"):
		frappe.delete_doc("Workflow", "Machinery Time Sheet Registration Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Machinery Time Sheet Registration Workflow"
	workflow.document_type = "Machinery Time Sheet Registration"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_fuel_request_workflow():
	"""Create workflow for Fuel Request"""
	if frappe.db.exists("Workflow", "Fuel Request Workflow"):
		frappe.delete_doc("Workflow", "Fuel Request Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Fuel Request Workflow"
	workflow.document_type = "Fuel Request"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_equipment_transfer_workflow():
	"""Create workflow for Equipment Transfer Form"""
	if frappe.db.exists("Workflow", "Equipment Transfer Form Workflow"):
		frappe.delete_doc("Workflow", "Equipment Transfer Form Workflow", force=1, ignore_permissions=True)
		frappe.db.commit()
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Equipment Transfer Form Workflow"
	workflow.document_type = "Equipment Transfer Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Cancelled",
		"doc_status": 2,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True, ignore_links=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_cost_control_workflow():
	"""Create workflow for Cost Control and Registration Form"""
	if frappe.db.exists("Workflow", "Cost Control and Registration Form Workflow"):
		frappe.delete_doc("Workflow", "Cost Control and Registration Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Cost Control and Registration Form Workflow"
	workflow.document_type = "Cost Control and Registration Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_machinery_handover_workflow():
	"""Create workflow for Machinery Handover Form"""
	if frappe.db.exists("Workflow", "Machinery Handover Form Workflow"):
		frappe.delete_doc("Workflow", "Machinery Handover Form Workflow", force=1, ignore_permissions=True)
		frappe.db.commit()
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Machinery Handover Form Workflow"
	workflow.document_type = "Machinery Handover Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Received",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Handed Over",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Receive",
		"next_state": "Received",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Received",
		"action": "Hand Over",
		"next_state": "Handed Over",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Received",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True, ignore_links=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_maintenance_work_order_workflow():
	"""Create workflow for Maintenance Work Order"""
	if frappe.db.exists("Workflow", "Maintenance Work Order Workflow"):
		frappe.delete_doc("Workflow", "Maintenance Work Order Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Maintenance Work Order Workflow"
	workflow.document_type = "Maintenance Work Order"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_maintenance_job_completion_workflow():
	"""Create workflow for Maintenance Job Completion"""
	if frappe.db.exists("Workflow", "Maintenance Job Completion Workflow"):
		frappe.delete_doc("Workflow", "Maintenance Job Completion Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Maintenance Job Completion Workflow"
	workflow.document_type = "Maintenance Job Completion"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Collected",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Collect",
		"next_state": "Collected",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_request_workflow():
	"""Create workflow for Tyre Request and Analysis Form"""
	if frappe.db.exists("Workflow", "Tyre Request and Analysis Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Request and Analysis Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Request and Analysis Form Workflow"
	workflow.document_type = "Tyre Request and Analysis Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_issue_return_workflow():
	"""Create workflow for Tyre Issue and Return Report Form"""
	if frappe.db.exists("Workflow", "Tyre Issue and Return Report Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Issue and Return Report Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Issue and Return Report Form Workflow"
	workflow.document_type = "Tyre Issue and Return Report Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)

def create_tyre_recording_workflow():
	"""Create workflow for Tyre Recording Database Form"""
	if frappe.db.exists("Workflow", "Tyre Recording Database Form Workflow"):
		frappe.delete_doc("Workflow", "Tyre Recording Database Form Workflow", force=1, ignore_permissions=True)
	
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = "Tyre Recording Database Form Workflow"
	workflow.document_type = "Tyre Recording Database Form"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	
	workflow.append("states", {
		"state": "Draft",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Checked",
		"doc_status": 0,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	workflow.append("states", {
		"state": "Approved",
		"doc_status": 1,
		"allow_edit": "System Manager",
		"is_optional_state": 0,
		"send_email": 0
	})
	
	workflow.append("transitions", {
		"state": "Draft",
		"action": "Check",
		"next_state": "Checked",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	workflow.append("transitions", {
		"state": "Checked",
		"action": "Reject",
		"next_state": "Draft",
		"allowed": "System Manager",
		"allow_self_approval": 1
	})
	
	workflow.insert(ignore_permissions=True)
