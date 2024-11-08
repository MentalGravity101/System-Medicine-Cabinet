import tkinter as tk
from tkinter import ttk

motif_color = '#42a7f5'

def table_style(type=None):
    # Treeview styling
    style = ttk.Style()
    style.configure("Treeview", rowheight=38, borderwidth=2, relief="solid", font=("Arial", 18))
    style.configure("Treeview.Heading", font=("Arial", 18, "bold"))
    style.map('Treeview', 
                background=[('selected', motif_color)],
                foreground=[('selected', 'white')])

    # Customize scrollbar
    style.configure("Vertical.TScrollbar", 
                    gripcolor=motif_color,  # Color of the grip
                    background="#f0f0f0",  # Background color of scrollbar
                    troughcolor=motif_color,  # Background color of the trough
                    arrowcolor=motif_color)  # Color of the arrows