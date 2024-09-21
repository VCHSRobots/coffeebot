import serial
import time

try:
    ser = serial.Serial('COM5', 115200, timeout=1)
    print("Connected to COM5")

    while True:
        command = input("Enter a color (red, green, blue, random, clear) or 'exit' to quit: ").strip().lower()
        
        if command == 'exit':
            break

        if command in ['red', 'green', 'blue', 'random', 'clear']:
            try:
                print(f"Sending command: {command}")
                ser.write(command.encode())
                
                # Wait a bit and then read any response
                time.sleep(0.5)
                response = ser.readline().decode('utf-8').strip()
                if response:
                    print(f"Received response: {response}")
                else:
                    print("No response received")

            except serial.SerialException as e:
                print(f"An error occurred while communicating: {e}")
        else:
            print("Invalid command. Please enter red, green, blue, random, clear, or exit.")

except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial connection closed")