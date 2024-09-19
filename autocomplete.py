import tkinter as tk
from tkinter import ttk
import mysql.connector
import os

# Class for Autocompletion of Combobox based on the values of the particular comboboxes
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)  # sort case insensitive
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())
        _hits = []
        for item in self._completion_list:
            if item.lower().startswith(self.get().lower()):
                _hits.append(item)
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        else:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        if self._hits:
            self.set_completion(self._hits[self._hit_index])

    def set_completion(self, completion):
        self.delete(0, tk.END)
        self.insert(0, completion)
        self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        if event.keysym in ['BackSpace', 'Left', 'Right', 'Up', 'Down', 'Shift']:
            return
        if event.keysym == 'Return':
            self.set_completion(self._hits[self._hit_index])
            return
        if event.keysym == 'Escape':
            self.delete(0, tk.END)
            self['values'] = self._completion_list
            return
        self.autocomplete()
