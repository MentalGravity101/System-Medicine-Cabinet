import qrcode
from PIL import Image, ImageTk
from datetime import datetime
import os
import mysql.connector
import tkinter as tk
from tkinter import messagebox
from custom_messagebox import CustomMessageBox

class MedicineDeposit:
    def __init__(self, name, type_, quantity, unit, expiration_date, db_connection, root):
        self.root = root
        self.name = name
        self.type = type_
        self.quantity = quantity
        self.unit = unit
        self.expiration_date = expiration_date
        self.db_connection = db_connection

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
        qr_image_resized = qr_image.resize((400, 400), Image.LANCZOS)
        qr_image_tk = ImageTk.PhotoImage(qr_image_resized)


    def save_to_database(self):
        # Generate QR code and get the image file path
        qr_code_filepath = self.generate_qr_code()  # Now returns the file path of the QR code image
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

            # Show success message and QR code in a custom message box
            self.show_success_message(qr_code_filepath)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()

    def show_success_message(self, qr_code_filepath):
        """Display the custom messagebox after successfully adding the medicine."""

        # Initialize the CustomMessageBox with QR code icon
        CustomMessageBox(
            root=self.root,
            title="Medicine Deposited",
            message=f"Medicine '{self.name}' has been successfully added!",
            icon_path=qr_code_filepath,  # Pass the QR code image path here
            sound_file="success_sound.mp3",  # Optional sound file for added effect
        )

