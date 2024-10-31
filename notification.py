import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from custom_messagebox import CustomMessageBox
import os

class NotificationManager:
    def __init__(self, root, asap=True):
        self.root = root
        self.asap = asap
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="db_medicine_cabinet"
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful for Notification.")
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.conn, self.cursor = None, None  # Set to None to avoid accidental usage if the connection fails

    def check_soon_to_expire(self):
        """Check for medicines that are expiring within 7 days and show notifications."""
        if not self.conn or not self.cursor:
            print("Database connection is not established.")
            return

        today = datetime.now().date()
        soon_date = today + timedelta(days=7)

        try:
            # Query the database for soon-to-expire medicines
            self.cursor.execute(
                "SELECT name, expiration_date FROM medicine_inventory WHERE expiration_date <= %s AND expiration_date >= %s ORDER BY expiration_date DESC", 
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

                self.log_notification(med_name, exp_date, days_left)

                if self.asap == True: 
                    self.log_notification(med_name, exp_date, days_left)
                else:
                    pass

                # Increment the notification count after the pop-up
                notification_count += 1

        except Error as e:
            print(f"Error while checking soon-to-expire medicines: {e}")

    def create_notification_popup(self, medicine_name, expiration_date, days_left, notification_count):
        """Create a notification popup with the notification count in the title."""
        try:
            CustomMessageBox(
                root=self.root,
                title=f"Notification ({notification_count})",
                message=f"The medicine '{medicine_name}' is expiring soon!\nExpiration Date: {expiration_date}\nDays left: {days_left}",
                color='red',
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
        except Exception as e:
            print(f"Error displaying notification popup: {e}")

    def log_notification(self, medicine_name, expiration_date, days_left):
        """Log the notification in the database only if it hasn't been logged yet and the medicine still exists."""
        if not self.conn or not self.cursor:
            print("Database connection is not established.")
            return

        notification_date = datetime.now().date()
        notification_time = datetime.now().time()  # Get the current time

        try:
            # Fetch the medicine_id based on the medicine name and expiration date
            self.cursor.execute(
                "SELECT id FROM medicine_inventory WHERE name = %s AND expiration_date = %s",
                (medicine_name, expiration_date)
            )
            result = self.cursor.fetchone()

            if result:
                medicine_id = result[0]  # Get the id (medicine_id)

                # Check if this notification already exists in the logs
                self.cursor.execute(
                    "SELECT COUNT(*) FROM notification_logs WHERE medicine_id = %s AND notification_date = %s",
                    (medicine_id, notification_date)
                )
                already_logged = self.cursor.fetchone()[0]

                if already_logged == 0:
                    # If not logged yet, insert the new log entry with notification_time
                    self.cursor.execute(
                        "INSERT INTO notification_logs (medicine_id, medicine_name, expiration_date, notification_date, notification_time, days_until_expiration) "
                        "VALUES (%s, %s, %s, %s, %s, %s)", 
                        (medicine_id, medicine_name, expiration_date, notification_date, notification_time, days_left)
                    )
                    self.conn.commit()
            else:
                print(f"Medicine '{medicine_name}' no longer exists in inventory.")

        except Error as e:
            print(f"Error logging notification for '{medicine_name}': {e}")

    def fetch_recent_notifications(self):
        """Fetch recent notifications from notification_logs ordered by the most recent notification date and time."""
        if not self.conn or not self.cursor:
            print("Database connection is not established.")
            return []

        try:
            # Sort by notification_date and potentially notification_time, in descending order to get most recent first
            self.cursor.execute(
                """
                SELECT medicine_name, expiration_date, notification_date, days_until_expiration
                FROM notification_logs
                ORDER BY notification_date DESC AND notification_time ASC
                """
            )
            notifications = self.cursor.fetchall()
            return notifications
        except Error as e:
            print(f"Error fetching recent notifications: {e}")
            return []

    def close(self):
        """Close the cursor and database connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("Database connection closed.")
        except Error as e:
            print(f"Error closing database connection: {e}")
