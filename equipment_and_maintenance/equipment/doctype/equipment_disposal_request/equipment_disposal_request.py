# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentDisposalRequest(Document):
	def before_insert(self):
		"""Set prepared_by to current user"""
		if not self.prepared_by:
			self.prepared_by = frappe.session.user

