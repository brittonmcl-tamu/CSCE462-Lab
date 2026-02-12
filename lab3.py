import spidev
import time

# Open SPI Bus 0, Device 0 (Connected to Pin 22/CE0) [cite: 58]
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    # 1. Start Bit: 1
    # 2. SGL/DIFF: 1 (Single Ended), D2, D1, D0: Channel bits
    # We construct the request byte based on the manual's protocol 
    if channel < 0 or channel > 7:
        return -1
    
    # This math creates the 3 bytes the Pi sends to the chip
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    
    # 3. Merge bits 8 & 9 with bits 0-7 to get the 10-bit result [cite: 67]
    result = ((r[1] & 3) << 8) + r[2]
    return result

try:
    print("Reading MCP3008 Channel 0...")
    while True:
        value = read_adc(0) # Reading from CH0 [cite: 34]
        voltage = (value / 1023.0) * 3.3
        print(f"Digital Value: {value} | Voltage: {voltage:.2f}V")
        time.sleep(0.5)
        
except KeyboardInterrupt:
    spi.close()
