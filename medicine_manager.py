import mysql.connector
import qrcode
import os
from tkinter import messagebox
from datetime import datetime, date

class MedicineDeposit:
    def __init__(self, name, type_, quantity, unit, expiration_date):
        self.name = name
        self.type = type_
        self.quantity = quantity
        self.unit = unit
        self.expiration_date = expiration_date  # Expecting the expiration_date to be a string

    def validate_inputs(self):
        """Checks if the expiration date is not the current date."""
        current_date = date.today()
        
        if not self.name or not self.type or not self.quantity or not self.unit or not self.expiration_date:
            messagebox.showerror("Input Error", "Please fill out all fields.")
            return False
        
        # Convert expiration_date from string to a date object for comparison
        try:
            exp_date = datetime.strptime(self.expiration_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid expiration date (YYYY-MM-DD).")
            return False
        
        # Compare current date with expiration date
        if exp_date == current_date:
            messagebox.showerror("Invalid Expiration Date", "Expiration date cannot be the current date!")
            return False
        
        return True

    def generate_qr_code(self):
        try:
            # Create the QR code content
            qr_data = f"Medicine: {self.name}, Expiration Date: {self.expiration_date}"
            qr_img = qrcode.make(qr_data)
            
            # Save the QR code image in the current directory
            qr_filename = f"{self.name}_{self.expiration_date.replace('/', '-')}.png"
            qr_filepath = os.path.join(os.path.dirname(__file__), 'qr_codes', qr_filename)  # Save in 'qr_codes' folder
            os.makedirs(os.path.dirname(qr_filepath), exist_ok=True)
            qr_img.save(qr_filepath)
            
            return qr_filepath
        except Exception as e:
            messagebox.showerror("QR Code Error", f"Failed to generate QR code: {str(e)}")
            return None

    def save_to_database(self, qr_filepath):
        try:
            # Open a connection to the MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Make sure the username is correct
                password="",  # Ensure the password is correct
                database="db_medicine_cabinet"  # Ensure the correct database name is used
            )
            cursor = conn.cursor()

            # Check if the connection is successful
            if conn.is_connected():
                print("Connected to database")
            
            # Read the QR code file as binary
            with open(qr_filepath, "rb") as qr_file:
                qr_code_data = qr_file.read()

            # SQL query to insert data into the medicine_inventory table
            insert_query = """
            INSERT INTO medicine_inventory (name, type, quantity, unit, expiration_date, qr_code)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (self.name, self.type, self.quantity, self.unit, self.expiration_date, qr_code_data))
            
            # Commit the transaction to save changes
            conn.commit()

            messagebox.showinfo("Success", "Medicine data and QR code saved successfully.")
            return True

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            return False

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def process_medicine(self):
        # Validate inputs
        if not self.validate_inputs():
            return False
        
        # Generate the QR code
        qr_filepath = self.generate_qr_code()
        if qr_filepath is None:
            return False
        
        # Save the medicine data and QR code to the database
        return self.save_to_database(qr_filepath)
