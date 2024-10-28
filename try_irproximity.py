import tkinter as tk
from tkinter import messagebox
import serial
import time

# Set up the serial connection (adjust COM port and baud rate as needed)
ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)  # Allow some time for the serial connection to initialize

def check_sensors():
    ser.flushInput()  # Clear any old data in the serial buffer
    time.sleep(0.1)  # Brief delay to ensure data is ready
    
    if ser.in_waiting > 0:  # Check if there's data to read
        data = ser.readline().decode('utf-8').strip()
        if data:
            try:
                sensor1, sensor2 = map(int, data.split(","))
                if sensor1 == 0 and sensor2 == 0:  # Both sensors detect an object
                    messagebox.showinfo("Result", "Both sensors detected an object!")
                else:
                    messagebox.showwarning("Result", "One or both sensors did not detect an object.")
            except ValueError:
                messagebox.showerror("Error", "Invalid data received from sensors.")
    else:
        messagebox.showerror("Error", "No data received from Arduino.")

# Tkinter GUI setup
root = tk.Tk()
root.title("IR Sensor Check")

# Button to check sensors only when clicked
check_button = tk.Button(root, text="Check Sensors", command=check_sensors)
check_button.pack(pady=20)

root.mainloop()

# Close the serial connection on exit
ser.close()
