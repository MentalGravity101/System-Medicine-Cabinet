import requests
from datetime import datetime
import os
import tkinter as tk

class NotificationManager:
    def __init__(self, root, asap=False):
        self.root = root
        self.api_url = "https://emc-san-mateo.com/api"  # Base URL for Flask API
        self.asap = asap
        self.message_box = None

    def check_soon_to_expire(self):
        try:
            response = requests.get(f"{self.api_url}/soon_to_expire")
            response.raise_for_status()  # Raise an error for non-200 responses
            medicines = response.json()

            for notification_count, med in enumerate(medicines):
                med_name, med_type, dosage, exp_date = med
                days_left = (datetime.strptime(exp_date, "%Y-%m-%d").date() - datetime.now().date()).days

                # Log the notification via API
                self.log_notification({
                    "medicine_id": notification_count,  # Replace with actual ID from the API if available
                    "medicine_name": med_name,
                    "med_type": med_type,
                    "dosage": dosage,
                    "expiration_date": exp_date,
                    "days_left": days_left,
                })

                if self.asap:
                    self.create_notification_popup(med_name, med_type, dosage, exp_date, days_left, notification_count)
        except requests.RequestException as e:
            print(f"Error fetching data from API: {e}")

    def create_notification_popup(self, medicine_name, med_type, dosage, expiration_date, days_left, notification_count):
        try:
            from System import CustomMessageBox
            self.message_box = CustomMessageBox(
                root=self.root,
                title=f'Notification ({notification_count})',
                message=(
                    f'Expiring medicine:\n'
                    f'{medicine_name} - {med_type} - {dosage}\n'
                    f'Expiration Date: {expiration_date}\n'
                    f'Days left: {days_left}'
                ),
                color='red',
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
        except Exception as e:
            print(f"Error displaying notification popup: {e}")

    def log_notification(self, data):
        try:
            response = requests.post(f"{self.api_url}/log_notification", json=data)
            response.raise_for_status()  # Raise an error for non-200 responses
            print("Notification logged successfully.")
        except requests.RequestException as e:
            print(f"Error logging notification: {e}")
