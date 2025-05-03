import cv2
from ultralytics import YOLO
import requests
import time

# Initialize YOLO model (you can use a smaller model for faster detection)
model = YOLO("yolov8n.pt")  # You can use yolov8n.pt for better speed

# Open the webcam
cap = cv2.VideoCapture(0)

# Function to send alert to the server
def send_alert_to_server(type, location):
    try:
        print("📡 Sending alert to server...")
        response = requests.post(
            "http://127.0.0.1:8000/alert",
            json={"type": type, "location": location}
        )
        if response.status_code == 200:
            print("✅ Alert sent successfully!")
        else:
            print(f"❌ Failed to send alert. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending alert: {e}")

# Run the loop to capture frames
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Resize the frame to make processing faster
    frame_resized = cv2.resize(frame, (640, 480))  # Resize to 640x480

    # Run YOLO detection
    results = model(frame_resized)

    # Extract detection results
    for result in results:
        for obj in result.boxes:
            class_name = obj.cls[0]  # Get the class of the detected object
            confidence = obj.conf[0]  # Get the confidence level
            if class_name == 0 and confidence > 0.5:  # Class 0 is 'person' in YOLO
                print("✅ Detected person!")
                
                # Send an alert to the server
                send_alert_to_server(type="Person Detected", location="Living Room")
                
                # Save video clip (optional)
                cv2.imwrite("detected_person.jpg", frame)

    # Display the frame
    cv2.imshow("YOLO Detection", frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()