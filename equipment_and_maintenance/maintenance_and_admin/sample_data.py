# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

"""
Sample Data for Preventive Maintenance System
Run this script to populate sample maintenance intervals, tasks, and templates
Based on the service guide with proper interval mappings
"""

import frappe


def delete_all_preventive_maintenance_data():
	"""Delete all data from preventive maintenance doctypes"""
	print("Deleting all preventive maintenance data...")
	
	deleted_counts = {}
	batch_size = 10  # Commit every N records
	
	# Delete Preventive Maintenance Logs first (they reference schedules)
	logs = frappe.get_all("Preventive Maintenance Log", pluck="name")
	deleted_counts["logs"] = 0
	for i, log in enumerate(logs, 1):
		try:
			frappe.delete_doc("Preventive Maintenance Log", log, force=1)
			deleted_counts["logs"] += 1
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting log {log}: {str(e)}")
			frappe.db.rollback()
	if logs:
		frappe.db.commit()
	
	# Delete Preventive Maintenance Schedules
	schedules = frappe.get_all("Preventive Maintenance Schedule", pluck="name")
	deleted_counts["schedules"] = 0
	for i, schedule in enumerate(schedules, 1):
		try:
			frappe.delete_doc("Preventive Maintenance Schedule", schedule, force=1)
			deleted_counts["schedules"] += 1
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting schedule {schedule}: {str(e)}")
			frappe.db.rollback()
	if schedules:
		frappe.db.commit()
	
	# Delete templates
	templates = frappe.get_all("Preventive Maintenance Template", pluck="name")
	deleted_counts["templates"] = 0
	for i, template in enumerate(templates, 1):
		try:
			frappe.delete_doc("Preventive Maintenance Template", template, force=1)
			deleted_counts["templates"] += 1
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting template {template}: {str(e)}")
			frappe.db.rollback()
	if templates:
		frappe.db.commit()
	
	# Delete tasks
	tasks = frappe.get_all("Preventive Maintenance Task", pluck="name")
	deleted_counts["tasks"] = 0
	for i, task in enumerate(tasks, 1):
		try:
			frappe.delete_doc("Preventive Maintenance Task", task, force=1)
			deleted_counts["tasks"] += 1
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting task {task}: {str(e)}")
			frappe.db.rollback()
	if tasks:
		frappe.db.commit()
	
	# Delete intervals
	intervals = frappe.get_all("Maintenance Interval", pluck="name")
	deleted_counts["intervals"] = 0
	for i, interval in enumerate(intervals, 1):
		try:
			frappe.delete_doc("Maintenance Interval", interval, force=1)
			deleted_counts["intervals"] += 1
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting interval {interval}: {str(e)}")
			frappe.db.rollback()
	if intervals:
		frappe.db.commit()
	
	print(f"\nDeleted:")
	print(f"  - {deleted_counts.get('logs', 0)} Preventive Maintenance Logs")
	print(f"  - {deleted_counts.get('schedules', 0)} Preventive Maintenance Schedules")
	print(f"  - {deleted_counts.get('templates', 0)} Preventive Maintenance Templates")
	print(f"  - {deleted_counts.get('tasks', 0)} Preventive Maintenance Tasks")
	print(f"  - {deleted_counts.get('intervals', 0)} Maintenance Intervals")
	print("\nAll preventive maintenance data has been deleted.")


def delete_sample_data():
	"""Delete existing sample data (used internally by create_sample_data)"""
	print("Deleting existing sample data...")
	
	batch_size = 10  # Commit every N records
	
	# Delete templates
	templates = frappe.get_all("Preventive Maintenance Template", 
		filters={"template_name": ["in", ["Standard Vehicle Maintenance Template", "Standard Equipment Maintenance Template"]]},
		pluck="name")
	for i, template in enumerate(templates, 1):
		try:
			frappe.delete_doc("Preventive Maintenance Template", template, force=1)
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting template {template}: {str(e)}")
			frappe.db.rollback()
	if templates:
		frappe.db.commit()
	
	# Delete tasks
	tasks = frappe.get_all("Preventive Maintenance Task", pluck="name")
	for i, task in enumerate(tasks, 1):
		try:
			frappe.delete_doc("Preventive Maintenance Task", task, force=1)
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting task {task}: {str(e)}")
			frappe.db.rollback()
	if tasks:
		frappe.db.commit()
	
	# Delete intervals
	intervals = frappe.get_all("Maintenance Interval", pluck="name")
	for i, interval in enumerate(intervals, 1):
		try:
			frappe.delete_doc("Maintenance Interval", interval, force=1)
			if i % batch_size == 0:
				frappe.db.commit()
		except Exception as e:
			print(f"  Error deleting interval {interval}: {str(e)}")
			frappe.db.rollback()
	if intervals:
		frappe.db.commit()
	
	print(f"  Deleted {len(templates)} templates, {len(tasks)} tasks, {len(intervals)} intervals")


def create_sample_data():
	"""Create sample data for preventive maintenance system"""
	
	# Delete existing sample data first
	delete_sample_data()
	
	print("\nCreating Maintenance Intervals...")
	create_maintenance_intervals()
	print("✓ Maintenance Intervals created")
	
	print("\nCreating Preventive Maintenance Tasks...")
	create_maintenance_tasks()
	print("✓ Preventive Maintenance Tasks created")
	
	print("\nCreating Preventive Maintenance Templates...")
	create_maintenance_templates()
	print("✓ Preventive Maintenance Templates created")
	
	print("\n" + "="*50)
	print("Sample data created successfully!")
	print("="*50)
	frappe.msgprint("Sample data created successfully!")


def create_maintenance_intervals():
	"""Create standard maintenance intervals"""
	intervals = [
		{"name": "250 Hours", "type": "Hours", "value": 250},
		{"name": "500 Hours", "type": "Hours", "value": 500},
		{"name": "1000 Hours", "type": "Hours", "value": 1000},
		{"name": "2000 Hours", "type": "Hours", "value": 2000},
		{"name": "6000 Hours", "type": "Hours", "value": 6000},
		{"name": "2500 KM", "type": "Kilometers", "value": 2500},
		{"name": "5000 KM", "type": "Kilometers", "value": 5000},
		{"name": "10000 KM", "type": "Kilometers", "value": 10000},
		{"name": "30000 KM", "type": "Kilometers", "value": 30000},
		{"name": "60000 KM", "type": "Kilometers", "value": 60000},
	]
	
	created_count = 0
	for interval in intervals:
		if not frappe.db.exists("Maintenance Interval", interval["name"]):
			doc = frappe.get_doc({
				"doctype": "Maintenance Interval",
				"interval_name": interval["name"],
				"interval_type": interval["type"],
				"interval_value": interval["value"],
				"is_active": 1
			})
			doc.insert()
			created_count += 1
			frappe.db.commit()
	print(f"  Created {created_count} new intervals")


# Interval mapping: A=250H, B=500H, C=1000H, D=2000H, E=6000H, F=2500KM, G=5000KM, H=10000KM, I=30000KM, J=60000KM
# X = True, - = False
INTERVAL_MAP = {
	"250_hours": 0,  # Column A
	"500_hours": 1,  # Column B
	"1000_hours": 2,  # Column C
	"2000_hours": 3,  # Column D
	"6000_hours": 4,  # Column E
	"2500_km": 5,     # Column F
	"5000_km": 6,     # Column G
	"10000_km": 7,    # Column H
	"30000_km": 8,    # Column I
	"60000_km": 9     # Column J
}


def get_interval_flags(pattern):
	"""
	Convert pattern string (e.g., "X-X-X-X-X-X-X-X-X-X") to interval flags
	pattern: string with X or - for each interval (A-J)
	Columns: A=250H, B=500H, C=1000H, D=2000H, E=6000H, F=2500KM, G=5000KM, H=10000KM, I=30000KM, J=60000KM
	Returns: dict with interval flags
	"""
	flags = {
		"interval_250_hours": 0,
		"interval_500_hours": 0,
		"interval_1000_hours": 0,
		"interval_2000_hours": 0,
		"interval_6000_hours": 0,
		"interval_2500_km": 0,
		"interval_5000_km": 0,
		"interval_10000_km": 0,
		"interval_30000_km": 0,
		"interval_60000_km": 0
	}
	
	# Remove spaces and split by dash
	parts = pattern.replace(" ", "").split("-")
	if len(parts) != 10:
		# Try splitting by tab or other separators
		parts = pattern.replace(" ", "").replace("\t", "-").split("-")
		if len(parts) != 10:
			return flags
	
	interval_keys = [
		"interval_250_hours",    # A
		"interval_500_hours",    # B
		"interval_1000_hours",   # C
		"interval_2000_hours",   # D
		"interval_6000_hours",   # E
		"interval_2500_km",      # F
		"interval_5000_km",      # G
		"interval_10000_km",     # H
		"interval_30000_km",     # I
		"interval_60000_km"      # J
	]
	
	for i, part in enumerate(parts):
		if i < len(interval_keys):
			part_clean = part.strip().upper()
			if part_clean == "X":
				flags[interval_keys[i]] = 1
	
	return flags


def create_maintenance_tasks():
	"""Create maintenance tasks with proper interval mappings from service guide"""
	
	# Tasks with their interval patterns from the service guide
	# Pattern format: A-B-C-D-E-F-G-H-I-J where X=include, -=exclude
	tasks_data = [
		# LUBRICATION CHECK
		{"task_name": "Complete lubrication (as per Specifications)", "category": "LUBRICATION CHECK", 
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 1.0},
		
		# ENGINE SECTION
		{"task_name": "Wash /steam clean as required", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check coolant inhibitor strength", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Change coolant filters (as required)", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "--X-X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Check radiator mountings, thermostat, water pump circulation and all hoses /fittings",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check operation temperature", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "--X-X-X---X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Pressure test coolant system, flush system (as required)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "---X-X-X---X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Check shutter operation", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Inspect all drive belts and brackets (adjust as required)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect for all leaks, coolant leaks, fuel leaks and exhaust system leaks",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect for looseness /deterioration of linkages (hose/clamps), drive pulleys, etc",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect and service air intake system", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Air cleaner /pre cleaner (as required)", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "---X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Service/ change fuel filters (as required)", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Check operation of governor, throttle, choke (as applicable)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect lift pump, injection pump and injectors", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Clean and calibrate fuel injectors (pump every third time)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "----X----X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Change engine oil", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Change engine oil filter", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X---X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check oil pressure with master gauge", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Service crankcase ventilation system", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect/ adjust carburetor and linkages", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check spark plugs, ignition points, condenser, distributor cap, rotor, coil (replace if necessary)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Visually inspect condition of high tension leads/test suppression leads",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check for deterioration of wiring harness and clips (visually)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check dwell, timing and advance", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check engine governed RPM (as required)", "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Torque manifolds, adjust valve clearance (as required)",
		 "category": "ENGINE SECTION (MAIN & AUX. ENGINES) CHECK", "pattern": "----X----X", "mandatory": 0, "duration": 1.0},
		
		# ELECTRICAL SECTION
		{"task_name": "Clean battery cables; check cable and carrier condition", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check battery electrolyte level", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check/tighten starter motor mountings, connections and operation", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Perform cranking motor test", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "-----X---X", "mandatory": 0, "duration": 0.25},
		{"task_name": "Check operation of generator/alternator, regulator and circuits", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Monitor all instruments/gauges for correct operation/reading", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check proper operation of all lights, flashers, beacons, heater and defroster", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect all wiring and connections (Visual)", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check operating of safety controls /warning lights and horn's)", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Perform battery capacity (load) test", "category": "ELECTRICAL SECTION CHECK",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.5},
		
		# STEERING SECTION
		{"task_name": "Check for leaks and lubricant level power steering unit, steering box", "category": "STEERING SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check condition of power steering hydraulic cylinder and hoses", "category": "STEERING SECTION CHECK",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.25},
		{"task_name": "Check steering column linkages for looseness or wear", "category": "STEERING SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Inspect steering gear linkages/ball joints/tie rod ends/drag link/steering arms", "category": "STEERING SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect king-pins /Pitman arm for wear", "category": "STEERING SECTION CHECK",
		 "pattern": "---X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Inspect articulating pivot bearings, pins and bushings for wear", "category": "STEERING SECTION CHECK",
		 "pattern": "---X-X----X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Inspect steering brake band/lining (as applicable)", "category": "STEERING SECTION CHECK",
		 "pattern": "----X----X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Check wheel alignment (toe-in), camber angle etc", "category": "STEERING SECTION CHECK",
		 "pattern": "----X----X", "mandatory": 0, "duration": 1.0},
		
		# CHASSIS/AIR SYSTEM
		{"task_name": "Drain moisture from air tanks, fuel traps etc. (as applicable)", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check air compressor and mounting brackets", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Change filter (as required)", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "----X-X---X-X", "mandatory": 0, "duration": 0.25},
		{"task_name": "Check all lines, valves, connections for leaks", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check governor for leaks and operation", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check air cylinders for proper operation", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Complete system/valve pressure tests", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "----X-X---X-X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Inspect frame springs/hitch/hoist for cracks, wear, bends, breakage", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect tow bar /eye/ mounting/ safety chain for damage and cracks", "category": "CHASSIS/AIR SYSTEM CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		
		# BUCKET, BLADE CHECK
		{"task_name": "Check security of bolts, nuts, cotter pins, pivot pins and clevis pins", "category": "BUCKET, BLADE CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check bucket, blade, teeth, tips, cutting edges and general condition (excessive wear)", "category": "BUCKET, BLADE CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check bristles, slides, shoes, skids, etc", "category": "BUCKET, BLADE CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check articulated pivot pins and bearings for excess wear", "category": "BUCKET, BLADE CHECK",
		 "pattern": "----X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Check adjustments, circle, draw bar ball sockets, mould-board", "category": "BUCKET, BLADE CHECK",
		 "pattern": "----X-X---X-X", "mandatory": 0, "duration": 0.5},
		
		# TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES
		{"task_name": "Check for leaks and damage", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check lubricant levels", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "---X-X---X-X", "mandatory": 0, "duration": 0.25},
		{"task_name": "Inspect/ clean breather vents (as applicable)", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check clutch pedal clearance/ reservoir fluid level (as applicable)", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check drive couplings, flanges/ \"U\" joints, splines/ slip yokes for wear", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Check chain drives for looseness /misalignment (as applicable)", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Change Transmission filter", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "-X-X-X-X-----", "mandatory": 0, "duration": 0.5},
		{"task_name": "Changing Transmission Oil", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "--X-X-X-----", "mandatory": 0, "duration": 1.0},
		{"task_name": "Change axle /Differential Oil & Gear Box Oil", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "--X-X-X---X-X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Final Drive Oil Change", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "--X-X-X---X-X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Winch Oil Change", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "--X-X-X-----", "mandatory": 0, "duration": 0.5},
		{"task_name": "Circle Drive Oil Change", "category": "TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES",
		 "pattern": "--X-X-X-----", "mandatory": 0, "duration": 0.5},
		
		# BRAKE SECTION
		{"task_name": "Inspect brake hydraulic/ air system leaks, loose connections, deterioration, corrosion", "category": "BRAKE SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check hydro vac", "category": "BRAKE SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check reservoir fluid level", "category": "BRAKE SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check and adjust pedal travel", "category": "BRAKE SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check for fluid leaks at wheel cylinders (external visual)", "category": "BRAKE SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Lubricate pivots as necessary", "category": "BRAKE SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Inspect brake drums, linings, discs, chambers", "category": "BRAKE SECTION CHECK",
		 "pattern": "---X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Inspect wheel cylinders for fluid leaks", "category": "BRAKE SECTION CHECK",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Lubricate shoe anchors and pivots", "category": "BRAKE SECTION CHECK",
		 "pattern": "-X-X-X-X---X-X", "mandatory": 0, "duration": 0.25},
		{"task_name": "Change brake fluid/ bleed system (as required)", "category": "BRAKE SECTION CHECK",
		 "pattern": "--------X", "mandatory": 0, "duration": 1.0},
		
		# WHEEL, AXLES, HUB CHECK
		{"task_name": "Check for leaks and lubricant levels-axle, planetary hubs", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Inspect/ clean breather vents as applicable", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check front/ rear wheel bearings (as just as required)", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "---X-X---X-X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Check wheel studs and nuts for tightness/ condition", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check tire pressure/ tread deterioration/ side-wall damage", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "-----X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Replace wheel bearings with proper type grease", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "---X-X---X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Check wheel/ oil seals (replace as required)", "category": "WHEEL, AXLES, HUB CHECK",
		 "pattern": "---X-X---X", "mandatory": 0, "duration": 0.5},
		
		# MAIN HYDRAULIC SECTION
		{"task_name": "Check for leaks and reservoir fluid level; check/ clean reservoir breather", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check lines and fittings for deterioration and loose connections", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect all hydraulic system pivots, pins, mountings, etc", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check operation of spool and other control valves", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect for leaks and check operation of all lift/ shift cylinders", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check safety devices/ overrides", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Change filter", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "X-X-X-X-X---X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Change Hydraulic Oil (As Per Manual)", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "-----------", "mandatory": 0, "duration": 2.0},
		{"task_name": "Check cycle time", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "---X---X", "mandatory": 0, "duration": 0.5},
		{"task_name": "Pressure test system", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "---X---X", "mandatory": 0, "duration": 1.0},
		{"task_name": "Drain, flush and replace oil", "category": "MAIN HYDRAULIC SECTION CHECK",
		 "pattern": "---X---X", "mandatory": 0, "duration": 2.0},
		
		# CAB AND BODY SECTION
		{"task_name": "Wash/ steam clean as required", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check operation and condition of locks, windows, mirrors, mountings etc", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check and lubricate all hinges", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Inspect condition/ security of seats, mats, safety belts and other fittings etc", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check w/wiper/ washer operation, inspect arms/ blades, check reservoir fluid level", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check cab/ body mounting for looseness", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check fuel/ air tank mountings for security", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check body condition, touch up paint", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check for lose, bent, missing parts, panels, safety guards, etc", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check condition/ mountings of fuel/ water tank bodies/ fittings and operation of pumps etc", "category": "CAB AND BODY SECTION CHECK",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		
		# ADDITIONAL CHECK FOR TRACKED EQUIPMENT (Equipment only)
		{"task_name": "Check condition of track, rollers, sprockets, idlers, grousers etc", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 1.0},
		{"task_name": "Check track tension and adjust (as required)", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check idler guide wear strips and diagonal braces", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 0.5},
		{"task_name": "Lubricate track rollers/ front idler (as required)", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 0.5},
		{"task_name": "Adjust/ lubricate chains, belts, gears, sprockets and tensioner, etc", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 1.0},
		{"task_name": "Check track shock absorber/ torsion bars (as required)", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check steering clutch operation and linkages and adjust as required", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 0.5},
		{"task_name": "Inspect ROS for damage /security", "category": "ADDITIONAL CHECK FOR TRACKED EQUIPMENT",
		 "pattern": "X-X-X-X-X-----", "mandatory": 1, "duration": 0.25},
		
		# ROAD TEST INSPECTION (Vehicles only)
		{"task_name": "Check engine acceleration/ deceleration", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check clutch operation", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Test transmission/ gear change operation", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Stall Test and parking brake operation on gradient", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Test steering on both locks", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Test brakes at varying speeds and for pulling to one side", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
		{"task_name": "Check operation of Speedometer/ Odometer/ Hour Meter", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.25},
		{"task_name": "Check that all gauges/ warning lights and other devices are working properly", "category": "ROAD TEST INSPECTION",
		 "pattern": "X-X-X-X-X-X-X-X-X-X", "mandatory": 1, "duration": 0.5},
	]
	
	created_count = 0
	for task_data in tasks_data:
		if not frappe.db.exists("Preventive Maintenance Task", task_data["task_name"]):
			doc = frappe.get_doc({
				"doctype": "Preventive Maintenance Task",
				"task_name": task_data["task_name"],
				"task_category": task_data["category"],
				"description": task_data.get("description", ""),
				"is_mandatory": task_data["mandatory"],
				"estimated_duration": task_data["duration"],
				"is_active": 1
			})
			doc.insert()
			created_count += 1
			frappe.db.commit()
	
	print(f"  Created {created_count} new tasks")
	
	# Store interval patterns for template creation
	frappe.local.task_intervals = {}
	for task_data in tasks_data:
		frappe.local.task_intervals[task_data["task_name"]] = get_interval_flags(task_data["pattern"])


def create_maintenance_templates():
	"""Create two separate templates - one for vehicles, one for equipment"""
	
	# Get all tasks
	all_tasks = frappe.get_all("Preventive Maintenance Task",
		filters={"is_active": 1},
		fields=["name", "task_name", "task_category"])
	
	if not all_tasks:
		frappe.msgprint("Please create maintenance tasks first")
		return
	
	# Vehicle template (excludes TRACKED EQUIPMENT, includes ROAD TEST)
	vehicle_template_name = "Standard Vehicle Maintenance Template"
	if not frappe.db.exists("Preventive Maintenance Template", vehicle_template_name):
		vehicle_template = frappe.get_doc({
			"doctype": "Preventive Maintenance Template",
			"template_name": vehicle_template_name,
			"description": "Standard preventive maintenance template for vehicles based on service guide"
		})
		
		for task in all_tasks:
			# Exclude tracked equipment tasks, include all others
			if task.task_category != "ADDITIONAL CHECK FOR TRACKED EQUIPMENT":
				task_row = vehicle_template.append("maintenance_tasks")
				task_row.task = task.name
				task_row.task_name = task.task_name
				task_row.task_category = task.task_category
				
				# Set intervals based on stored pattern
				if hasattr(frappe.local, 'task_intervals') and task.task_name in frappe.local.task_intervals:
					intervals = frappe.local.task_intervals[task.task_name]
					for key, value in intervals.items():
						setattr(task_row, key, value)
		
		vehicle_template.insert()
		frappe.db.commit()
		print(f"  Created template: {vehicle_template_name} with {len(vehicle_template.maintenance_tasks)} tasks")
	
	# Equipment template (includes TRACKED EQUIPMENT, excludes ROAD TEST)
	equipment_template_name = "Standard Equipment Maintenance Template"
	if not frappe.db.exists("Preventive Maintenance Template", equipment_template_name):
		equipment_template = frappe.get_doc({
			"doctype": "Preventive Maintenance Template",
			"template_name": equipment_template_name,
			"description": "Standard preventive maintenance template for equipment based on service guide"
		})
		
		for task in all_tasks:
			# Exclude road test tasks, include all others
			if task.task_category != "ROAD TEST INSPECTION":
				task_row = equipment_template.append("maintenance_tasks")
				task_row.task = task.name
				task_row.task_name = task.task_name
				task_row.task_category = task.task_category
				
				# Set intervals based on stored pattern
				if hasattr(frappe.local, 'task_intervals') and task.task_name in frappe.local.task_intervals:
					intervals = frappe.local.task_intervals[task.task_name]
					for key, value in intervals.items():
						setattr(task_row, key, value)
		
		equipment_template.insert()
		frappe.db.commit()
		print(f"  Created template: {equipment_template_name} with {len(equipment_template.maintenance_tasks)} tasks")
