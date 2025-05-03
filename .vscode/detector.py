from twilio.rest import Client
from ultralytics import YOLO
import cv2
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
your_phone_number = os.getenv("TARGET_PHONE_NUMBER")

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Cooldown to avoid spamming alerts
last_alert_time = 0
cooldown_seconds = 30  # Send alert only every 30 seconds

# Filter only specific detections (based on class names in YOLO model)
target_labels = ['person']  # You can add more relevant labels if using a custom model

def send_sms_alert(message):
    try:
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=your_phone_number
        )
        print("📩 SMS sent:", sms.sid)
    except Exception as e:
        print("❌ Failed to send SMS:", e)

print("🚀 Script started...")

# Load YOLO model
print("📦 Loading YOLOv8 model...")
model = YOLO('yolov8n.pt')  # Using a smaller YOLO model for faster processing
class_names = model.names
print("✅ Model loaded.")

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Failed to open webcam.")
    exit()
else:
    print("🎥 Webcam opened.")

# Main loop to process webcam frames
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from webcam.")
            break

        print("📸 Frame captured, running YOLO...")
        results = model.predict(frame, stream=True)
        detected = False

        # Loop through results and process detections
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = class_names[cls]
                print(f"✅ Detected: {label} with confidence: {conf:.2f}")

                # Filter detection based on confidence and target label
                if label in target_labels and conf > 0.3:
                    # Draw bounding box on the frame
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = xyxy
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    detected = True

        # Send alert only once in the cooldown period
        if detected and (time.time() - last_alert_time > cooldown_seconds):
            try:
                print("📱 Sending alert to server and SMS...")
                requests.post("http://127.0.0.1:8000/alert", json={
                    "type": label,  # from YOLO label
                    "location": "Hostel Camera 1"
                })
                send_sms_alert("🚨 Emergency detected by AI system!")
                last_alert_time = time.time()
            except Exception as e:
                print("❌ Failed to send request or SMS:", e)

        # Display resized frame
        resized_frame = cv2.resize(frame, (800, 600))
        cv2.imshow("YOLOv8 Detection", resized_frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Quitting...")
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("🔚 Cleanup complete.")