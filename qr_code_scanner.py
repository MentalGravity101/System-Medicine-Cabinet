import tkinter as tk
from PIL import Image, ImageTk
import os

class QRCodeScanner:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("QR Code Scanner")
        self.window.geometry("400x300")
        self.window.resizable(False, False)

        # Add a label to indicate the scanning process
        self.label = tk.Label(self.window, text="Scanning QR Code...", font=("Arial", 18))
        self.label.pack(pady=20)

        # Add a dummy camera or scanning icon (you can replace this with live camera feed or actual scanner)
        camera_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((150, 150), Image.LANCZOS))
        self.camera_label = tk.Label(self.window, image=camera_icon)
        self.camera_label.image = camera_icon  # Keep a reference to avoid garbage collection
        self.camera_label.pack(pady=10)

        # Simulate scan completion after a delay (you can replace this with actual scanning code)
        self.window.after(5000, self.simulate_scan_complete)  # Simulate a 3-second scan

    def simulate_scan_complete(self):
        """Simulate the completion of QR scanning."""
        self.label.config(text="QR Code Scanned Successfully!")
        # You can add further actions here (e.g., close the window after a delay)
        self.window.after(2000, self.window.destroy)  # Close the window after 2 seconds
