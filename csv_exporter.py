# csv_exporter.py

import os
import csv
import tkinter as tk
from tkinter import messagebox, filedialog
import mysql.connector
import ctypes
from datetime import datetime


def is_removable_drive(drive_letter):
    # Use ctypes to call the GetDriveTypeW function from kernel32.dll
    drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_letter + '\\')
    return drive_type == 2  # 2 indicates a removable drive

def get_flash_drive_path():
    drives = os.popen("wmic logicaldisk get caption").read().strip().splitlines()[1:]
    for drive in drives:
        drive = drive.strip()
        if is_removable_drive(drive):
            return drive  # Return the first detected USB drive
    return None  # No flash drive found

def export_to_csv():
    flash_drive_path = get_flash_drive_path()
    if not flash_drive_path:
        messagebox.showerror("Error", "Please insert a flash drive to extract.")
        return

    # Get the current date for the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"medicine_inventory_{current_date}.csv"
    file_path = os.path.join(flash_drive_path, file_name)

    # Connect to the database
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
        )
        cursor = conn.cursor()

        # Fetch all data from the medicine_inventory table
        query = "SELECT name, type, quantity, unit, date_stored, expiration_date FROM medicine_inventory"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Write data to CSV
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(["Name", "Type", "Quantity", "Unit", "Date Stored", "Expiration Date"])
            # Write data rows
            for row in rows:
                # Convert date objects to strings (handling NoneType)
                date_stored_str = row[4].strftime("%b %d, %Y") if row[4] else "N/A"
                expiration_date_str = row[5].strftime("%b %d, %Y") if row[5] else "N/A"
                writer.writerow([row[0], row[1], row[2], row[3], date_stored_str, expiration_date_str])
        
        # Inform the user that the file was saved successfully
        messagebox.showinfo("Success", f"CSV file has been created successfully at {file_path}!")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()