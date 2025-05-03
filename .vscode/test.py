# webcam_test.py
import cv2

print("🧪 Starting webcam test...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame grab failed.")
        break

    cv2.imshow("Webcam Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
