# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, date_diff, get_first_day, get_last_day
from datetime import datetime


def execute(filters=None):
	"""Generate Preventive Maintenance Plan Calendar View"""
	
	# Get start date from filters or use current date
	start_date = filters.get("start_date") if filters else getdate()
	start_date = getdate(start_date)
	
	# Generate 12 months from start date
	months = []
	month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
	
	for i in range(12):
		month_date = add_months(start_date, i)
		months.append({
			"month": month_date.month,
			"year": month_date.year,
			"name": month_names[month_date.month - 1],
			"date": month_date
		})
	
	# Get all active Preventive Maintenance Schedules
	schedules = frappe.get_all(
		"Preventive Maintenance Schedule",
		filters={"status": ["in", ["Active", "Overdue"]]},
		fields=[
			"name", "equipment", "equipment_code", "plate_no",
			"current_hours", "current_kilometers",
			"last_service_hours", "last_service_kilometers",
			"next_service_due_hours", "next_service_due_kilometers",
			"start_date"
		]
	)
	
	# Get equipment details
	equipment_map = {}
	if schedules:
		equipment_names = list(set([s.equipment for s in schedules if s.equipment]))
		if equipment_names:
			equipment_list = frappe.get_all(
				"Equipment Master",
				filters={"name": ["in", equipment_names]},
				fields=["name", "equipment_category", "equipment_sub_category"]
			)
			for eq in equipment_list:
				equipment_map[eq.name] = eq
	
	# Standard intervals
	hour_intervals = [250, 500, 1000, 2000, 6000]
	km_intervals = [2500, 5000, 10000, 30000, 60000]
	
	# Average usage rates (can be made configurable)
	avg_monthly_hours = flt(filters.get("avg_monthly_hours")) if filters else 50
	avg_monthly_km = flt(filters.get("avg_monthly_km")) if filters else 500
	
	columns = get_columns(months)
	data = []
	
	# Statistics for charts
	stats = {
		"total_equipment": len(schedules),
		"services_by_month": {},
		"services_by_type": {"Hours": 0, "Kilometers": 0},
		"overdue_count": 0,
		"upcoming_services": []
	}
	
	for schedule in schedules:
		equipment = equipment_map.get(schedule.equipment, {})
		equipment_type = equipment.get("equipment_category") or equipment.get("equipment_sub_category") or ""
		
		# Get initial readings
		initial_hours = flt(schedule.current_hours) or 0
		initial_km = flt(schedule.current_kilometers) or 0
		
		# Get last service readings
		last_hours = flt(schedule.last_service_hours) or initial_hours
		last_km = flt(schedule.last_service_kilometers) or initial_km
		
		# Calculate all future service milestones
		service_milestones = []
		
		# Calculate hour milestones
		if schedule.current_hours:
			current_hours = flt(schedule.current_hours)
			for interval in hour_intervals:
				next_milestone = last_hours + interval
				if next_milestone > current_hours:
					# Calculate estimated date
					hours_needed = next_milestone - current_hours
					months_needed = hours_needed / avg_monthly_hours if avg_monthly_hours > 0 else 0
					estimated_date = add_months(start_date, int(months_needed))
					
					service_milestones.append({
						"type": "Hours",
						"value": interval,
						"milestone": next_milestone,
						"estimated_date": estimated_date,
						"display": f"{interval}H"
					})
		
		# Calculate kilometer milestones
		if schedule.current_kilometers:
			current_km = flt(schedule.current_kilometers)
			for interval in km_intervals:
				next_milestone = last_km + interval
				if next_milestone > current_km:
					# Calculate estimated date
					km_needed = next_milestone - current_km
					months_needed = km_needed / avg_monthly_km if avg_monthly_km > 0 else 0
					estimated_date = add_months(start_date, int(months_needed))
					
					service_milestones.append({
						"type": "Kilometers",
						"value": interval,
						"milestone": next_milestone,
						"estimated_date": estimated_date,
						"display": f"{interval}KM"
					})
		
		# Create row data
		row = {
			"equipment_type": equipment_type,
			"plate_number": schedule.plate_no or schedule.equipment_code or "",
			"initial_km_hr": f"{initial_km:.0f}KM / {initial_hours:.0f}H" if initial_km or initial_hours else "",
		}
		
		# Fill monthly columns
		for month_info in months:
			month_key = f"{month_info['name']}_{month_info['year']}"
			row[month_key] = ""
			
			# Check if any service milestone falls in this month
			# Use first day of month for comparison
			month_start = get_first_day(month_info["date"])
			month_end = get_last_day(month_info["date"])
			
			for milestone in service_milestones:
				est_date = milestone["estimated_date"]
				if month_start <= est_date <= month_end:
					if row[month_key]:
						row[month_key] += ", " + milestone["display"]
					else:
						row[month_key] = milestone["display"]
					
					# Update statistics
					month_label = f"{month_info['name']} {month_info['year']}"
					if month_label not in stats["services_by_month"]:
						stats["services_by_month"][month_label] = 0
					stats["services_by_month"][month_label] += 1
					stats["services_by_type"][milestone["type"]] += 1
					
					# Track upcoming services
					if est_date >= getdate():
						stats["upcoming_services"].append({
							"equipment": schedule.plate_no or schedule.equipment_code,
							"date": est_date,
							"milestone": milestone["display"]
						})
		
		data.append(row)
	
	# Sort upcoming services by date
	stats["upcoming_services"].sort(key=lambda x: x["date"])
	
	return columns, data


def get_columns(months):
	"""Generate column definitions"""
	columns = [
		{
			"fieldname": "equipment_type",
			"label": _("Equipment Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "plate_number",
			"label": _("Plate Number"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "initial_km_hr",
			"label": _("Initial KM / HR"),
			"fieldtype": "Data",
			"width": 120
		}
	]
	
	# Add monthly columns
	for month_info in months:
		month_key = f"{month_info['name']}_{month_info['year']}"
		columns.append({
			"fieldname": month_key,
			"label": f"{month_info['name']} {month_info['year']}",
			"fieldtype": "Data",
			"width": 100
		})
	
	return columns

