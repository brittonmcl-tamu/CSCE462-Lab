import spidev
import time
import math
import statistics

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((r[1] & 3) << 8) + r[2]

def sample_wave(n_samples=1000, delay=0.0005):
    data = []
    start_t = time.time()
    for _ in range(n_samples):
        val = read_adc(0)
        data.append(val)
        time.sleep(delay)
    end_t = time.time()
    return data, (end_t - start_t)

def analyze_wave(data, duration):
    if not data: return

    v_min = min(data)
    v_max = max(data)
    v_pp = v_max - v_min
    avg = sum(data) / len(data)

    if v_pp < 100:
        print(f"[Noise] V_pp: {v_pp} (Too small)")
        return

    crossings = 0
    for i in range(1, len(data)):
        if data[i-1] < avg and data[i] >= avg:
            crossings += 1

    freq = crossings / duration
    stdev = statistics.stdev(data)
    ratio = stdev / v_pp

    shape = "Unknown"
    if ratio > 0.42:
        shape = "SQUARE"
    elif ratio > 0.34:
        shape = "SINE"
    else:
        shape = "TRIANGLE"
    print(f"Detected: {shape} | Freq: {freq:.1f} Hz | Vpp: {((v_pp / 1023.0) * 3.3):.2f}")

try:
    print("Oscilloscope Started... (Press Ctrl+C to stop)")
    while True:
        samples, dur = sample_wave(1000, 0.0005)
        analyze_wave(samples, dur)
        time.sleep(0.5)

except KeyboardInterrupt:
    spi.close()
    print("\nScope Closed.")
