import board
import busio
import adafruit_mpu6050
import math
from time import time, sleep
from collections import deque

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

# Pedometer Variables
steps = 0
threshold = 0.8  # The lowered threshold optimized for the filter
is_stepping = False

# Filter & Cooldown Variables
last_step_time = 0
COOLDOWN = 0.3  # 300 milliseconds minimum between steps
WINDOW_SIZE = 5 # Average the last 5 sensor readings
accel_history = deque(maxlen=WINDOW_SIZE)

print("Terminal Pedometer Started! Start walking...")
print("Press Ctrl+C to stop and see the final count.\n")

try:
    while True:
        # Read raw sensor data
        x, y, z = mpu.acceleration
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        raw_net_accel = abs(magnitude - 9.8)

        # Apply the Moving Average Filter
        accel_history.append(raw_net_accel)
        
        # Calculate the smoothed average
        if len(accel_history) > 0:
            current_smoothed_accel = sum(accel_history) / len(accel_history)
        else:
            current_smoothed_accel = 0.0

        # Step Detection & Cooldown
        current_time = time()
        
        if current_smoothed_accel > threshold and not is_stepping and (current_time - last_step_time > COOLDOWN):
            steps += 1
            is_stepping = True
            last_step_time = current_time 
            
            # Print to the terminal the moment a step is registered
            print(f"Step Detected! Total Steps: {steps}")
            
        elif current_smoothed_accel < (threshold - 0.3): 
            # Reset the stepping flag once the acceleration drops
            is_stepping = False
            
        # Poll the sensor every 20 ms
        sleep(0.02) 

except KeyboardInterrupt:
    print(f"\Pedometer stopped. Final Step Count: {steps}")
