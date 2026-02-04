# LFA Batch Analyzer Code Base
A Raspberry Pi 5-based system for automated Lateral Flow Assay (LFA) image capture and batch analysis.

## Setup & Usage
1. Ensure your virtual environment is active:
```Bash
source venv/bin/activate
```

2. Install the needed dependencies:
```Bash
pip install -r requirements.txt
```

3. Launch the LFA batch analyzer application with:
```Bash
python app.py
```

4. Power procedures:
- Launch the application first to initialize GPIO pins to a safe state.
- Switch ON the motor power supply only when prompted in the Instructions or Calibration screens.
- Switch OFF the power supply after the batch is complete to prevent motor overheating.

## File & Directory Descriptions
| File / Directory | Description |
|------------------|-------------|
| **`app.py`** | Main entry point. Launches the GUI application and manages the workflow (Instructions → Calibration → Batch → Review). |
| **`camera.py`** | Manages the OpenCV camera stream, autofocus, and image saving. Run ```python camera.py``` to test the camera. |
| **`motor.py`** | Handles GPIO logic for the stepper motor (Enable/Disable, Direction, Step control). Run ```python motor.py``` to move the motor back and forth and verify hardware wiring. |
| **`test_images/`** | Directory used for temporary storage during standalone hardware tests. ***Note:*** Created only if ```camera.py``` is run directly. |
| **`requirements.txt`** | Lists required Python libraries (e.g., opencv-python, Pillow, rpi-lgpio). |
| **`.gitignore`** | Prevents unnecessary files (e.g., \_\_pycache\_\_, .venv, test_images/) from being tracked in version control. |

##
> ***Additional Notes:***
> - **Calibration:** Slow manual centering of the first cassette is required before starting a batch.
> - **Storage:** Captured batches are saved to ~/Desktop/batch_images/ for easy access.
> - **Power:** Please ensure that you follow the power ON/OFF instructions in the GUI applicaton ```app.py``` & ```motor.py``` for safe usage of the motor without overheating.
