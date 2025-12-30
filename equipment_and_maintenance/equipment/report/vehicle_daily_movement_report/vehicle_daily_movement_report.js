// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Vehicle Daily Movement Report"] = {
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
					border-left: 4px solid #007bff;
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
					color: #007bff;
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
	
	if (!data.length && !stats.total_movements) return;
	
	// Calculate stats from data if not provided
	let calculatedStats = stats;
	if (!stats.total_movements && data.length) {
		calculatedStats = calculate_stats_from_data(data);
	}
	
	// Create stats cards container
	let statsHTML = `
		<div class="stats-container">
			<div class="stat-card">
				<h3>Total Movements</h3>
				<div class="value">${calculatedStats.total_movements || 0}</div>
			</div>
			<div class="stat-card">
				<h3>Total KM Traveled</h3>
				<div class="value">${flt(calculatedStats.total_km || 0, 2).toLocaleString()}</div>
			</div>
			<div class="stat-card">
				<h3>Total Fuel Used (L)</h3>
				<div class="value">${flt(calculatedStats.total_fuel || 0, 2).toLocaleString()}</div>
			</div>
			<div class="stat-card">
				<h3>Avg KM per Movement</h3>
				<div class="value">${calculatedStats.total_movements ? flt(calculatedStats.total_km / calculatedStats.total_movements, 2).toLocaleString() : 0}</div>
			</div>
		</div>
	`;
	
	// Create charts container
	let chartsHTML = `
		<div class="chart-container">
			<h3>Movements by Reason of Travel</h3>
			<div id="reason-chart" style="height: 300px;"></div>
		</div>
		<div class="chart-container">
			<h3>Movements by Project</h3>
			<div id="project-chart" style="height: 300px;"></div>
		</div>
	`;
	
	// Insert before the report table
	$(".report-container").prepend(statsHTML + chartsHTML);
	
	// Render charts
	if (calculatedStats.reason_counts) {
		render_reason_chart(calculatedStats.reason_counts);
	}
	if (calculatedStats.project_counts) {
		render_project_chart(calculatedStats.project_counts);
	}
}

function calculate_stats_from_data(data) {
	let total_movements = data.length;
	let total_km = 0;
	let total_fuel = 0;
	let reason_counts = {};
	let project_counts = {};
	
	data.forEach(d => {
		total_km += flt(d.km_difference || 0);
		total_fuel += flt(d.received_fuel || 0);
		
		const reason = d.reason_of_travel || "Not Specified";
		reason_counts[reason] = (reason_counts[reason] || 0) + 1;
		
		const project = d.project || "Not Specified";
		project_counts[project] = (project_counts[project] || 0) + 1;
	});
	
	return {
		total_movements,
		total_km,
		total_fuel,
		reason_counts,
		project_counts
	};
}

function render_reason_chart(data) {
	const chartData = Object.keys(data).map(key => ({
		name: key,
		value: data[key]
	}));
	
	new frappe.Chart("#reason-chart", {
		data: {
			labels: chartData.map(d => d.name),
			datasets: [{
				name: "Movements",
				values: chartData.map(d => d.value)
			}]
		},
		type: "bar",
		colors: ["#007bff"],
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
				name: "Movements",
				values: chartData.map(d => d.value)
			}]
		},
		type: "donut",
		colors: ["#007bff", "#28a745", "#ffc107", "#dc3545", "#17a2b8"],
		height: 300
	});
}

