import time
import math
import RPi.GPIO as GPIO

# Pin for the button (from Lab 1)
BUTTON_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_user_input():
    print("\n--- Function Generator Settings ---")
    shape = input("Enter wave shape (square, triangle, sin): ").lower()
    freq = float(input("Enter frequency (Hz): "))
    max_v = float(input("Enter max voltage (0-3.3): "))
    return shape, freq, max_v

def run_generator():
    try:
        while True:
            print("Waiting for button press to start...")
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.1) # Idle State
            
            shape, freq, max_v = get_user_input()
            v_limit = (max_v / 3.3) * 4095
            
            print(f"Generating {shape} wave at {freq}Hz. Press Ctrl+C to stop.")
            
            # The Generation Loop
            start_time = time.time()
            try:
                while True:
                    # Check button again to stop (optional) or just use Ctrl+C
                    t = time.time() - start_time
                    
                    if shape == "sin":
                        # Lab formula: 2048 * (1 + 0.5 * sin(2*pi*f*t))
                        # Adjusted for user's max_v:
                        val = int((v_limit/2) * (1 + math.sin(2 * math.pi * freq * t)))
                        # print(f"DAC Value: {val}") # Debug instead of dac.raw_value
                        
                    elif shape == "triangle":
                        # Symmetric Triangle logic
                        # Period = 1/freq. 
                        # This math creates a rising/falling value based on time
                        period = 1 / freq
                        relative_t = t % period
                        if relative_t < (period / 2):
                            val = int((2 * v_limit / period) * relative_t)
                        else:
                            val = int(v_limit - (2 * v_limit / period) * (relative_t - period/2))
                    
                    # If DAC works later, you just add: dac.raw_value = val
                    time.sleep(0.001) # Small delay to prevent CPU lockup
                    
            except KeyboardInterrupt:
                print("\nStopped. Ready for new settings.")

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    run_generator()
