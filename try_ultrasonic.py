import serial
import time
import tkinter as tk
from tkinter import messagebox

# Configure the serial port (make sure this matches your Arduino port)
SERIAL_PORT = 'COM5'  # Update this to your Arduino's port
BAUD_RATE = 9600

# Set up serial connection
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)  # Allow time for the connection to establish

def check_object_presence():
    arduino.write(b'R')  # Send request for range
    response = arduino.readline().decode().strip()  # Read Arduino response
    if response == "DETECTED":
        on_object_detected()  # Call the function if object is detected
    else:
        print("No object detected within 1 inch")

def on_object_detected():
    # This function will be called when the object is within 1 inch
    messagebox.showinfo("Alert", "Object detected within 1 inch!")

# Set up the Tkinter interface
root = tk.Tk()
root.title("Ultrasonic Sensor Check")

check_button = tk.Button(root, text="Check for Object", command=check_object_presence)
check_button.pack(pady=20)

root.mainloop()

# Close the serial connection when done
arduino.close()