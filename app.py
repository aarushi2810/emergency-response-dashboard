from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime
import os
import logging
import bleach

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Model
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(10), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    SEVERITY_CHOICES = ['low', 'medium', 'high']
    INCIDENT_TYPE_CHOICES = ['fire', 'accident', 'medical', 'other']

    @classmethod
    def validate_severity(cls, value):
        return value in cls.SEVERITY_CHOICES

    @classmethod
    def validate_incident_type(cls, value):
        return value in cls.INCIDENT_TYPE_CHOICES

# Routes
@app.route("/", methods=["GET"])
def dashboard():
    severity = request.args.get("severity")
    incident_type = request.args.get("incident_type")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5

    query = Alert.query.order_by(Alert.timestamp.desc())
    if severity:
        query = query.filter_by(severity=severity)
    if incident_type:
        query = query.filter(Alert.incident_type.ilike(f"%{incident_type}%"))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    alerts = pagination.items

    return render_template("index.html", alerts=alerts, pagination=pagination)

@app.route("/alert", methods=["POST"])
def receive_alert():
    try:
        message = request.form.get("message", "").strip()
        severity = request.form.get("severity", "").lower()
        incident_type = request.form.get("incident_type", "").lower()

        if not message or not severity or not incident_type:
            return jsonify({"error": "Missing fields"}), 400

        if not Alert.validate_severity(severity):
            return jsonify({"error": f"Invalid severity. Must be one of: {Alert.SEVERITY_CHOICES}"}), 400

        if not Alert.validate_incident_type(incident_type):
            return jsonify({"error": f"Invalid incident type. Must be one of: {Alert.INCIDENT_TYPE_CHOICES}"}), 400

        new_alert = Alert(message=message, severity=severity, incident_type=incident_type)
        db.session.add(new_alert)
        db.session.commit()

        return jsonify({"status": "Alert stored", "alert_id": new_alert.id}), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# Run
if __name__ == "__main__":
    if not os.path.exists("alerts.db"):
        with app.app_context():
            db.create_all()
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> 616c2fe (Add: Flask dashboard with logging and templates)
