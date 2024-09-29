import os
import mysql.connector
import csv
from datetime import datetime
from tkinter import messagebox
import win32file
import win32con

# Define the missing constants manually
FSCTL_LOCK_VOLUME = 0x00090018
FSCTL_DISMOUNT_VOLUME = 0x00090020
IOCTL_STORAGE_EJECT_MEDIA = 0x002D4808

# Function to safely eject the flash drive using pywin32
def safely_eject_drive(drive_letter):
    try:
        # Open the volume to get the handle
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

        # Lock the volume for safe removal
        win32file.DeviceIoControl(handle, FSCTL_LOCK_VOLUME, None, None)
        # Dismount the volume
        win32file.DeviceIoControl(handle, FSCTL_DISMOUNT_VOLUME, None, None)
        # Eject the media
        win32file.DeviceIoControl(handle, IOCTL_STORAGE_EJECT_MEDIA, None, None)

        # Close the handle
        win32file.CloseHandle(handle)
        print(f"Flash drive {drive_letter}: safely ejected.")
    except Exception as e:
        print(f"Failed to eject flash drive: {e}")

# Function to get the flash drive path (your existing logic)
def get_flash_drive_path():
    # You will need to implement your logic to get the flash drive path.
    # Assuming you are using 'E:/' as an example flash drive path.
    return "E:/"

# Your original function for exporting CSV (untouched, just adding the ejection part)
def export_to_csv():
    flash_drive_path = get_flash_drive_path()
    if not flash_drive_path:
        messagebox.showerror("Error", "Please insert a flash drive to extract.")
        return

    current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"medicine_inventory_{current_date_time}.csv"
    file_path = os.path.join(flash_drive_path, file_name)

    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
        )
        cursor = conn.cursor()

        # Execute the query
        query = "SELECT name, type, quantity, unit, date_stored, expiration_date FROM medicine_inventory"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Write the data to a CSV file on the flash drive
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Type", "Quantity", "Unit", "Date Stored", "Expiration Date"])
            for row in rows:
                date_stored_str = row[4].strftime("%b %d, %Y") if row[4] else "N/A"
                expiration_date_str = row[5].strftime("%b %d, %Y") if row[5] else "N/A"
                writer.writerow([row[0], row[1], row[2], row[3], date_stored_str, expiration_date_str])

        messagebox.showinfo("Success", f"CSV file has been created successfully at {file_path}!")

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
