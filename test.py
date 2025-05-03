import cv2

print("Script started.")  # Check if the script is even running

img_path = '/Users/aarushi/Downloads/6a265594d9b5620aad75b958bcf6bf1e.jpg'
print(f"Trying to read image from: {img_path}")

img = cv2.imread(img_path)

if img is None:
    print("Error: Image not found or cannot be opened.")
else:
    print("Image loaded successfully!")
    cv2.imshow('Test Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
