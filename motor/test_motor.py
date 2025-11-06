# motor/test_motor.py
from stepper import StepperMotor
import time

motor = StepperMotor(step_delay=0.001)  # adjust delay for speed

try:
    print("Moving forward 200 steps...")
    motor.step(200, direction=1)
    time.sleep(1)

    print("Moving backward 200 steps...")
    motor.step(200, direction=0)

finally:
    motor.cleanup()
