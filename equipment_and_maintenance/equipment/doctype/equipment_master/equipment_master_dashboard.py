from frappe import _


def get_data():
	"""
	Dashboard connections for Equipment Master.

	Notes:
	- This dashboard is primarily driven by non-standard link fieldnames across related doctypes.
	- Some doctypes have multiple link fields to Equipment Master; the dashboard can only filter by one
	  fieldname per doctype (limitation of standard dashboard links).
	"""
	return {
		"heatmap": True,
		"fieldname": "plate_no",
		"non_standard_fieldnames": {
			# Operations
			"Fuel Request": "plate_number",
			"Vehicle Daily Movement": "plate_number",
			"Machinery Time Sheet Registration": "plate_number",
			"Machinery Handover Form": "plate_number",
			# Compliance
			"Bollo Followup Form": "plate_number",
			"Insurance Followup Form": "plate_number",
			# Transfers / disposal
			"Equipment Transfer Form": "equipment_plate_no",
			"Equipment Disposal Request": "plate_no",
			# Maintenance
			"Maintenance Request": "plate_no",
			"Maintenance Work Order": "plate_no",
			"Preventive Maintenance Plan": "equipment",
			"Preventive Maintenance Schedule": "equipment",
			"Preventive Maintenance Log": "equipment",
			"Preventive Maintenance Done": "equipment",
			"Preventive Maintenance History": "equipment",
			# Tyres
			"Tyre Request and Analysis Form": "plate_no",
			"Tyre Issue and Return Report Form": "plate_no",
			"Tyre Recording Database Form": "plate_no",
			"Tyre Recording Database": "current_equipment",
			# Batteries
			"Battery Request and Analysis Form": "plate_no",
			"Battery Issue and Return Report Form": "plate_no",
			"Battery Recording Database": "current_equipment",
			# Rental (linked via child table; included here as a fallback when routed as an external link)
			"Rental Agreement Items": "created_equipment_id",
			# Incidents
			"Accident Report Form": "plate_number",
			# Cannibalization (has 2 link fields; we pick one for dashboard filter)
			"Cannibalization Form": "fitted_to_plate_no",
		},
		"transactions": [
			{
				"label": _("Maintenance"),
				"items": [
					"Maintenance Request",
					"Maintenance Work Order",
					"Preventive Maintenance Plan",
					# "Preventive Maintenance Schedule",
					# "Preventive Maintenance Log",
					"Preventive Maintenance Done",
					# "Preventive Maintenance History",
				],
			},
			{
				"label": _("Operations"),
				"items": [
					"Fuel Request",
					"Vehicle Daily Movement",
					"Machinery Time Sheet Registration",
					"Machinery Handover Form",
				],
			},
			{
				"label": _("Tyres"),
				"items": [
					"Tyre Request and Analysis Form",
					"Tyre Recording Database",
					"Battery Request and Analysis Form",
					"Battery Recording Database",
				]
			},
			{
				"label": _("Transfers"),
				"items": [
					"Equipment Transfer Form",
					"Equipment Disposal Request",
				],
			},
			{
				"label": _("Compliance"),
				"items": [
					"Insurance Followup Form",
					"Bollo Followup Form",
				],
			},
			{
				"label": _("Others"),
				"items": [
					# "Rental Agreement",
					"Accident Report Form",
					"Cannibalization Form",


				],
			},
		],
	}

