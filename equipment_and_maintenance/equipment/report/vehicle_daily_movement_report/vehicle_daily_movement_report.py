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
			"fieldname": "vehicle_type",
			"label": _("Vehicle Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "start_place",
			"label": _("Start Place"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "end_place",
			"label": _("End Place"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "reason_of_travel",
			"label": _("Reason of Travel"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "starting_km",
			"label": _("Starting KM"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "ending_km",
			"label": _("Ending KM"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "km_difference",
			"label": _("KM Difference"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "driver_name",
			"label": _("Driver's Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "traveler_name",
			"label": _("Traveler's Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "received_fuel",
			"label": _("Received Fuel (L)"),
			"fieldtype": "Float",
			"width": 100
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
			vehicle_type,
			start_place,
			end_place,
			reason_of_travel,
			starting_km,
			ending_km,
			km_difference,
			driver_name,
			traveler_name,
			received_fuel
		FROM `tabVehicle Daily Movement`
		WHERE {where_clause}
		ORDER BY date DESC, creation DESC
	""", as_dict=1)
	
	return data


def calculate_statistics(data):
	if not data:
		return {}
	
	total_movements = len(data)
	total_km = sum([flt(d.get("km_difference", 0)) for d in data])
	total_fuel = sum([flt(d.get("received_fuel", 0)) for d in data])
	
	# Group by reason of travel
	reason_counts = {}
	for d in data:
		reason = d.get("reason_of_travel") or "Not Specified"
		reason_counts[reason] = reason_counts.get(reason, 0) + 1
	
	# Group by project
	project_counts = {}
	for d in data:
		project = d.get("project") or "Not Specified"
		project_counts[project] = project_counts.get(project, 0) + 1
	
	return {
		"total_movements": total_movements,
		"total_km": total_km,
		"total_fuel": total_fuel,
		"reason_counts": reason_counts,
		"project_counts": project_counts
	}

