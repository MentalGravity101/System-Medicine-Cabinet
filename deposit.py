import qrcode
from PIL import Image, ImageTk
from datetime import datetime
import os
import mysql.connector
import tkinter as tk
from tkinter import messagebox
from custom_messagebox import CustomMessageBox
from lockunlock import LockUnlock

class MedicineDeposit:
    def __init__(self, name, generic_name, quantity, unit, expiration_date, dosage, db_connection, root, content_frame, keyboardFrame, Username, Password, arduino, action="unlock", yes_callback=None):
        self.root = root
        self.name = name.lower()
        self.generic_name = generic_name.lower()
        self.quantity = int(quantity)
        self.unit = unit.lower()
        self.expiration_date = expiration_date
        self.dosage = int(dosage)
        self.db_connection = db_connection
        self.content_frame = content_frame
        self.keyboardFrame = keyboardFrame
        self.Username = Username
        self.Password = Password
        self.arduino = arduino
        self.action = action
        self.yes_callback = yes_callback

    def validate_inputs(self):
        # Check if all fields are filled
        if not all([self.name, self.generic_name, self.quantity, self.unit, self.expiration_date, self.dosage]):
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                message='All fields must be filled',
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        # Check if quantity and dosage are not zero
        if self.quantity <= 0:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                message="Quantity must be greater than 0.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False
        if self.dosage <= 0:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                message="Dosage must be greater than 0.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        # Check if expiration date is in the future
        today = datetime.now().date()
        if self.expiration_date <= today:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                message="Expiration date must be later than today.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
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
        # Add code here to update the label widget if necessary

    def save_to_database(self):
        # Generate QR code and get the image file path
        qr_code_filepath = self.generate_qr_code()  # Now returns the file path of the QR code image
        qr_code_data = f"{self.name}_{self.expiration_date}"  # Store data string in the database

        # Convert name and type to Title Case for database insertion
        name_for_db = self.name.capitalize()
        type_for_db = self.generic_name.capitalize()

        dosage_for_db = f"{self.dosage}{self.unit}" 
        if self.unit == 'capsule' or self.unit == 'tablet':
            dosage_for_db = f"{self.dosage}mg"
        elif self.unit == 'syrup':
            dosage_for_db = f"{self.dosage}ml"

        # Save the medicine data to the database
        try:
            cursor = self.db_connection.cursor()
            insert_query = """
                INSERT INTO medicine_inventory (name, type, quantity, unit, dosage, expiration_date, date_stored, qr_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name_for_db, type_for_db, self.quantity, self.unit.capitalize(), dosage_for_db,
                                          self.expiration_date, datetime.now().date(), qr_code_data))
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
        self.message_box = CustomMessageBox(
            root=self.root,
            title="Medicine Deposited",
            message=f"Adding medicine: '{self.name.capitalize()}'\nPlease attach the printed QR Code with Exp. Date to the medicine.\nDo you want to add more medicine?.",
            icon_path=qr_code_filepath,  # Pass the QR code image path here
            no_callback=lambda: (LockUnlock(self.content_frame, self.Username, self.Password, self.arduino, self.action, "medicine inventory", type="deposit"), self.message_box.destroy()),
            yes_callback=lambda: (self._yes_action(), self.message_box.destroy())
        )

    def _yes_action(self):
        """Trigger the yes callback and close the window."""
        print("yes Callback called")
        if self.yes_callback:
            self.yes_callback()
