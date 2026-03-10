# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

from frappe import _


def get_data():
	return {
		"fieldname": "battery_request_form",
		"transactions": [
			{
				"label": _("Battery Management"),
				"items": ["Battery Recording Database Form", "Battery Issue and Return Report Form"]
			}
		]
	}

