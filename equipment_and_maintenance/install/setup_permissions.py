# Copyright (c) 2025, Equipment and Maintenance and contributors
# License: MIT. See LICENSE

import frappe

def execute():
	"""Ensure Maintenance roles can access all doctypes/workspaces in this app's modules.

	This sets up DB-level permissions using Custom DocPerm (no file writes), and
	whitelists the three workspaces via their Workspace Roles table.
	"""
	
	roles = ["Maintenance User", "Maintenance Manager"]
	modules = ["Equipment", "Maintenance and Admin", "Equipment And Maintenance"]

	def _ensure_role(role_name: str) -> None:
		if frappe.db.exists("Role", role_name):
			return
		frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 1,
			}
		).insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"✓ Created role: {role_name}")

	def _get_custom_perm_name(doctype: str, role: str, permlevel: int = 0) -> str | None:
		return frappe.db.get_value(
			"Custom DocPerm",
			{
				"parent": doctype,
				"role": role,
				"permlevel": permlevel,
				"if_owner": 0,
			},
			"name",
		)

	def _ensure_custom_perm(doctype: str, role: str, perms: dict) -> None:
		name = _get_custom_perm_name(doctype, role, permlevel=0)
		if name:
			doc = frappe.get_doc("Custom DocPerm", name)
			changed = False
			for k, v in perms.items():
				if getattr(doc, k, 0) != v:
					setattr(doc, k, v)
					changed = True
			if changed:
				doc.save(ignore_permissions=True)
			return

		doc = frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": doctype,
				"role": role,
				"permlevel": 0,
				"if_owner": 0,
				**perms,
			}
		)
		doc.insert(ignore_permissions=True)
	
	# Ensure roles exist
	for role_name in roles:
		_ensure_role(role_name)
	
	# Get all doctypes in the requested modules (these are the modules inside this app)
	doctypes = frappe.get_all("DocType", filters={"module": ["in", modules]}, pluck="name")
	
	print(f"\nFound {len(doctypes)} doctypes in modules: {', '.join(modules)}")

	# Ensure the roles can open dashboards/workspaces UI
	core_doctypes_to_allow_read = [
		"Workspace",
		"Dashboard",
		"Dashboard Chart",
		"Number Card",
		"Custom HTML Block",
		"Workspace Sidebar",
	]

	for dt in core_doctypes_to_allow_read:
		for role in roles:
			_ensure_custom_perm(dt, role, {"read": 1, "select": 1})

	for doctype_name in doctypes:
		# Skip system doctypes (if they ever end up inside these modules)
		if doctype_name in ["Custom Field", "Property Setter", "Workflow", "Workflow State"]:
			continue

		is_submittable = bool(frappe.get_meta(doctype_name).is_submittable)

		for role in roles:
			if role == "Maintenance Manager":
				perms = {
					"read": 1,
					"select": 1,
					"write": 1,
					"create": 1,
					"delete": 1,
					"report": 1,
					"export": 1,
					"import": 1,
					"print": 1,
					"email": 1,
					"share": 1,
				}
				if is_submittable:
					perms.update({"submit": 1, "cancel": 1, "amend": 1})
			else:
				perms = {
					"read": 1,
					"select": 1,
					"write": 1,
					"create": 1,
					"report": 1,
					"export": 1,
					"print": 1,
				}

			_ensure_custom_perm(doctype_name, role, perms)

	# Workspaces: allow these roles explicitly (Workspace uses roles table)
	for ws_name in ["Equipment and Maintenance", "Equipment", "Maintenance"]:
		if not frappe.db.exists("Workspace", ws_name):
			continue
		ws = frappe.get_doc("Workspace", ws_name)
		existing = {r.role for r in (ws.roles or [])}
		changed = False
		for role in roles:
			if role not in existing:
				ws.append("roles", {"role": role})
				changed = True
		if changed:
			ws.save(ignore_permissions=True)

	frappe.clear_cache()
	frappe.db.commit()
	print("\n" + "=" * 60)
	print("✓ Permissions setup completed for modules: " + ", ".join(modules))
	print("✓ Roles granted: " + ", ".join(roles))
	print("=" * 60)
