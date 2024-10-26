import tkinter as tk
from tkinter import messagebox
import mysql.connector
import os
from PIL import Image, ImageTk, ImageSequence
import time

motif_color = '#42a7f5'  # Primary color used for the theme

class QRLogin:
    def __init__(self, parent, callback=None):
        self.window = tk.Toplevel(parent, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)
        self.window.grab_set()

        self.callback = callback

        # Title frame
        title_frame = tk.Frame(self.window, bg=motif_color)
        title_frame.pack(fill=tk.X)

        # Title label
        title_label = tk.Label(title_frame, text="Login Credentials", font=('Arial', 15, 'bold'), bg=motif_color, fg='white', pady=12)
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        # Add the close button icon at the top-right corner
        self.close_icon_path = os.path.join(os.path.dirname(__file__), 'images', 'cancel_icon.png')
        if os.path.exists(self.close_icon_path):
            self.close_img = ImageTk.PhotoImage(Image.open(self.close_icon_path).resize((18, 18), Image.LANCZOS))
        else:
            self.close_img = None

        close_button = tk.Button(title_frame, image=self.close_img, command=self.window.destroy, bg=motif_color, relief=tk.FLAT, bd=0)
        close_button.image = self.close_img  # Keep a reference to avoid garbage collection
        close_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 5))

        # QR Code Scanner Icon
        original_logo_img = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((170, 170), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(original_logo_img)
        logo_label = tk.Label(self.window, image=logo_img)
        logo_label.image = logo_img  # Keep reference to avoid garbage collection
        logo_label.pack(side=tk.TOP, pady=(10, 10))

        # Instruction Message
        instruction_label = tk.Label(self.window, text=f"Please use the Scanner to login\nusing your QR Code", font=("Arial", 18), fg='black')
        instruction_label.pack(pady=10)

        # QR Code Entry Frame
        entry_frame = tk.Frame(self.window)
        entry_frame.pack(pady=(5, 3))

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(self.window, font=("Arial", 14), justify='center', width=35, relief='flat', bd=3)
        self.qr_entry.pack(pady=(10, 5))
        self.qr_entry.focus_set()

        # Label to display the contents corresponding to qrcode
        self.result_label = tk.Label(self.window, text="", font=("Arial", 15), fg='green', pady=2, height=5)
        self.result_label.pack()

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self._process_qrcode)

        self._adjust_window_height()

    def _adjust_window_height(self):
        """Adjust window height based on the message length while keeping the width fixed."""
        # Fixed width, dynamic height
        window_width = 465  # Adjusted width to fit better
        self.window.update_idletasks()

        required_height = self.window.winfo_reqheight()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate the position to center the window
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (required_height / 2))

        # Set the new geometry with fixed width and dynamic height
        self.window.geometry(f"{window_width}x{required_height}+{position_x}+{position_y}")
    
    #Function that validates user login credentials via QR code
    def _process_qrcode(self, event):
        if self.qr_entry.winfo_exists():
            scanned_qr_code = self.qr_entry.get().strip()
            print(f"Final scanned QR code: {scanned_qr_code}")  # Debugging statement

            if scanned_qr_code:
                # Clear the Entry widget for the next scan
                self.qr_entry.delete(0, tk.END)

                # Connect to the MySQL database
                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="db_medicine_cabinet"
                    )
                    cursor = conn.cursor()

                    # Check if the scanned QR code matches any user in the database
                    cursor.execute("SELECT username, password FROM users WHERE qrcode_data = %s", (scanned_qr_code,))
                    result = cursor.fetchone()

                    if result:
                        self.qr_entry.delete(0, tk.END)
                        self.result_label.config(text="QR Code is Valid.", fg="green")
                        username, password = result
                        time.sleep(1)
                        self.callback(username, password)
                        self.window.destroy()
                    else:
                        # If no match found, show an error
                        self.result_label.config(text="Invalid QR code or credentials.", fg="red")

                except mysql.connector.Error as err:
                    print(f"Error: {err}")
                    messagebox.showerror("Database Error", "Could not connect to the database.")

                finally:
                    # Close the cursor and connection
                    cursor.close()
                    conn.close()
            else:
                self.result_label.config(text="No QR code data scanned.", fg="red")


