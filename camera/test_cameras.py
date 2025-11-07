import cv2
import time
import os

# Camera indices (usually 0 and 1 for USB cameras)
cams = [0, 1]

# Open both cameras
caps = [cv2.VideoCapture(i) for i in cams]

# Small delay to let cameras warm up
time.sleep(1)

for idx, cap in zip(cams, caps):
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Failed to capture from camera {idx}")
        continue

    filename = os.path.join("images", f"camera_{idx}.jpg")
    cv2.imwrite(filename, frame)
    print(f"✅ Saved image from camera {idx} -> {filename}")

# Release all cameras
for cap in caps:
    cap.release()

cv2.destroyAllWindows()