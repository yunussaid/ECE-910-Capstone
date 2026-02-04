import os
import time
import tkinter as tk

import cv2
from PIL import Image, ImageTk

from motor import Motor
from camera import Camera

CASSETTE_PITCH_MM = 36.0
MAX_CASSETTES = 30

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("LFA Batch Analyzer")

        self.motor = Motor()
        self.camera = None

        self.state = None
        self.preview_job = None

        self.running_batch = False
        self.batch_dir = None
        self.captured_paths = []
        self.tk_images = []

        self.preview_label = tk.Label(root)
        self.preview_label.pack(padx=10, pady=10)

        # Create Frames for all states
        self.frame_instr = tk.Frame(root, padx=20, pady=20)
        self.frame_cal = tk.Frame(root, padx=10, pady=10)
        self.frame_batch = tk.Frame(root, padx=10, pady=10)
        self.frame_done = tk.Frame(root, padx=10, pady=10)

        # Build UIs
        self._build_instructions_ui()
        self._build_calibration_ui()
        self._build_batch_ui()
        self._build_done_ui()

        # Start with Instructions state
        self.set_state("instructions")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- UI BUILD ----------------

    def _build_instructions_ui(self):
        tk.Label(self.frame_instr, text="Process Instructions", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))

        instructions = [
            "Described below are the 4 stages of the LFA Batch Analysis process:",
            "1. Instructions (current): Ensure the LFA tray is loaded with cassettes. Read all instructions carefully.",
            "2. Calibration: Manually center the first cassette in the camera frame. Switch ON the motor power supply and continue to autofocus camera.",
            "3. Batch Analysis: Input the number of cassettes in the batch. Monitor the system as it automatically moves, captures and returns to start position.",
            "4. Review: View and verify all captured images at the end of the run. Choose whether to recalibrate, run another batch or exit. Please ensure that motor power is switched OFF before exiting the application.",
            "",
            "Note: Once you click Continue, the camera will do it's initial auto-focus. Please ensure no manual movement occurs during this time."
        ]

        for text in instructions:
            tk.Label(self.frame_instr, text=text, font=("Arial", 11), wraplength=500, justify="left").pack(anchor="w", pady=2)

        btn_frame = tk.Frame(self.frame_instr, pady=20)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Continue", width=16, command=self.init_camera_and_proceed).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Exit", width=16, command=self.on_close).pack(side="left", padx=5)

    def _build_calibration_ui(self):
        tk.Label(self.frame_cal, text="Calibration Steps", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(self.frame_cal, text="1) Slowly and manually position the motor with cassette 01 centered between the black lines.",
                 wraplength=500, justify="left").grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))
        tk.Label(self.frame_cal, text="2) Switch ON the motor's power supply.",
                 wraplength=500, justify="left").grid(row=2, column=0, columnspan=2, sticky="w")
        tk.Label(self.frame_cal, text="3) When you click Continue, the camera will auto-focus again. Please ensure no manual movement occurs during this time.",
                 wraplength=500, justify="left").grid(row=3, column=0, columnspan=2, sticky="w")

        tk.Button(self.frame_cal, text="Continue", width=16, command=self.autofocus_and_proceed).grid(
            row=4, column=0, pady=(14, 0), sticky="w"
        )
        tk.Button(self.frame_cal, text="Exit", width=16, command=self.on_close).grid(
            row=4, column=1, pady=(14, 0), sticky="e"
        )

    def _build_batch_ui(self):
        tk.Label(self.frame_batch, text="Batch Analysis", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")

        tk.Label(self.frame_batch, text="Enter number of cassettes (1-30):").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.n_var = tk.StringVar(value="30")
        self.n_entry = tk.Entry(self.frame_batch, textvariable=self.n_var, width=8)
        self.n_entry.grid(row=1, column=1, sticky="w", pady=(10, 0))

        self.start_btn = tk.Button(self.frame_batch, text="Start", width=16, command=self.start_batch)
        self.start_btn.grid(row=1, column=2, sticky="e", pady=(10, 0))

        self.status_var = tk.StringVar(value="")
        tk.Label(self.frame_batch, textvariable=self.status_var).grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.last_img_label = tk.Label(self.frame_batch)
        self.last_img_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        tk.Button(self.frame_batch, text="Back to Calibration", width=20, command=lambda: self.set_state("calibration")).grid(
            row=4, column=0, columnspan=3, pady=(10, 0)
        )

    def _build_done_ui(self):
        tk.Label(self.frame_done, text="Review & Verify", font=("Arial", 14, "bold")).pack(anchor="w")

        self.done_msg = tk.StringVar(value="")
        tk.Label(self.frame_done, textvariable=self.done_msg, wraplength=500, justify="left").pack(anchor="w", pady=(6, 10))

        self.thumb_frame = tk.Frame(self.frame_done)
        self.thumb_frame.pack()

        btns = tk.Frame(self.frame_done, pady=10)
        btns.pack(fill="x")

        tk.Button(btns, text="Back to Calibration", width=18, command=lambda: self.set_state("calibration")).pack(side="left", padx=5)
        tk.Button(btns, text="Run Another Batch", width=18, command=lambda: self.set_state("batch")).pack(side="left", padx=5)
        tk.Button(btns, text="Exit", width=18, command=self.on_close).pack(side="left", padx=5)

    # ---------------- HARDWARE INIT ----------------

    def init_camera_and_proceed(self):
        """Initializes camera only when the user is ready to proceed."""
        if self.camera is None:
            self.camera = Camera()
        self.set_state("calibration")

    def autofocus_and_proceed(self):
        if self.camera:
            self.camera.autofocus()
        self.set_state("batch")

    # ---------------- STATE ----------------

    def set_state(self, state):
        self.state = state
        self.frame_instr.pack_forget()
        self.frame_cal.pack_forget()
        self.frame_batch.pack_forget()
        self.frame_done.pack_forget()

        if state == "instructions":
            self.frame_instr.pack(fill="both", expand=True)
            self._stop_preview(clear=True)
        elif state == "calibration":
            self.running_batch = False
            self.status_var.set("")
            if self.motor: self.motor.disable()
            self.frame_cal.pack(fill="x", padx=10, pady=5)
            self._start_preview()
        elif state == "batch":
            self.running_batch = False
            self.status_var.set("")
            self.last_img_label.configure(image="")
            self.frame_batch.pack(fill="x", padx=10, pady=5)
            self._stop_preview(clear=True)
        elif state == "done":
            self.frame_done.pack(fill="both", expand=True, padx=10, pady=5)
            self._stop_preview(clear=True)

    # ---------------- PREVIEW (CALIBRATION ONLY) ----------------

    def _start_preview(self):
        if self.preview_job is None:
            self._update_preview()

    def _stop_preview(self, clear=False):
        if self.preview_job is not None:
            try:
                self.root.after_cancel(self.preview_job)
            except Exception:
                pass
            self.preview_job = None

        if clear:
            self.preview_label.configure(image="")
            self.preview_label.image = None

    def _update_preview(self):
        if self.state != "calibration" or self.camera is None:
            self.preview_job = None
            return

        ok, frame = self.camera.cap.read()
        if ok and frame is not None:
            h, w = frame.shape[:2]
            w_crop_factor=0.3
            margin_pct = (1.0 - w_crop_factor) / 2      # 0.35 margin on each side.
            x_left = int(w * margin_pct)
            x_right = int(w * (1.0 - margin_pct))
            cv2.line(frame, (x_left, 0), (x_left, h), (0, 0, 0), 15)
            cv2.line(frame, (x_right, 0), (x_right, h), (0, 0, 0), 15)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).resize((600, 450))
            tk_img = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=tk_img)
            self.preview_label.image = tk_img

        self.preview_job = self.root.after(30, self._update_preview)

    # ---------------- BATCH ----------------

    def start_batch(self):
        if self.running_batch:
            return

        try:
            n = int(self.n_var.get().strip())
        except Exception:
            n = 0

        if n < 1:
            self.status_var.set("Enter a valid number (1-30).")
            return
        if n > MAX_CASSETTES:
            n = MAX_CASSETTES
            self.n_var.set(str(n))

        self.running_batch = True
        self.start_btn.config(state="disabled")
        self.n_entry.config(state="disabled")

        ts = time.strftime("%Y-%m-%d_%H:%M:%S")
        self.batch_dir = os.path.join(os.path.expanduser("~"), "Desktop", "batch_images", f"batch_{ts}")
        os.makedirs(self.batch_dir, exist_ok=True)

        self.captured_paths = []
        self.tk_images = []
        self.status_var.set(f"Capturing {n} images...")

        if self.motor: self.motor.enable()
        self._batch_step(i=0, n=n)

    def _batch_step(self, i, n):
        if not self.running_batch or self.camera is None:
            return

        img_name = f"cassette_{i+1:02d}.jpg"
        w_crop_factor=0.3
        frame, img_path = self.camera.capture(self.batch_dir, img_name=img_name, w_crop_factor=w_crop_factor)

        self.captured_paths.append(img_path)
        self._show_last_image(img_path, w_crop_factor)
        self.status_var.set(f"Captured {i+1}/{n}: {img_name}")
        self.root.update_idletasks()

        if i == n - 1:
            total_back = (n - 1) * CASSETTE_PITCH_MM
            if total_back > 0 and self.motor:
                self.motor.move_left(total_back)
                self.motor.disable()

            self.running_batch = False
            self.start_btn.config(state="normal")
            self.n_entry.config(state="normal")
            self._show_done(n, w_crop_factor=w_crop_factor)
            return

        if self.motor: self.motor.move_right(CASSETTE_PITCH_MM)
        self.root.after(200, lambda: self._batch_step(i + 1, n))

    def _show_last_image(self, path, w_crop_factor=1):
        try:
            img = Image.open(path)
            img.thumbnail((600*w_crop_factor, 450))
            tk_img = ImageTk.PhotoImage(img)
            self.last_img_label.configure(image=tk_img)
            self.last_img_label.image = tk_img
        except Exception:
            pass

    # ---------------- DONE ----------------

    def _show_done(self, n, w_crop_factor=1):
        self.done_msg.set(
            f"Batch analysis completed for {n} cassettes. Next steps:\n"
            "1. Switch OFF the motor power now if you don't plan to run another batch.\n"
            "2. View and verify the captured images. These images are also saved at: ~/Desktop/batch_images.\n"
            "3. Choose whether to recalibrate, run another batch or exit."
        )
        for w in self.thumb_frame.winfo_children():
            w.destroy()
        self.tk_images = []

        cols = 10
        for idx, path in enumerate(self.captured_paths):
            try:
                img = Image.open(path)
                img.thumbnail((160*w_crop_factor, 120))
                tk_img = ImageTk.PhotoImage(img)
                self.tk_images.append(tk_img)
                lbl = tk.Label(self.thumb_frame, image=tk_img)
                lbl.grid(row=idx // cols, column=idx % cols, padx=4, pady=4)
            except Exception:
                pass

        self.set_state("done")

    # ---------------- CLEANUP ----------------

    def on_close(self):
        try:
            self.running_batch = False
            self._stop_preview(clear=True)
            if self.camera: self.camera.release()
            if self.motor: self.motor.cleanup()
        except Exception:
            pass
        self.root.destroy()

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()