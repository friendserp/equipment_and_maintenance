# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccidentReportForm(Document):
	def validate(self):
		# Auto-set signature date if not set
		if not self.signature_date:
			self.signature_date = self.date

