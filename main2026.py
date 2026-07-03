from machine import Pin, UART, PWM
from time import sleep_ms
import _thread

#Set up GPIOs
pin1 = Pin(1, Pin.OUT)
pin2 = Pin(2, Pin.OUT)

# 1. Set up UART0 strictly for RECEIVING (rx)
# We completely omit the tx pin to keep it clean.
# Baud rate must be exactly 250,000 with 2 stop bits for standard DMX.
dmx_receiver = UART(0, baudrate=250000, bits=8, parity=None, stop=2, rx=Pin(1))

# 2. Create a clean storage buffer for the 512 channels
# DMX packets have 513 bytes (1 start code byte + 512 channel values)
dmx_universe = bytearray(513)

print("Starting DMX Receiver Mode...\r\n")

while True:
    # Check if a DMX packet is waiting in the buffer
    # This line forces the Pico to wait until a complete, 
    # valid packet arrives before it bothers wasting 
    # processing power to check the numbers.
    if dmx_receiver.any() >= 513:
        
        # Read the exact 513-byte frame into our universe buffer
        dmx_receiver.readinto(dmx_universe)
        
        # Check the mandatory DMX Start Code (the very first byte must be 0)
        if dmx_universe[0] == 0x00:
            
            # --- CHOOSE YOUR CHANNELS TO READ HERE ---
            # Index 1 = DMX Channel 1, Index 2 = DMX Channel 2, etc.
            channel_1 = dmx_universe[1]
            channel_2 = dmx_universe[2]
            channel_3 = dmx_universe[3]
            
            # Print the feedback out to your VS Code terminal
            print(f"DMX Data Received -> CH1: {channel_1} | CH2: {channel_2} | CH3: {channel_3}\r\n")
            
    # Small sleep to keep Core 0 stable and prevent freezing
    sleep_ms(10)


# counter = 10
# lock = _thread.allocate_lock()

# def core1():
#   global counter

#   while True:
#     sleep_ms(900)
#     lock.acquire()
#     if counter <= 0:
#       lock.release()
#       break
#     print("core1 is running " + str(counter))
#     counter -= 1
#     lock.release()

# _thread.start_new_thread(core1, ())

# while True:
#     sleep_ms(800)
#     lock.acquire()
#     if counter <= 0:
#         lock.release()
#         break
#     print("core0 is running " + str(counter))
#     counter -= 1
#     lock.release()




  