import tkinter as tk
from tkinter import ttk

motif_color = '#42a7f5'

class TreeViewApp:
    def __init__(self, parent_frame, columns):
        self.parent_frame = parent_frame
        self.columns = columns
        
        # Define motif color (set this to any color value you need)
        self.motif_color = motif_color
        
        # Create the treeview frame
        self.create_treeview_frame()
        
        # Set up the treeview widget with dynamic columns
        self.setup_treeview()

    def create_treeview_frame(self):
        # Treeview frame and scrollbar
        self.tree_frame = tk.Frame(self.parent_frame, bg="#f0f0f0")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_treeview(self):
        # Add styling for the treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=40, borderwidth=2, relief="solid")
        style.configure("Treeview.Heading", font=("Helvetica", 13, "bold"))
        style.map('Treeview', 
                  background=[('selected', self.motif_color)],
                  foreground=[('selected', 'white')])

        # Create the treeview with dynamic columns
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show="headings", yscrollcommand=self.tree_scroll.set, height=10)

        self.tree_scroll.config(command=self.tree.yview)

        # Configure headings and columns dynamically based on the provided columns
        for col in self.columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor=tk.CENTER, width=100)

        # Tagging for alternating row colors
        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background="#f2f2f2")

        self.tree.pack(fill="both", expand=True)
