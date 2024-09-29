import os
import mysql.connector
import csv
from datetime import datetime
from custom_messagebox import *
import win32file
import win32con
import ctypes

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
        print(f"File buffers flushed for drive {drive_letter}:")
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
def export_to_csv(root, table_name):
    flash_drive_path = get_flash_drive_path()
    if not flash_drive_path:
        CustomMessageBox(
            root, 
            title="Error", 
            message="Please insert a flash drive to extract.", 
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey.png')
        )
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

        # Function to show the ejection confirmation after success message
        def show_eject_confirmation():
            def eject_yes_callback():
                drive_letter = flash_drive_path[0]  # Extract drive letter (e.g., 'E' from 'E:/')
                safely_eject_drive(drive_letter)
                return

            def eject_no_callback():
                print("Flash drive not ejected.")

            # Close the success message before showing the eject confirmation
            if success_message_box:
                success_message_box.destroy()

            CustomMessageBox(
                root,
                title="Eject Flash Drive",
                message="Do you want to safely eject the flash drive?",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'ejectFlashdrive_icon.png'),  # Add your icon path
                yes_callback=eject_yes_callback,
                no_callback=eject_no_callback
            )

        # Show the success message first, then the eject confirmation
        success_message_box = CustomMessageBox(
            root, 
            title="Success", 
            message=f"CSV file has been created successfully at \n{file_path}!",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'okGrey_icon.png'),
            ok_callback=show_eject_confirmation  # Trigger ejection confirmation after clicking "OK"
        )

    except mysql.connector.Error as err:
        CustomMessageBox(
            root, 
            title="Database Error", 
            message=f"Error: {err}",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
    except Exception as e:
        CustomMessageBox(
            root, 
            title="Error", 
            message=f"An error occurred: {e}",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
    finally:
        if conn:
            cursor.close()
            conn.close()
