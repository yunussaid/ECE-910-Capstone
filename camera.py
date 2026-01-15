import os
import cv2
from datetime import datetime



# █████████████████████████████████████████████████
# ██████████████ DEFINE CAMERA CLASS ██████████████

class Camera:
    def __init__(self, idx=0, width=3264, height=2448):
        self.idx = idx
        self.width = width
        self.height = height
        print(f"camera.py:\tIntializing camera_{self.idx} ...")

        # Windows: cv2.CAP_MSMF is slow during initialization but minimal lag during runtime.
        # Windows: cv2.CAP_DSHOW is very quick to initalize but laggy during runtime.
        # Linux: cv2.CAP_V4L2 is the preferred backend
        # Auto: cv2.CAP_ANY lets OpenCV choose the best backend
        self.cap = cv2.VideoCapture(self.idx, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError(f"camera.py:\t__init__() could not open camera_{self.idx}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        actual_backend = f'cv2.{self.cap.getBackendName()}'
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"camera.py:\tIntialized camera_{self.idx} with {actual_backend} and {actual_width}x{actual_height}p res")

        self.autofocus()
        
    def autofocus(self):
        window_name=f"Camera_{self.idx} Autofocus"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, int(self.width/4), int(self.height/4))
        
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1) # Enable Autofocus before warm-up
        actual_auto_focus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        print(f"camera.py:\tAutofocusing camera_{self.idx} (AF={actual_auto_focus}) ...")

        # Flush frames to allow Autofocus to settle
        flush_frames = 200
        for i in range(flush_frames):
            ret, frame = self.cap.read()
            if ret:
                cv2.putText(frame, f"Autofocusing: Frame {i}/{flush_frames}", (100, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
                cv2.imshow(window_name, frame)
                cv2.waitKey(1)

        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) # Disable Autofocus to lock focus
        actual_auto_focus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        actual_focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        cv2.destroyWindow(window_name)
        for i in range(5): cv2.waitKey(1) # Increment event loop to ensure window closes
        print(f"camera.py:\tAutofocusing camera_{self.idx} complete. Focus locked at {actual_focus} (AF={actual_auto_focus})")

    def capture(self, img_dir, img_name=None):
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("camera.py:\tcapture() failed to capture frame")
        
        os.makedirs(img_dir, exist_ok=True)
        
        if img_name is None:
            ts = datetime.now().strftime("%Y-%m-%d-%H;%M;%S")
            img_name = f"camera_{self.idx}_{ts}.jpg"
        
        img_path = os.path.join(img_dir, img_name)
        cv2.imwrite(img_path, frame)
        print(f"camera.py:\tSaved {img_name} -> at -> {img_dir}")
        
        return frame, img_path

    def live(self, img_dir):
        window_name=f"Camera_{self.idx} Live Feed"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, int(self.width/4), int(self.height/4))
        
        while True:
            ok, frame = self.cap.read()
            if not ok or frame is None:
                continue

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('s'):
                _ = self.capture(img_dir)
        
        cv2.destroyWindow(window_name)
        for i in range(5): cv2.waitKey(1) # Increment event loop to ensure window closes

    def set_and_get_adjustable_specs(self, width=None, height=None, auto_focus=None, focus=None,
                                     brightness=None, auto_exposure=None, exposure=None):
        # 1. Set Resolution
        if width is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"camera.py:\tcamera_{self.idx} resolution is {actual_width}x{actual_height}p")

        # 2. Turn off Auto Focus to set it manually
        if auto_focus is not None:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, auto_focus)
            # self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        if focus is not None:
            self.cap.set(cv2.CAP_PROP_FOCUS, focus) # Value between 0-1024
            # self.cap.set(cv2.CAP_PROP_FOCUS, 255) # Value between 0-1024
        actual_auto_focus = int(self.cap.get(cv2.CAP_PROP_AUTOFOCUS))
        actual_focus = int(self.cap.get(cv2.CAP_PROP_FOCUS))
        print(f"camera.py:\tcamera_{self.idx} auto-focus is {actual_auto_focus}")
        print(f"camera.py:\tcamera_{self.idx} focus is {actual_focus}")

        # 3. Adjust Brightness
        if brightness is not None:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
            # self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
        actual_brightness = int(self.cap.get(cv2.CAP_PROP_BRIGHTNESS))
        print(f"camera.py:\tcamera_{self.idx} brightness is {actual_brightness}")

        # 4. Turn off Auto Exposure and set manually
        if auto_exposure is not None:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure)
            # self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # 1 is manual in some UVC drivers
        if exposure is not None:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            # self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)     # Logarithmic scale usually
        actual_auto_exposure = self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        actual_exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f"camera.py:\tcamera_{self.idx} auto-exposure is {actual_auto_exposure}")
        print(f"camera.py:\tcamera_{self.idx} exposure is {actual_exposure}")
        
        # 5. Live Feed to See
        self.live('test_images\live()')

    def scan_available_cameras(self, max_index=10):
        print("camera.py:\tScanning for available cameras...")
        available = []

        for i in range(max_index):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    available.append(i)
                cap.release()

        if not available:
            print("camera.py:\tNo cameras detected")
        else:
            print(f"camera.py:\tAvailable cameras -> {available}")

        return available

    def release(self):
        if self.cap:
            print(f"camera.py:\tReleasing camera_{self.idx} ...")
            self.cap.release()
            self.cap = None

    def __del__(self):
        try:
            self.release()
        except Exception:
            pass



# ███████████████████████████████████████████████
# ██████████████ TEST CAMERA CLASS ██████████████

def main():
    camera = Camera(1, 3264, 2448)              # idx=1 for Windows
    camera.capture('test_images\capture()')
    camera.live('test_images\live()')

if __name__=="__main__":
    main()