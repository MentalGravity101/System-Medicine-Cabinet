import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class OnScreenKeyboard:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.keyboard_frame = None
        self.capslock_on = False  # Ensure CapsLock is off by default (lowercase)
        self.keys_buttons = {}  # Store button references for updating keys dynamically

        # Load and resize images for CapsLock button
        self.capslock_image_on = ImageTk.PhotoImage(
            Image.open(os.path.join(os.path.dirname(__file__), 'images', 'capsOn_icon.png')).resize((30, 30), Image.LANCZOS))
        self.capslock_image_off = ImageTk.PhotoImage(
            Image.open(os.path.join(os.path.dirname(__file__), 'images', 'capsOff_icon.png')).resize((30, 30), Image.LANCZOS))
        
    def bind_widgets(self):
        """Bind all entry and combobox widgets to show the keyboard on focus."""
        for widget in self.parent_frame.winfo_children():
            if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
                widget.bind("<FocusIn>", self.show_keyboard)  # Show keyboard on focus

    def create_keyboard(self):
        if self.keyboard_frame:
            return

        self.keyboard_frame = tk.Frame(self.parent_frame, bg='lightgrey', relief='sunken', bd=3)

        keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['CapsLock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/'],
            ['Space']
        ]

        for row in keys:
            row_frame = tk.Frame(self.keyboard_frame)
            row_frame.pack(pady=5, padx=3)

            for key in row:
                if key == "CapsLock":
                    button = tk.Button(
                        row_frame,
                        image=self.capslock_image_off,  # Image for CapsLock button
                        width=55, height=55,  # Increase width and height for better visibility
                        command=self.toggle_capslock,
                        borderwidth=0, padx=5, pady=5,
                        font=('Arial', 12),
                        relief='raised', bd=4
                    )
                elif key == "Enter":
                    button = tk.Button(
                        row_frame,
                        text=key, width=10, height=3,
                        command=lambda: self.on_key_press("Enter"),  # Ensure key is passed as "Enter"
                        font=('Arial', 12),
                        relief='raised', bd=3
                    )
                elif key == "Backspace":
                    button = tk.Button(
                        row_frame,
                        text=key, width=10, height=3,
                        font=('Arial', 12),
                        command=self.handle_backspace
                    )
                elif key == "Space":
                    button = tk.Button(
                        row_frame,
                        text=key, width=35, height=3,
                        font=('Arial', 12),
                        command=lambda: self.on_key_press(" "),  # Ensure key is passed as "Space"
                        relief='raised', bd=3
                    )
                else:
                    button = tk.Button(
                        row_frame,
                        text=key.lower(),  # Set keys to lowercase by default
                        width=6, height=3,
                        command=lambda key=key: self.on_key_press(key),
                        font=('Arial', 12),
                        relief='raised', bd=3
                    )
                    self.keys_buttons[key] = button  # Save reference to button for updates

                button.pack(side="left", padx=3)

        self.keyboard_frame.pack(side="bottom", fill="x")

    def on_key_press(self, key):
        """Handle key press event, supporting CapsLock functionality."""
        focused_widget = self.parent_frame.focus_get()

        # Handle Enter key press separately
        if key == "Enter":
            if isinstance(focused_widget, (tk.Entry, ttk.Combobox)):
                # Generate the <Return> event to simulate form submission
                focused_widget.event_generate("<Return>")
                # Hide the keyboard
                self.hide_keyboard()
                # Remove focus from the focused widget
                self.parent_frame.focus_set()  # Set focus back to the parent frame
            return  # Exit here to ensure no additional character insertion happens

        # Handle Space key separately
        if key == " ":
            if isinstance(focused_widget, tk.Entry):
                focused_widget.insert(tk.INSERT, " ")
            elif isinstance(focused_widget, ttk.Combobox):
                current_text = focused_widget.get()
                focused_widget.delete(0, tk.END)
                focused_widget.insert(0, current_text + " ")
            return  # Exit here to ensure proper space handling

        # Handle all other keys (alphabetic and others)
        # Toggle case based on CapsLock state for alphabetic characters
        if key.isalpha():
            key = key.upper() if self.capslock_on else key.lower()

        # Insert the key into the currently focused widget
        if isinstance(focused_widget, tk.Entry):
            focused_widget.insert(tk.INSERT, key)
        elif isinstance(focused_widget, ttk.Combobox):
            current_text = focused_widget.get()
            focused_widget.delete(0, tk.END)
            focused_widget.insert(0, current_text + key)

    def handle_backspace(self):
        focused_widget = self.parent_frame.focus_get()
        if isinstance(focused_widget, tk.Entry):
            cursor_pos = focused_widget.index(tk.INSERT)
            if cursor_pos > 0:
                focused_widget.delete(cursor_pos - 1, cursor_pos)
        elif isinstance(focused_widget, tk.Text):
            cursor_pos = focused_widget.index(tk.INSERT)
            if focused_widget.tag_ranges(tk.SEL):
                focused_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                row, col = map(int, cursor_pos.split('.'))
                if col > 0:
                    focused_widget.delete(f"{row}.{col-1}")
                else:
                    if row > 1:
                        prev_line_length = len(focused_widget.get(f"{row-1}.0", f"{row-1}.end"))
                        focused_widget.delete(f"{row-1}.{prev_line_length}")

    def toggle_capslock(self):
        """Toggle the CapsLock state."""
        self.capslock_on = not self.capslock_on
        self.update_capslock_button()
        self.update_keys()

    def update_capslock_button(self):
        """Update CapsLock button appearance based on the current state."""
        for row in self.keyboard_frame.winfo_children():
            for button in row.winfo_children():
                if isinstance(button, tk.Button) and button.cget("image") != "":
                    if self.capslock_on:
                        button.config(image=self.capslock_image_on)
                    else:
                        button.config(image=self.capslock_image_off)

    def update_keys(self):
        """Update displayed keys to reflect current CapsLock state (uppercase/lowercase)."""
        for key, button in self.keys_buttons.items():
            if key.isalpha():
                if self.capslock_on:
                    button.config(text=key.upper())
                else:
                    button.config(text=key.lower())

    def toggle_keyboard(self):
        if self.keyboard_frame.winfo_ismapped():
            self.hide_keyboard()
        else:
            self.show_keyboard()

    def show_keyboard(self):
        if not self.keyboard_frame:
            self.create_keyboard()
        self.keyboard_frame.pack(side="bottom", fill="x")

    def hide_keyboard(self):
        if self.keyboard_frame:
            self.keyboard_frame.pack_forget()


class NumericKeyboard:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.keyboard_frame = None
        self.create_keyboard()
        self.bind_focus_events()  # Bind focus events upon initialization

    def create_keyboard(self):
        """Creates the numeric keyboard layout."""
        if self.keyboard_frame:
            return

        self.keyboard_frame = tk.Frame(self.parent_frame, bg='lightgrey', relief='sunken', bd=3)

        # Define the keys layout
        keys = [
            ['7', '8', '9', 'Backspace'],
            ['4', '5', '6', 'Enter'],
            ['1', '2', '3', '0']
        ]

        # Load Backspace image
        backspace_image_path = os.path.join(os.path.dirname(__file__), "images", "backspace_icon.png")
        self.backspace_image = ImageTk.PhotoImage(Image.open(backspace_image_path).resize((30, 30), Image.LANCZOS))

        for row in keys:
            row_frame = tk.Frame(self.keyboard_frame)
            row_frame.pack(pady=5, padx=3)

            for key in row:
                button_config = {
                    'width': 6, 'height': 3,
                    'font': ('Arial', 12),
                    'relief': 'raised', 'bd': 3
                }
                if key == "Backspace":
                    button = tk.Button(
                        row_frame,
                        image=self.backspace_image,
                        width=55, height=55,
                        command=self.on_backspace,
                        relief='raised', bd=3
                    )
                elif key == "Enter":
                    button = tk.Button(
                        row_frame,
                        text=key,
                        command=self.on_enter,
                        **button_config
                    )
                else:
                    button = tk.Button(
                        row_frame,
                        text=key,
                        command=lambda key=key: self.on_key_press(key),
                        **button_config
                    )
                button.pack(side="left", padx=3)

        self.keyboard_frame.pack(side="bottom", fill="x")

    def on_key_press(self, key):
        """Handles key presses on the numeric keyboard."""
        focused_widget = self.parent_frame.focus_get()

        # Handle numeric input
        if isinstance(focused_widget, tk.Spinbox):
            current_value = focused_widget.get()
            # Allow adding numbers even if the current value is empty
            if current_value.isdigit() or current_value == "":
                focused_widget.delete(0, tk.END)
                focused_widget.insert(0, current_value + key)

    def on_enter(self):
        """Handles the Enter key press."""
        self.hide()  # Hide the keyboard
        focused_widget = self.parent_frame.focus_get()
        if isinstance(focused_widget, tk.Spinbox):
            focused_widget.focus_set()  # Reset focus to the Spinbox

    def on_backspace(self):
        """Handles the backspace action."""
        focused_widget = self.parent_frame.focus_get()
        if isinstance(focused_widget, tk.Spinbox):
            current_value = focused_widget.get()
            if current_value:  # Only backspace if there's something to delete
                focused_widget.delete(0, tk.END)
                focused_widget.insert(0, current_value[:-1])  # Remove last character

    def show(self):
        """Displays the numeric keyboard."""
        self.keyboard_frame.pack(side="bottom", fill="x")

    def hide(self):
        """Hides the numeric keyboard."""
        self.keyboard_frame.pack_forget()

    def bind_focus_events(self):
        """Binds focus events to show/hide the keyboard."""
        def show_keyboard(event):
            self.show()
        
        def hide_keyboard(event):
            self.hide()

        for widget in self.parent_frame.winfo_children():
            if isinstance(widget, tk.Spinbox):
                widget.bind("<FocusIn>", show_keyboard)
                widget.bind("<FocusOut>", hide_keyboard)