import RPi.GPIO as GPIO
from time import sleep


# ████████████████████████████████████████████████
# ██████████████ DEFINE MOTOR CLASS ██████████████

LEFT = 0
RIGHT = 1
DIST_PER_REV = 49.87278  # 1 rev = 49.87278 mm
STEPS_PER_REV = 6400     

class Motor:
    def __init__(self, steps_per_rev = 6400, step_delay=0.0002, pul_pin=23, dir_pin=24, ena_pin=25):
        self.steps_per_rev = steps_per_rev # (manually configured on driver)
        self.step_delay = step_delay
        self.pul_pin, self.dir_pin, self.ena_pin = pul_pin, dir_pin, ena_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pul_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.ena_pin, GPIO.OUT)

        self.disable()

    def enable(self):
        GPIO.output(self.ena_pin, GPIO.LOW)

    def disable(self):
        GPIO.output(self.ena_pin, GPIO.HIGH)

    def step(self, steps, direction):
        GPIO.output(self.dir_pin, GPIO.LOW if direction == RIGHT else GPIO.HIGH)

        for _ in range(steps):
            GPIO.output(self.pul_pin, GPIO.HIGH)
            sleep(self.step_delay)
            GPIO.output(self.pul_pin, GPIO.LOW)
            sleep(self.step_delay)
    
    def move_left(self, dist_mm):
        if dist_mm < 0: self.move_right(-dist_mm)
        num_revs = dist_mm / DIST_PER_REV
        num_steps = round(num_revs * self.steps_per_rev)
        print(f"motor.py:\tMoving left {dist_mm} mm ({num_revs:.2f} revs) ({num_steps} steps) ...")
        self.step(num_steps, LEFT)
    
    def move_right(self, dist_mm):
        if dist_mm < 0: self.move_left(-dist_mm)
        num_revs = dist_mm / DIST_PER_REV
        num_steps = round(num_revs * self.steps_per_rev)
        print(f"motor.py:\tMoving right {dist_mm} mm ({num_revs:.2f} revs) ({num_steps} steps) ...")
        self.step(num_steps, RIGHT)

    def cleanup(self):
        self.disable()
        GPIO.cleanup()



# ██████████████████████████████████████████████
# ██████████████ TEST MOTOR CLASS ██████████████

def main():
    cassette_count = 2
    cassette_width_mm = 36
    
    motor = Motor(step_delay=0.0002) # Initializes motor and sets GPIO pins to LOW/Safe state
    
    # Guard Rail 1: Power On
    print("\n--- SAFETY CHECK ---")
    input("1. Switch ON the motor power supply, then press Enter to continue...")
    
    motor.enable()

    for _ in range(cassette_count):
        motor.move_right(cassette_width_mm)
        sleep(1)
    
    motor.move_left(cassette_width_mm * cassette_count)
    motor.disable()
    
    # Guard Rail 2: Power Off
    print("\n--- BATCH COMPLETE ---")
    input("2. Switch OFF the motor power supply, then press Enter to finish cleanup...")
    
    motor.cleanup()
    print("\nCleanup complete. Script exiting...")
    

if __name__=="__main__":
    main()