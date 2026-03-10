# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

"""
Script to import equipment data into Equipment Master
Run with: bench --site [site-name] execute equipment_and_maintenance.equipment.import_equipment_data.import_equipment_data
"""

import frappe
from frappe.utils import now

def import_equipment_data():
	"""Import equipment data from the provided list"""
	
	# First, let's check existing categories and sub-categories
	print("\n=== Checking Categories and Sub-Categories ===")
	categories = frappe.get_all("Asset Category", fields=["name", "asset_category_name", "custom_asset_category_code"])
	print("\nAsset Categories:")
	for cat in categories:
		print(f"  - {cat.name} (Code: {cat.custom_asset_category_code})")
	
	sub_categories = frappe.get_all("Asset Sub Category", fields=["name", "asset_sub_category_name", "code", "asset_category"])
	print("\nAsset Sub Categories:")
	for sub in sub_categories:
		print(f"  - {sub.name} (Code: {sub.code}, Parent: {sub.asset_category})")
	
	# Create locations (Projects) if they don't exist
	print("\n=== Creating Locations (Projects) ===")
	locations = ["DUKEM", "ADDIS ABABA", "ARSI", "ALEM GENA", "BISHOFTU"]
	location_map = {}
	for loc in locations:
		existing = frappe.db.get_value("Project", {"project_name": loc}, "name")
		if not existing:
			try:
				project = frappe.get_doc({
					"doctype": "Project",
					"project_name": loc
				})
				project.insert()
				location_map[loc] = project.name
				print(f"  Created Project: {loc}")
			except Exception as e:
				print(f"  ERROR creating project {loc}: {str(e)}")
				# Try to get it anyway in case it was created
				existing = frappe.db.get_value("Project", {"project_name": loc}, "name")
				if existing:
					location_map[loc] = existing
		else:
			location_map[loc] = existing
			print(f"  Found existing Project: {loc}")
	
	frappe.db.commit()
	
	# Create "NOT ASSIGNED" employee if it doesn't exist
	print("\n=== Creating 'NOT ASSIGNED' Employee ===")
	not_assigned_employee = frappe.db.get_value("Employee", {"employee_name": "NOT ASSIGNED"}, "name")
	if not not_assigned_employee:
		try:
			employee = frappe.get_doc({
				"doctype": "Employee",
				"employee_name": "NOT ASSIGNED",
				"first_name": "NOT ASSIGNED"
			})
			employee.insert()
			not_assigned_employee = employee.name
			print(f"  Created Employee: NOT ASSIGNED")
			frappe.db.commit()
		except Exception as e:
			print(f"  ERROR creating NOT ASSIGNED employee: {str(e)}")
			not_assigned_employee = frappe.db.get_value("Employee", {"employee_name": "NOT ASSIGNED"}, "name")
	else:
		print(f"  Found existing Employee: NOT ASSIGNED")
	
	# Category name mapping (from data to system)
	category_mapping = {
		"HEAVY MACHINERIES": "Heavy Machineries",
		"HEAVY VEHICLES": "Heavy Vehicles",
		"LIGHT VEHICLES": "Light Vehicles",
		"Auxiliaries": "Auxiliaries"
	}
	
	# Equipment data mapping
	equipment_data = [
		# HEAVY MACHINERIES - BULLDOZER
		{"make": "CATERPILLER", "model": "D8R", "plate_number": "DZ-0927", "serial_number": "CAT00D8RL9EM08998", "engine_number": "TXC03204", "hp": "310", "cc": "14.6 LITER", "capacity": "310 HP", "yom": "2013", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "BULLDOZER"},
		{"make": "LIUGONG", "model": "CGB320", "plate_number": "DZ-1522", "serial_number": "TJ1400045", "engine_number": "41213903", "hp": "344", "cc": "-", "capacity": "344 HP", "yom": "2018", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "BULLDOZER"},
		{"make": "LIUGONG", "model": "CGB320", "plate_number": "DZ-1523", "serial_number": "TJ1400070", "engine_number": "41213639", "hp": "344", "cc": "-", "capacity": "344 HP", "yom": "2018", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "BULLDOZER"},
		{"make": "LIUGONG", "model": "CGB320", "plate_number": "DZ-1539", "serial_number": "TJ1400058", "engine_number": "41213904", "hp": "344", "cc": "-", "capacity": "344 HP", "yom": "2018", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "BULLDOZER"},
		
		# HEAVY MACHINERIES - CHAIN EXCAVATOR
		{"make": "KOBELCO", "model": "SK350LC-8", "plate_number": "EX-2657", "serial_number": "YC11-06373", "engine_number": "J08ETM29701", "hp": "268", "cc": "-", "capacity": "1.6 M3", "yom": "2019", "location": "ALEM GENA", "operators_name": "BEZAWORK", "operators_phone_no": "0913226759", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "CHAIN EXCAVATOR"},
		{"make": "KOBELCO", "model": "SK350LC-8", "plate_number": "EX-2658", "serial_number": "YC11-06371", "engine_number": "J08ETM29671", "hp": "268", "cc": "-", "capacity": "1.6 M3", "yom": "2019", "location": "ARSI", "operators_name": "EDOSA", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "CHAIN EXCAVATOR"},
		
		# HEAVY MACHINERIES - MOTOR GRADER
		{"make": "CATERPILLER", "model": "140H", "plate_number": "GR-0676", "serial_number": "CAT0140HTCCA02988", "engine_number": "3PD17926", "hp": "185", "cc": "10.3 LITER", "capacity": "185 HP", "yom": "2006", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "MOTOR GRADER"},
		{"make": "CATERPILLER", "model": "140H", "plate_number": "GR-0777", "serial_number": "*CAT0140HACCA03731*", "engine_number": "*3PD19951*", "hp": "205", "cc": "10.3 LITER", "capacity": "205 HP", "yom": "2007", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "MOTOR GRADER"},
		
		# HEAVY MACHINERIES - WHEEL LOADER
		{"make": "XCMG", "model": "ZL50G", "plate_number": "LD-2759", "serial_number": "15GL0141068", "engine_number": "1210E041965", "hp": "217", "cc": "7.2 LITER", "capacity": "3 M3", "yom": "2014", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "WHEEL LOADER"},
		{"make": "SEM", "model": "SEM655D", "plate_number": "LD-2850", "serial_number": "SEM00655HS5506169", "engine_number": "*12195007275", "hp": "217", "cc": "7.1 LITER", "capacity": "3 M3", "yom": "2019", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "WHEEL LOADER"},
		{"make": "SEM", "model": "SEM655D", "plate_number": "LD-2851", "serial_number": "SEM00655CS5506160", "engine_number": "*12195007273", "hp": "217", "cc": "7.1 LITER", "capacity": "3 M3", "yom": "2019", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "WHEEL LOADER"},
		{"make": "SEM", "model": "SEM655D", "plate_number": "LD-2911", "serial_number": "SEM00655JS5506228", "engine_number": "1219J007781", "hp": "217", "cc": "7.1 LITER", "capacity": "3 M3", "yom": "2019", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "WHEEL LOADER"},
		{"make": "SEM", "model": "SEM655D", "plate_number": "LD-2912", "serial_number": "SEM00655CS5506229", "engine_number": "1219J007773", "hp": "217", "cc": "7.1 LITER", "capacity": "3 M3", "yom": "2019", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "WHEEL LOADER"},
		
		# HEAVY MACHINERIES - ROLLER
		{"make": "LUTONG", "model": "LTS216H", "plate_number": "CM-1063", "serial_number": "*012835", "engine_number": "87572437", "hp": "148", "cc": "-", "capacity": "16 T", "yom": "2014", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "ROLLER"},
		{"make": "XCMG", "model": "XS142J", "plate_number": "CM-1696", "serial_number": "3142120018", "engine_number": "D9121000204", "hp": "123", "cc": "-", "capacity": "14 T", "yom": "2011", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "ROLLER"},
		{"make": "XCMG", "model": "XS142J", "plate_number": "CM-1697", "serial_number": "3142130002", "engine_number": "D912C039633", "hp": "123", "cc": "-", "capacity": "14 T", "yom": "2013", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "ROLLER"},
		
		# HEAVY MACHINERIES - Crane
		{"make": "IVECO", "model": "110NC", "plate_number": "ET-3-A05796", "serial_number": "11NCB018738", "engine_number": "*806*002*062440044", "hp": "-", "cc": "-", "capacity": "1 PERSON & 20 OTHER", "yom": "1992", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY MACHINERIES", "sub_category": "Crane"},
		{"make": "XCMG", "model": "XCT30M", "plate_number": "ET-3-A08716", "serial_number": "LXGCPA335LA000081", "engine_number": "SCTH260Q3*H9197010121*", "hp": "-", "cc": "-", "capacity": "1 PERSON", "yom": "2020", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "HEAVY MACHINERIES", "sub_category": "Crane"},
		
		# HEAVY VEHICLES - Dump Truck
		{"make": "GENLYON", "model": "KS3240", "plate_number": "ET-3-57814", "serial_number": "LZFF25T4XCD247472", "engine_number": "F2CE0681B*B052-12C00032183", "hp": "380", "cc": "9726", "capacity": "1 PERSON & 138 QUINTALS", "yom": "2012", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 2", "plate_number": "ET-3-A03851", "serial_number": "LZZ5ELND7HW318307", "engine_number": "WD615.69*171007032257", "hp": "336", "cc": "9726", "capacity": "1 PERSON & 132 QUINTALS", "yom": "2019", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 1", "plate_number": "ET-3-A03852", "serial_number": "LZZ5ELND9HW318308", "engine_number": "WD615.69*171007032337*", "hp": "336", "cc": "9726", "capacity": "1 PERSON & 132 QUINTALS", "yom": "2019", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 1", "plate_number": "ET-3-A03915", "serial_number": "LZZ5ELNCHD316977", "engine_number": "WD615.69*171017007097", "hp": "335", "cc": "9726", "capacity": "1 PERSON & 157 QUINTALS", "yom": "2019", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 1", "plate_number": "ET-3-A03916", "serial_number": "LZZ5ELNC3HD316976", "engine_number": "WD615.69*171017005497", "hp": "335", "cc": "9726", "capacity": "1 PERSON & 157 QUINTALS", "yom": "2019", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 1", "plate_number": "ET-3-A03917", "serial_number": "LZZ5ELND6HD316978", "engine_number": "WD615.69*171017007197", "hp": "335", "cc": "9726", "capacity": "1 PERSON & 157 QUINTALS", "yom": "2019", "location": "ARSI", "operators_name": "JAWAR YAZID", "operators_phone_no": "0917370394", "current_status": "ACTIVE", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 1", "plate_number": "ET-3-A04634", "serial_number": "LZZ5ELND9HD240740", "engine_number": "WD615.69*170507022727", "hp": "336", "cc": "9726", "capacity": "1 PERSON & 132 QUINTALS", "yom": "2019", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		{"make": "SINOTRUK", "model": "ZZ3257N3447A 1", "plate_number": "ET-3-A04636", "serial_number": "LZ5ELND2HD240742", "engine_number": "WD615.69*170507024467", "hp": "336", "cc": "9726", "capacity": "1 PERSON & 132 QUINTALS", "yom": "2019", "location": "ARSI", "operators_name": "LAMESSA DEREJE", "operators_phone_no": "0917737622", "current_status": "ACTIVE", "category": "HEAVY VEHICLES", "sub_category": "Dump Truck"},
		
		# HEAVY VEHICLES - Water Truck
		{"make": "FIAT", "model": "619NIP", "plate_number": "ET-3-02952", "serial_number": "619N1P-016221", "engine_number": "FIAT-8210-02-055-178772", "hp": "177", "cc": "11548", "capacity": "1 PERSON & 12296 LITERS", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Water Truck"},
		{"make": "FIAT", "model": "619JN1", "plate_number": "ET-3-04761", "serial_number": "619NL-007200", "engine_number": "8210.02*059-20925", "hp": "260", "cc": "13798", "capacity": "1 PERSON & 14000 LITERS", "yom": "", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Water Truck"},
		
		# HEAVY VEHICLES - Fuel Truck (Note: sub-category might be "Fuel Track" in system, will handle both)
		{"make": "IVECO", "model": "AT380T38H", "plate_number": "ET-3-29971", "serial_number": "166739", "engine_number": "67580", "hp": "380", "cc": "13798", "capacity": "17836 LITERS", "yom": "2006", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Fuel Track"},
		{"make": "", "model": "36H/ET/317.5/", "plate_number": "ET-3-05132", "serial_number": "TT0217.99", "engine_number": "-", "hp": "-", "cc": "-", "capacity": "26456 LITERS", "yom": "1999", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "HEAVY VEHICLES", "sub_category": "Fuel Track"},
		
		# LIGHT VEHICLES - Pick Up
		{"make": "TOYOTA", "model": "KDN170L-CRMSYM", "plate_number": "AA-3-72522", "serial_number": "JTFWS796600003982", "engine_number": "2KD-0909866", "hp": "100", "cc": "2494", "capacity": "1 PERSON & 10 QUINTALS", "yom": "2002", "location": "BISHOFTU", "operators_name": "SOLOMON MOSISSA", "operators_phone_no": "0911896195", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "KUN26L-PRASYW", "plate_number": "AA-3-A09044", "serial_number": "AHTFZ29G409110074", "engine_number": "3Z19128", "hp": "119", "cc": "2982", "capacity": "4 PERSON & 6 QUINTALS", "yom": "2014", "location": "ADDIS ABABA", "operators_name": "ADUGNA MEKONNEN", "operators_phone_no": "0946627332", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "KUN25L-PRMDHV", "plate_number": "AA-3-A09328", "serial_number": "MR0FR22G1E0718705", "engine_number": "2KD-A434594", "hp": "102", "cc": "2494", "capacity": "4 PERSON & 6 QUINTALS", "yom": "2014", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "GUN125L-DNTHXW", "plate_number": "AA-3-B01091", "serial_number": "AHTBB3CDX01766351", "engine_number": "2GD-0757594", "hp": "101", "cc": "2393", "capacity": "4 PERSON & 6 QUINTALS", "yom": "2019", "location": "ADDIS ABABA", "operators_name": "ADDISU MOSISSA", "operators_phone_no": "0911245036", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "HZJ79L-RKMRS", "plate_number": "AA-3-B05085", "serial_number": "JTEBB71J20B015747", "engine_number": "1HZ-0955094", "hp": "130", "cc": "4164", "capacity": "4 PERSON & 7 QUINTALS", "yom": "2020", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "KUN125L-DNTSHN", "plate_number": "AA-3-B05700", "serial_number": "AHTKB8CDX02977220", "engine_number": "2GD-0777407", "hp": "102", "cc": "2393", "capacity": "4 PERSON & 6 QUINTALS", "yom": "2019", "location": "ADDIS ABABA", "operators_name": "GEZAHEGN MARIE", "operators_phone_no": "0940642021", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "KUN125L-DNTSHN", "plate_number": "AA-3-B05825", "serial_number": "AHTKB8CD602977649", "engine_number": "2GD-0787834", "hp": "102", "cc": "2393", "capacity": "4 PERSON & 6 QUINTALS", "yom": "2019", "location": "ADDIS ABABA", "operators_name": "MICHAEL GEBREHIWOT", "operators_phone_no": "0914747237", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		{"make": "TOYOTA", "model": "HZJ79L-RKMRS", "plate_number": "AA-3-B05889", "serial_number": "JTEBB71JX0B015804", "engine_number": "1HZ-0955181", "hp": "130", "cc": "4164", "capacity": "4 PERSON & 7 QUINTALS", "yom": "2020", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		
		# LIGHT VEHICLES - Automobile
		{"make": "TOYOTA", "model": "NZE120L-AEMDKV", "plate_number": "AA-3-84554", "serial_number": "JTDBW22E973158180", "engine_number": "2NZ-4692022", "hp": "84", "cc": "1298", "capacity": "4 PERSON", "yom": "2007", "location": "ADDIS ABABA", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "LIGHT VEHICLES", "sub_category": "Automobile"},
		
		# LIGHT VEHICLES - ISUZU FUEL TRUCK
		{"make": "ISUZU", "model": "NPR-66", "plate_number": "SP-3-01662", "serial_number": "JAAJP34G157P02424", "engine_number": "167543", "hp": "-", "cc": "4334", "capacity": "2 PERSON & 3500 LITERS", "yom": "2004", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "DOWN", "category": "LIGHT VEHICLES", "sub_category": "Pick Up"},
		
		# AUXILIARIES (using model field for description since no make/model available)
		{"make": "", "model": "AIR COMPRESSOR", "plate_number": "AUX-001", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "AIR COMPRESSOR", "plate_number": "AUX-002", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "AIR COMPRESSOR", "plate_number": "AUX-003", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CAR WASHING MACHINE", "plate_number": "AUX-004", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CAR WASHING MACHINE", "plate_number": "AUX-005", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "JAMPER COMPACTOR", "plate_number": "AUX-006", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "JAMPER COMPACTOR", "plate_number": "AUX-007", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "JAMPER COMPACTOR", "plate_number": "AUX-008", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "COMPACTOR", "plate_number": "AUX-009", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE MIXER", "plate_number": "AUX-010", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE MIXER", "plate_number": "AUX-011", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE MIXER", "plate_number": "AUX-012", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE MIXER", "plate_number": "AUX-013", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE MIXER", "plate_number": "AUX-014", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE VIBRATOR", "plate_number": "AUX-015", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE VIBRATOR", "plate_number": "AUX-016", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE VIBRATOR", "plate_number": "AUX-017", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE VIBRATOR", "plate_number": "AUX-018", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "CONCRETE VIBRATOR", "plate_number": "AUX-019", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "FUEL DISPENSOR", "plate_number": "AUX-020", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "FUEL DISPENSOR", "plate_number": "AUX-021", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "FUEL DISPENSOR", "plate_number": "AUX-022", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "FUEL DISPENSOR", "plate_number": "AUX-023", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "GENERATOR", "plate_number": "AUX-024", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "GENERATOR", "plate_number": "AUX-025", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "GENERATOR", "plate_number": "AUX-026", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-027", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-028", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-029", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-030", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-031", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-032", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WATER PUMP", "plate_number": "AUX-033", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WELDING MACHINE", "plate_number": "AUX-034", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WELDING MACHINE", "plate_number": "AUX-035", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "WELDING MACHINE", "plate_number": "AUX-036", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "BATTERY CHARGER", "plate_number": "AUX-037", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "GRINDER MACHINE", "plate_number": "AUX-038", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
		{"make": "", "model": "METAL CUTTER", "plate_number": "AUX-039", "serial_number": "", "engine_number": "", "hp": "", "cc": "", "capacity": "", "yom": "", "location": "DUKEM", "operators_name": "NOT ASSIGNED", "operators_phone_no": "", "current_status": "ACTIVE", "category": "Auxiliaries", "sub_category": "Auxiliaries"},
	]
	
	print("\n=== Starting Equipment Import ===")
	created = 0
	updated = 0
	errors = 0
	
	for idx, eq_data in enumerate(equipment_data, 1):
		try:
			# Find category and sub-category
			category_name = None
			sub_category_name = None
			
			# Map category name if needed
			category_to_find = category_mapping.get(eq_data["category"], eq_data["category"])
			
			# Try to find category by name (case-insensitive)
			# First try exact match
			category_match = frappe.db.get_value("Asset Category", {"asset_category_name": category_to_find}, "name")
			if not category_match:
				# Try case-insensitive search
				all_categories = frappe.get_all("Asset Category", fields=["name", "asset_category_name"])
				category_name = None
				for cat in all_categories:
					if cat.asset_category_name.upper() == category_to_find.upper():
						category_name = cat.name
						print(f"  Found category (case-insensitive): {cat.asset_category_name} -> {category_name}")
						break
				
				if not category_name:
					# Try partial match
					categories_list = frappe.get_all("Asset Category", filters={"asset_category_name": ["like", f"%{category_to_find}%"]}, fields=["name", "asset_category_name"])
					if categories_list:
						category_name = categories_list[0].name
						print(f"  Found category (partial match): {categories_list[0].asset_category_name} -> {category_name}")
					else:
						print(f"  WARNING: Category '{eq_data['category']}' (mapped to '{category_to_find}') not found for {eq_data['plate_number']}")
						errors += 1
						continue
			else:
				category_name = category_match
			
			# Try to find sub-category by name and parent (case-insensitive)
			# First try exact match
			sub_category_match = frappe.db.get_value("Asset Sub Category", 
				{"asset_sub_category_name": eq_data["sub_category"], "asset_category": category_name}, "name")
			if not sub_category_match:
				# Try case-insensitive search
				all_sub_categories = frappe.get_all("Asset Sub Category", 
					filters={"asset_category": category_name}, 
					fields=["name", "asset_sub_category_name"])
				sub_category_name = None
				for sub in all_sub_categories:
					if sub.asset_sub_category_name.upper() == eq_data["sub_category"].upper():
						sub_category_name = sub.name
						print(f"  Found sub-category (case-insensitive): {sub.asset_sub_category_name} -> {sub_category_name}")
						break
				
				if not sub_category_name:
					# Try partial match
					sub_categories_list = frappe.get_all("Asset Sub Category", 
						filters={"asset_sub_category_name": ["like", f"%{eq_data['sub_category']}%"], "asset_category": category_name}, 
						fields=["name", "asset_sub_category_name"])
					if sub_categories_list:
						sub_category_name = sub_categories_list[0].name
						print(f"  Found sub-category (partial match): {sub_categories_list[0].asset_sub_category_name} -> {sub_category_name}")
					else:
						# Try alternative names (Fuel Truck -> Fuel Track)
						if eq_data["sub_category"].upper() == "FUEL TRUCK":
							alt_match = frappe.db.get_value("Asset Sub Category", 
								{"asset_sub_category_name": "Fuel Track", "asset_category": category_name}, "name")
							if alt_match:
								sub_category_name = alt_match
								print(f"  Found sub-category (alternative): Fuel Track -> {sub_category_name}")
							else:
								print(f"  WARNING: Sub-category '{eq_data['sub_category']}' not found under '{category_name}' for {eq_data['plate_number']}")
								errors += 1
								continue
						else:
							print(f"  WARNING: Sub-category '{eq_data['sub_category']}' not found under '{category_name}' for {eq_data['plate_number']}")
							errors += 1
							continue
			else:
				sub_category_name = sub_category_match
			
			# Check if equipment already exists by plate_number - SKIP if exists
			existing = frappe.db.get_value("Equipment Master", {"plate_number": eq_data["plate_number"]}, "name")
			if existing:
				print(f"  [{idx}] SKIPPED (already exists): {eq_data['plate_number']} - {eq_data['make']} {eq_data['model']}")
				continue
			
			# Get location (Project) and operator (Employee)
			location_project = location_map.get(eq_data["location"])
			if not location_project:
				print(f"  WARNING: Location '{eq_data['location']}' not found in location map for {eq_data['plate_number']}")
				errors += 1
				continue
			
			# Get operator - create employee if needed (for named operators)
			operator_employee = not_assigned_employee
			if eq_data["operators_name"] and eq_data["operators_name"] != "NOT ASSIGNED":
				operator_match = frappe.db.get_value("Employee", {"employee_name": eq_data["operators_name"]}, "name")
				if not operator_match:
					# Try to create employee
					try:
						employee = frappe.get_doc({
							"doctype": "Employee",
							"employee_name": eq_data["operators_name"],
							"first_name": eq_data["operators_name"].split()[0] if " " in eq_data["operators_name"] else eq_data["operators_name"]
						})
						employee.insert()
						operator_employee = employee.name
						frappe.db.commit()
						print(f"  Created Employee: {eq_data['operators_name']}")
					except Exception as e:
						print(f"  WARNING: Could not create employee '{eq_data['operators_name']}': {str(e)}")
						# Use NOT ASSIGNED as fallback
						operator_employee = not_assigned_employee
				else:
					operator_employee = operator_match
			
			# Prepare data
			doc_data = {
				"doctype": "Equipment Master",
				"make": eq_data["make"] or "",
				"model": eq_data["model"] or "",
				"plate_number": eq_data["plate_number"],
				"serial_number": eq_data["serial_number"] or "",
				"engine_number": eq_data["engine_number"] or "",
				"hp": eq_data["hp"] if eq_data["hp"] != "-" else "",
				"cc": eq_data["cc"] if eq_data["cc"] != "-" else "",
				"capacity": eq_data["capacity"] or "",
				"yom": eq_data["yom"] if eq_data["yom"] else None,
				"location": location_project,
				"operators_name": operator_employee,
				"operators_phone_no": eq_data["operators_phone_no"] or "",
				"current_status": eq_data["current_status"] or "",
				"equipment_category": category_name,
				"equipment_sub_category": sub_category_name
			}
			
			# Create new (we already skipped existing ones above)
			doc = frappe.get_doc(doc_data)
			doc.insert()
			created += 1
			display_name = f"{eq_data.get('make', '')} {eq_data.get('model', '')}".strip()
			if not display_name:
				display_name = eq_data.get('model', '') or eq_data['plate_number']
			print(f"  [{idx}] Created: {eq_data['plate_number']} - {display_name}")
			
			# Commit every 10 records
			if (idx % 10 == 0):
				frappe.db.commit()
				
		except Exception as e:
			errors += 1
			print(f"  ERROR [{idx}] {eq_data.get('plate_number', 'Unknown')}: {str(e)}")
			frappe.db.rollback()
	
	frappe.db.commit()
	
	frappe.db.commit()
	
	print(f"\n=== Import Complete ===")
	print(f"  Created: {created}")
	print(f"  Skipped (already exists): {len(equipment_data) - created - errors}")
	print(f"  Errors: {errors}")
	print(f"  Total: {len(equipment_data)}")

if __name__ == "__main__":
	import_equipment_data()

