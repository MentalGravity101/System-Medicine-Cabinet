import os
import mysql.connector
import csv
from datetime import datetime
from tkinter import messagebox
import win32file
import win32con
import ctypes
from custom_messagebox import *

# Define constants
FSCTL_LOCK_VOLUME = 0x00090018
FSCTL_DISMOUNT_VOLUME = 0x00090020
IOCTL_STORAGE_EJECT_MEDIA = 0x002D4808

# Flush file buffers to ensure all data is written to the flash drive
def flush_volume_buffers(drive_letter):
    try:
        volume_path = f"\\\\.\\{drive_letter}:"
        handle = win32file.CreateFile(
            volume_path,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            0,
            None
        )
        win32file.FlushFileBuffers(handle)
        win32file.CloseHandle(handle)
        print(f"File buffers flushed for drive {drive_letter}:.")
    except Exception as e:
        print(f"Failed to flush file buffers for drive {drive_letter}: {e}")

# Function to safely eject the flash drive
def safely_eject_drive(drive_letter):
    try:
        volume_path = f"\\\\.\\{drive_letter}:"
        handle = win32file.CreateFile(
            volume_path,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            0,
            None
        )

        # Flush the file system buffers before ejecting
        flush_volume_buffers(drive_letter)

        # Lock and dismount the volume
        win32file.DeviceIoControl(handle, FSCTL_LOCK_VOLUME, None, None)
        win32file.DeviceIoControl(handle, FSCTL_DISMOUNT_VOLUME, None, None)

        # Eject the media
        win32file.DeviceIoControl(handle, IOCTL_STORAGE_EJECT_MEDIA, None, None)
        win32file.CloseHandle(handle)
        
        print(f"Flash drive {drive_letter}: safely ejected.")
    except Exception as e:
        print(f"Failed to eject flash drive: {e}")

# Function to get the flash drive path
def get_flash_drive_path():
    return "E:/"

# CSV export function
def export_to_csv(table_name):
    flash_drive_path = get_flash_drive_path()
    if not flash_drive_path:
        messagebox.showerror("Error", "Please insert a flash drive to extract.")
        return

    current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{table_name}_{current_date_time}.csv"  # Use table name in file name
    file_path = os.path.join(flash_drive_path, file_name)

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
        )
        cursor = conn.cursor()

        # Use the passed table_name to query the correct table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Get column names dynamically from the cursor description
        column_names = [i[0] for i in cursor.description]

        # Write the data to a CSV file on the flash drive
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)  # Write column headers
            for row in rows:
                writer.writerow(row)

        messagebox.showinfo("Success", f"CSV file has been created successfully at {file_path}!")

        # Ask the user if they want to eject the flash drive
        eject_choice = messagebox.askyesno("Eject Flash Drive", "Do you want to safely eject the flash drive?")

        if eject_choice:
            # Safely eject the flash drive after successful export
            drive_letter = flash_drive_path[0]  # Extract drive letter (e.g., 'E' from 'E:/')
            safely_eject_drive(drive_letter)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
