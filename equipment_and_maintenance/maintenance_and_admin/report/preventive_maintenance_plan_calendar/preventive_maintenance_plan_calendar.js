// Copyright (c) 2025, Friends ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Preventive Maintenance Plan Calendar"] = {
	"filters": [
		{
			"fieldname": "start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "avg_monthly_hours",
			"label": __("Average Monthly Hours"),
			"fieldtype": "Float",
			"default": 50,
			"description": __("Estimated average hours per month for date calculation")
		},
		{
			"fieldname": "avg_monthly_km",
			"label": __("Average Monthly Kilometers"),
			"fieldtype": "Float",
			"default": 500,
			"description": __("Estimated average kilometers per month for date calculation")
		}
	],
	
	"onload": function(report) {
		// Add custom CSS for calendar view
		$('<style>')
			.prop('type', 'text/css')
			.html(`
				.report-container {
					background: #f8f9fa;
					padding: 20px;
					border-radius: 8px;
					margin-bottom: 20px;
				}
				.stats-cards {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
					gap: 15px;
					margin-bottom: 20px;
				}
				.stat-card {
					background: white;
					padding: 20px;
					border-radius: 6px;
					border: 1px solid #e0e0e0;
					text-align: center;
					transition: box-shadow 0.2s;
				}
				.stat-card:hover {
					box-shadow: 0 2px 8px rgba(0,0,0,0.1);
				}
				.stat-value {
					font-size: 32px;
					font-weight: bold;
					color: #2c3e50;
					margin: 10px 0;
				}
				.stat-label {
					color: #6c757d;
					font-size: 14px;
					text-transform: uppercase;
					letter-spacing: 0.5px;
				}
				.charts-container {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
					gap: 20px;
					margin-bottom: 20px;
				}
				.chart-wrapper {
					background: white;
					padding: 20px;
					border-radius: 6px;
					border: 1px solid #e0e0e0;
				}
				.chart-title {
					font-size: 16px;
					font-weight: 600;
					margin-bottom: 15px;
					color: #2c3e50;
					border-bottom: 1px solid #e0e0e0;
					padding-bottom: 10px;
				}
				.calendar-cell {
					min-height: 60px;
					padding: 8px;
					border: 1px solid #e0e0e0;
					position: relative;
				}
				.service-badge {
					display: inline-block;
					padding: 4px 8px;
					margin: 2px;
					border-radius: 4px;
					font-size: 11px;
					font-weight: 600;
					color: white;
				}
				.service-badge.hours {
					background: #3498db;
				}
				.service-badge.km {
					background: #e74c3c;
				}
				.table-calendar {
					background: white;
					border-radius: 6px;
					overflow: hidden;
					border: 1px solid #e0e0e0;
				}
				.table-calendar thead {
					background: #f8f9fa;
					color: #2c3e50;
					border-bottom: 2px solid #dee2e6;
				}
				.table-calendar thead th {
					padding: 15px;
					font-weight: 600;
					text-align: center;
					color: #2c3e50;
				}
				.table-calendar tbody td {
					padding: 12px;
					text-align: center;
					vertical-align: middle;
					border-bottom: 1px solid #f0f0f0;
				}
				.table-calendar tbody tr:hover {
					background: #f8f9fa;
				}
				.month-header {
					background: #f8f9fa;
					color: #2c3e50;
					font-weight: 600;
					padding: 10px;
					border-bottom: 2px solid #dee2e6;
				}
			`)
			.appendTo('head');
	},
	
	"after_datatable_render": function(datatable) {
		// Add charts after data table is rendered
		setTimeout(() => {
			add_charts_to_report(datatable);
		}, 1000);
	},
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Highlight service due dates with beautiful badges
		if (column.fieldname.includes("_") && value && value.trim() !== "") {
			const services = value.split(", ");
			const badges = services.map(service => {
				const isHours = service.includes("H");
				const badgeClass = isHours ? "hours" : "km";
				return `<span class="service-badge ${badgeClass}">${service}</span>`;
			}).join("");
			value = `<div style="text-align: center;">${badges}</div>`;
		}
		
		// Style equipment type column
		if (column.fieldname === "equipment_type" && value) {
			value = `<strong style="color: #2c3e50;">${value}</strong>`;
		}
		
		// Style plate number column
		if (column.fieldname === "plate_number" && value) {
			value = `<span style="font-family: monospace; background: #f0f0f0; padding: 4px 8px; border-radius: 4px;">${value}</span>`;
		}
		
		return value;
	}
};

function add_charts_to_report(datatable) {
	// Get chart data from report message
	const report_wrapper = $(".report-wrapper");
	if (!report_wrapper.length) {
		setTimeout(() => add_charts_to_report(datatable), 500);
		return;
	}
	
	// Check if charts already added
	if ($(".stats-cards").length) return;
	
	// Create stats cards container
	const statsContainer = $(`
		<div class="report-container">
			<div class="stats-cards" id="stats-cards"></div>
			<div class="charts-container" id="charts-container"></div>
		</div>
	`);
	
	report_wrapper.prepend(statsContainer);
	
	// Add stat cards
	const statsCards = $(`
		<div class="stat-card">
			<div class="stat-label">Total Equipment</div>
			<div class="stat-value" id="total-equipment">0</div>
		</div>
		<div class="stat-card">
			<div class="stat-label">Upcoming Services</div>
			<div class="stat-value" id="upcoming-services">0</div>
		</div>
		<div class="stat-card">
			<div class="stat-label">Services This Month</div>
			<div class="stat-value" id="services-this-month">0</div>
		</div>
		<div class="stat-card">
			<div class="stat-label">Overdue</div>
			<div class="stat-value" id="overdue-count">0</div>
		</div>
	`);
	
	$("#stats-cards").html(statsCards);
	
	// Get data from datatable if available, otherwise read from DOM
	if (datatable && datatable.data && datatable.data.length > 0) {
		calculate_stats_from_datatable(datatable);
		add_services_by_month_chart_from_data(datatable);
		add_services_by_type_chart_from_data(datatable);
	} else {
		// Fallback to DOM reading
		setTimeout(() => {
			calculate_stats_from_table();
			add_services_by_month_chart();
			add_services_by_type_chart();
		}, 500);
	}
}

function calculate_stats_from_datatable(datatable) {
	const data = datatable.data || [];
	const columns = datatable.columns || [];
	
	let totalServices = 0;
	let thisMonthServices = 0;
	const today = new Date();
	const currentMonth = today.getMonth();
	const currentYear = today.getFullYear();
	const currentMonthName = getMonthName(currentMonth);
	
	// Find month column indices
	const monthColumns = [];
	columns.forEach((col, index) => {
		if (index > 2 && col.fieldname && col.fieldname.includes("_")) {
			const headerText = col.label || col.content || "";
			monthColumns.push({
				index: index,
				fieldname: col.fieldname,
				label: headerText,
				isCurrentMonth: headerText.includes(currentMonthName) && headerText.includes(currentYear.toString())
			});
		}
	});
	
	data.forEach(row => {
		monthColumns.forEach(monthCol => {
			const value = row[monthCol.fieldname];
			if (value && value.trim() !== "") {
				// Count services (split by comma)
				const services = value.split(",").filter(s => s.trim());
				const count = services.length;
				totalServices += count;
				
				if (monthCol.isCurrentMonth) {
					thisMonthServices += count;
				}
			}
		});
	});
	
	// Update stat cards
	$("#total-equipment").text(data.length || 0);
	$("#upcoming-services").text(totalServices || 0);
	$("#services-this-month").text(thisMonthServices || 0);
}

function add_services_by_month_chart_from_data(datatable) {
	const data = datatable.data || [];
	const columns = datatable.columns || [];
	
	const headers = [];
	const values = [];
	
	columns.forEach((col, index) => {
		if (index > 2 && col.fieldname && col.fieldname.includes("_")) {
			const headerText = col.label || col.content || "";
			if (headerText) {
				headers.push(headerText);
				
				// Count services in this column
				let count = 0;
				data.forEach(row => {
					const value = row[col.fieldname];
					if (value && value.trim() !== "") {
						count += value.split(",").filter(s => s.trim()).length;
					}
				});
				values.push(count);
			}
		}
	});
	
	if (headers.length > 0 && values.some(v => v > 0)) {
		const chartContainer = $(`
			<div class="chart-wrapper">
				<div class="chart-title">Services by Month</div>
				<canvas id="services-by-month-chart"></canvas>
			</div>
		`);
		$("#charts-container").append(chartContainer);
		
		setTimeout(() => {
			new frappe.Chart("#services-by-month-chart", {
				type: "bar",
				data: {
					labels: headers,
					datasets: [{
						name: "Services",
						values: values
					}]
				},
				colors: ["#3498db"],
				barOptions: {
					spaceRatio: 0.5
				}
			});
		}, 300);
	}
}

function add_services_by_type_chart_from_data(datatable) {
	const data = datatable.data || [];
	const columns = datatable.columns || [];
	
	let hoursCount = 0;
	let kmCount = 0;
	
	columns.forEach((col, index) => {
		if (index > 2 && col.fieldname && col.fieldname.includes("_")) {
			data.forEach(row => {
				const value = row[col.fieldname];
				if (value && value.trim() !== "") {
					const services = value.split(",");
					services.forEach(service => {
						const s = service.trim();
						if (s.includes("H") || s.match(/\d+H/)) {
							hoursCount++;
						} else if (s.includes("KM") || s.match(/\d+KM/)) {
							kmCount++;
						}
					});
				}
			});
		}
	});
	
	if (hoursCount > 0 || kmCount > 0) {
		const chartContainer = $(`
			<div class="chart-wrapper">
				<div class="chart-title">Services by Type</div>
				<canvas id="services-by-type-chart"></canvas>
			</div>
		`);
		$("#charts-container").append(chartContainer);
		
		setTimeout(() => {
			new frappe.Chart("#services-by-type-chart", {
				type: "donut",
				data: {
					labels: ["Hours", "Kilometers"],
					datasets: [{
						name: "Services",
						values: [hoursCount, kmCount]
					}]
				},
				colors: ["#3498db", "#e74c3c"]
			});
		}, 300);
	}
}

function calculate_stats_from_table() {
	// Try multiple selectors to find the table
	let table = $(".dt-scrollable tbody");
	if (!table.length) {
		table = $("table tbody");
	}
	if (!table.length) {
		table = $(".report-table tbody");
	}
	
	if (!table.length) {
		console.log("Table not found, retrying...");
		setTimeout(calculate_stats_from_table, 500);
		return;
	}
	
	const rows = table.find("tr");
	let totalServices = 0;
	let thisMonthServices = 0;
	const today = new Date();
	const currentMonth = today.getMonth();
	const currentYear = today.getFullYear();
	const currentMonthName = getMonthName(currentMonth);
	
	// Get headers
	let headers = [];
	$(".dt-scrollable thead th, table thead th").each(function(index) {
		if (index > 2) { // Skip first 3 columns
			headers.push({
				index: index,
				text: $(this).text().trim()
			});
		}
	});
	
	rows.each(function() {
		const cells = $(this).find("td");
		cells.each(function(cellIndex) {
			if (cellIndex > 2) { // Skip first 3 columns
				const cell = $(this);
				const cellText = cell.text().trim();
				
				// Check for service badges or text
				const badges = cell.find(".service-badge");
				let serviceCount = 0;
				
				if (badges.length > 0) {
					serviceCount = badges.length;
				} else if (cellText) {
					// Count services in text (split by comma)
					const services = cellText.split(",").filter(s => s.trim());
					serviceCount = services.length;
				}
				
				if (serviceCount > 0) {
					totalServices += serviceCount;
					
					// Check if this month
					const header = headers.find(h => h.index === cellIndex);
					if (header && header.text.includes(currentMonthName) && header.text.includes(currentYear.toString())) {
						thisMonthServices += serviceCount;
					}
				}
			}
		});
	});
	
	// Update stat cards
	$("#total-equipment").text(rows.length || 0);
	$("#upcoming-services").text(totalServices || 0);
	$("#services-this-month").text(thisMonthServices || 0);
}

function add_services_by_month_chart() {
	const chartContainer = $(`
		<div class="chart-wrapper">
			<div class="chart-title">Services by Month</div>
			<canvas id="services-by-month-chart"></canvas>
		</div>
	`);
	
	$("#charts-container").append(chartContainer);
	
	// Get data from table headers
	const headers = [];
	const values = [];
	
	// Try multiple selectors
	let headerRow = $(".dt-scrollable thead th");
	if (!headerRow.length) {
		headerRow = $("table thead th");
	}
	
	headerRow.each(function(index) {
		if (index > 2) { // Skip first 3 columns
			const headerText = $(this).text().trim();
			if (headerText) {
				headers.push(headerText);
				
				// Count services in this month column
				let count = 0;
				let tbody = $(".dt-scrollable tbody");
				if (!tbody.length) {
					tbody = $("table tbody");
				}
				
				tbody.find("tr").each(function() {
					const cell = $(this).find("td").eq(index);
					const badges = cell.find(".service-badge");
					if (badges.length > 0) {
						count += badges.length;
					} else {
						const text = cell.text().trim();
						if (text) {
							count += text.split(",").filter(s => s.trim()).length;
						}
					}
				});
				values.push(count);
			}
		}
	});
	
	if (headers.length > 0 && values.some(v => v > 0)) {
		setTimeout(() => {
			new frappe.Chart("#services-by-month-chart", {
				type: "bar",
				data: {
					labels: headers,
					datasets: [{
						name: "Services",
						values: values
					}]
				},
				colors: ["#3498db"],
				barOptions: {
					spaceRatio: 0.5
				}
			});
		}, 300);
	} else {
		$("#services-by-month-chart").parent().append("<p style='text-align: center; color: #999; padding: 20px;'>No data available</p>");
	}
}

function add_services_by_type_chart() {
	const chartContainer = $(`
		<div class="chart-wrapper">
			<div class="chart-title">Services by Type</div>
			<canvas id="services-by-type-chart"></canvas>
		</div>
	`);
	
	$("#charts-container").append(chartContainer);
	
	// Count services by type from table
	let hoursCount = 0;
	let kmCount = 0;
	
	// Try multiple selectors
	let tbody = $(".dt-scrollable tbody");
	if (!tbody.length) {
		tbody = $("table tbody");
	}
	
	tbody.find("tr").each(function() {
		$(this).find("td").each(function(index) {
			if (index > 2) {
				const cell = $(this);
				const badges = cell.find(".service-badge");
				
				if (badges.length > 0) {
					badges.each(function() {
						const badge = $(this);
						if (badge.hasClass("hours")) {
							hoursCount++;
						} else if (badge.hasClass("km")) {
							kmCount++;
						}
					});
				} else {
					const text = cell.text().trim();
					if (text) {
						const services = text.split(",");
						services.forEach(service => {
							const s = service.trim();
							if (s.includes("H") || s.match(/\d+H/)) {
								hoursCount++;
							} else if (s.includes("KM") || s.match(/\d+KM/)) {
								kmCount++;
							}
						});
					}
				}
			}
		});
	});
	
	if (hoursCount > 0 || kmCount > 0) {
		setTimeout(() => {
			new frappe.Chart("#services-by-type-chart", {
				type: "donut",
				data: {
					labels: ["Hours", "Kilometers"],
					datasets: [{
						name: "Services",
						values: [hoursCount, kmCount]
					}]
				},
				colors: ["#3498db", "#e74c3c"]
			});
		}, 300);
	} else {
		$("#services-by-type-chart").parent().append("<p style='text-align: center; color: #999; padding: 20px;'>No data available</p>");
	}
}

function getMonthName(monthIndex) {
	const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
	return months[monthIndex];
}

