import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

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

# Initialize the database and train model if needed
@app.before_request
def initialize_db():
    if not os.path.exists("alerts.db"):
        with app.app_context():
            db.create_all()

    # Train the Naive Bayes model if not already trained
    if not os.path.exists('alert_classifier.pkl'):
        # Sample data for training (replace with actual dataset)
        data = [
            {"message": "Fire alarm triggered in the kitchen", "incident_type": "fire"},
            {"message": "Car accident on highway", "incident_type": "accident"},
            {"message": "Medical emergency, heart attack", "incident_type": "medical"},
            {"message": "Chemical spill in lab", "incident_type": "other"}
        ]
        
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Feature (text messages) and Target (incident type)
        X = df["message"]
        y = df["incident_type"]

        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create a pipeline with TF-IDF vectorization and Naive Bayes classifier
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())

        # Train the model
        model.fit(X_train, y_train)

        # Save the trained model to a file
        joblib.dump(model, 'alert_classifier.pkl')
        print("Model trained and saved as alert_classifier.pkl")

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

@csrf.exempt
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

        # Load the trained model
        model = joblib.load('alert_classifier.pkl')

        # Predict the incident type using the model
        predicted_type = model.predict([message])[0]

        # Create and save the alert
        new_alert = Alert(message=message, severity=severity, incident_type=predicted_type)
        db.session.add(new_alert)
        db.session.commit()

        return jsonify({"status": "Alert stored", "alert_id": new_alert.id, "predicted_type": predicted_type}), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)