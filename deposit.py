import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageTk
from datetime import datetime
import os
import mysql.connector
import serial
import time
import tkinter as tk
from tkinter import messagebox
from custom_messagebox import CustomMessageBox
import threading

SERIAL_PORT = 'COM4'  # Update to your printer's COM port if different
BAUD_RATE = 9600
TIMEOUT = 1

motif_color = '#42a7f5'


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

        self.reference_window = root 
        if self.unit == 'capsule' or self.unit == 'tablet':
            self.dosage_for_db = f"{self.dosage} mg"
        elif self.unit == 'syrup':
            self.dosage_for_db = f"{self.dosage} ml"
        
        


    def validate_inputs(self):
        # Check if all fields are filled
        if not all([self.name, self.generic_name, self.quantity, self.unit, self.expiration_date, self.dosage]):
            global message_box
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message='Please fill-out all the fields',
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        # Check if quantity and dosage are numeric and greater than 0
        try:
            self.quantity = int(self.quantity)
            self.dosage = int(self.dosage)
            if self.quantity <= 0:
                message_box = CustomMessageBox(
                    root=self.root,
                    title='Error',
                    color='red',
                    message="Quantity must be greater than 0.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
                )
                return False
            if self.dosage <= 0:
                message_box = CustomMessageBox(
                    root=self.root,
                    title='Error',
                    color='red',
                    message="Dosage must be greater than 0.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
                )
                return False
        except ValueError:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message="Quantity and Dosage must be numeric values greater than 0.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        # Check if expiration date is in the future
        today = datetime.now().date()
        if self.expiration_date <= today:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message="Expiration date must be later than today.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        return True

    def generate_qr_code(self):
        # Combine name and expiration date to create a unique identifier for the QR code
        qr_code_data = f"{self.name}_{self.dosage_for_db}_{self.expiration_date}"
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
        qr_image_resized = qr_image.resize((450, 450), Image.LANCZOS)
        qr_image_tk = ImageTk.PhotoImage(qr_image_resized)
        # Add code here to update the label widget if necessary

    def show_loading_window(self):
        """Display a Toplevel window with a 'Loading...' message."""
        self.loading_window = tk.Toplevel(self.root, relief='raised', bd=5)
        self.loading_window.title("Printing")
        self.loading_window.geometry("500x300")
        self.loading_window.resizable(False, False)
        self.loading_window.attributes('-topmost', True)
        self.loading_window.focus_set()
        self.loading_window.grab_set()  # Make it modal (disable interaction with main window)
        self.loading_window.overrideredirect(True)  # Remove the title bar
        
        # Center the loading window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 100
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 50
        self.loading_window.geometry(f"+{x}+{y}")

        loading_label = tk.Label(self.loading_window, text="Loading...", font=("Arial", 18, 'bold'), bg=motif_color, fg='white')
        loading_label.pack(expand=True, fill='both')

    def close_loading_window(self):
        """Close the loading window."""
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

    def print_qr_code(self, expiration_date):
        """Prints the QR code and expiration date on the thermal printer,
        repeating the print if the unit is 'syrup' based on quantity,
        and showing a loading window during the process."""
        try:
            # Show the loading window before starting the print task
            self.show_loading_window()

            # Generate QR code image
            qr_code_filepath = self.generate_qr_code()
            qr_image = Image.open(qr_code_filepath)

            # Resize QR code to fit with text beside it (adjust as needed)
            qr_image = qr_image.resize((170, 170), Image.LANCZOS)

            # Prepare expiration date text as an image with a larger, bold font
            expiration_text = f"{expiration_date.strftime('%Y-%m-%d')}"

            # Load a bold TrueType font (adjust the path as needed for your system)
            font_path = "C:/Windows/Fonts/arialbd.ttf"  # Arial Bold on Windows
            font = ImageFont.truetype(font_path, 33)  # 33px for larger text
            text_width, text_height = font.getbbox(expiration_text)[2:]

            # Create a new blank image with space for both the QR and expiration text
            combined_width = qr_image.width + text_width + 20  # 20px padding between QR and text
            combined_height = max(qr_image.height, text_height)
            combined_image = Image.new('1', (combined_width, combined_height + 60), 255)  # Add 30px padding below

            # Place the QR code on the left
            combined_image.paste(qr_image, (0, 0))

            # Add the expiration date text to the right of the QR code
            draw = ImageDraw.Draw(combined_image)
            text_x_position = qr_image.width + 18  # Adjust padding here if needed
            draw.text((text_x_position, (combined_height - text_height) // 2), expiration_text, font=font, fill=0)

            # Convert the combined image to ESC/POS format for printing
            img_data = self.image_to_escpos_data(combined_image)

            # Define the print task in a separate thread to prevent UI freezing
            def print_task():
                try:
                    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as printer:
                        # If the unit is 'syrup', repeat printing based on quantity
                        if self.unit == 'syrup':
                            for _ in range(self.quantity):
                                printer.write(img_data)
                                printer.flush()
                                # Optional cut command if printer supports it
                                printer.write(b'\x1d\x56\x42\x00')  # ESC i - Cut paper
                                printer.flush()
                                time.sleep(1)  # Slight delay if needed between prints
                        else:
                            # Print only once for 'capsule' or 'tablet'
                            printer.write(img_data)
                            printer.flush()
                            # Optional cut command if printer supports it
                            printer.write(b'\x1d\x56\x42\x00')  # ESC i - Cut paper
                            printer.flush()

                        print("QR code and expiration date printed with spacing successfully.")
                except serial.SerialException as e:
                    print(f"Printer communication error: {e}")
                finally:
                    # Ensure both the loading window is closed and success message is shown after printing
                    self.close_loading_window()
                    self.show_success_message(qr_code_filepath)

            # Start the print task in a new thread
            threading.Thread(target=print_task).start()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.close_loading_window()  # Ensure loading window is closed in case of error



    def save_to_database(self):
        # Generate QR code and get the image file path
        qr_code_filepath = self.generate_qr_code()
        qr_code_data = f"{self.name}_{self.dosage_for_db}_{self.expiration_date}"

        # Convert name and type to Title Case for database insertion
        name_for_db = self.name.capitalize()
        type_for_db = self.generic_name.capitalize()
        
        # Save the medicine data to the database
        try:
            cursor = self.db_connection.cursor()
            insert_query = """
                INSERT INTO medicine_inventory (name, type, quantity, unit, dosage, expiration_date, date_stored, qr_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name_for_db, type_for_db, self.quantity, self.unit.capitalize(), self.dosage_for_db,
                                        self.expiration_date, datetime.now().date(), qr_code_data))
            self.db_connection.commit()

            # Start printing process after database save
            print("Attempting to print expiration date on thermal printer...")
            self.print_qr_code(self.expiration_date)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()

    def image_to_escpos_data(self, img):
        """Converts a monochrome image to ESC/POS format."""
        width, height = img.size
        bytes_per_row = (width + 7) // 8  # 1 bit per pixel, so 8 pixels per byte
        img_data = b''

        # ESC/POS command for image printing
        img_data += b'\x1d\x76\x30\x00' + bytes([bytes_per_row % 256, bytes_per_row // 256, height % 256, height // 256])

        # Loop through pixels and convert to ESC/POS data
        for y in range(height):
            row_data = 0
            byte = 0
            for x in range(width):
                if img.getpixel((x, y)) == 0:  # Pixel is black
                    byte |= (1 << (7 - row_data))
                row_data += 1
                if row_data == 8:
                    img_data += bytes([byte])
                    row_data = 0
                    byte = 0
            if row_data > 0:  # Remaining bits in the row
                img_data += bytes([byte])

        return img_data


    def show_success_message(self, qr_code_filepath):
        """Display the custom messagebox after successfully adding the medicine."""
        self.close_loading_window()
        from System import LockUnlock
        self.message_box = CustomMessageBox(
            root=self.root,
            title="Medicine Deposited",
            message=f"Adding medicine: '{self.name.capitalize()}'\nPlease attach the printed QR Code with Exp. Date to the medicine.\n\nDo you want to add more medicine?",
            icon_path=qr_code_filepath,
            no_callback=lambda: (LockUnlock(self.root, self.Username, self.Password, self.arduino,"unlock", "medicine inventory", type="deposit"), self.message_box.destroy()),
            yes_callback=lambda: (self._yes_action(), self.message_box.destroy())
        )

    def _yes_action(self):
        """Trigger the yes callback and close the window."""
        print("yes Callback called")
        if self.yes_callback:
            self.yes_callback()

