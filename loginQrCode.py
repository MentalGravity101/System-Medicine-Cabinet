import tkinter as tk
from tkinter import messagebox
import mysql.connector
import os
from PIL import Image, ImageTk, ImageSequence

motif_color = '#42a7f5'  # Primary color used for the theme

class QRLogin:
    def __init__(self, parent, Action, callback=None):
        print("QRCodeScanner initialized")  # Debugging statement
        # Create a new Toplevel window
        self.top = tk.Toplevel(parent, relief='raised', bd=5)

        self.top.overrideredirect(True)  # Remove the title bar
        self.top.resizable(width=False, height=False)

        self.top.focus_set()

        # Title Frame
        self.title_frame = tk.Frame(self.top, bg=motif_color)
        self.title_frame.pack(fill=tk.X, expand=True, pady=(0, 10))

        # Title Label
        title_label = tk.Label(self.title_frame, text="  Login", font=('Arial', 15, 'bold'), fg='white', bg=motif_color, pady=12)
        title_label.pack(side=tk.LEFT)

        # Add the close button icon at the top-right corner
        self.close_icon_path = os.path.join(os.path.dirname(__file__), 'images', 'cancel_icon.png')
        if os.path.exists(self.close_icon_path):
            self.close_img = ImageTk.PhotoImage(Image.open(self.close_icon_path).resize((18, 18), Image.LANCZOS))
        else:
            self.close_img = None

        close_button = tk.Button(self.title_frame, image=self.close_img, command=self.top.destroy, relief=tk.FLAT, bd=0, bg=motif_color, activebackground=motif_color)
        close_button.image = self.close_img  # Keep a reference to avoid garbage collection
        close_button.pack(side=tk.RIGHT, padx=(0, 5))

        # Content Frame
        content_frame = tk.Frame(self.top)
        content_frame.pack(pady=(10, 2))

        # QR Code Scanner Icon
        original_logo_img = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((170, 170), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(original_logo_img)
        logo_label = tk.Label(content_frame, image=logo_img)
        logo_label.image = logo_img  # Keep reference to avoid garbage collection
        logo_label.pack(side=tk.TOP, pady=(10, 10))

        # Instruction Message
        instruction_label = tk.Label(content_frame, text=f"Please scan your qrcode to {Action}", font=("Arial", 14), fg='black')
        instruction_label.pack(pady=10)

        # QR Code Entry Frame
        entry_frame = tk.Frame(self.top)
        entry_frame.pack(pady=(5, 3))

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(content_frame, font=("Arial", 14), justify='center', width=35, relief='sunken', bd=3)
        self.qr_entry.pack(pady=(10, 5))
        self.qr_entry.focus_set()

        # Label to display the contents corresponding to qrcode
        self.result_label = tk.Label(self.top, text="", font=("Arial", 15), fg='green', pady=2, height=5)
        self.result_label.pack()

        self.callback = callback  # This will be a function passed from the main app

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self.process_qrcode)

        self._adjust_window_height()

    def _adjust_window_height(self):
        """Adjust window height based on the message length while keeping the width fixed."""
        # Fixed width, dynamic height
        window_width = 450  # Adjusted width to fit better
        self.top.update_idletasks()

        required_height = self.top.winfo_reqheight()

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()

        # Calculate the position to center the window
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (required_height / 2))

        # Set the new geometry with fixed width and dynamic height
        self.top.geometry(f"{window_width}x{required_height}+{position_x}+{position_y}")

    def process_qrcode(self, event):
        if self.qr_entry.winfo_exists():
            scanned_qr_code = self.qr_entry.get().strip()
            print(f"Final scanned QR code: {scanned_qr_code}")  # Debugging statement

            if scanned_qr_code:
                # Clear the Entry widget for the next scan
                self.qr_entry.delete(0, tk.END)
                # Call the callback function if it's defined
                self.checkQR()
            else:
                self.result_label.config(text="No QR code data scanned.", fg="red")
        
    def checkQR(self, qrcode):
        print(f"Login with QR code: {qrcode}")

        try:
            # Connect to the MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Your MySQL password
                database="db_medicine_cabinet"
            )
            cursor = conn.cursor()

            # Query to check if the medicine exists and retrieve name, quantity, type, and unit
            cursor.execute("SELECT qrcode_data FROM user WHERE qr_code = %s", (qrcode_data,))
            result = cursor.fetchone()

            if result:
                self.result_label.config(text="QR code found.", fg="green")
                if self.callback:  # Call the callback to send data to System.py
                    self.callback(result)
            else:
                self.result_label.config(text="QR code not found in the database.", fg="red")
                if self.callback:  # Inform System.py of the failure
                    self.callback(None)

        except mysql.connector.Error as err:
            self.result_label.config(text=f"Database Error: {err}", fg="red")
            if self.callback:  # Inform System.py of the failure
                self.callback(None)

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()


