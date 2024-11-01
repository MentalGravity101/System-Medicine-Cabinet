import tkinter as tk
from tkinter import ttk

class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self._variable = tk.StringVar()
        self['textvariable'] = self._variable
        self._variable.trace_add("write", self.on_text_change)  # Trace text changes

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)  # Sort case-insensitively
        self['values'] = self._completion_list

    def on_text_change(self, *args):
        current_text = self.get()
        if current_text:  # Only search if there's input
            # Filter completion list based on the current input
            matches = [item for item in self._completion_list if item.lower().startswith(current_text.lower())]
            if matches:
                self['values'] = matches  # Update combobox values with matching suggestions
                self.set('')  # Clear the entry field to prevent autocompletion
            else:
                self['values'] = []  # Clear values if no matches
        else:
            self['values'] = self._completion_list  # Reset if input is empty