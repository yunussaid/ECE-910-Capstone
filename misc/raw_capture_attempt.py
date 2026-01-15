import cv2
import numpy as np
import tifffile

# --- CAMERA SETTINGS ---
WIDTH = 1280
HEIGHT = 720

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# # --- PART 1: Save one DNG image ---
# ret, raw_frame = cap.read()
# if ret:
#     # 1. Reshape the 1D byte array to 2D
#     # This assumes 8-bit raw data (1 byte per pixel)
#     raw_2d = raw_frame.reshape((HEIGHT, WIDTH))

#     # 2. Save as DNG using tifffile
#     # We use Photometric.CFA to tell software it's a Bayer raw image
#     tifffile.imwrite(
#         "temp_image.dng",
#         raw_2d,
#         photometric='CFA',
#         metadata={'CFAPattern': [0, 1, 1, 2]} # Example: RGGB pattern
#     )
#     print("Successfully saved 'captured_image.dng' using tifffile")
# else:
#     print("Error: Failed to capture frame.")


ret, raw_frame = cap.read()
if ret:
    # 1. Calculate actual dimensions based on the buffer size (Assuming 2 bytes per pixel)
    actual_total_pixels = raw_frame.size // 2
    # If HEIGHT is 720, then WIDTH = total / 720
    calc_width = actual_total_pixels // HEIGHT
    
    print(f"Buffer size: {raw_frame.size}. Interpreted resolution: {calc_width}x{HEIGHT}")

    # 2. Reshape into (Height, Width, 2 bytes) or (Height, Width) 16-bit
    # We view the raw bytes as uint16 to satisfy the "2 bytes per pixel" requirement
    raw_16bit = raw_frame.view(dtype=np.uint16).reshape((HEIGHT, calc_width))

    # 3. Save as DNG
    tifffile.imwrite(
        "raw_attempt.dng",
        raw_16bit,
        photometric='minisblack', # YUY2 is better stored as grayscale or converted
        metadata={'Description': 'Raw UVC YUY2 Capture'}
    )
    print("Successfully saved 'raw_attempt.dng'")

# cap.release()



# --- PART 2: Live raw feed ---
print("Starting live feed. Press 'q' to quit.")
try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        cv2.imshow("Live Raw Bytes", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
