import cv2
import time
import os
import argparse
import sys


def print_usage():
    print("""
==================== Dual USB Camera Utility ====================

Usage:
  python cameras.py [OPTIONS]

Modes:
  --find
      Scan and list available camera indices.

  --mode live
      Show live feed from selected cameras.
      Controls:
        q  -> quit
        s  -> save snapshot from all cameras

  --mode snap
      Capture one image per camera and exit.

Options:
  --cams <idx1 idx2 ...>
      Camera indices to use (default: 0 1)

  --width <pixels>
      Frame width (default: 1280)

  --height <pixels>
      Frame height (default: 720)

Examples:
  Find cameras:
      python cameras.py --find

  Live feed with two cameras:
      python cameras.py --mode live --cams 1 2

  Take snapshots only:
      python cameras.py --mode snap --cams 1 2

===============================================================
""")


def find_cameras(max_index=10):
    """
    Scan camera indices and report which ones open successfully
    """
    print("🔍 Scanning for available cameras...")
    available = []

    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera found at index {i}")
                available.append(i)
            cap.release()

    if not available:
        print("❌ No cameras detected.")
    else:
        print(f"📷 Available camera indices: {available}")

    return available


def open_cameras(cam_indices, width=1280, height=720, warmup_sec=1.0):
    caps = []
    for i in cam_indices:
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print(f"❌ Could not open camera {i}")
            caps.append(None)
            continue

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        caps.append(cap)

    time.sleep(warmup_sec)
    return caps


def take_snapshots(cams, caps, img_dir):
    os.makedirs(img_dir, exist_ok=True)

    for idx, cap in zip(cams, caps):
        if cap is None:
            continue

        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"❌ Failed to capture from camera {idx}")
            continue

        filename = os.path.join(img_dir, f"camera_{idx}.jpg")
        cv2.imwrite(filename, frame)
        print(f"✅ Saved image from camera {idx} -> {filename}")


def live_feed(cams, caps):
    print("🎥 Live feed controls:")
    print("  q = quit")
    print("  s = save snapshot (both cameras)")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    while True:
        frames = []

        for idx, cap in zip(cams, caps):
            if cap is None:
                continue
            ret, frame = cap.read()
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
            if not ret or frame is None:
                continue

            cv2.putText(frame, f"Camera {idx}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            frames.append(frame)

        if not frames:
            print("❌ No frames received.")
            time.sleep(0.5)
            continue

        if len(frames) == 2:
            h = min(frames[0].shape[0], frames[1].shape[0])
            f0 = cv2.resize(frames[0], (int(frames[0].shape[1] * h / frames[0].shape[0]), h))
            f1 = cv2.resize(frames[1], (int(frames[1].shape[1] * h / frames[1].shape[0]), h))
            display = cv2.hconcat([f0, f1])
        else:
            display = frames[0]

        cv2.imshow("Dual Camera Live Feed", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            ts = int(time.time())
            for idx, cap in zip(cams, caps):
                if cap is None:
                    continue
                ret, frame = cap.read()
                if ret and frame is not None:
                    filename = os.path.join(img_dir, f"camera_{idx}_{ts}.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"✅ Saved snapshot -> {filename}")


def release_all(caps):
    for cap in caps:
        if cap is not None:
            cap.release()
    cv2.destroyAllWindows()


def main():

    # If no arguments were provided, print usage and exit
    if len(sys.argv) == 1:
        print_usage()
        return

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--mode", choices=["live", "snap"])
    parser.add_argument("--find", action="store_true")
    parser.add_argument("--cams", type=int, nargs="+")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--max_index", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.find:
        find_cameras(args.max_index)
        return

    caps = open_cameras(args.cams, args.width, args.height)

    try:
        if args.mode == "snap":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_dir = os.path.join(base_dir, "images")
            take_snapshots(args.cams, caps, img_dir)
        else:
            live_feed(args.cams, caps)
    finally:
        release_all(caps)


if __name__ == "__main__":
    main()

    # for i in range(5):    
    #     cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
    #     print("Camera", i, "Supported frame width × height:", cap.get(cv2.CAP_PROP_FRAME_WIDTH), "×", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    #     # Try printing input formats — this is a rough way:
    #     for j in range(0, 10):
    #         print("FOURCC", j, cap.get(cv2.CAP_PROP_FOURCC))

    #     cap.release()

