from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# === Database Config ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === Alert DB Model ===
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    incident_type = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    SEVERITY_CHOICES = ['low', 'medium', 'high']
    INCIDENT_TYPE_CHOICES = ['burn', 'choking', 'unconscious', 'fall', 'heart attack', 'stroke', 'seizure', 'hypothermia', 'heatstroke', 'snake bite', 'fracture', 'allergic reaction', 'poisoning']

    def __repr__(self):
        return f"<Alert {self.id} - {self.incident_type}>"

    # Validation
    @staticmethod
    def validate_severity(severity):
        return severity in Alert.SEVERITY_CHOICES

    @staticmethod
    def validate_incident_type(incident_type):
        return incident_type in Alert.INCIDENT_TYPE_CHOICES

# === First-Aid Knowledge Base ===
first_aid_knowledge = {
    "burn": "Cool the burn with running water for 10–15 minutes. Do not apply creams.",
    "choking": "Give 5 back blows between shoulder blades. If needed, perform Heimlich.",
    "unconscious": "Check breathing. If none, begin CPR and call emergency services.",
    "fall": "Check for injuries. If unconscious, check breathing and call emergency services. Immobilize if necessary.",
    "heart attack": "Call emergency services. If conscious, have them chew aspirin if not allergic. Perform CPR if unconscious.",
    "stroke": "Call emergency services immediately. Note time symptoms started. Don't give anything to eat or drink.",
    "seizure": "Ensure safe surroundings. Don't hold them down. Place something soft under head. Check breathing after.",
    "hypothermia": "Move to warm place. Remove wet clothes. Use blankets. Avoid direct heat.",
    "heatstroke": "Move to cooler place. Hydrate if conscious. Apply cool cloths.",
    "snake bite": "Keep person still. Call emergency services. Elevate and immobilize the bite area.",
    "fracture": "Immobilize with splint. Call emergency services.",
    "allergic reaction": "Use epinephrine if available. Call emergency services.",
    "poisoning": "Call emergency services. Don't induce vomiting unless told to."
}

def get_chatbot_response(message):
    message = message.lower()
    for keyword, advice in first_aid_knowledge.items():
        if keyword in message:
            return advice
    return "Sorry, I don't know how to help with that. Try asking about burns, choking, or unconsciousness."

# === Routes ===
@app.route("/", methods=["GET", "POST"])
def index():
    severity_filter = request.args.get('severity')
    incident_type_filter = request.args.get('incident_type')

    # Build the query with optional filters
    query = Alert.query

    if severity_filter:
        query = query.filter(Alert.severity == severity_filter)
    
    if incident_type_filter:
        query = query.filter(Alert.incident_type == incident_type_filter)

    # Fetch filtered alerts, ordered by the timestamp (most recent first)
    all_alerts = query.order_by(Alert.timestamp.desc()).all()

    return render_template("index.html", alerts=all_alerts)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    user_message = ""
    bot_response = ""
    if request.method == "POST":
        user_message = request.form["message"]
        bot_response = get_chatbot_response(user_message)
    return render_template("chat.html", user_message=user_message, bot_response=bot_response)

@app.route("/alert", methods=["POST"])
def receive_alert():
    message = request.form.get("message")
    severity = request.form.get("severity")
    incident_type = request.form.get("incident_type")

    # Validate the data
    if not message or not severity or not incident_type:
        return jsonify({"error": "Missing fields"}), 400

    # Check for valid severity
    if not Alert.validate_severity(severity.lower()):
        return jsonify({"error": "Invalid severity"}), 400

    # Check for valid incident type
    if not Alert.validate_incident_type(incident_type.lower()):
        return jsonify({"error": "Invalid incident type"}), 400

    new_alert = Alert(
        message=message.strip(),
        severity=severity.lower(),
        incident_type=incident_type.lower()
    )
    db.session.add(new_alert)
    db.session.commit()

    return jsonify({"status": "Alert stored", "alert_id": new_alert.id}), 200

# === Run App ===
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)





