import mysql.connector
from datetime import datetime, timedelta
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

        # Sort the results by expiration date (ascending order, soonest expiration first)
        sorted_meds = sorted(soon_to_expire_meds, key=lambda x: x[1])

        # Initialize notification count starting from 0
        notification_count = 0

        # If there are soon-to-expire medicines, process notifications
        for med in sorted_meds:
            med_name, exp_date = med
            days_left = (exp_date - today).days

            # Show a notification pop-up with the count in the title
            self.create_notification_popup(med_name, exp_date, days_left, notification_count)

            # Log the notification to the notification_logs table
            self.log_notification(med_name, exp_date, days_left)

            # Increment the notification count after the pop-up
            notification_count += 1

    def create_notification_popup(self, medicine_name, expiration_date, days_left, notification_count):
        """Create a notification popup with the notification count in the title."""
        CustomMessageBox(
            root=self.root,
            title=f"Notification ({notification_count})",
            message=f"The medicine '{medicine_name}' is expiring soon!\nExpiration Date: {expiration_date}\nDays left: {days_left}",
            color='red',
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )

    def log_notification(self, medicine_name, expiration_date, days_left):
        """Log the notification in the database only if it hasn't been logged yet."""
        notification_date = datetime.now().date()

        # Check if this notification already exists in the logs
        self.cursor.execute(
            "SELECT COUNT(*) FROM notification_logs WHERE medicine_name = %s AND expiration_date = %s AND notification_date = %s",
            (medicine_name, expiration_date, notification_date)
        )
        already_logged = self.cursor.fetchone()[0]

        if already_logged == 0:
            # If not logged yet, insert the new log entry
            self.cursor.execute(
                "INSERT INTO notification_logs (medicine_name, expiration_date, notification_date, days_until_expiration) "
                "VALUES (%s, %s, %s, %s)", 
                (medicine_name, expiration_date, notification_date, days_left)
            )
            self.conn.commit()
        else:
            print(f"Notification for {medicine_name} (expiring on {expiration_date}) has already been logged today.")

    def close(self):
        """Close the database connection."""
        self.conn.close()

