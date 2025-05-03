import os

TEMPLATES = {
    "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Emergency Alerts Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
        .filter-form { margin-bottom: 20px; }
        .alert { border: 1px solid #ccc; padding: 12px; margin-bottom: 10px; border-left: 6px solid #007BFF; }
        .pagination { margin-top: 20px; }
        .pagination a { margin: 0 5px; text-decoration: none; }
        .active-page { font-weight: bold; }
    </style>
</head>
<body>
<h1>Emergency Alerts Dashboard</h1>

<form class="filter-form" method="get" action="/">
    <label for="severity">Severity:</label>
    <select name="severity" id="severity">
        <option value="">All</option>
        <option value="low" {{ 'selected' if request.args.get('severity') == 'low' else '' }}>Low</option>
        <option value="medium" {{ 'selected' if request.args.get('severity') == 'medium' else '' }}>Medium</option>
        <option value="high" {{ 'selected' if request.args.get('severity') == 'high' else '' }}>High</option>
    </select>

    <label for="incident_type">Incident:</label>
    <input type="text" name="incident_type" id="incident_type" value="{{ request.args.get('incident_type', '') }}">

    <button type="submit">Filter</button>
</form>

{% for alert in alerts %}
    <div class="alert">
        <strong>[{{ alert.severity|capitalize }}] {{ alert.incident_type|capitalize }}</strong><br>
        {{ alert.message }}<br>
        <small>{{ alert.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</small>
    </div>
{% else %}
    <p>No alerts found.</p>
{% endfor %}

<div class="pagination">
    {% if pagination.has_prev %}
        <a href="?page={{ pagination.prev_num }}&severity={{ request.args.get('severity', '') }}&incident_type={{ request.args.get('incident_type', '') }}">« Prev</a>
    {% endif %}
    {% for page_num in pagination.iter_pages(left_edge=2, right_edge=2, left_current=2, right_current=2) %}
        {% if page_num %}
            {% if page_num == pagination.page %}
                <span class="active-page">{{ page_num }}</span>
            {% else %}
                <a href="?page={{ page_num }}&severity={{ request.args.get('severity', '') }}&incident_type={{ request.args.get('incident_type', '') }}">{{ page_num }}</a>
            {% endif %}
        {% else %}
            ...
        {% endif %}
    {% endfor %}
    {% if pagination.has_next %}
        <a href="?page={{ pagination.next_num }}&severity={{ request.args.get('severity', '') }}&incident_type={{ request.args.get('incident_type', '') }}">Next »</a>
    {% endif %}
</div>
</body>
</html>
""",

    "404.html": """<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>Oops! The page you're looking for doesn't exist.</p>
</body>
</html>
""",

    "500.html": """<!DOCTYPE html>
<html>
<head><title>500 Internal Server Error</title></head>
<body>
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong. Please try again later.</p>
</body>
</html>
"""
}

# === Create Templates Directory & Files ===
os.makedirs("templates", exist_ok=True)

for filename, content in TEMPLATES.items():
    path = os.path.join("templates", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Templates generated in the 'templates/' directory.")