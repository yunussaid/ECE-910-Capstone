import cv2
import time
import os

# Get absolute path to folder where script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

cams = [0, 1] # Camera indices (usually 0 and 1 for USB cameras)
caps = [cv2.VideoCapture(i) for i in cams]
time.sleep(1) # Small delay to let cameras warm up

for idx, cap in zip(cams, caps):
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Failed to capture from camera {idx}")
        continue

    filename = os.path.join(IMG_DIR, f"camera_{idx}.jpg")
    cv2.imwrite(filename, frame)
    print(f"✅ Saved image from camera {idx} -> {filename}")

# Release all cameras
for cap in caps:
    cap.release()

cv2.destroyAllWindows()