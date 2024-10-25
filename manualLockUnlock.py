import tkinter as tk
from tkinter import messagebox
import mysql.connector
import os
from PIL import Image, ImageTk, ImageSequence
from keyboard import OnScreenKeyboard

motif_color = '#42a7f5'

class ManualCabinet:
    def __init__(self, root, keyboardframe):
        self.window = tk.Toplevel(root, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)

        self.keyboardFrame = keyboardframe
        # Instantiate OnScreenKeyboard
        self.keyboard = OnScreenKeyboard(self.keyboardFrame)
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

        title = tk.Label(self.window, text='ELECTRONIC\nMEDICINE CABINET', font=('Arial', 23, 'bold'))
        title.pack()

        username_label = tk.Label(self.window, text="Username", font=("Arial", 18))
        username_label.pack(pady=10)

        username_entry = tk.Entry(self.window, font=("Arial", 16), relief='sunken', bd=3)
        username_entry.pack(pady=5, fill='x', padx=20)

        password_label = tk.Label(self.window, text="Password", font=("Arial", 18))
        password_label.pack(pady=10)

        password_entry = tk.Entry(self.window, show="*", font=("Arial", 16), relief='sunken', bd=3)
        password_entry.pack(pady=5, fill='x', padx=20)

        # Function to show/hide password based on Checkbutton state
        def toggle_password_visibility():
            if show_password_var.get():
                password_entry.config(show='')
            else:
                password_entry.config(show='*')

        # Variable to track the state of the Checkbutton
        show_password_var = tk.BooleanVar()
        show_password_checkbutton = tk.Checkbutton(self.window, text="Show Password", variable=show_password_var,
                                                    command=toggle_password_visibility, font=("Arial", 14))
        show_password_checkbutton.pack(anchor='w', padx=20, pady=(5, 10))  # Align to the left with padding

        # Button Frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X)
        button_frame.grid_columnconfigure(0, weight=1)  # Center buttons

        enter_button = tk.Button(button_frame, text="Enter", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7)
        enter_button.pack()

        qr_button = tk.Button(button_frame, text="QR Code", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7)
        qr_button.pack()

        # Bind the FocusIn event to show the keyboard when focused
        username_entry.bind("<FocusIn>", lambda event: self._show_keyboard())
        password_entry.bind("<FocusIn>", lambda event: self._show_keyboard())

        # Bind FocusOut to hide the keyboard when losing focus (optional)
        username_entry.bind("<FocusOut>", lambda event: self._hide_keyboard())
        password_entry.bind("<FocusOut>", lambda event: self._hide_keyboard())

        if self.keyboard.returnClose == "Closed":
            self._restore_window()

    # def _monitor_keyboard(self):
    #     """Monitor the existence of the keyboard frame and adjust the Toplevel window position accordingly."""
    #     if self.keyboard.winfo_exists():
    #         # Move the window up when keyboard exists
    #         self._move_window_up()
    #     else:
    #         # Restore the window to its original position
    #         self._restore_window()

    #     # Continue monitoring every 100 milliseconds
    #     self.window.after(100, self._monitor_keyboard)

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

