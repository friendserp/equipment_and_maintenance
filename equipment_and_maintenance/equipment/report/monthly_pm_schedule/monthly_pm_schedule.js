// Copyright (c) 2026, Friends ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly PM Schedule"] = {
	"filters": [
		{
			"fieldname": "planning_month",
			"label": __("Planning Month"),
			"fieldtype": "Select",
			"options": "All\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember"
		},
		{
			"fieldname": "planning_year",
			"label": __("Planning Year"),
			"fieldtype": "Int",
			"default": new Date().getFullYear()
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		{
			"fieldname": "equipment",
			"label": __("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment Master"
		}
	]
};
