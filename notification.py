import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import os
import tkinter as tk
from tkinter import ttk
import requests

class NotificationManager:
    def __init__(self, root, asap=False):
        self.root = root
        self.api_url = "https://emc-san-mateo.com/api"
        self.asap = asap

    def check_soon_to_expire(self):
        response = requests.get(f"{self.api_url}/soon_to_expire")
        if response.status_code == 200:
            medicines = response.json()
            for notification_count, med in enumerate(medicines):
                med_name, med_type, dosage, exp_date = med
                days_left = (datetime.strptime(exp_date, "%Y-%m-%d").date() - datetime.now().date()).days

                self.log_notification({
                    "medicine_id": notification_count,  # Replace with actual ID if available from API
                    "medicine_name": med_name,
                    "med_type": med_type,
                    "dosage": dosage,
                    "expiration_date": exp_date,
                    "days_left": days_left,
                })
            if self.asap == True:
                self.create_notification_popup(med_name, med_type, dosage, exp_date, days_left, notification_count)

    def create_notification_popup(self, medicine_name, med_type, dosage, expiration_date, days_left, notification_count):
        # Custom logic for pop-up
        print(f"Notification {notification_count}: {medicine_name} expiring in {days_left} days.")
        from System import CustomMessageBox
        message_box = CustomMessageBox(
            root=self.root,
            title=f'Notification ({notification_count})',
            message=f'Expiring medicine:\n{medicine_name} - {med_type} - {dosage}\nexpiring in {expiration_date}\nDays left: {days_left}',
            color='red',
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )

    def log_notification(self, data):
        response = requests.post(f"{self.api_url}/log_notification", json=data)
        if response.status_code == 200:
            print("Notification logged successfully.")
        else:
            print(f"Error logging notification: {response.json().get('error')}")