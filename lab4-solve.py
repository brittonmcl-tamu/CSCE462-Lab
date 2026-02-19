import board
import busio
import adafruit_mpu6050
import math
from time import sleep

# Initialize I2C and the sensor
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

steps = 0
# The 'threshold' is how hard a step needs to be to count.
# You will need to experiment with this number!
threshold = 2.0 
is_stepping = False

print("Pedometer Started! Start walking...")

try:
    while True:
        # 1. Get raw acceleration data
        x, y, z = mpu.acceleration
        
        # 2. Calculate the total acceleration magnitude
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        
        # 3. Remove standard gravity (~9.8 m/s^2)
        net_accel = abs(magnitude - 9.8)
        
        # ---> ADD THIS DEBUG LINE <---
        print(f"DEBUG: Net Accel = {net_accel:.2f}")
        
        # 4. Detect a peak (a step)
        if net_accel > threshold and not is_stepping:
            
        # 5. Reset when the foot is relatively still
        # We use a lower threshold here to prevent "double bouncing"
        elif net_accel < (threshold - 0.5):
            is_stepping = False
            
        # Poll the sensor frequently [cite: 304]
        sleep(0.05) 

except KeyboardInterrupt:
    print(f"\nFinal Step Count: {steps}")
