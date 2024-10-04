import tkinter as tk
from tkinter import messagebox
import mysql.connector

class QRCodeScanner:
    def __init__(self, parent):
        print("QRCodeScanner initialized")  # Debugging statement
        # Create a new Toplevel window
        self.top = tk.Toplevel(parent)
        self.top.title("Withdraw Medicine")
        
        # Center the window (optional)
        self.top.geometry("400x200")
        
        # Display message to the user
        tk.Label(self.top, text="Please scan the medicine QR code to withdraw", font=("Arial", 16)).pack(pady=20)

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(self.top, font=("Arial", 16))
        self.qr_entry.pack(pady=10)
        self.qr_entry.focus_set()

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self.process_qrcode)

    def process_qrcode(self, event):
        # Ensure we check the widget exists before trying to delete or update its content
        if self.qr_entry.winfo_exists():
            scanned_qr_code = self.qr_entry.get().strip()
            print(f"Final scanned QR code: {scanned_qr_code}")  # Debugging statement

            if scanned_qr_code:
                # Proceed with withdrawal process if the QR code is scanned
                self.withdraw_medicine(scanned_qr_code)

                # Clear the Entry widget for the next scan BEFORE destroying the window
                self.qr_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "No QR code data scanned.")

            # Close the top-level window after clearing the entry
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
            print(f"Database query result: {result}")  # Debugging

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
            print(f"Database Error: {err}")  # Debugging

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
