import qrcode
from PIL import Image, ImageTk
from datetime import datetime
import os
import mysql.connector
import tkinter as tk
from tkinter import messagebox

class MedicineDeposit:
    def __init__(self, name, type_, quantity, unit, expiration_date, db_connection, qr_code_label):
        self.name = name
        self.type = type_
        self.quantity = quantity
        self.unit = unit
        self.expiration_date = expiration_date
        self.db_connection = db_connection
        self.qr_code_label = qr_code_label

    def validate_inputs(self):
        # Check if all fields are filled
        if not all([self.name, self.type, self.quantity, self.unit, self.expiration_date]):
            messagebox.showerror("Error", "All fields must be filled.")
            return False

        # Check if expiration date is in the future
        today = datetime.now().date()
        if self.expiration_date <= today:
            messagebox.showerror("Error", "Expiration date must be later than today.")
            return False

        return True

    def generate_qr_code(self):
        # Combine name and expiration date to create a unique identifier for the QR code
        qr_code_data = f"{self.name}_{self.expiration_date}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill='black', back_color='white')

        # Save the generated QR code image
        qr_code_filename = f"qr_{self.name}_{self.expiration_date}.png"
        qr_code_filepath = os.path.join(os.path.dirname(__file__), 'qr_codes', qr_code_filename)
        qr_image.save(qr_code_filepath)

        # Update the QR code label in the UI
        self.update_qr_code_image(qr_code_filepath)

        return qr_code_filepath

    def update_qr_code_image(self, qr_code_filepath):
        # Load the new QR code image
        qr_image = Image.open(qr_code_filepath)
        qr_image_resized = qr_image.resize((250, 250), Image.LANCZOS)
        qr_image_tk = ImageTk.PhotoImage(qr_image_resized)

        # Update the label with the new QR code
        self.qr_code_label.config(image=qr_image_tk)
        self.qr_code_label.image = qr_image_tk  # Keep a reference to avoid garbage collection

    def save_to_database(self):
        # Generate QR code and get the data string
        qr_code_data = f"{self.name}_{self.expiration_date}"  # Store data string in the database

        # Save the medicine data to the database
        try:
            cursor = self.db_connection.cursor()
            insert_query = """
                INSERT INTO medicine_inventory (name, type, quantity, unit, expiration_date, date_stored, qr_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (self.name, self.type, self.quantity, self.unit, self.expiration_date,
                                        datetime.now().date(), qr_code_data))
            self.db_connection.commit()
            messagebox.showinfo("Success", "Medicine successfully deposited!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()

