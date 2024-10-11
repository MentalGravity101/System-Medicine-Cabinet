import tkinter as tk
from tkinter import ttk, messagebox
import time
import pywifi
from pywifi import const
from keyboard import OnScreenKeyboard
from custom_messagebox import CustomMessageBox
from PIL import Image, ImageTk
import os

motif_color = '#42a7f5'

class WiFiConnectUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connect to Wi-Fi")
        self.configure(bg='#f7f7f7')

        # Set initial small window size (e.g., for the "Scanning" state)
        self.geometry("300x320")

        # Center the initial small window on the screen
        self.center_window(300, 320)

        # Initialize PyWiFi and get the first wireless interface
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]

        # Ensure the interface is in a state that can scan
        if self.iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:
            self.iface.disconnect()
            time.sleep(1)  # Allow some time for disconnection

        # Check if Wi-Fi interface is active
        if self.iface.status() == const.IFACE_INACTIVE:
            messagebox.showerror("Wi-Fi Error", "No active Wi-Fi interface found.")
            return

        # Show a "Loading..." message initially
        self.loading_label = tk.Label(self, text="Scanning Available Wi-Fi...", font=("Arial", 16), bg='#f7f7f7')
        self.loading_label.pack(pady=100)

        # Automatically scan for Wi-Fi networks when the Toplevel opens
        self.after(100, self.scan_wifi)  # Delay the scan to allow UI to update with the loading message

        # On-screen keyboard reference to control its visibility
        self.on_screen_keyboard = None

    def center_window(self, width, height):
        """Centers the window on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate coordinates for centering
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Set the window geometry to the calculated coordinates
        self.geometry(f"{width}x{height}+{x}+{y}")

    def scan_wifi(self):
        """Scans for available Wi-Fi networks and updates the dropdown list."""
        # Start scanning for networks
        try:
            self.iface.scan()
            self.after(10000, self.update_wifi_results)  # Wait 10 seconds for scan results and then update the UI
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error scanning for networks: {e}")
            print(f"Scan Error: {e}")

    def update_wifi_results(self):
        """Updates the UI with the Wi-Fi scan results after the scan is complete."""
        # Get the scan results
        scan_results = self.iface.scan_results()

        # Extract SSID names
        networks = [result.ssid for result in scan_results if result.ssid]

        # Debug: Print scan results to console for troubleshooting
        print("Found networks:", networks)

        # Expand to fullscreen once scanning is complete and results are available
        self.attributes('-fullscreen', True)

        if networks:
            self.create_widgets(networks)  # Call the function to create the actual UI with found networks
        else:
            messagebox.showinfo("Wi-Fi Scan", "No networks found!")
            self.create_widgets([])  # Call the function with an empty list if no networks are found

    def create_widgets(self, networks):
        """Creates the actual UI after scanning is complete."""
        # Remove the loading message
        self.loading_label.pack_forget()

        title_label = tk.Label(self, text="BRGY. SAN MATEO HEALTH CENTER MEDICINE CABINET", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1, justify='left', padx=10)
        title_label.pack(fill='both')

        UI_frame=tk.LabelFrame(self, text='Connect to Wi-Fi', relief='raised', bd=2, padx=50, font=('Arial', 14), pady=20)
        UI_frame.pack(anchor='center', pady=(20,0), expand=True)

        wifi_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'noWifi_icon.png')).resize((300, 300), Image.LANCZOS))
        wifi_image_status = tk.Label(UI_frame, image=wifi_icon, padx=20)
        wifi_image_status.image = wifi_icon
        wifi_image_status.grid(row=0, column=0, pady=(20, 5), rowspan=5, padx=(0, 20))

        # Label for Wi-Fi networks
        tk.Label(UI_frame, text="Select Wi-Fi Network", font=("Arial", 14), bg='#f7f7f7').grid(row=0, column=1, pady=10)

        # Dropdown (Combobox) to select a Wi-Fi network
        self.network_combobox = ttk.Combobox(UI_frame, values=networks, state="readonly", font=("Arial", 12))
        self.network_combobox.grid(row=1, column=1, pady=10)
        if networks:
            self.network_combobox.current(0)  # Set default selection

        # Label and Entry for Wi-Fi password
        tk.Label(UI_frame, text="Wi-Fi Password", font=("Arial", 14), bg='#f7f7f7').grid(row=2, column=1, pady=10)
        self.password_entry = tk.Entry(UI_frame, show="*", font=("Arial", 12))  # Default is hidden
        self.password_entry.grid(row=3, column=1, pady=10)

        # Checkbutton to show/hide password
        self.show_password_var = tk.IntVar()
        self.show_password_check = tk.Checkbutton(UI_frame, text="Show Password", variable=self.show_password_var,
                                                  command=self.toggle_password_visibility, bg='#f7f7f7', font=("Arial", 10))
        self.show_password_check.grid(row=4, column=1, pady=5)

        # Button to connect to the selected Wi-Fi network
        self.connect_button = tk.Button(UI_frame, text="Connect", font=("Arial", 14, 'bold'), bg=motif_color, fg='white', padx=20, command=self.connect_to_wifi)
        self.connect_button.grid(row=5, column=1, pady=20)

        wifi_label_status = tk.Label(UI_frame, text="No Wifi Connected", font=('Arial', 14), fg='red')
        wifi_label_status.grid(row=5, column=0, pady=10)

        proceed_login = tk.Button(self, text="Proceed to Login", state='disabled', font=("Arial", 14, 'bold'), fg='white', bg='#2c3e50', padx=30, pady=10)
        proceed_login.pack(anchor='center', pady=20)

        # Show on-screen keyboard when password entry is focused
        self.password_entry.bind("<FocusIn>", lambda e: self.show_on_screen_keyboard(self.password_entry))
        self.password_entry.bind("<FocusOut>", lambda e: self.hide_on_screen_keyboard())

    def toggle_password_visibility(self):
        """Toggle between showing and hiding the Wi-Fi password."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def connect_to_wifi(self):
        """Attempts to connect to the selected Wi-Fi network using the provided password."""
        selected_network = self.network_combobox.get()
        password = self.password_entry.get()

        if not selected_network:
            messagebox.showwarning("Input Error", "Please select a network.")
            return
        if not password:
            messagebox.showwarning("Input Error", "Please enter the Wi-Fi password.")
            return

        self.iface.disconnect()
        time.sleep(1)

        profile = pywifi.Profile()
        profile.ssid = selected_network
        profile.key = password
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP

        self.iface.remove_all_network_profiles()
        tmp_profile = self.iface.add_network_profile(profile)

        # Connection attempt with retries
        connected = False
        for i in range(5):  # Retry 5 times, checking every 3 seconds
            self.iface.connect(tmp_profile)
            time.sleep(3)

            if self.iface.status() == const.IFACE_CONNECTED:
                connected = True
                break

        if connected:
            messagebox.showinfo("Success", f"Connected to {selected_network}!")
            self.destroy()
        else:
            # Providing more detailed error messages based on status
            error_message = self.get_error_message()
            messagebox.showerror("Failed", f"Failed to connect to the network. {error_message}")

    def get_error_message(self):
        """Provide a detailed error message based on the connection status."""
        status = self.iface.status()
        if status == const.IFACE_DISCONNECTED:
            return "The connection was disconnected."
        elif status == const.IFACE_INACTIVE:
            return "The interface is inactive or could not connect."
        else:
            return "Please check the password or network availability."

    def show_on_screen_keyboard(self, widget):
        """Shows an on-screen keyboard below the password entry."""
        if self.on_screen_keyboard is None:
            self.on_screen_keyboard = OnScreenKeyboard(self)
        self.on_screen_keyboard.show_keyboard()

    def hide_on_screen_keyboard(self):
        """Hides the on-screen keyboard."""
        if self.on_screen_keyboard:
            self.on_screen_keyboard.hide_keyboard()

# For testing purposes: create a root Tk window and instantiate WiFiConnectUI
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window since we are focusing on the Toplevel
    
    wifi_window = WiFiConnectUI(root)
    
    root.mainloop()
