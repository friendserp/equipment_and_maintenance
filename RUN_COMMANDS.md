# Equipment and Maintenance - Common Commands

## Running Number Cards Creation

### Option 1: Using bench execute (Recommended)
```bash
bench --site erp.kushladder.com execute equipment_and_maintenance.dashboard_fixtures.create_number_cards
```

### Option 2: Using bench console
```bash
bench --site erp.kushladder.com console
```

Then in the console:
```python
from equipment_and_maintenance.dashboard_fixtures import create_number_cards
create_number_cards()
```

### Option 3: Using Python directly
```python
import frappe
frappe.init(site='erp.kushladder.com')
frappe.connect()
from equipment_and_maintenance.dashboard_fixtures import create_number_cards
create_number_cards()
frappe.db.commit()
frappe.destroy()
```

## Running Custom Blocks Creation

### Option 1: Using bench execute (Recommended)
```bash
bench --site erp.kushladder.com execute equipment_and_maintenance.dashboard_fixtures.create_custom_blocks
```

### Option 2: Using bench console
```bash
bench --site erp.kushladder.com console
```

Then in the console:
```python
from equipment_and_maintenance.dashboard_fixtures import create_custom_blocks
create_custom_blocks()
```

## Automatic Execution

Both number cards and custom blocks are automatically created/updated:
- After app installation (`after_install` hook)
- After every migration (`after_migrate` hook)

So you don't need to run them manually after migrations!

## Recreating Workspaces

To recreate all workspaces:
```bash
bench --site erp.kushladder.com execute equipment_and_maintenance.install.recreate_workspaces.execute
```
