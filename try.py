import serial
import time
import tkinter as tk
from tkinter import messagebox
import os

# Create a path to store the file in a 'door_status' folder within the current directory
file_path = os.path.join(os.getcwd(), "door_status", "door_status.txt")

# Ensure the folder exists before writing the file
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Write to the file
with open(file_path, "w") as file:
    file.write("Unlocked")

def load_data():
    try:
        with open(file_path, "r") as file:  # Use file_path here to load from the correct location
            return file.read().strip()  # Use strip() to remove any extra whitespace or newline
    except FileNotFoundError:
        return None

# Load the data
data = load_data()

# Use the data in a condition
if data == "Locked":
    print("1")
elif data == "Unlocked":
    print("0")
else:
    print("User not recognized.")
