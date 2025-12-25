import os
import cv2
from datetime import datetime



# █████████████████████████████████████████████████
# ██████████████ DEFINE CAMERA CLASS ██████████████

class Camera:
    def __init__(self, idx=0, width=1280, height=720):
        self.idx = idx
        self.width = width
        self.height = height
        print(f"camera.py: Intializing camera_{self.idx} ...")

        # Windows: cv2.CAP_MSMF is slow during initialization but minimal lag during runtime.
        # Windows: cv2.CAP_DSHOW is very quick to initalize but laggy during runtime.
        # Linux: cv2.CAP_V4L2 is the preferred backend
        # Auto: cv2.CAP_ANY lets OpenCV choose the best backend
        self.cap = cv2.VideoCapture(self.idx, cv2.CAP_ANY)
        if not self.cap.isOpened():
            raise RuntimeError(f"camera.py: __init__() could not open camera_{self.idx}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        actual_backend = f'cv2.{self.cap.getBackendName()}'
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"camera.py: Intialized camera_{self.idx} with {actual_backend} and {actual_width}x{actual_height}p res")

    def capture(self, img_dir, img_name=None):
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("camera.py: capture() failed to capture frame")
        
        os.makedirs(img_dir, exist_ok=True)
        
        if img_name is None:
            ts = datetime.now().strftime("%Y-%m-%d-%H;%M;%S")
            img_name = f"camera_{self.idx}_{ts}.jpg"
        
        img_path = os.path.join(img_dir, img_name)
        print(f"camera.py: img_path is {img_path}")
        cv2.imwrite(img_path, frame)
        print(f"camera.py: Saved {img_name} -> at -> {img_dir}")
        
        return frame

    def live(self, img_dir):
        while True:
            ok, frame = self.cap.read()
            if not ok or frame is None:
                continue

            window_name=f"Camera_{self.idx} Live Feed"
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('s'):
                _ = self.capture(img_dir)
        
        cv2.destroyWindow(window_name)

    def scan_available_cameras(max_index=10):
        print("camera.py: Scanning for available cameras...")
        available = []

        for i in range(max_index):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    available.append(i)
                cap.release()

        if not available:
            print("camera.py: No cameras detected")
        else:
            print(f"camera.py: Available cameras -> {available}")

        return available

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def __del__(self):
        try:
            print(f"camera.py: Releasing camera_{self.idx} ...")
            self.release()
        except Exception:
            pass



# ███████████████████████████████████████████████
# ██████████████ TEST CAMERA CLASS ██████████████

def main():
    # idx 0 for cv2.CAP_MSMF, 1 for cv2.CAP_DSHOW, 1 for cv2.CAP_DSHOW
    camera = Camera(0, 1280, 720)
    camera.capture('test_images\capture()')
    camera.live('test_images\live()')

if __name__=="__main__":
    main()