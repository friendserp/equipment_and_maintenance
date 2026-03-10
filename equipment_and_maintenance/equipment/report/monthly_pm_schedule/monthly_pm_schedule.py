# Copyright (c) 2026, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "equipment_type",
			"label": _("Equipment Type"),
			"fieldtype": "Link",
			"options": "Asset Sub Category",
			"width": 120
		},
		{
			"fieldname": "make",
			"label": _("Make"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "model",
			"label": _("Model"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "plate_number",
			"label": _("Plate No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "planned_hours_km",
			"label": _("Planned: Hr/Km"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "planned_service_type",
			"label": _("Planned: Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "performed_hours_km",
			"label": _("Performed: Hr/Km"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "performed_service_type",
			"label": _("Performed: Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "performed_date",
			"label": _("Performed Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "pm_performed_as_per_schedule",
			"label": _("As per Schedule?"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "current_hours_km",
			"label": _("Current Hr/Km"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "scheduled_hours_km",
			"label": _("Next: Hr/Km"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "scheduled_service_type",
			"label": _("Next: Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "week_1",
			"label": _("W1"),
			"fieldtype": "Data",
			"width": 50
		},
		{
			"fieldname": "week_2",
			"label": _("W2"),
			"fieldtype": "Data",
			"width": 50
		},
		{
			"fieldname": "week_3",
			"label": _("W3"),
			"fieldtype": "Data",
			"width": 50
		},
		{
			"fieldname": "week_4",
			"label": _("W4"),
			"fieldtype": "Data",
			"width": 50
		},
		{
			"fieldname": "remark",
			"label": _("Remark"),
			"fieldtype": "Small Text",
			"width": 200
		}
	]


def get_data(filters=None):
	"""Get all submitted Preventive Maintenance Plans with PM Done data"""
	
	if not filters:
		filters = {}
	
	# Build WHERE conditions
	conditions = ["pmp.docstatus = 1"]
	
	planning_month = filters.get("planning_month")
	if planning_month and planning_month != "All":
		conditions.append(f"pmp.planning_month = '{planning_month}'")
	
	if filters.get("planning_year"):
		conditions.append(f"pmp.planning_year = {filters.planning_year}")
	
	if filters.get("department"):
		conditions.append(f"pmp.department = '{filters.department}'")
	
	if filters.get("project"):
		conditions.append(f"pmp.project = '{filters.project}'")
	
	if filters.get("equipment"):
		conditions.append(f"pmp.equipment = '{filters.equipment}'")
	
	where_clause = " AND ".join(conditions)
	
	# Get month number for next month calculation
	month_map = {
		"January": 1, "February": 2, "March": 3, "April": 4,
		"May": 5, "June": 6, "July": 7, "August": 8,
		"September": 9, "October": 10, "November": 11, "December": 12
	}
	
	# Get all submitted plans
	data = frappe.db.sql(f"""
		SELECT 
			pmp.name as plan_name,
			pmp.equipment,
			pmp.equipment,
			pmp.equipment_code,
			pmp.make,
			pmp.model,
			pmp.equipment_category,
			pmp.equipment_sub_category as equipment_type,
			pmp.planning_month,
			pmp.planning_year,
			pmp.current_hours_km,
			pmp.planned_week,
			pmp.planned_service_type,
			pmp.planned_hours_km,
			pmp.remark,
			pmp.department,
			pmp.project,
			pmp.is_maintenance_done
		FROM `tabPreventive Maintenance Plan` pmp
		WHERE {where_clause}
		ORDER BY pmp.equipment_category, pmp.equipment_sub_category, pmp.equipment, pmp.planning_year DESC, pmp.planning_month DESC
	""", as_dict=1)
	
	# Enrich data with PM Done information
	result = []
	
	for row in data:
		equipment = row.get("equipment")
		plan_name = row.get("plan_name")
		planning_month = row.get("planning_month")
		planning_year = row.get("planning_year")
		
		# Get PM Done linked to this plan (or latest PM Done for this equipment)
		pm_done = frappe.db.get_all(
			"Preventive Maintenance Done",
			filters={
				"equipment": equipment,
				"docstatus": 1,
				"plan": plan_name
			},
			fields=["actual_hours_km", "service_type", "actual_date", 
					"pm_performed_as_per_schedule", "remark", "completion_notes"],
			order_by="actual_date DESC",
			limit=1
		)
		
		# If no PM Done linked to this plan, get latest PM Done for equipment
		if not pm_done:
			pm_done = frappe.db.get_all(
				"Preventive Maintenance Done",
				filters={
					"equipment": equipment,
					"docstatus": 1
				},
				fields=["actual_hours_km", "service_type", "actual_date", 
						"pm_performed_as_per_schedule", "remark", "completion_notes"],
				order_by="actual_date DESC",
				limit=1
			)
		
		# Get next month plan (only if planning_month and planning_year are available)
		next_month_plan = None
		if planning_month and planning_year:
			next_month_num = month_map.get(planning_month, 1) + 1
			if next_month_num > 12:
				next_month_num = 1
				next_year = planning_year + 1
			else:
				next_year = planning_year
			
			next_month_name = [k for k, v in month_map.items() if v == next_month_num][0]
			
			next_month_plan = frappe.db.get_all(
				"Preventive Maintenance Plan",
				filters={
					"equipment": equipment,
					"planning_month": next_month_name,
					"planning_year": next_year,
					"docstatus": 1
				},
				fields=["planned_week", "planned_service_type", "planned_hours_km"],
				limit=1
			)
		
		# Build week indicators for next month
		week_1 = ""
		week_2 = ""
		week_3 = ""
		week_4 = ""
		
		if next_month_plan:
			planned_week = next_month_plan[0].get("planned_week", "")
			if planned_week == "Week 1":
				week_1 = "X"
			elif planned_week == "Week 2":
				week_2 = "X"
			elif planned_week == "Week 3":
				week_3 = "X"
			elif planned_week == "Week 4":
				week_4 = "X"
		
		# Get current reading from latest PM Done
		current_reading = row.get("current_hours_km", 0)
		if pm_done and pm_done[0]:
			current_reading = pm_done[0].get("actual_hours_km", current_reading)
		
		# Build result row
		result_row = {
			"equipment_type": row.get("equipment_type"),
			"make": row.get("make"),
			"model": row.get("model"),
			"plate_number": row.get("equipment"),
			"planned_hours_km": row.get("planned_hours_km"),
			"planned_service_type": row.get("planned_service_type"),
			"performed_hours_km": pm_done[0].get("actual_hours_km") if pm_done and pm_done[0] else None,
			"performed_service_type": pm_done[0].get("service_type") if pm_done and pm_done[0] else None,
			"performed_date": pm_done[0].get("actual_date") if pm_done and pm_done[0] else None,
			"pm_performed_as_per_schedule": pm_done[0].get("pm_performed_as_per_schedule") if pm_done and pm_done[0] else None,
			"current_hours_km": current_reading,
			"scheduled_hours_km": next_month_plan[0].get("planned_hours_km") if next_month_plan else None,
			"scheduled_service_type": next_month_plan[0].get("planned_service_type") if next_month_plan else None,
			"week_1": week_1,
			"week_2": week_2,
			"week_3": week_3,
			"week_4": week_4,
			"remark": row.get("remark") or (pm_done[0].get("remark") if pm_done and pm_done[0] else None) or (pm_done[0].get("completion_notes") if pm_done and pm_done[0] else None)
		}
		
		result.append(result_row)
	
	return result
