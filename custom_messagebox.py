# custom_messagebox.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

motif_color = '#42a7f5'

class CustomMessageBox:
    def __init__(self, root, title, message, color=motif_color, icon_path=None, ok_callback=None, yes_callback=None, no_callback=None):
        self.window = tk.Toplevel(root, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)

        # Set title and color
        self.title = title
        self.message = message
        self.color = color
        self.icon_path = icon_path

        # Default behavior for callbacks
        self.ok_callback = ok_callback if ok_callback else self._default_ok_callback
        self.yes_callback = yes_callback
        self.no_callback = no_callback

        # Get the window dimensions and center the window
        self._set_window_position()

        # Create the UI components
        self._create_ui()

    def _set_window_position(self):
        """Set the window dimensions and center it on the screen."""
        window_width = 620
        window_height = 385
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
        self.window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _create_ui(self):
        """Create UI components for the messagebox."""
        # Title label
        tk.Label(self.window, text=self.title, font=('Arial', 25, 'bold'), bg=self.color, fg='white', pady=12).pack(fill=tk.X)

        # Add the icon if provided
        if self.icon_path:
            status_img = ImageTk.PhotoImage(Image.open(self.icon_path).resize((150, 150), Image.LANCZOS))
        else:
            status_img = None

        # Message label
        logo_label = tk.Label(self.window, text=self.message, image=status_img, compound=tk.TOP, font=('Arial', 18))
        logo_label.image = status_img  # Keep a reference to avoid garbage collection
        logo_label.pack(pady=(10, 20))

        # Button Frame
        button_frame = tk.Frame(self.window, bg=self.color)
        button_frame.pack(fill=tk.X)
        button_frame.grid_columnconfigure(0, weight=1)  # Center buttons

        if self.yes_callback and self.no_callback:
            self._create_yes_no_buttons(button_frame)
        else:
            self._create_ok_button(button_frame)

    def _create_yes_no_buttons(self, button_frame):
        """Create Yes/No buttons for confirmation dialogs."""
        yes_button = tk.Button(button_frame, text="Yes", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, command=self._yes_action)
        yes_button.grid(row=0, column=0, padx=50, pady=18, sticky="ew")

        no_button = tk.Button(button_frame, text="No", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, command=self._no_action)
        no_button.grid(row=0, column=1, padx=50, pady=18, sticky="ew")

    def _create_ok_button(self, button_frame):
        """Create an OK button if the messagebox is just an information dialog."""
        ok_button = tk.Button(button_frame, text="OK", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, command=self.ok_callback)
        ok_button.grid(row=0, column=0, padx=90, pady=18, sticky="ew")

    def _yes_action(self):
        """Trigger the yes callback and close the window."""
        if self.yes_callback:
            self.yes_callback()
        self.window.destroy()

    def _no_action(self):
        """Trigger the no callback and close the window."""
        if self.no_callback:
            self.no_callback()
        self.window.destroy()

    def _default_ok_callback(self):
        """Default OK action to just close the window."""
        self.window.destroy()