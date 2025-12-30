# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	
	# Calculate statistics for charts
	stats = calculate_statistics(data)
	
	return columns, data, None, None, stats


def get_columns():
	return [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 120
		},
		{
			"fieldname": "plate_number",
			"label": _("Plate Number"),
			"fieldtype": "Link",
			"options": "Equipment Master",
			"width": 120
		},
		{
			"fieldname": "machine_type",
			"label": _("Machine Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "operators_name",
			"label": _("Operator's Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "morning_start",
			"label": _("Morning Start"),
			"fieldtype": "Time",
			"width": 100
		},
		{
			"fieldname": "morning_end",
			"label": _("Morning End"),
			"fieldtype": "Time",
			"width": 100
		},
		{
			"fieldname": "afternoon_start",
			"label": _("Afternoon Start"),
			"fieldtype": "Time",
			"width": 100
		},
		{
			"fieldname": "afternoon_end",
			"label": _("Afternoon End"),
			"fieldtype": "Time",
			"width": 100
		},
		{
			"fieldname": "total_working_hour",
			"label": _("Total Working Hour"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "idle_time",
			"label": _("Idle Time"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "time_keeper",
			"label": _("Time Keeper"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "performed_work",
			"label": _("Performed Work"),
			"fieldtype": "Data",
			"width": 200
		}
	]


def get_data(filters):
	conditions = []
	
	if filters.get("project"):
		conditions.append(f"project = '{filters.project}'")
	if filters.get("plate_number"):
		conditions.append(f"plate_number = '{filters.plate_number}'")
	if filters.get("from_date"):
		conditions.append(f"date >= '{filters.from_date}'")
	if filters.get("to_date"):
		conditions.append(f"date <= '{filters.to_date}'")
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	data = frappe.db.sql(f"""
		SELECT 
			date,
			project,
			plate_number,
			machine_type,
			operators_name,
			morning_start,
			morning_end,
			afternoon_start,
			afternoon_end,
			total_working_hour,
			idle_time,
			time_keeper,
			performed_work
		FROM `tabMachinery Time Sheet Registration`
		WHERE {where_clause}
		ORDER BY date DESC, creation DESC
	""", as_dict=1)
	
	return data


def calculate_statistics(data):
	if not data:
		return {}
	
	total_records = len(data)
	total_working_hours = sum([flt(d.get("total_working_hour", 0)) for d in data])
	total_idle_time = sum([flt(d.get("idle_time", 0)) for d in data])
	
	# Group by machine type
	machine_counts = {}
	for d in data:
		machine = d.get("machine_type") or "Not Specified"
		machine_counts[machine] = machine_counts.get(machine, 0) + 1
	
	# Group by project
	project_counts = {}
	for d in data:
		project = d.get("project") or "Not Specified"
		project_counts[project] = project_counts.get(project, 0) + 1
	
	# Group by operator
	operator_counts = {}
	for d in data:
		operator = d.get("operators_name") or "Not Specified"
		operator_counts[operator] = operator_counts.get(operator, 0) + 1
	
	return {
		"total_records": total_records,
		"total_working_hours": total_working_hours,
		"total_idle_time": total_idle_time,
		"machine_counts": machine_counts,
		"project_counts": project_counts,
		"operator_counts": operator_counts
	}

