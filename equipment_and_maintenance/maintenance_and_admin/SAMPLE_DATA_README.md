# Preventive Maintenance Sample Data

This document explains how to populate sample data for the Preventive Maintenance system.

## What Gets Created

The sample data script creates:

1. **Maintenance Intervals** (10 intervals):
   - 250 Hours, 500 Hours, 1000 Hours, 2000 Hours, 6000 Hours
   - 2500 KM, 5000 KM, 10000 KM, 30000 KM, 60000 KM

2. **Preventive Maintenance Tasks** (~150+ tasks):
   - Tasks organized by category:
     - LUBRICATION CHECK
     - ENGINE SECTION (MAIN & AUX. ENGINES) CHECK
     - ELECTRICAL SECTION CHECK
     - STEERING SECTION CHECK
     - CHASSIS/AIR SYSTEM CHECK
     - BUCKET, BLADE CHECK
     - TRANS, DIFF, ALL GEAR CASES, FINAL DRIVES
     - BRAKE SECTION CHECK
     - WHEEL, AXLES, HUB CHECK
     - MAIN HYDRAULIC SECTION CHECK
     - CAB AND BODY SECTION CHECK
     - ADDITIONAL CHECK FOR TRACKED EQUIPMENT
     - ROAD TEST INSPECTION

3. **Preventive Maintenance Template**:
   - "Standard Vehicle Maintenance Template"
   - Includes all tasks with all intervals enabled (you can customize this later)

## How to Delete All Data

To delete all preventive maintenance data (logs, schedules, templates, tasks, and intervals):

### Using Bench Console
```bash
bench console
```

Then in the console:
```python
from equipment_and_maintenance.maintenance_and_admin.sample_data import delete_all_preventive_maintenance_data
delete_all_preventive_maintenance_data()
```

This will delete:
- All Preventive Maintenance Logs
- All Preventive Maintenance Schedules
- All Preventive Maintenance Templates
- All Preventive Maintenance Tasks
- All Maintenance Intervals

## How to Run

### Method 1: Using Bench Console (Recommended)

1. Open a terminal in your bench directory
2. Run:
```bash
bench console
```

3. In the console, execute:
```python
from equipment_and_maintenance.maintenance_and_admin.sample_data import create_sample_data
create_sample_data()
```

### Method 2: Using Bench Execute

1. Open a terminal in your bench directory
2. Run:
```bash
bench --site [your-site-name] execute equipment_and_maintenance.maintenance_and_admin.sample_data.create_sample_data
```

### Method 3: Using System Console (Web Interface)

1. Go to: **Setup > System Console**
2. Select **Type: Python**
3. Paste the following code:
```python
from equipment_and_maintenance.maintenance_and_admin.sample_data import create_sample_data
create_sample_data()
```
4. Click **Execute**

## After Running

Once the sample data is created, you can:

1. **View Maintenance Intervals**: Go to **Maintenance and Admin > Maintenance Interval**
2. **View Maintenance Tasks**: Go to **Maintenance and Admin > Preventive Maintenance Task**
3. **View Template**: Go to **Maintenance and Admin > Preventive Maintenance Template**

## Creating a Preventive Maintenance Schedule

After the sample data is loaded:

1. Go to **Maintenance and Admin > Preventive Maintenance Schedule**
2. Create a new schedule
3. Select an **Equipment** (Equipment Master)
4. Select the **Template** (e.g., "Standard Vehicle Maintenance Template")
5. Enter the current **Hours** and **Kilometers** readings
6. Click **Populate from Template** button
7. Save the document

The system will automatically:
- Calculate the next service due dates
- Create schedule items for all tasks
- Track maintenance status

## Notes

- The script checks if records already exist before creating them, so it's safe to run multiple times
- You can customize the template after creation to enable/disable specific intervals for specific tasks
- The template includes all tasks with all intervals enabled by default - you may want to customize this based on your actual maintenance requirements

