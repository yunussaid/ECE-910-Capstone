# motor/test_motor.py
from stepper import StepperMotor
from time import sleep

motor = StepperMotor(step_delay=0.00001)  # adjust delay for speed
num_revs = 18
steps_per_rev = 6400
num_steps = num_revs * steps_per_rev

try:
    print("Moving forward", num_revs, "revolutions...")
    motor.step(num_steps, direction=0)
    sleep(1)

    print("Moving backward", num_revs, "revolutions...")
    motor.step(num_steps, direction=1)

finally:
    motor.cleanup()
