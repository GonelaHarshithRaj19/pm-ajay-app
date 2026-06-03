from flask import Flask, render_template, request, jsonify
import csv
import io

app = Flask(__name__)

projects = []

# 🌍 ALL STATES + UTs COORDINATES
state_coords = {
    # States
    "AP": (15.9129, 79.7400),
    "AR": (28.2180, 94.7278),
    "AS": (26.2006, 92.9376),
    "BR": (25.0961, 85.3131),
    "CG": (21.2787, 81.8661),
    "GA": (15.2993, 74.1240),
    "GJ": (22.2587, 71.1924),
    "HR": (29.0588, 76.0856),
    "HP": (31.1048, 77.1734),
    "JH": (23.6102, 85.2799),
    "KA": (15.3173, 75.7139),
    "KL": (10.8505, 76.2711),
    "MP": (23.4733, 77.9470),
    "MH": (19.7515, 75.7139),
    "MN": (24.6637, 93.9063),
    "ML": (25.4670, 91.3662),
    "MZ": (23.1645, 92.9376),
    "NL": (26.1584, 94.5624),
    "OD": (20.9517, 85.0985),
    "PB": (31.1471, 75.3412),
    "RJ": (27.0238, 74.2179),
    "SK": (27.5330, 88.5122),
    "TN": (11.1271, 78.6569),
    "TS": (18.1124, 79.0193),
    "TR": (23.9408, 91.9882),
    "UP": (26.8467, 80.9462),
    "UK": (30.0668, 79.0193),
    "WB": (22.9868, 87.8550),

    # UTs
    "AN": (11.7401, 92.6586),
    "CH": (30.7333, 76.7794),
    "DN": (20.1809, 73.0169),
    "DD": (20.4283, 72.8397),
    "DL": (28.7041, 77.1025),
    "JK": (33.7782, 76.5762),
    "LA": (34.1526, 77.5771),
    "LD": (10.5667, 72.6417),
    "PY": (11.9416, 79.8083)
}

# 🧠 FULL NAMES
state_full_names = {
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal",

    # UTs
    "AN": "Andaman & Nicobar",
    "CH": "Chandigarh",
    "DN": "Dadra & Nagar Haveli",
    "DD": "Daman & Diu",
    "DL": "Delhi",
    "JK": "Jammu & Kashmir",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "PY": "Puducherry"
}


# 📂 LOAD CSV
def load_csv():
    global projects
    projects = []

    try:
        with open("data/projects.csv", "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                state_code = row.get('State', '').strip()

                state = state_full_names.get(state_code, state_code)
                lat, lon = state_coords.get(state_code, (20, 78))

                projects.append({
                    "project_name": row.get("Project_Name", "Project"),
                    "component": row.get("Component", "General"),
                    "status": row.get("Status", "On Track"),
                    "state": state,
                    "completion": int(float(row.get("Completion_Percentage", 0))),
                    "delay": int(float(row.get("Delay_Days", 0))),
                    "lat": lat,
                    "lon": lon,
                    "project_id": row.get("Project_ID", ""),
                    "agency_type": row.get("Agency_Type", ""),
                    "funds_allocated": float(row.get("Funds_Allocated", 0)),
                    "funds_utilized": float(row.get("Funds_Utilized", 0)),
                    "manpower": int(row.get("Manpower", 0)),
                    "duration": int(row.get("Project_Duration", 0))
                })

    except Exception as e:
        print("CSV Load Error:", e)


# 📊 STATS
def get_stats():
    total = len(projects)
    ontrack = sum(1 for p in projects if p['status'] == "On Track")
    delayed = sum(1 for p in projects if p['status'] == "Delayed")
    risk = sum(1 for p in projects if p['status'] == "At Risk")
    return total, ontrack, delayed, risk


# 🏠 HOME
@app.route('/')
def home():
    load_csv()
    total, ontrack, delayed, risk = get_stats()

    return render_template("index.html",
        total=total,
        ontrack=ontrack,
        delayed=delayed,
        risk=risk,
        projects=projects
    )


# 🔮 PREDICTION PAGE
@app.route('/prediction')
def prediction_page():
    return render_template("prediction.html")


# 🤖 PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    load_csv()

    completion = float(request.form['completion'])
    delay = float(request.form['delay'])
    state_code = request.form['state']

    if completion > 80 and delay < 5:
        status = "On Track"
    elif delay > 10:
        status = "Delayed"
    else:
        status = "At Risk"

    state = state_full_names.get(state_code, state_code)
    lat, lon = state_coords.get(state_code, (20, 78))

    new_project = {
        "project_name": request.form.get("project_name", "Predicted Project"),
        "component": request.form.get("component", "AI Prediction"),
        "status": status,
        "state": state,
        "completion": completion,
        "delay": delay,
        "lat": lat,
        "lon": lon
    }

    projects.append(new_project)

    total, ontrack, delayed, risk = get_stats()

    return render_template("index.html",
        total=total,
        ontrack=ontrack,
        delayed=delayed,
        risk=risk,
        projects=projects,
        last_prediction=new_project
    )


# 📡 API
@app.route('/api/projects')
def api_projects():
    load_csv()
    return jsonify(projects)


@app.route('/api/stats')
def api_stats():
    load_csv()
    total, ontrack, delayed, risk = get_stats()

    return jsonify({
        "total": total,
        "ontrack": ontrack,
        "delayed": delayed,
        "risk": risk
    })


# 📊 AGENCIES
@app.route('/api/agencies')
def api_agencies():
    load_csv()
    agencies = {}
    for p in projects:
        agency = p.get('agency_type', 'Unknown')
        if agency not in agencies:
            agencies[agency] = {'count': 0, 'states': set()}
        agencies[agency]['count'] += 1
        agencies[agency]['states'].add(p['state'])

    result = []
    for agency, data in agencies.items():
        result.append({
            'name': agency,
            'projects': data['count'],
            'states': list(data['states'])
        })
    return jsonify(result)


# 💰 FUND MANAGEMENT
@app.route('/api/funds')
def api_funds():
    load_csv()
    total_allocated = sum(p.get('funds_allocated', 0) for p in projects)
    total_utilized = sum(p.get('funds_utilized', 0) for p in projects)

    return jsonify({
        'total_allocated': total_allocated,
        'total_utilized': total_utilized,
        'pending': total_allocated - total_utilized
    })


# 📈 CHART DATA
@app.route('/api/chart/project-status')
def api_chart_project_status():
    load_csv()
    status_counts = {}
    for p in projects:
        status = p['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    return jsonify({
        'labels': list(status_counts.keys()),
        'datasets': [{
            'data': list(status_counts.values()),
            'backgroundColor': ['#28a745', '#ffc107', '#dc3545', '#17a2b8']
        }]
    })


@app.route('/api/chart/fund-utilization')
def api_chart_fund_utilization():
    load_csv()
    component_funds = {}
    for p in projects:
        comp = p['component']
        if comp not in component_funds:
            component_funds[comp] = {'allocated': 0, 'utilized': 0}
        component_funds[comp]['allocated'] += p.get('funds_allocated', 0)
        component_funds[comp]['utilized'] += p.get('funds_utilized', 0)

    return jsonify({
        'labels': list(component_funds.keys()),
        'datasets': [{
            'label': 'Allocated',
            'data': [component_funds[c]['allocated'] for c in component_funds],
            'backgroundColor': '#007bff'
        }, {
            'label': 'Utilized',
            'data': [component_funds[c]['utilized'] for c in component_funds],
            'backgroundColor': '#28a745'
        }]
    })


# 📤 EXPORT ENDPOINTS
@app.route('/api/export/projects')
def export_projects():
    load_csv()
    # Return CSV data
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['project_id', 'project_name', 'component', 'state', 'status', 'completion', 'funds_allocated', 'funds_utilized'])
    writer.writeheader()
    for p in projects:
        writer.writerow({
            'project_id': p['project_id'],
            'project_name': p['project_name'],
            'component': p['component'],
            'state': p['state'],
            'status': p['status'],
            'completion': p['completion'],
            'funds_allocated': p['funds_allocated'],
            'funds_utilized': p['funds_utilized']
        })
    return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=projects.csv'}


@app.route('/api/export/agencies')
def export_agencies():
    load_csv()
    agencies = {}
    for p in projects:
        agency = p.get('agency_type', 'Unknown')
        if agency not in agencies:
            agencies[agency] = {'count': 0, 'states': set()}
        agencies[agency]['count'] += 1
        agencies[agency]['states'].add(p['state'])

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['agency', 'projects', 'states'])
    writer.writeheader()
    for agency, data in agencies.items():
        writer.writerow({
            'agency': agency,
            'projects': data['count'],
            'states': ', '.join(data['states'])
        })
    return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=agencies.csv'}


@app.route('/api/export/dashboard')
def export_dashboard():
    load_csv()
    total, ontrack, delayed, risk = get_stats()
    data = {
        'total_projects': total,
        'on_track': ontrack,
        'delayed': delayed,
        'at_risk': risk,
        'total_funds_allocated': sum(p.get('funds_allocated', 0) for p in projects),
        'total_funds_utilized': sum(p.get('funds_utilized', 0) for p in projects)
    }
    return jsonify(data), 200, {'Content-Disposition': 'attachment; filename=dashboard.json'}


@app.route('/api/export/map')
def export_map():
    load_csv()
    map_data = [{'lat': p['lat'], 'lon': p['lon'], 'project': p['project_name'], 'state': p['state'], 'status': p['status']} for p in projects]
    return jsonify(map_data), 200, {'Content-Disposition': 'attachment; filename=map_data.json'}


# Dummy data for other exports
@app.route('/api/export/beneficiaries')
def export_beneficiaries():
    beneficiaries = [
        {'id': 'BEN-2023-001', 'name': 'Ramesh Kumar', 'category': 'SC', 'location': 'Uttar Pradesh', 'score': 95},
        {'id': 'BEN-2023-002', 'name': 'Sunita Devi', 'category': 'ST', 'location': 'Rajasthan', 'score': 92},
        {'id': 'BEN-2023-003', 'name': 'Arun Meena', 'category': 'OBC', 'location': 'Madhya Pradesh', 'score': 88}
    ]
    return jsonify(beneficiaries), 200, {'Content-Disposition': 'attachment; filename=beneficiaries.json'}


@app.route('/api/export/fund-releases')
def export_fund_releases():
    releases = [
        {'id': 'TXN-2023-04512', 'project': 'Adarsh Gram - Baripada', 'agency': 'Rural Development Dept.', 'amount': 5.2, 'date': '2023-11-15', 'status': 'Completed'},
        {'id': 'TXN-2023-04511', 'project': 'GIA Scholarship Program', 'agency': 'Education Directorate', 'amount': 3.8, 'date': '2023-11-14', 'status': 'Completed'}
    ]
    return jsonify(releases), 200, {'Content-Disposition': 'attachment; filename=fund_releases.json'}


@app.route('/api/export/pending-approvals')
def export_pending_approvals():
    approvals = [
        {'id': 'REQ-2023-07841', 'project': 'Hostel - Udaipur', 'agency': 'Education Directorate', 'amount': 6.5, 'date': '2023-11-16'},
        {'id': 'REQ-2023-07840', 'project': 'Adarsh Gram - Satna', 'agency': 'Rural Development Dept.', 'amount': 3.2, 'date': '2023-11-15'}
    ]
    return jsonify(approvals), 200, {'Content-Disposition': 'attachment; filename=pending_approvals.json'}


@app.route('/api/export/recent-reports')
def export_recent_reports():
    reports = [
        {'id': 'RPT-2023-0451', 'title': 'Q3 2023 Performance Report', 'type': 'Performance', 'period': 'Quarterly', 'generated': '2023-11-15', 'downloads': 142},
        {'id': 'RPT-2023-0450', 'title': 'October 2023 Financial Summary', 'type': 'Financial', 'period': 'Monthly', 'generated': '2023-11-05', 'downloads': 89}
    ]
    return jsonify(reports), 200, {'Content-Disposition': 'attachment; filename=recent_reports.json'}


@app.route('/api/export/scheduled-reports')
def export_scheduled_reports():
    reports = [
        {'id': 'SCH-2023-012', 'title': 'Weekly Progress Update', 'frequency': 'Weekly', 'next_run': '2023-11-20', 'recipients': 24, 'status': 'Active'},
        {'id': 'SCH-2023-011', 'title': 'Monthly Financial Report', 'frequency': 'Monthly', 'next_run': '2023-12-01', 'recipients': 18, 'status': 'Active'}
    ]
    return jsonify(reports), 200, {'Content-Disposition': 'attachment; filename=scheduled_reports.json'}


# 📊 CHART DATA FOR FRONTEND
@app.route('/api/chart/project-timeline')
def api_chart_project_timeline():
    # Dummy timeline data
    return jsonify({
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'datasets': [{
            'label': 'Completed',
            'data': [10, 15, 20, 25, 30, 35],
            'backgroundColor': '#28a745',
            'borderColor': '#28a745',
            'fill': False
        }, {
            'label': 'In Progress',
            'data': [5, 8, 12, 15, 18, 20],
            'backgroundColor': '#ffc107',
            'borderColor': '#ffc107',
            'fill': False
        }]
    })


@app.route('/api/chart/project-state')
def api_chart_project_state():
    load_csv()
    state_counts = {}
    for p in projects:
        state = p['state']
        state_counts[state] = state_counts.get(state, 0) + 1

    return jsonify({
        'labels': list(state_counts.keys()),
        'datasets': [{
            'data': list(state_counts.values()),
            'backgroundColor': '#007bff'
        }]
    })


@app.route('/api/chart/fund-utilization-rate')
def api_chart_fund_utilization_rate():
    return jsonify({
        'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
        'datasets': [{
            'label': 'Utilization Rate (%)',
            'data': [65, 70, 75, 80],
            'backgroundColor': '#28a745',
            'borderColor': '#28a745',
            'fill': False
        }]
    })


@app.route('/api/chart/performance-trend')
def api_chart_performance_trend():
    return jsonify({
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'datasets': [{
            'label': 'Performance Score',
            'data': [60, 65, 70, 68, 72, 75, 78, 80, 82, 85, 87, 90],
            'backgroundColor': '#007bff',
            'borderColor': '#007bff',
            'fill': False
        }]
    })


@app.route('/api/chart/impact-analysis')
def api_chart_impact_analysis():
    return jsonify({
        'labels': ['Education', 'Health', 'Infrastructure', 'Employment'],
        'datasets': [{
            'label': 'Impact Score',
            'data': [85, 78, 92, 88],
            'backgroundColor': '#28a745'
        }]
    })


# 🚀 RUN
if __name__ == "__main__":
    app.run(debug=True)