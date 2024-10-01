import mysql.connector
from datetime import datetime, timedelta
from tkinter import Toplevel, Label, Button
from custom_messagebox import CustomMessageBox
import os

class NotificationManager:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.cursor = self.conn.cursor()

    def check_soon_to_expire(self):
        """Check for medicines that are expiring within 7 days and show notifications."""
        today = datetime.now().date()
        soon_date = today + timedelta(days=7)

        # Query the database for soon-to-expire medicines
        self.cursor.execute(
            "SELECT name, expiration_date FROM medicine_inventory WHERE expiration_date <= %s AND expiration_date >= %s", 
            (soon_date, today)
        )
        soon_to_expire_meds = self.cursor.fetchall()

        for med in soon_to_expire_meds:
            med_name, exp_date = med
            days_left = (exp_date - today).days

            # Show a notification pop-up
            self.create_notification_popup(med_name, exp_date, days_left)

            # Log the notification to the notification_logs table
            self.log_notification(med_name, exp_date, days_left)

    def create_notification_popup(self, medicine_name, expiration_date, days_left):
        CustomMessageBox(root=self.root, 
                         title="Notification Alert", 
                         message=f"The medicine '{medicine_name}' is expiring soon!\nExpiration Date: {expiration_date}\nDays left: {days_left}",
                         color='red',
                         icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'))

    def log_notification(self, medicine_name, expiration_date, days_left):
        """Log the notification in the database."""
        notification_date = datetime.now().date()
        self.cursor.execute(
            "INSERT INTO notification_logs (medicine_name, expiration_date, notification_date, days_until_expiration) "
            "VALUES (%s, %s, %s, %s)", 
            (medicine_name, expiration_date, notification_date, days_left)
        )
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()