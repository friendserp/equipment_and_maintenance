// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Machinery Time Sheet Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end()
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		{
			"fieldname": "plate_number",
			"label": __("Plate Number"),
			"fieldtype": "Link",
			"options": "Equipment Master"
		}
	],
	
	onload: function(report) {
		// Add custom CSS for clean UI
		$('<style>')
			.prop("type", "text/css")
			.html(`
				.report-container {
					background-color: #f5f5f5;
					padding: 20px;
				}
				.stats-container {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
					gap: 15px;
					margin-bottom: 20px;
				}
				.stat-card {
					background: white;
					padding: 20px;
					border-radius: 8px;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					border-left: 4px solid #28a745;
				}
				.stat-card h3 {
					margin: 0 0 10px 0;
					font-size: 14px;
					color: #666;
					font-weight: 500;
				}
				.stat-card .value {
					font-size: 24px;
					font-weight: 600;
					color: #28a745;
				}
				.chart-container {
					background: white;
					padding: 20px;
					border-radius: 8px;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					margin-bottom: 20px;
				}
				.chart-container h3 {
					margin: 0 0 15px 0;
					font-size: 16px;
					color: #333;
				}
			`)
			.appendTo("head");
	},
	
	after_datatable_render: function(report) {
		// Add statistics cards and charts
		add_charts_to_report(report);
	}
};

function add_charts_to_report(report) {
	// Get stats from report data - stats are passed as the 5th return value
	const stats = report.message || {};
	const data = report.data || [];
	
	if (!data.length && !stats.total_records) return;
	
	// Calculate stats from data if not provided
	let calculatedStats = stats;
	if (!stats.total_records && data.length) {
		calculatedStats = calculate_stats_from_data(data);
	}
	
	// Create stats cards container
	let statsHTML = `
		<div class="stats-container">
			<div class="stat-card">
				<h3>Total Records</h3>
				<div class="value">${calculatedStats.total_records || 0}</div>
			</div>
			<div class="stat-card">
				<h3>Total Working Hours</h3>
				<div class="value">${flt(calculatedStats.total_working_hours || 0, 2).toLocaleString()}</div>
			</div>
			<div class="stat-card">
				<h3>Total Idle Time</h3>
				<div class="value">${flt(calculatedStats.total_idle_time || 0, 2).toLocaleString()}</div>
			</div>
			<div class="stat-card">
				<h3>Avg Hours per Record</h3>
				<div class="value">${calculatedStats.total_records ? flt(calculatedStats.total_working_hours / calculatedStats.total_records, 2).toLocaleString() : 0}</div>
			</div>
		</div>
	`;
	
	// Create charts container
	let chartsHTML = `
		<div class="chart-container">
			<h3>Time Sheets by Machine Type</h3>
			<div id="machine-chart" style="height: 300px;"></div>
		</div>
		<div class="chart-container">
			<h3>Time Sheets by Project</h3>
			<div id="project-chart" style="height: 300px;"></div>
		</div>
		<div class="chart-container">
			<h3>Time Sheets by Operator</h3>
			<div id="operator-chart" style="height: 300px;"></div>
		</div>
	`;
	
	// Insert before the report table
	$(".report-container").prepend(statsHTML + chartsHTML);
	
	// Render charts
	if (calculatedStats.machine_counts) {
		render_machine_chart(calculatedStats.machine_counts);
	}
	if (calculatedStats.project_counts) {
		render_project_chart(calculatedStats.project_counts);
	}
	if (calculatedStats.operator_counts) {
		render_operator_chart(calculatedStats.operator_counts);
	}
}

function calculate_stats_from_data(data) {
	let total_records = data.length;
	let total_working_hours = 0;
	let total_idle_time = 0;
	let machine_counts = {};
	let project_counts = {};
	let operator_counts = {};
	
	data.forEach(d => {
		total_working_hours += flt(d.total_working_hour || 0);
		total_idle_time += flt(d.idle_time || 0);
		
		const machine = d.machine_type || "Not Specified";
		machine_counts[machine] = (machine_counts[machine] || 0) + 1;
		
		const project = d.project || "Not Specified";
		project_counts[project] = (project_counts[project] || 0) + 1;
		
		const operator = d.operators_name || "Not Specified";
		operator_counts[operator] = (operator_counts[operator] || 0) + 1;
	});
	
	return {
		total_records,
		total_working_hours,
		total_idle_time,
		machine_counts,
		project_counts,
		operator_counts
	};
}

function render_machine_chart(data) {
	const chartData = Object.keys(data).map(key => ({
		name: key,
		value: data[key]
	}));
	
	new frappe.Chart("#machine-chart", {
		data: {
			labels: chartData.map(d => d.name),
			datasets: [{
				name: "Time Sheets",
				values: chartData.map(d => d.value)
			}]
		},
		type: "bar",
		colors: ["#28a745"],
		height: 300
	});
}

function render_project_chart(data) {
	const chartData = Object.keys(data).map(key => ({
		name: key,
		value: data[key]
	}));
	
	new frappe.Chart("#project-chart", {
		data: {
			labels: chartData.map(d => d.name),
			datasets: [{
				name: "Time Sheets",
				values: chartData.map(d => d.value)
			}]
		},
		type: "donut",
		colors: ["#28a745", "#007bff", "#ffc107", "#dc3545", "#17a2b8"],
		height: 300
	});
}

function render_operator_chart(data) {
	const chartData = Object.keys(data).slice(0, 10).map(key => ({
		name: key,
		value: data[key]
	}));
	
	new frappe.Chart("#operator-chart", {
		data: {
			labels: chartData.map(d => d.name),
			datasets: [{
				name: "Time Sheets",
				values: chartData.map(d => d.value)
			}]
		},
		type: "bar",
		colors: ["#17a2b8"],
		height: 300
	});
}

