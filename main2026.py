from machine import Pin, UART
from time import sleep_ms, ticks_us, ticks_diff

# The MAX485 RO pin is connected to the Pico's UART1 RX pin on GPIO 5.
# DMX uses 8-bit data, no parity, and 2 stop bits.
# DE/RE tied low so the module stays in receive mode.
dmx_receiver = UART(1, baudrate=250000, bits=8, parity=None, stop=2, rx=Pin(5))

# GPIO 2 for channel 1 trigger (falling edge)
# GPIO 3-17 for channels 2-16 triggers (rising edge)
trigger_pins = {
    1: Pin(2, Pin.OUT),   # Channel 1 (falling edge)
    2: Pin(3, Pin.OUT),   # Channel 2 (rising edge)
    3: Pin(4, Pin.OUT),   # Channel 3 (rising edge)
    4: Pin(6, Pin.OUT),   # Channel 4 (rising edge) - skipped GPIO 5 (UART RX)
    5: Pin(7, Pin.OUT),   # Channel 5 (rising edge)
    6: Pin(8, Pin.OUT),   # Channel 6 (rising edge)
    7: Pin(9, Pin.OUT),   # Channel 7 (rising edge)
    8: Pin(10, Pin.OUT),  # Channel 8 (rising edge)
    9: Pin(11, Pin.OUT),  # Channel 9 (rising edge)
    10: Pin(12, Pin.OUT), # Channel 10 (rising edge)
    11: Pin(13, Pin.OUT), # Channel 11 (rising edge)
    12: Pin(14, Pin.OUT), # Channel 12 (rising edge)
    13: Pin(15, Pin.OUT), # Channel 13 (rising edge)
    14: Pin(16, Pin.OUT), # Channel 14 (rising edge)
    15: Pin(17, Pin.OUT), # Channel 15 (rising edge)
    16: Pin(18, Pin.OUT), # Channel 16 (rising edge)
}

# Set all pins low initially
for pin in trigger_pins.values():
    pin.low()

# Track inter-byte gaps to detect DMX break
last_byte_time = ticks_us()
BREAK_THRESHOLD_US = 500  # DMX break is >100us gap; we use 500us to be safe

# 3-frame debouncing for 100% reliability (theater-grade)
frame_buffer = [
    [0] * 16,  # frame 1 - 16 channels
    [0] * 16,  # frame 2
    [0] * 16,  # frame 3
]
frame_index = 0

# Track previous state for each channel (for edge detection)
last_channel_state = [False] * 16  # 0=OFF (≤100), 1=ON (>100)

print("Starting DMX Receiver Mode (3-frame debounce, 16-channel trigger)...\r\n")

while True:
    byte_count = dmx_receiver.any()
    if byte_count > 0:
        data = dmx_receiver.read(byte_count)
        
        if data is not None and len(data) > 0:
            # Check for break by looking at first byte timing
            now = ticks_us()
            gap = ticks_diff(now, last_byte_time)
            
            # If we detect a break (large gap), the next data is a fresh frame
            if gap > BREAK_THRESHOLD_US and len(data) > 16:
                # data[0] is start code (should be 0x00 for standard DMX)
                # data[1:17] are channels 1-16
                
                # Validate start code (0x00 = standard DMX)
                if data[0] == 0x00:
                    # Store this frame in the circular buffer
                    frame_buffer[frame_index] = list(data[1:17])
                    frame_index = (frame_index + 1) % 3
                    
                    # Check if all 3 frames match (debouncing for reliability)
                    if frame_buffer[0] == frame_buffer[1] == frame_buffer[2]:
                        channels = frame_buffer[0]
                        
                        # Check each channel for edge transitions
                        for ch_num in range(1, 17):
                            ch_value = channels[ch_num - 1]  # channels[0] = ch1
                            ch_is_on = ch_value > 100
                            
                            if ch_num == 1:
                                # Channel 1: fire on FALLING edge (ON → OFF)
                                if not ch_is_on and last_channel_state[0]:
                                    trigger_pins[1].high()
                                    sleep_ms(250)
                                    trigger_pins[1].low()
                            else:
                                # Channels 2-16: fire on RISING edge (OFF → ON)
                                if ch_is_on and not last_channel_state[ch_num - 1]:
                                    trigger_pins[ch_num].high()
                                    sleep_ms(250)
                                    trigger_pins[ch_num].low()
                            
                            last_channel_state[ch_num - 1] = ch_is_on
                        
                        # Print first 5 channels for monitoring
                        print(f"DMX Ch1-5: {channels[0]} {channels[1]} {channels[2]} {channels[3]} {channels[4]}")
            
            last_byte_time = ticks_us()
    
    sleep_ms(10)