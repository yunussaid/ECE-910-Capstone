import os
import time
import tkinter as tk
from tkinter import simpledialog

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
        self.camera = Camera(0, 1280, 720)

        self.state = None
        self.running_batch = False
        self.batch_dir = None
        self.captured_paths = []
        self.tk_images = []

        self.preview_label = tk.Label(root)
        self.preview_label.pack(padx=10, pady=10)

        self.frame_cal = tk.Frame(root, padx=10, pady=10)
        self.frame_batch = tk.Frame(root, padx=10, pady=10)
        self.frame_done = tk.Frame(root, padx=10, pady=10)

        self._build_calibration_ui()
        self._build_batch_ui()
        self._build_done_ui()

        self.set_state("calibration")
        self._update_preview()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- UI BUILD ----------------

    def _build_calibration_ui(self):
        tk.Label(self.frame_cal, text="Calibration", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(self.frame_cal, text="1) Location: manually position cassette 01 centered in the frame.").grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        tk.Label(self.frame_cal, text="2) Focus: adjust focus until cassette 01 is sharp.").grid(row=2, column=0, columnspan=4, sticky="w")

        tk.Button(self.frame_cal, text="Disable Motor", width=14, command=self.motor.disable).grid(row=3, column=0, pady=(10, 0))
        tk.Button(self.frame_cal, text="Enable Motor", width=14, command=self.motor.enable).grid(row=3, column=1, pady=(10, 0))
        tk.Button(self.frame_cal, text="Jog Left", width=14, command=lambda: self._jog("l")).grid(row=3, column=2, pady=(10, 0))
        tk.Button(self.frame_cal, text="Jog Right", width=14, command=lambda: self._jog("r")).grid(row=3, column=3, pady=(10, 0))

        tk.Button(self.frame_cal, text="Done", width=14, command=lambda: self.set_state("batch")).grid(row=4, column=0, columnspan=4, pady=(14, 0))

    def _build_batch_ui(self):
        tk.Label(self.frame_batch, text="Batch Analysis", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")

        tk.Label(self.frame_batch, text="Number of cassettes (1-30):").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.n_var = tk.StringVar(value="30")
        self.n_entry = tk.Entry(self.frame_batch, textvariable=self.n_var, width=8)
        self.n_entry.grid(row=1, column=1, sticky="w", pady=(10, 0))

        self.start_btn = tk.Button(self.frame_batch, text="Start", width=14, command=self.start_batch)
        self.start_btn.grid(row=1, column=2, sticky="e", pady=(10, 0))

        self.status_var = tk.StringVar(value="")
        tk.Label(self.frame_batch, textvariable=self.status_var).grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.last_img_label = tk.Label(self.frame_batch)
        self.last_img_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        tk.Button(self.frame_batch, text="Back to Calibration", width=18, command=lambda: self.set_state("calibration")).grid(row=4, column=0, columnspan=3, pady=(10, 0))

    def _build_done_ui(self):
        tk.Label(self.frame_done, text="Completed", font=("Arial", 14, "bold")).pack(anchor="w")

        self.done_msg = tk.StringVar(value="")
        tk.Label(self.frame_done, textvariable=self.done_msg).pack(anchor="w", pady=(6, 10))

        self.thumb_frame = tk.Frame(self.frame_done)
        self.thumb_frame.pack()

        btns = tk.Frame(self.frame_done, pady=10)
        btns.pack(fill="x")

        tk.Button(btns, text="Back to Calibration", width=18, command=lambda: self.set_state("calibration")).pack(side="left", padx=5)
        tk.Button(btns, text="Run Another Batch", width=18, command=lambda: self.set_state("batch")).pack(side="left", padx=5)

    # ---------------- STATE ----------------

    def set_state(self, state):
        self.state = state
        self.frame_cal.pack_forget()
        self.frame_batch.pack_forget()
        self.frame_done.pack_forget()

        if state == "calibration":
            self.running_batch = False
            self.status_var.set("")
            self.frame_cal.pack(fill="x", padx=10, pady=5)
        elif state == "batch":
            self.running_batch = False
            self.status_var.set("")
            self.frame_batch.pack(fill="x", padx=10, pady=5)
        elif state == "done":
            self.frame_done.pack(fill="both", expand=True, padx=10, pady=5)

    # ---------------- PREVIEW ----------------

    def _update_preview(self):
        ok, frame = self.camera.cap.read()
        if ok and frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((640, 360))
            tk_img = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=tk_img)
            self.preview_label.image = tk_img

        self.root.after(30, self._update_preview)

    # ---------------- CALIBRATION ACTIONS ----------------

    def _jog(self, direction):
        dist = simpledialog.askfloat("Jog", "Distance (mm):", initialvalue=5.0, minvalue=0.0)
        if dist is None:
            return
        if direction == "l":
            self.motor.move_left(dist)
        else:
            self.motor.move_right(dist)

    # ---------------- BATCH ACTIONS ----------------

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

        ts = time.strftime("%Y-%m-%d-%H;%M;%S")
        self.batch_dir = os.path.join("batch_images", f"batch_{ts}")

        self.captured_paths = []
        self.tk_images = []
        self.status_var.set(f"Capturing {n} images...")

        self.motor.enable()
        self._batch_step(i=0, n=n)

    def _batch_step(self, i, n):
        if not self.running_batch:
            return
        
        img_name = f"cassette_{i+1:02d}.jpg"
        frame, img_path = self.camera.capture(self.batch_dir, img_name)

        self.captured_paths.append(img_path)
        self._show_last_image(img_path)
        self.status_var.set(f"Captured {i+1}/{n}: {img_name}")

        if i == n - 1:
            total_back = (n - 1) * CASSETTE_PITCH_MM
            if total_back > 0:
                self.motor.move_left(total_back)
            self.running_batch = False
            self.start_btn.config(state="normal")
            self.n_entry.config(state="normal")
            self._show_done(n)
            return

        self.motor.move_right(CASSETTE_PITCH_MM)
        self.root.after(200, lambda: self._batch_step(i + 1, n))

    def _show_last_image(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((640, 360))
            tk_img = ImageTk.PhotoImage(img)
            self.last_img_label.configure(image=tk_img)
            self.last_img_label.image = tk_img
        except Exception:
            pass

    # ---------------- DONE STATE ----------------

    def _show_done(self, n):
        self.done_msg.set(f"Batch analysis completed for {n} cassettes.")
        for w in self.thumb_frame.winfo_children():
            w.destroy()
        self.tk_images = []

        cols = 6
        for idx, path in enumerate(self.captured_paths):
            try:
                img = Image.open(path)
                img.thumbnail((160, 120))
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
            self.camera.release()
            self.motor.cleanup()
        except Exception:
            pass
        self.root.destroy()

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
