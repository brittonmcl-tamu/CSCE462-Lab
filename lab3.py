import spidev
import time
import math
import statistics

# --- SETUP ---
spi = spidev.SpiDev()
spi.open(0, 0) # Connected to CE0 (Pin 24)
spi.max_speed_hz = 1350000

def read_adc(channel):
    # Standard MCP3008 Read
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((r[1] & 3) << 8) + r[2]

def sample_wave(n_samples=1000, delay=0.0005):
    # Added 'delay' parameter. Default 0.0005 is good for 10Hz-100Hz.
    data = []
    start_t = time.time()
    for _ in range(n_samples):
        val = read_adc(0)
        data.append(val)
        time.sleep(delay) # <--- THIS IS THE CRITICAL ADDITION
    end_t = time.time()
    return data, (end_t - start_t)

def analyze_wave(data, duration):
    if not data: return

    # 1. Calculate Stats
    v_min = min(data)
    v_max = max(data)
    v_pp = v_max - v_min # Peak-to-Peak
    avg = sum(data) / len(data)

    # Noise Filter: If signal is too small, it's just noise
    if v_pp < 100:
        print(f"[Noise] V_pp: {v_pp} (Too small)")
        return

    # 2. Calculate Frequency (Zero-Crossing Method)
    crossings = 0
    # We look for when the signal crosses the 'average' line
    for i in range(1, len(data)):
        # Rising Edge: Previous was below avg, Current is above
        if data[i-1] < avg and data[i] >= avg:
            crossings += 1

    freq = crossings / duration

    # 3. Recognize Shape (Standard Deviation Method)
    # Square waves have HIGH StdDev (values are far from center)
    # Triangle waves have LOW StdDev (values are clustered)
    stdev = statistics.stdev(data)
    ratio = stdev / v_pp

    shape = "Unknown"
    # Theoretical Ratios: Square (~0.5), Sine (~0.35), Triangle (~0.29)
    if ratio > 0.42:
        shape = "SQUARE"
    elif ratio > 0.34:
        shape = "SINE"
    else:
        shape = "TRIANGLE"
    # print(f"DEBUG RATIO: {ratio:.3f} | Vpp: {v_pp}")
    print(f"Detected: {shape} | Freq: {freq:.1f} Hz | Vpp: {((v_pp / 1023.0) * 3.3):.2f}")

# --- MAIN LOOP ---
try:
    print("Oscilloscope Started... (Press Ctrl+C to stop)")
    while True:
        # 1. Grab 500 points really fast
        samples, dur = sample_wave(1000, 0.0005)

        # 2. Analyze them
        analyze_wave(samples, dur)

        # 3. Pause briefly so text is readable
        time.sleep(0.5)

except KeyboardInterrupt:
    spi.close()
    print("\nScope Closed.")
