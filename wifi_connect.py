import tkinter as tk
from tkinter import ttk, messagebox
import pywifi
from pywifi import const
import time
from keyboard import OnScreenKeyboard
from custom_messagebox import CustomMessageBox

class WiFiConnectUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connect to Wi-Fi")
        self.configure(bg='#f7f7f7')

        # Set window size and disable resizing
        self.geometry("300x320")
        self.resizable(False, False)

        # Center the window on the screen
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

    def center_window(self, width, height):
        """Centers the window on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate coordinates for centering
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Set the window geometry to the calculated coordinates
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self, networks):
        """Creates the actual UI after scanning is complete."""
        # Remove the loading message
        self.loading_label.pack_forget()

        # Label for Wi-Fi networks
        tk.Label(self, text="Select Wi-Fi Network", font=("Arial", 14), bg='#f7f7f7').pack(pady=10)

        # Dropdown (Combobox) to select a Wi-Fi network
        self.network_combobox = ttk.Combobox(self, values=networks, state="readonly", font=("Arial", 12))
        self.network_combobox.pack(pady=10)
        if networks:
            self.network_combobox.current(0)  # Set default selection

        # Label and Entry for Wi-Fi password
        tk.Label(self, text="Wi-Fi Password", font=("Arial", 14), bg='#f7f7f7').pack(pady=10)
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 12))  # Default is hidden
        self.password_entry.pack(pady=10)

        # Checkbutton to show/hide password
        self.show_password_var = tk.IntVar()
        self.show_password_check = tk.Checkbutton(self, text="Show Password", variable=self.show_password_var,
                                                  command=self.toggle_password_visibility, bg='#f7f7f7', font=("Arial", 10))
        self.show_password_check.pack(pady=5)

        # Button to connect to the selected Wi-Fi network
        self.connect_button = tk.Button(self, text="Connect", font=("Arial", 14), command=self.connect_to_wifi)
        self.connect_button.pack(pady=20)


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

        if networks:
            self.create_widgets(networks)  # Call the function to create the actual UI with found networks
        else:
            messagebox.showinfo("Wi-Fi Scan", "No networks found!")
            self.create_widgets([])  # Call the function with an empty list if no networks are found

    def toggle_password_visibility(self):
        """Toggles the visibility of the password in the password entry field."""
        if self.show_password_var.get():
            self.password_entry.config(show="")  # Show password
        else:
            self.password_entry.config(show="*")  # Hide password

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

        # Disconnect any existing connection first
        self.iface.disconnect()
        time.sleep(1)  # Wait for disconnection

        # Define the Wi-Fi connection profile
        profile = pywifi.Profile()
        profile.ssid = selected_network  # Set the SSID of the network
        profile.key = password  # Set the Wi-Fi password
        profile.auth = const.AUTH_ALG_OPEN  # Use open authentication
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # Use WPA2-PSK for security
        profile.cipher = const.CIPHER_TYPE_CCMP  # Set cipher type to CCMP

        self.iface.remove_all_network_profiles()  # Clear any previous profiles
        tmp_profile = self.iface.add_network_profile(profile)  # Add new profile

        # Attempt to connect
        self.iface.connect(tmp_profile)
        time.sleep(5)  # Allow time for the connection to be established

        # Check if connected
        if self.iface.status() == const.IFACE_CONNECTED:
            messagebox.showinfo("Success", f"Connected to {selected_network}!")
        else:
            messagebox.showerror("Failed", "Failed to connect to the network. Please check the password.")

# For testing purposes: create a root Tk window and instantiate WiFiConnectUI
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window since we are focusing on the Toplevel
    
    wifi_window = WiFiConnectUI(root)
    
    root.mainloop()
