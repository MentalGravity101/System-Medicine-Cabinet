import tkinter as tk
from tkinter import ttk, messagebox
import pywifi
from pywifi import const
import time

class WiFiConnectUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connect to Wi-Fi")
        self.geometry("300x320")  # Adjusted height to accommodate new checkbox
        self.configure(bg='#f7f7f7')

        # Initialize PyWiFi and get the first wireless interface
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]

        # Ensure the interface is in a state that can scan
        if self.iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:
            self.iface.disconnect()
            time.sleep(1)  # Allow some time for disconnection

        self.create_widgets()

    def create_widgets(self):
        # Label for Wi-Fi networks
        tk.Label(self, text="Select Wi-Fi Network", font=("Arial", 14), bg='#f7f7f7').pack(pady=10)

        # Dropdown (Combobox) to select a Wi-Fi network
        self.network_combobox = ttk.Combobox(self, state="readonly", font=("Arial", 12))
        self.network_combobox.pack(pady=10)

        # Button to scan and populate Wi-Fi networks
        scan_button = tk.Button(self, text="Scan Networks", font=("Arial", 12), command=self.scan_wifi)
        scan_button.pack(pady=5)

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

    def toggle_password_visibility(self):
        """Toggles the visibility of the password in the password entry field."""
        if self.show_password_var.get():
            self.password_entry.config(show="")  # Show password
        else:
            self.password_entry.config(show="*")  # Hide password

    def scan_wifi(self):
        """Scans for available Wi-Fi networks and updates the dropdown list."""
        # Start scanning for networks
        self.iface.scan()
        time.sleep(5)  # Wait for scan results (increased to 5 seconds for better reliability)

        # Get the scan results
        scan_results = self.iface.scan_results()
        networks = [result.ssid for result in scan_results if result.ssid]  # Extract SSID names
        
        # Debug: Print scan results to console
        print("Found networks:", networks)

        if networks:
            self.network_combobox['values'] = networks  # Populate the combobox
            self.network_combobox.current(0)  # Set default selection
        else:
            messagebox.showinfo("Wi-Fi Scan", "No networks found!")

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
