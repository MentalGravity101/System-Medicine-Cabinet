# custom_messagebox.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import pygame

motif_color = '#42a7f5'

class CustomMessageBox:
    def __init__(self, root, title, message, color=motif_color, icon_path=None, sound_file=None, ok_callback=None, yes_callback=None, no_callback=None, close_icon_path=None, page='Home'):
        self.window = tk.Toplevel(root, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)

        self.window.attributes('-topmost', True)
        self.window.focus_set()



        # Set title and color
        self.title = title
        self.message = message
        self.color = color
        self.icon_path = icon_path
        self.sound_file = sound_file  # New parameter for sound file
        self.close_icon_path = os.path.join(os.path.dirname(__file__), 'images', 'cancel_icon.png')

        # Default behavior for callbacks
        self.ok_callback = ok_callback if ok_callback else self._default_ok_callback
        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.page = page

        # Initialize pygame mixer
        if self.sound_file:
            pygame.mixer.init()

        # Create the UI components
        self._create_ui()

        # Adjust only the height based on the message length
        self._adjust_window_height()

        # Play sound if a sound file is provided
        if self.sound_file:
            self.play_sound()

    def play_sound(self):
        """Play the sound file."""
        try:
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Sound Error: {str(e)}")

    def _adjust_window_height(self):
        """Adjust window height based on the message length while keeping the width fixed."""
        # Fixed width, dynamic height
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

        # Set the new geometry with fixed width and dynamic height
        self.window.geometry(f"{window_width}x{required_height}+{position_x}+{position_y}")

    def _create_ui(self):
        """Create UI components for the messagebox."""
        # Title frame
        title_frame = tk.Frame(self.window, bg=self.color)
        title_frame.pack(fill=tk.X)

        # Title label
        title_label = tk.Label(title_frame, text=self.title, font=('Arial', 15, 'bold'), bg=self.color, fg='white', pady=12)
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        # Add the close button icon at the top-right corner
        if self.close_icon_path:
            self.close_img = ImageTk.PhotoImage(Image.open(self.close_icon_path).resize((14, 14), Image.LANCZOS))
        else:
            self.close_img = None

        close_button = tk.Button(title_frame, image=self.close_img, command=self.destroy, bg=self.color, relief=tk.FLAT, bd=0)
        close_button.image = self.close_img  # Keep a reference to avoid garbage collection
        close_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 5))

        # Add the icon if provided
        if self.icon_path:
            self.status_img = ImageTk.PhotoImage(Image.open(self.icon_path).resize((150, 150), Image.LANCZOS))
        else:
            self.status_img = None

        # Message label (with wrapping to fit within a max width)
        logo_label = tk.Label(
            self.window, text=self.message, image=self.status_img, compound=tk.TOP,
            font=('Arial', 18), wraplength=550  # Adjust wrap length to prevent expanding horizontally
        )
        logo_label.image = self.status_img  # Keep a reference to avoid garbage collection
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
        # Set both buttons to the same width using 'sticky' and grid configuration
        yes_button = tk.Button(button_frame, text="Yes", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, command=self._yes_action)
        no_button = tk.Button(button_frame, text="No", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, command=self._no_action)

        # Make both buttons take the same grid space with sticky="ew"
        yes_button.grid(row=0, column=0, padx=50, pady=18, sticky="ew")
        no_button.grid(row=0, column=1, padx=50, pady=18, sticky="ew")

        # Set equal column weight to ensure equal button size
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

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
        

    def destroy(self):
        """Close the window."""
        self.window.destroy()
    
            

    
