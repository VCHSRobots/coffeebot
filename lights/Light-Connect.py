import serial
import time

try:
    ser = serial.Serial('COM3', 115200, timeout=1)
    print("Connected to COM3")

    while True:
        command = input("Enter a color (red, green, blue, clear) or 'exit' to quit: ").strip().lower()
        
        if command == 'exit':
            break

        if command in ['red', 'green', 'blue', 'clear']:
            try:
                # Clear input buffer
                ser.reset_input_buffer()

                command = command + "\n"
                print(f"Sending command: {command}")
                ser.write(command.encode())
                
                # Wait a bit for the response
                time.sleep(0.1)

                # Read all available responses
                while True:
                    if ser.in_waiting:
                        response = ser.readline().decode('utf-8').strip()
                        if response:
                            print(f"Received response: {response}")
                        else:
                            print("Empty response received")
                    else:
                        break
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