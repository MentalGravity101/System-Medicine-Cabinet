import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import os
from PIL import Image, ImageTk, ImageSequence
from keyboard import OnScreenKeyboard
from custom_messagebox import CustomMessageBox
import serial
from withdrawal import QRCodeScanner
import mysql.connector
from datetime import datetime
import time


motif_color = '#42a7f5'

class LockUnlock:
    def __init__(self, root, keyboardframe, userName, passWord, arduino, action):

        self.user_Username = userName
        self.user_Password = passWord

        self.arduino = arduino
        self.action = action

        self.window = tk.Toplevel(root, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)

        self.keyboardFrame = keyboardframe
        # Instantiate OnScreenKeyboard
        self.keyboard = OnScreenKeyboard(self.keyboardFrame, on_close_callback=self._restore_window)
        self.keyboard.create_keyboard()
        self.keyboard.hide_keyboard()  # Initially hide the keyboard

        self.window.attributes('-topmost', True)
        self.window.focus_set()

        # Store original window position
        self.original_position = None
        self.is_moved_up = False  # Flag to track if the window is moved up

        # Add the close button icon at the top-right corner
        self.close_icon_path = os.path.join(os.path.dirname(__file__), 'images', 'cancel_icon.png')
        if self.close_icon_path:
            self.close_img = ImageTk.PhotoImage(Image.open(self.close_icon_path).resize((14, 14), Image.LANCZOS))
        else:
            self.close_img = None

        # Create the UI components
        self._create_ui()

        # Adjust only the height based on the message length
        self._adjust_window_height()



    def _adjust_window_height(self):
        """Adjust window height based on the message length while keeping the width fixed."""
        window_width = 620  # Default width
        max_label_width = 550  # Maximum width for the message label

        # Allow widgets to calculate their required dimensions
        self.window.update_idletasks()

        # Calculate the required height of the message label
        required_height = self.window.winfo_reqheight()

        # Center the window on the screen with the new height
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate the position to center the window
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (required_height / 2))

        # Store the original position for later use
        self.original_position = (position_x, position_y)

        # Set the new geometry with fixed width and dynamic height
        self.window.geometry(f"{window_width}x{required_height}+{position_x}+{position_y}")

    def _create_ui(self):
        
        # Title frame
        title_frame = tk.Frame(self.window, bg=motif_color)
        title_frame.pack(fill=tk.X)

        # Title label
        title_label = tk.Label(title_frame, text="Login Credentials", font=('Arial', 15, 'bold'), bg=motif_color, fg='white', pady=12)
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        close_button = tk.Button(title_frame, image=self.close_img, command=lambda: [self.window.destroy(), self.keyboard.hide_keyboard()], bg=motif_color, relief=tk.FLAT, bd=0)
        close_button.image = self.close_img  # Keep a reference to avoid garbage collection
        close_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 5))


        # Create a Notebook widget
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True)
        
         # Create a custom style for the Notebook tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 18, 'bold'), padding=[20, 17])  # Adjust font size and padding

        # Create frames for each tab
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)

        # Add frames to the notebook with titles
        notebook.add(tab1, text="Manual")
        notebook.add(tab2, text="QR Code")

        manual_instruction = tk.Label(tab1, text='Enter your login credentials manually\nto lock or unlock the door.', font=('Arial', 18))
        manual_instruction.pack(pady=10, anchor='center')

        username_label = tk.Label(tab1, text="Username", font=("Arial", 18))
        username_label.pack(pady=10)

        self.username_entry = tk.Entry(tab1, font=("Arial", 16), relief='sunken', bd=3)
        self.username_entry.pack(pady=5, fill='x', padx=20)

        password_label = tk.Label(tab1, text="Password", font=("Arial", 18))
        password_label.pack(pady=10)

        self.password_entry = tk.Entry(tab1, show="*", font=("Arial", 16), relief='sunken', bd=3)
        self.password_entry.pack(pady=5, fill='x', padx=20)

        # Function to show/hide password based on Checkbutton state
        def toggle_password_visibility():
            if show_password_var.get():
                self.password_entry.config(show='')
            else:
                self.password_entry.config(show='*')

        # Variable to track the state of the Checkbutton
        show_password_var = tk.BooleanVar()
        show_password_checkbutton = tk.Checkbutton(tab1, text="Show Password", variable=show_password_var,
                                                    command=toggle_password_visibility, font=("Arial", 14))
        show_password_checkbutton.pack(anchor='w', padx=20, pady=(5, 10))  # Align to the left with padding

        enter_button = tk.Button(tab1, text="Enter", font=("Arial", 18, 'bold'), bg=motif_color, fg='white', relief="raised", bd=3, pady=7, padx=40, command=self._validate_credentials)
        enter_button.pack(anchor='center', pady=(0, 10))

        # Bind the FocusIn event to show the keyboard when focused
        self.username_entry.bind("<FocusIn>", lambda event: self._show_keyboard())
        self.password_entry.bind("<FocusIn>", lambda event: self._show_keyboard())



        #TAB 2 - QR SCANNING TO LOCK OUR UNLOCK THE DOOR

        # QR Code Scanner Icon
        original_logo_img = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((170, 170), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(original_logo_img)
        logo_label = tk.Label(tab2, image=logo_img)
        logo_label.image = logo_img  # Keep reference to avoid garbage collection
        logo_label.pack(side=tk.TOP, pady=(10, 10))

        # Instruction Message
        instruction_label = tk.Label(tab2, text=f"Please scan your qrcode\nto lock or unlock the door", font=("Arial", 18), fg='black')
        instruction_label.pack(pady=10)

        # QR Code Entry Frame
        entry_frame = tk.Frame(tab2)
        entry_frame.pack(pady=(5, 3))

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(tab2, font=("Arial", 14), justify='center', width=35, relief='flat', bd=3)
        self.qr_entry.pack(pady=(10, 5))
        self.qr_entry.focus_set()

        # Label to display the contents corresponding to qrcode
        self.result_label = tk.Label(tab2, text="", font=("Arial", 15), fg='green', pady=2, height=5)
        self.result_label.pack()

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self._process_qrcode)

        # Bind the tab change event
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    #Function that validates user login credentials manually
    def _validate_credentials(self):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
            )
        cursor = conn.cursor()

        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == self.user_Username and password == self.user_Password:

            search_query = "SELECT username, accountType, position FROM users WHERE username = %s AND password = %s"
            cursor.execute(search_query, (username, password))
            result = cursor.fetchone()
            userName, accountType, position = result

            insert_query = """
                INSERT INTO door_logs (username, accountType, position, date, time, action_taken)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (userName, accountType, position, datetime.now().date(), datetime.now().time(), self.action))
            conn.commit()
            self.window.destroy()
            if self.action == "unlock":
                self._unlock_door()

                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Success",
                    message="Door lock is now unlocked.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                    ok_callback=lambda: message_box.destroy()
                )
            elif self.action == "withdraw":
                self._unlock_door()
                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Success",
                    message="Door lock is now unlocked\nYou may now proceed to withdraw medicine.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                    ok_callback= lambda: (message_box.destroy(), QRCodeScanner(self.keyboardFrame))
                )
            elif self.action == "lock":
                self._lock_door()
        else:
            message_box = CustomMessageBox(
            root=self.keyboardFrame,
            title="Error",
            message="Invalid username or password.",
            color="red",  # Background color for warning
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),  # Path to your icon
            sound_file="sounds/invalidLogin.mp3"
        )


    def _on_tab_change(self, event):
        # Check if the selected tab is tab2 and hide the keyboard
        notebook = event.widget
        if notebook.index(notebook.select()) == 1:  # Index 1 for tab2
            self._hide_keyboard()


    def _show_keyboard(self):
        """Show the keyboard and move the window up."""
        self.keyboard.show_keyboard()
        self._move_window_up()

    def _hide_keyboard(self):
        """Hide the keyboard and restore the window position."""
        self.keyboard.hide_keyboard()
        self._restore_window()

    def _move_window_up(self):
        """Move the window up when the keyboard is shown."""
        if not self.is_moved_up and self.original_position:
            # Move the window up by 200 pixels (adjust this as necessary)
            new_y_position = self.original_position[1] - 200
            self.window.geometry(f"+{self.original_position[0]}+{new_y_position}")
            self.is_moved_up = True

    def _restore_window(self):
        """Restore the window to its original position when the keyboard is destroyed."""
        if self.is_moved_up and self.original_position:
            # Restore to the original position
            self.window.geometry(f"+{self.original_position[0]}+{self.original_position[1]}")
            self.is_moved_up = False

    #Function that validates user login credentials via QR code
    def _process_qrcode(self, event):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
            )
        cursor = conn.cursor()

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
                        password="",  # Adjust according to your MySQL setup
                        database="db_medicine_cabinet"
                    )
                    cursor = conn.cursor()

                    # Check if the scanned QR code matches any user in the database
                    query = "SELECT username, password FROM users WHERE username = %s AND password = %s"
                    cursor.execute(query, (self.user_Username, self.user_Password))
                    result = cursor.fetchone()

                    if result:
                        search_query = "SELECT username, accountType, position FROM users WHERE qrcode_data = %s"
                        cursor.execute(search_query, (scanned_qr_code,))
                        user_result = cursor.fetchone()
                        userName, accountType, position = user_result
                        self.window.destroy()
                        insert_query = """
                            INSERT INTO door_logs (username, accountType, position, date, time, action_taken)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (userName, accountType, position, datetime.now().date(), datetime.now().time(), self.action))
                        conn.commit()
                        if self.action == "unlock":
                            self._unlock_door()
                            message_box = CustomMessageBox(
                                root=self.keyboardFrame,
                                title="Success",
                                message="Door lock is now unlock.",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                                ok_callback=message_box.destroy
                            )
                        elif self.action == "withdraw":
                            self._unlock_door()
                            
                            message_box = CustomMessageBox(
                                root=self.keyboardFrame,
                                title="Success",
                                message="Door lock is now unlock\nYou may now proceed to withdraw medicine.",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                                ok_callback= lambda: (message_box.destroy(), QRCodeScanner(self.keyboardFrame))
                            )
                        elif self.action == "lock":
                            self._lock_door()
                            message_box = CustomMessageBox(
                                root=self.keyboardFrame,
                                title="Success",
                                message="Door lock is now locked.",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'lock_icon.png')
                            )
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

    # Function to send the lock command
    def _lock_door(self):
        # Step 1: Check the sensors before sending the lock command
        self.arduino.write(b'check_sensors\n')  # Send "check_sensors" command to Arduino
        time.sleep(0.1)  # Brief delay to allow Arduino to process and respond

        # Step 2: Read Arduino's response
        if self.arduino.in_waiting > 0:
            response = self.arduino.readline().decode().strip()
            
            # Step 3: Proceed based on the sensor check response
            if response == "Object detected":
                self.arduino.write(b'lock\n')  # Send the "lock" command to the Arduino
                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Success",
                    message="Door lock is now locked.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'lock_icon.png')
                )
                print("Lock command sent")
            else:
                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Warning",
                    color='red',
                    message="Doors are not properly closed\nPlease close both the doors properly.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
                )
                print("Lock command aborted: No object detected.")

    # Function to send the unlock command
    def _unlock_door(self):
        print("Unlock command sent")
        self.arduino.write(b'unlock\n')  # Send the "unlock" command to the Arduino
        

