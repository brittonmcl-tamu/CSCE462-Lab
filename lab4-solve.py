import board
import busio
import adafruit_mpu6050
import math
from time import sleep
import time # Make sure this is at the top

# Add this above your while loop:
last_step_time = 0 
cooldown_period = 0.3 # 0.3 seconds

# Initialize I2C and the sensor
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

history = [0, 0, 0]

steps = 0
# The 'threshold' is how hard a step needs to be to count.
# You will need to experiment with this number!
threshold = 2.0 
is_stepping = False

print("Pedometer Started! Start walking...")

try:
    while True:
        # 1. Get raw acceleration data
        current_time = time.time()        
        
        x, y, z = mpu.acceleration
        
        # 2. Calculate the total acceleration magnitude
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        
        # 3. Remove standard gravity (~9.8 m/s^2)
        net_accel = abs(magnitude - 9.8)
        
        # DEBUG LINE - Uncomment to see raw numbers
        # print(f"DEBUG: Net Accel = {net_accel:.2f}")

        history.append(net_accel) # Add new reading
        history.pop(0)            # Remove oldest reading
        
        smoothed_accel = sum(history) / 3.0
        
        # 4. Detect a peak (a step)
        if net_accel > threshold and not is_stepping and (current_time - last_step_time) > cooldown_period:
            steps += 1
            is_stepping = True
            last_step_time = current_time # Reset the cooldown timer
            print(f"Step Count: {steps}")
            
        # 5. Reset when the foot is relatively still
        elif smoothed_accel < (threshold - 0.5):
            is_stepping = False
            
        # Poll the sensor frequently
        sleep(0.05) 

except KeyboardInterrupt:
    print(f"\nFinal Step Count: {steps}")
