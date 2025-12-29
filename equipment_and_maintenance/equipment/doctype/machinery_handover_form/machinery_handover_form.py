# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MachineryHandoverForm(Document):
	def before_insert(self):
		# Auto-set custodian name if not set
		if not self.custodian_name:
			self.custodian_name = frappe.session.user

