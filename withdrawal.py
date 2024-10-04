import tkinter as tk
from tkinter import messagebox
import mysql.connector
import os
from PIL import Image, ImageTk

motif_color = '#42a7f5'  # Primary color used for the theme

class QRCodeScanner:
    def __init__(self, parent):
        print("QRCodeScanner initialized")  # Debugging statement
        # Create a new Toplevel window
        self.top = tk.Toplevel(parent, relief='raised', bd=5)

        self.top.overrideredirect(True)  # Remove the title bar
        self.top.resizable(width=False, height=False)

        self.top.focus_set()

        # Title Frame
        self.title_frame = tk.Frame(self.top, bg=motif_color)
        self.title_frame.pack(fill=tk.X, expand=True, padx=10, pady=10)

        # Title Label
        title_label = tk.Label(self.title_frame, text="Withdraw Medicine", font=('Arial', 15, 'bold'), fg='black')
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

        # Message Frame for user instruction
        message_frame = tk.Frame(self.top, bg='white')
        message_frame.pack(pady=10)

        # Instruction Message
        instruction_label = tk.Label(message_frame, text="Please scan the medicine QR code to withdraw", font=("Arial", 14), fg='black')
        instruction_label.pack(pady=10)

        # QR Code Entry Frame
        entry_frame = tk.Frame(self.top)
        entry_frame.pack(pady=5)

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(entry_frame, font=("Arial", 14), justify='center', width=35, relief='sunken', bd=3)
        self.qr_entry.pack(pady=10)
        self.qr_entry.focus_set()

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self.process_qrcode)

        # Confirm Button to allow manual QR code processing
        confirm_button = tk.Button(self.top, text="Confirm", font=("Arial", 12, "bold"), command=lambda: self.process_qrcode(None),
                                   bg='white', fg='black', activebackground='#fff', activeforeground=motif_color, relief=tk.RAISED)
        confirm_button.pack(pady=(10, 20))

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
                # Proceed with withdrawal process if the QR code is scanned
                self.withdraw_medicine(scanned_qr_code)
            else:
                messagebox.showerror("Error", "No QR code data scanned.")

            # Destroy the Toplevel window after clearing the entry
            self.top.destroy()


    def withdraw_medicine(self, qr_code):
        print(f"Withdrawing medicine with QR code: {qr_code}")

        try:
            # Connect to the MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Your MySQL password
                database="db_medicine_cabinet"
            )
            cursor = conn.cursor()

            # Query to check if the medicine exists
            cursor.execute("SELECT name, quantity FROM medicine_inventory WHERE qr_code = %s", (qr_code,))
            result = cursor.fetchone()

            if result:
                medicine_name, current_quantity = result
                if current_quantity > 0:
                    # Deduct 1 from quantity
                    new_quantity = current_quantity - 1
                    cursor.execute("UPDATE medicine_inventory SET quantity = %s WHERE qr_code = %s", (new_quantity, qr_code))
                    conn.commit()

                    # Show success message
                    messagebox.showinfo("Success", f"Withdrawn 1 unit of {medicine_name}. New quantity: {new_quantity}")
                else:
                    messagebox.showerror("Error", f"No more {medicine_name} available to withdraw.")
            else:
                messagebox.showerror("Error", "QR code not found in the database.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
