from machine import Pin, UART
from time import sleep_ms, ticks_us, ticks_diff, ticks_ms
import _thread

# ============================================================================
# DMX RECEIVER & TRIGGER CONTROL FOR SQUIB BOX (Raspberry Pi Pico)
# ============================================================================
# Receives DMX on UART1 (GPIO5 RX) via MAX485 transceiver
# Channel 1: Level control (HIGH when > 100, LOW when ≤ 100)
# Channels 2-16: Rising-edge triggered 250ms pulses

# --- UART Configuration ---
# MAX485 RO (Receiver Output) → Pico GPIO5 (UART1 RX)
# MAX485 DE/RE tied LOW for receive-only mode
dmx_receiver = UART(1, baudrate=250000, bits=8, parity=None, stop=2, rx=Pin(5))

# --- GPIO Outputs ---
# Channel 1: GPIO 2 (level control)
# Channels 2-16: GPIO 3-4, 6-18 (rising-edge pulses)
trigger_pins = {
    1:  Pin(2,  Pin.OUT),
    2:  Pin(3,  Pin.OUT),
    3:  Pin(4,  Pin.OUT),
    4:  Pin(6,  Pin.OUT),
    5:  Pin(7,  Pin.OUT),
    6:  Pin(8,  Pin.OUT),
    7:  Pin(9,  Pin.OUT),
    8:  Pin(10, Pin.OUT),
    9:  Pin(11, Pin.OUT),
    10: Pin(12, Pin.OUT),
    11: Pin(13, Pin.OUT),
    12: Pin(14, Pin.OUT),
    13: Pin(15, Pin.OUT),
    14: Pin(16, Pin.OUT),
    15: Pin(17, Pin.OUT),
    16: Pin(18, Pin.OUT),
}
for pin in trigger_pins.values():
    pin.low()

# DMX activity LED (GPIO 0)
# Blinks to indicate active DMX connection
dmx_led = Pin(0, Pin.OUT)
dmx_led.low()
dmx_led_blink_time = 0
dmx_last_activity = 0  # Start at 0 (triggers idle/heartbeat mode)

# --- Core 1: Pulse Runner (250ms pulse on rising edge) ---
pending_triggers = []
queue_lock = _thread.allocate_lock()

def core1_runner():
    from time import sleep_ms
    while True:
        with queue_lock:
            if pending_triggers:
                ch_num = pending_triggers.pop(0)
            else:
                ch_num = None
        
        if ch_num:
            pin = trigger_pins[ch_num]
            pin.high()
            print(f"Ch{ch_num} FIRE (250ms pulse)")
            sleep_ms(250)
            pin.low()
            print(f"Ch{ch_num} RELEASE")
        else:
            sleep_ms(10)

def queue_trigger(ch_num):
    with queue_lock:
        pending_triggers.append(ch_num)

# Start Core 1
_thread.start_new_thread(core1_runner, ())

# --- Main DMX Receiver Loop ---
NUM_FRAMES = 3
ch_history = [[0] * NUM_FRAMES for _ in range(16)]  # 16 channels × 3 samples
frame_slot = 0  # Circular buffer index
last_state = [False] * 16  # Track previous on/off state per channel
frame_count = 0

rx_buf = bytearray(1024)
rx_index = 0

print(">>> RUNNING dmx_receiver.py (STANDARD DMX512, OFFSET +1) <<<\r\n")
print("Starting DMX Receiver (3-frame debounce, 16-channel trigger, dual-core)...\r\n")

while True:
    # Blink LED to show DMX activity
    # Fast blink (100ms on/off) when receiving data, OFF when idle
    current_ms = ticks_ms()
    time_since_activity = current_ms - dmx_last_activity if dmx_last_activity > 0 else 10000
    
    if time_since_activity < 1000:  # Active (received data in last 1 second)
        # Fast blink when active
        if (current_ms // 100) % 2 == 0:
            dmx_led.high()
        else:
            dmx_led.low()
    else:
        # LED off when no DMX data
        dmx_led.low()
    
    n = dmx_receiver.any()

    if n > 0:
        dmx_last_activity = ticks_ms()  # Update last activity timestamp
        data = dmx_receiver.read(n)
        if data:
            rx_buf.extend(data)
            
            # Search for frame by finding non-zero data, then backtrack to find the 0x00 start code before it
            while len(rx_buf) >= 17:  # Need 0x00 + 16 channels
                # Find first non-zero byte (indicates start of real channel data)
                first_nonzero = -1
                for i in range(len(rx_buf)):
                    if rx_buf[i] != 0x00:
                        first_nonzero = i
                        break
                
                if first_nonzero == -1:
                    # No non-zero data found yet. Discard half the buffer and wait for more.
                    if len(rx_buf) > 100:
                        rx_buf = rx_buf[50:]
                    else:
                        break
                    continue
                
                if first_nonzero < 1:
                    # Non-zero is at position 0 (no start code before it) - skip and keep looking
                    rx_buf = rx_buf[1:]
                    continue
                
                # Backtrack to find the 0x00 start code (should be at first_nonzero - 1)
                frame_start = first_nonzero - 1
                
                # Verify we have enough data: frame_start (0x00) + 16 channels = 17 bytes total
                if frame_start + 17 > len(rx_buf):
                    # Not enough data yet - wait for more bytes to arrive
                    break
                

                
                # Store this frame's channels from frame_start+1 onwards (right after the 0x00 start code)
                # Extract into a temporary list first to avoid boundary issues
                frame_data = []
                try:
                    for ch in range(16):
                        frame_data.append(rx_buf[frame_start + 1 + ch])
                except IndexError:
                    # Safety: if we can't extract, skip this frame and move on
                    rx_buf = rx_buf[frame_start + 1:]
                    continue
                
                # Now store the extracted data
                for ch in range(16):
                    ch_history[ch][frame_slot] = frame_data[ch]
                    
                    frame_count += 1
                    frame_slot = (frame_slot + 1) % NUM_FRAMES
                    
                    # Process debounce every 3 frames
                    if frame_count % 3 == 0:
                        for ch_num in range(1, 17):
                            ch = ch_num - 1
                            vals = ch_history[ch]
                            all_on  = all(v > 100 for v in vals)
                            all_off = all(v <= 100 for v in vals)
                            
                            if ch_num == 1:
                                # Channel 1: Level control (continuous HIGH/LOW, NOT a pulse)
                                # > 100: GPIO HIGH (stays on)
                                # <= 100: GPIO LOW (stays off)
                                if all_on and not last_state[ch]:
                                    trigger_pins[1].high()
                                    print(f">>> Ch1 ON (vals: {vals})")
                                    last_state[ch] = True
                                elif all_off and last_state[ch]:
                                    trigger_pins[1].low()
                                    print(f">>> Ch1 OFF (vals: {vals})")
                                    last_state[ch] = False
                            else:
                                # Channels 2-16: Rising edge → 250ms pulse
                                if all_on and not last_state[ch]:
                                    queue_trigger(ch_num)
                                    print(f">>> Ch{ch_num} QUEUED PULSE (vals: {vals})")
                                    last_state[ch] = True
                                elif all_off:
                                    last_state[ch] = False
                    
                    # Discard consumed frame (from frame_start onwards for 17 bytes: marker + 16 channels)
                    rx_buf = rx_buf[frame_start + 17:]
                else:
                    # Not enough data yet, break and wait for more
                    break
