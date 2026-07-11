#!/usr/bin/env python3
import serial
import time

# Try common COM ports for the Pico
ports_to_try = ['COM3', 'COM4', 'COM5']

for port in ports_to_try:
    try:
        print(f"Trying {port}...")
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1)
        
        # Send Ctrl+C to stop any running code
        ser.write(b'\x03')
        time.sleep(0.2)
        
        # Send Ctrl+D to soft-reset and get to REPL
        ser.write(b'\x04')
        time.sleep(1)
        
        # Read any welcome message
        output = ser.read_all().decode('utf-8', errors='ignore')
        print(f"Port {port} opened. Output:\n{output}\n")
        
        # Now run the main2026.py script
        print("Running main2026.py...")
        ser.write(b'exec(open("main2026.py").read())\r\n')
        
        # Read output for 15 seconds (the script runs for about 0.5-1 sec max frames)
        output_lines = []
        start_time = time.time()
        while time.time() - start_time < 12:
            try:
                data = ser.read(256)
                if data:
                    output_lines.append(data.decode('utf-8', errors='ignore'))
            except:
                pass
            time.sleep(0.05)
        
        full_output = ''.join(output_lines)
        print("\n=== SCRIPT OUTPUT ===")
        print(full_output)
        print("=== END OUTPUT ===\n")
        
        ser.close()
        break
    except Exception as e:
        print(f"Failed on {port}: {e}")
        continue
