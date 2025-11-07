# motor/stepper.py
import RPi.GPIO as GPIO
from time import sleep

class StepperMotor:
    def __init__(self, pul_pin=23, dir_pin=24, ena_pin=25, step_delay=0.00001):
        self.pul_pin = pul_pin
        self.dir_pin = dir_pin
        self.ena_pin = ena_pin
        self.step_delay = step_delay

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pul_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.ena_pin, GPIO.OUT)

        GPIO.output(self.ena_pin, GPIO.LOW)  # enable driver

    def step(self, steps, direction=1):
        """Move the motor a given number of steps."""
        GPIO.output(self.dir_pin, GPIO.HIGH if direction == 1 else GPIO.LOW)

        for _ in range(steps):
            GPIO.output(self.pul_pin, GPIO.HIGH)
            sleep(self.step_delay)
            GPIO.output(self.pul_pin, GPIO.LOW)
            sleep(self.step_delay)

    def cleanup(self):
        GPIO.cleanup()
