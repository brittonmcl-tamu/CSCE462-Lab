import time
import math
import RPi.GPIO as GPIO
import board
import busio
import adafruit_mcp4725

BUTTON_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    dac = adafruit_mcp4725.MCP4725(i2c)
    print("SUCCESS: MCP4725 DAC detected.")
except Exception as e:
    print(f"WARNING: DAC not found ({e}). Running in SIMULATION MODE.")
    dac = None

def get_user_input():
    print("\n--- Function Generator Settings ---")
    shape = input("Enter wave shape (square, triangle, sin): ").lower()
    freq = float(input("Enter frequency (Hz): "))
    max_v = float(input("Enter max voltage (0-3.3): "))
    return shape, freq, max_v

def run_generator():
    try:
        while True:
            print("\nPress the button...")
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.1) 
            
            print("Button Pressed!")
            shape, freq, max_v = get_user_input()
            v_limit = (max_v / 3.3) * 4095
            
            print(f"Generating {shape} wave at {freq}Hz. Press Ctrl+C to stop.")
            
            start_time = time.time()
            while True:
                t = time.time() - start_time
                val = 0
                
                if shape == "sin":
                    val = int((v_limit/2) * (1 + math.sin(2 * math.pi * freq * t)))
                
                elif shape == "square":
                    val = int(v_limit) if (t * freq) % 1 < 0.5 else 0
                    
                elif shape == "triangle":
                    period = 1 / freq
                    relative_t = t % period
                    if relative_t < (period / 2):
                        val = int((2 * v_limit / period) * relative_t)
                    else:
                        val = int(v_limit - (2 * v_limit / period) * (relative_t - period/2))
                
                if dac:
                    dac.raw_value = val
                else:
                    if int(t * 10) % 5 == 0: 
                         print(f"Simulated DAC Value: {val}")

                time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nExiting Program...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    run_generator()
