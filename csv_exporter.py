import os
import mysql.connector
import csv
from datetime import datetime
from custom_messagebox import *
import win32file
import win32con
import ctypes
import requests     

# Define constants for volume control
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

# Function to detect removable flash drives
def get_removable_flash_drives():
    drives = []
    drive_bits = win32file.GetLogicalDrives()
    for letter in range(26):  # Iterate over A-Z (0-25 represents letters A-Z)
        mask = 1 << letter
        if drive_bits & mask:
            drive_letter = f"{chr(65 + letter)}:/"
            drive_type = win32file.GetDriveType(drive_letter)
            
            # Check if the drive type is removable (like a flash drive)
            if drive_type == win32file.DRIVE_REMOVABLE:
                drives.append(drive_letter)
    
    return drives

# Function to get the path of a removable flash drive
def get_flash_drive_path():
    removable_drives = get_removable_flash_drives()
    if removable_drives:
        # If there's at least one removable drive, return the first one found
        return removable_drives[0]
    return None

def export_to_csv(root, table_name):
    from System import CustomMessageBox
    flash_drive_path = get_flash_drive_path()
    if not flash_drive_path:
        CustomMessageBox(
            root,
            title="Warning",
            color='red',
            message="Please insert a flash drive to extract.",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        return

    current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{table_name}_{current_date_time}.csv"  # Use table name in file name
    file_path = os.path.join(flash_drive_path, file_name)

    try:
        # Flask API endpoint to fetch data
        api_url = f"https://emc-san-mateo.com/api/get_table_data/{table_name}"

        # Request the data from Flask API
        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from the server. Status Code: {response.status_code}")

        # Parse the data from the response
        data = response.json()
        if not data or 'columns' not in data or 'rows' not in data:
            raise Exception("Invalid data format received from the server.")

        columns = data['columns']  # Column names
        rows = data['rows']        # Row data

        # Write the data to a CSV file on the flash drive
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columns)  # Write column headers
            writer.writerows(rows)    # Write all rows

        # Function to show the ejection confirmation after success message
        def show_eject_confirmation():
            def eject_yes_callback():
                drive_letter = flash_drive_path[0]  # Extract drive letter (e.g., 'E' from 'E:/')
                safely_eject_drive(drive_letter)
                CustomMessageBox(
                    root=root,
                    title="Success",
                    message=f"Flash Drive {drive_letter} safely ejected.",
                    ok_callback=success_message_box.destroy(),
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'okGrey_icon.png')
                )
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
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'ejectFlashdrive_icon.png'),
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

    except Exception as e:
        CustomMessageBox(
            root,
            title="Error",
            color='red',
            message=f"An error occurred: {e}",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        print('Error: ', e)
