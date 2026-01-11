# Copyright (c) 2025, Friends ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class FuelRequest(Document):
	def before_insert(self):
		# Auto-set requested_by if not set
		if not self.requested_by:
			self.requested_by = frappe.session.user
		
		# Auto-set date_issued to date if not set
		if not self.date_issued:
			self.date_issued = self.date
	
	def validate(self):
		# Auto-populate workflow fields
		self.auto_populate_workflow_fields()
		
		# Calculate fuel efficiency (Km/Ltr) if we have previous data
		if (self.previous_fuel_consumption_liter and 
			self.previous_km_hr_reading and 
			self.current_km_hr_reading):
			
			distance_traveled = self.current_km_hr_reading - self.previous_km_hr_reading
			if distance_traveled > 0 and self.previous_fuel_consumption_liter > 0:
				self.vehicles_km_ltr = distance_traveled / self.previous_fuel_consumption_liter
		
		# Calculate current fuel cost in birr
		if self.current_fuel_requested_liter and self.current_price_per_liter:
			self.current_fuel_requested_birr = self.current_fuel_requested_liter * self.current_price_per_liter
	
	def auto_populate_workflow_fields(self):
		"""Auto-populate user fields when workflow state changes"""
		if not self.workflow_state:
			return
		
		if self.workflow_state == "Checked":
			if not self.checked_by:
				self.checked_by = frappe.session.user
		elif self.workflow_state == "Approved":
			if not self.approved_by:
				self.approved_by = frappe.session.user


@frappe.whitelist()
def get_fuel_price(fuel_item, date=None):
	"""Get fuel price from Equipment and Maintenance Setting for the given fuel item and date"""
	if not date:
		date = frappe.utils.today()
	
	date_obj = getdate(date)
	
	# Get settings
	settings = frappe.get_single("Equipment and Maintenance Setting")
	
	if not settings.fuel_prices:
		return 0
	
	# Find the most recent price entry for this fuel item that is effective on or before the given date
	matching_prices = []
	for price_item in settings.fuel_prices:
		if price_item.fuel_item == fuel_item:
			effective_date = getdate(price_item.effective_date) if price_item.effective_date else None
			if effective_date and effective_date <= date_obj:
				matching_prices.append({
					"effective_date": effective_date,
					"price": price_item.price_per_liter
				})
	
	if matching_prices:
		# Get the most recent price (latest effective_date)
		latest_price = max(matching_prices, key=lambda x: x["effective_date"])
		return latest_price["price"]
	
	return 0


@frappe.whitelist()
def get_previous_fuel_data(plate_number):
	"""Get previous fuel consumption data from the last Stock Entry of type 'Fuel and Lubricant Distribution Voucher'"""
	if not plate_number:
		return {}
	
	# Find the most recent Stock Entry with the matching plate number
	stock_entry = frappe.db.sql("""
		SELECT DISTINCT se.name, se.posting_date, se.creation
		FROM `tabStock Entry` se
		INNER JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
		WHERE se.stock_entry_type = 'Fuel and Lubricant Distribution Voucher'
		AND se.docstatus = 1
		AND sed.custom_plate_no = %s
		ORDER BY se.posting_date DESC, se.creation DESC
		LIMIT 1
	""", (plate_number,), as_dict=True)
	
	if not stock_entry:
		return {}
	
	stock_entry_name = stock_entry[0].name
	
	# Get the Stock Entry Detail row with the matching plate number
	detail_row = frappe.db.get_all(
		"Stock Entry Detail",
		filters={
			"parent": stock_entry_name,
			"custom_plate_no": plate_number
		},
		fields=[
			"custom_current_kmhr_reading",
			"qty",
			"amount"
		],
		order_by="idx ASC",
		limit=1
	)
	
	if not detail_row:
		return {}
	
	row = detail_row[0]
	return {
		"previous_km_hr_reading": row.custom_current_kmhr_reading or 0,
		"previous_fuel_consumption_liter": row.qty or 0,
		"previous_fuel_consumption_birr": row.amount or 0
	}


@frappe.whitelist()
def get_fuel_request_data(fuel_request):
	"""Get fuel request data for populating Stock Entry Detail"""
	if not fuel_request:
		return {}
	
	try:
		fuel_request_doc = frappe.get_doc("Fuel Request", fuel_request)
		return {
			"item_code": fuel_request_doc.fuel_type or "",
			"qty": fuel_request_doc.current_fuel_requested_liter or 0,
			"basic_rate": fuel_request_doc.current_price_per_liter or 0,
			"amount": (fuel_request_doc.current_fuel_requested_liter or 0) * (fuel_request_doc.current_price_per_liter or 0),
			"custom_previous_kmhr_reading": fuel_request_doc.previous_km_hr_reading or 0,
			"custom_current_kmhr_reading": fuel_request_doc.current_km_hr_reading or 0,
			"custom_kmhr_difference": fuel_request_doc.current_km_hr_reading - fuel_request_doc.previous_km_hr_reading or 0,
			"custom_plate_no": fuel_request_doc.plate_number or "",
			"project": fuel_request_doc.project or ""
		}
	except frappe.DoesNotExistError:
		return {}


@frappe.whitelist()
def get_items_from_fuel_requests(fuel_requests):
	"""Get items from Fuel Request(s) for Stock Entry"""
	if not fuel_requests:
		return []
	
	# Handle both single string and list
	if isinstance(fuel_requests, str):
		fuel_requests = [fuel_requests]
	
	items = []
	for fuel_request_name in fuel_requests:
		try:
			fuel_request_doc = frappe.get_doc("Fuel Request", fuel_request_name)
			
			# Calculate km/hr difference
			kmhr_difference = 0
			current_reading = fuel_request_doc.current_km_hr_reading or 0
			previous_reading = fuel_request_doc.previous_km_hr_reading or 0
			if current_reading and previous_reading:
				kmhr_difference = current_reading - previous_reading
			
			item = {
				"item_code": fuel_request_doc.fuel_type or "",
				"qty": fuel_request_doc.current_fuel_requested_liter or 0,
				"basic_rate": fuel_request_doc.current_price_per_liter or 0,
				"amount": (fuel_request_doc.current_fuel_requested_liter or 0) * (fuel_request_doc.current_price_per_liter or 0),
				"custom_fuel_request": fuel_request_name,
				"custom_plate_no": fuel_request_doc.plate_number or "",
				"custom_previous_kmhr_reading": fuel_request_doc.previous_km_hr_reading or 0,
				"custom_current_kmhr_reading": fuel_request_doc.current_km_hr_reading or 0,
				"custom_kmhr_difference": kmhr_difference
			}
			items.append(item)
		except frappe.DoesNotExistError:
			continue
	
	return items


@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	"""Create Stock Entry from Fuel Request - called once per Fuel Request when multiple selected"""
	import json
	
	# Handle target_doc - can be dict (from form) or string (name) or None
	if isinstance(target_doc, dict):
		# Convert dict to doc object
		doclist = frappe.get_doc(target_doc)
	elif isinstance(target_doc, str):
		# It's a JSON string, parse it
		try:
			doclist = frappe.get_doc(json.loads(target_doc))
		except:
			doclist = frappe.get_doc("Stock Entry", target_doc)
	elif target_doc:
		doclist = target_doc
	else:
		# Create new Stock Entry
		doclist = frappe.new_doc("Stock Entry")
		doclist.stock_entry_type = "Fuel and Lubricant Distribution Voucher"
		doclist.purpose = "Material Issue"
	
	# Get Fuel Request
	fuel_request_doc = frappe.get_doc("Fuel Request", source_name)
	
	# Validate that Fuel Request is submitted and not already distributed
	if fuel_request_doc.docstatus != 1:
		frappe.throw(_("Fuel Request {0} is not submitted").format(fuel_request_doc.name))
	
	if fuel_request_doc.status == "Distributed":
		frappe.throw(_("Fuel Request {0} has already been distributed").format(fuel_request_doc.name))
	
	# Add item row for this Fuel Request (each Fuel Request gets its own row)
	if fuel_request_doc.fuel_type and fuel_request_doc.current_fuel_requested_liter:
		item_row = doclist.append("items")
		item_row.item_code = fuel_request_doc.fuel_type
		
		# Get item details to fetch stock_uom
		item_doc = frappe.get_doc("Item", fuel_request_doc.fuel_type)
		item_row.stock_uom = item_doc.stock_uom or "Litre"
		item_row.uom = item_doc.stock_uom or "Litre"
		item_row.conversion_factor = 1
		
		item_row.qty = fuel_request_doc.current_fuel_requested_liter
		item_row.transfer_qty = item_row.qty
		item_row.basic_rate = fuel_request_doc.current_price_per_liter or 0
		item_row.amount = (fuel_request_doc.current_fuel_requested_liter or 0) * (fuel_request_doc.current_price_per_liter or 0)
		item_row.basic_amount = item_row.amount
		item_row.valuation_rate = item_row.basic_rate
		item_row.project = fuel_request_doc.project or ""
		
		# Set custom fields from Fuel Request
		item_row.custom_fuel_request = fuel_request_doc.name
		item_row.custom_plate_no = fuel_request_doc.plate_number or ""
		item_row.custom_previous_kmhr_reading = fuel_request_doc.previous_km_hr_reading or 0
		item_row.custom_current_kmhr_reading = fuel_request_doc.current_km_hr_reading or 0
		
		# Calculate km/hr difference
		current = fuel_request_doc.current_km_hr_reading or 0
		previous = fuel_request_doc.previous_km_hr_reading or 0
		item_row.custom_kmhr_difference = current - previous if (current and previous) else 0
		
		# Set posting date from Fuel Request if not set
		if not doclist.posting_date:
			doclist.posting_date = fuel_request_doc.date
	
	return doclist

@frappe.whitelist()
def update_fuel_request_status_on_stock_entry_submit(doc, method=None):
	"""Update Fuel Request status to 'Distributed' when Stock Entry is submitted"""
	if doc.stock_entry_type != "Fuel and Lubricant Distribution Voucher":
		return
	
	# Get all unique Fuel Requests from the items
	fuel_requests = set()
	for item in doc.items:
		if item.custom_fuel_request:
			fuel_requests.add(item.custom_fuel_request)
	
	# Update status for each Fuel Request
	for fuel_request_name in fuel_requests:
		try:
			fuel_request_doc = frappe.get_doc("Fuel Request", fuel_request_name)
			if fuel_request_doc.status != "Distributed":
				fuel_request_doc.status = "Distributed"
				fuel_request_doc.save(ignore_permissions=True)
		except frappe.DoesNotExistError:
			continue


@frappe.whitelist()
def update_fuel_request_status_on_stock_entry_cancel(doc, method=None):
	"""Update Fuel Request status back to 'Pending' when Stock Entry is cancelled"""
	if doc.stock_entry_type != "Fuel and Lubricant Distribution Voucher":
		return
	
	# Get all unique Fuel Requests from the items
	fuel_requests = set()
	for item in doc.items:
		if item.custom_fuel_request:
			fuel_requests.add(item.custom_fuel_request)
	
	# Update status for each Fuel Request
	for fuel_request_name in fuel_requests:
		try:
			fuel_request_doc = frappe.get_doc("Fuel Request", fuel_request_name)
			if fuel_request_doc.status == "Distributed":
				fuel_request_doc.status = "Pending"
				fuel_request_doc.save(ignore_permissions=True)
		except frappe.DoesNotExistError:
			continue


