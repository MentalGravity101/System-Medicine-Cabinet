import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sqlite3
import qrcode
from tkinter import messagebox
import io
from tkcalendar import DateEntry
from datetime import datetime

INACTIVITY_PERIOD = 60000 #automatic logout timer in milliseconds
inactivity_timer = None #initialization of idle timer
root = None  # Global variable for root window
login_frame = None

motif_color = '#42a7f5'

# Define the active and default background colors for Sidebar
active_bg_color = "#fff"  # Active background color
default_bg_color = motif_color  # Default background color
active_fg_color ='#000000' # Active foreground color
default_fg_color="#fff" # Default foreground color


#----------------------------------------------------LOGIN WINDOW--------------------------------------------------------

#function for authentication during the login frame
def authenticate_user(username, password):
    conn = sqlite3.connect('Medicine Cabinet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        user_role = user[2] 
        main_ui_frame.tkraise()
        reset_timer()
        bind_activity_events()
        show_medicine_supply()
        configure_sidebar(user_role)
        not_lock()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

#function to create the UI of login frame
def create_login_frame(container):
    global login_frame
    login_frame = tk.Frame(container, bg=motif_color)
    box_frame = tk.Frame(login_frame, bg='#ffffff', bd=5, relief="ridge", padx=50, pady=30)
    box_frame.place(relx=0.5, rely=0.5, anchor='center')
    tk.Label(box_frame, text='ELECTRONIC \n MEDICINE CABINET', font=('Arial', 23, 'bold'), bg='white').pack()
    logo_path = os.path.join(os.path.dirname(__file__), 'images', 'SanMateoLogo.png')
    original_logo_img = Image.open(logo_path)
    desired_width = 200
    desired_height = 200
    resized_logo_img = original_logo_img.resize((desired_width, desired_height), Image.LANCZOS)
    logo_img = ImageTk.PhotoImage(resized_logo_img)
    logo_label = tk.Label(box_frame, image=logo_img, bg='#ffffff')
    logo_label.image = logo_img
    logo_label.pack(pady=(20, 10))
    username_label = tk.Label(box_frame, text="Username", font=("Arial", 18), bg='#ffffff')
    username_label.pack(pady=10)
    global username_entry
    username_entry = tk.Entry(box_frame, font=("Arial", 16), relief='sunken', bd=3, width=25)
    username_entry.pack(pady=5)
    password_label = tk.Label(box_frame, text="Password", font=("Arial", 18), bg='#ffffff')
    password_label.pack(pady=10)
    password_frame = tk.Frame(box_frame, bg='#ffffff')
    password_frame.pack(pady=5, fill='x')
    global password_entry
    password_entry = tk.Entry(password_frame, show="*", font=("Arial", 16), relief='sunken', bd=3, width=20)
    password_entry.pack(side='left', fill='x', expand=True)
    eye_open_image = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'eye_open.png')).resize((20, 20), Image.LANCZOS))
    eye_closed_image = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'eye_close.png')).resize((20, 20), Image.LANCZOS))
    
    #function for toggleable hidden/visible password (eye icon)
    def toggle_password():
        if password_entry.cget('show') == '':
            password_entry.config(show='*')
            toggle_button.config(image=eye_closed_image)
        else:
            password_entry.config(show='')
            toggle_button.config(image=eye_open_image)
    toggle_button = tk.Button(password_frame, image=eye_closed_image, bg='#ffffff', command=toggle_password, bd=0)
    toggle_button.pack(side='right')
    login_button = tk.Button(box_frame, text="Login", font=("Arial", 16), command=lambda: authenticate_user(username_entry.get(), password_entry.get()), fg='#ffffff', bg='#2c3e50', width=20)
    login_button.pack(pady=20)
    login_frame.grid(row=0, column=0, sticky='nsew')
    return login_frame


# -----------------------------------------------MAIN UI (Sidebar)------------------------------------------------------

#functin to create the UI of Main UI Frame, including the sidebar navigation
def create_main_ui_frame(container): 
    global main_ui_frame
    main_ui_frame = tk.Frame(container, bg=motif_color)
    global content_frame, inventory_img, cabinet_img, notification_img, account_setting_img
    global sidebar_frame
    sidebar_frame = tk.Frame(main_ui_frame, bg=motif_color, height=768, relief='raised', borderwidth=3)
    sidebar_frame.pack(expand=False, fill='both', side='left', anchor='ne')
    sidebar_frame.grid_columnconfigure(1, weight=1)
    logo_path = os.path.join(os.path.dirname(__file__), 'images', 'SanMateoLogo.png')
    original_logo_img = Image.open(logo_path)
    desired_width = 100
    desired_height = 100
    title_frame = tk.Frame(sidebar_frame, bg=motif_color, relief='raised', bd=5)
    title_frame.grid(row=0, column=0, columnspan=2, sticky='new')
    resized_logo_img = original_logo_img.resize((desired_width, desired_height), Image.LANCZOS)
    logo_img = ImageTk.PhotoImage(resized_logo_img)
    logo_label = tk.Label(title_frame, image=logo_img, bg=motif_color)
    logo_label.image = logo_img
    logo_label.grid(row=0, column=0, pady=5, padx=10, sticky="w")
    app_name_label = tk.Label(title_frame, text="Barangay San Mateo \nHealth Center\nMedicine Cabinet", font=("Arial", 18), fg="white", bg=motif_color, justify="left")
    app_name_label.grid(row=0, column=1, pady=10, padx=0, sticky="w", columnspan=1)
    inventory_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'inventory_icon.png')).resize((40, 40), Image.LANCZOS))
    global inventory_button
    inventory_button = tk.Button(sidebar_frame, height=100, width=350, text="Medicine Inventory", command=show_medicine_supply, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=inventory_img, padx=10)
    inventory_button.image = inventory_img
    inventory_button.grid(row=1, column=0, sticky="w", columnspan=2)
    doorLogs_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cabinet_Icon.png')).resize((40, 40), Image.LANCZOS))
    global doorLogs_button
    doorLogs_button = tk.Button(sidebar_frame, height=100, width=350, text="Door Functions", command=show_doorLog, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=doorLogs_img, padx=10)
    doorLogs_button.image = doorLogs_img
    doorLogs_button.grid(row=2, column=0, sticky="we", columnspan=2)
    notification_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'notification_Icon.png')).resize((40, 40), Image.LANCZOS))
    global notification_button
    notification_button = tk.Button(sidebar_frame, height=100, width=350, text="Notification", command=show_notification, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=notification_img, justify="left", padx=10)
    notification_button.image = notification_img
    notification_button.grid(row=4, column=0, sticky="we", columnspan=2)
    
    account_setting_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'accountSetting_Icon.png')).resize((40, 40), Image.LANCZOS))
    global account_setting_button
    account_setting_button = None
    
    logout_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'logout_icon.png')).resize((40, 40), Image.LANCZOS))
    logout_button = tk.Button(sidebar_frame, height=100, width=350, text="Log Out", command=lambda: logout('manual logout'), font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=logout_img, padx=10)
    logout_button.image = logout_img
    logout_button.grid(row=6, column=0, sticky="we", columnspan=2)
    content_frame = tk.Frame(main_ui_frame, bg='#ecf0f1')
    content_frame.pack(expand=True, fill='both', side='right')
    main_ui_frame.grid(row=0, column=0, sticky='nsew')
    show_medicine_supply()
    return main_ui_frame

#Function to handle the background colors of sidebar buttons
def reset_button_colors():
    inventory_button.config(bg=default_bg_color)
    inventory_button.config(fg=default_fg_color)
    notification_button.config(bg=default_bg_color)
    notification_button.config(fg=default_fg_color)
    doorLogs_button.config(bg=default_bg_color)
    doorLogs_button.config(fg=default_fg_color)
    if account_setting_button:
        account_setting_button.config(bg=default_bg_color)
        account_setting_button.config(fg=default_fg_color)

#Function that checks if the user is an 'Admin' or 'Staff' to configure the sidebar,
def configure_sidebar(user_role):
    global account_setting_button
    if user_role == "Admin":     #if the user is 'Admin' then the account setting button will be present in the sidebar
        if account_setting_button is None:
            account_setting_button = tk.Button(sidebar_frame, height=100, width=350, text="   Account Settings", command=show_account_setting, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="groove", compound=tk.LEFT, image=account_setting_img, padx=10)
            account_setting_button.image = account_setting_img
        account_setting_button.grid(row=5, column=0, sticky="we", columnspan=2)
    else:
        if account_setting_button:
            account_setting_button.grid_remove()


# -------------------------------------------------------------LOGOUT AND IDLE--------------------------------------------------------------------
#Function for log out and ressetting of UIs
def logout(reason):
    global inactivity_timer
    global account_setting_button
    clear_frame()
    unbind_activity_events()
    if inactivity_timer:
        root.after_cancel(inactivity_timer)
        inactivity_timer = None
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel):
            window.destroy()
    login_frame.tkraise()
    if account_setting_button:
        account_setting_button.grid_remove()
    account_setting_button = None
    if reason == 'inactivity':
        messagebox.showinfo('Logged Out', 'You have been logged out due to inactivity.')

#Function that initialize the counting for user idle
def start_timer():
    global inactivity_timer
    if inactivity_timer:
        root.after_cancel(inactivity_timer)
    inactivity_timer = root.after(INACTIVITY_PERIOD, automatic_logout)

#Function that resets the idle timer if the user has an activity in the Main UI Frame or Toplevels
def reset_timer(event=None):
    start_timer()

#Function for automatic logout during idle
def automatic_logout():
    print("User has been automatically logged out due to inactivity.")
    logout('inactivity')

#Function for binding user activities in the Main UI Frame and toplevels
def bind_activity_events():
    activity_events = ["<Motion>", "<KeyPress>", "<ButtonPress>"]
    for event in activity_events:
        root.bind(event, reset_timer)

#Function for unbinding user activities in the Main UI Frame and toplevels
def unbind_activity_events():
    activity_events = ["<Motion>", "<KeyPress>", "<ButtonPress>"]
    for event in activity_events:
        root.unbind(event)

        
#--------------------------------------------------------------MEDICINE INVENTORY---------------------------------------------------------------------    

#Function that creates a pop-up window (toplevel) for depositing medicine
def deposit_window():
    deposit_toplevel = tk.Toplevel(relief='groove', bd=5)
    deposit_toplevel.overrideredirect(True)  # Remove the title bar
    deposit_toplevel.resizable(width=False, height=False)

    # Get the window dimensions
    deposit_toplevel.update_idletasks()  # Ensure the window size is calculated
    window_width = 620  # Adjust the width as needed
    window_height = 580  # Adjust the height as needed

    # Calculate the center position
    screen_width = deposit_toplevel.winfo_screenwidth()
    screen_height = deposit_toplevel.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the window position
    deposit_toplevel.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Bind activity events to the edit_window to reset the inactivity timer
    deposit_toplevel.bind("<Motion>", reset_timer)
    deposit_toplevel.bind("<KeyPress>", reset_timer)
    deposit_toplevel.bind("<ButtonPress>", reset_timer)

    # Ensure the inactivity timer starts when the edit_window is shown
    start_timer()

    title_label = tk.Label(deposit_toplevel, text="Deposit Medicine", font=("Arial", 18, "bold"), bg=motif_color, fg='white')
    title_label.grid(row=0, column=0, columnspan=2, sticky='new')

    # Display QR code if it exists
    qr_image = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'image_icon.png')).resize((200, 200), Image.LANCZOS))
    qr_code_image_label = tk.Label(deposit_toplevel, image=qr_image)
    qr_code_image_label.image = qr_image
    qr_code_image_label.grid(row=1, column=0, columnspan=2, pady=10)

    input_frame = tk.Frame(deposit_toplevel)
    input_frame.grid(row=2, column=0, sticky='new')

    # Ensure the input_frame expands to fill the available space
    input_frame.grid_rowconfigure(1, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)

    # Labels and AutocompleteComboboxes for the form
    tk.Label(input_frame, text="Name of Medicine", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10)
    name_combobox = AutocompleteCombobox(input_frame, font=("Arial", 16), width=20)
    name_combobox.set_completion_list(["Biogesic", "Alaxan", "Mefenamic", "Paracetamol"])
    name_combobox.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Type", font=("Arial", 16)).grid(row=1, column=0, padx=10, pady=10)
    type_combobox = AutocompleteCombobox(input_frame, font=("Arial", 16), width=20)
    type_combobox.set_completion_list(["Hypertension", "Fever", "Pain Reliever"])
    type_combobox.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Quantity", font=("Arial", 16)).grid(row=2, column=0, padx=10, pady=10)
    quantity_spinbox = tk.Spinbox(input_frame, from_=0, to=100, font=("Arial", 16), width=20)
    quantity_spinbox.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Unit", font=("Arial", 16)).grid(row=3, column=0, padx=10, pady=10)
    unit_combobox = AutocompleteCombobox(input_frame, font=("Arial", 16), width=20)
    unit_combobox.set_completion_list(["Tablet", "Syrup", "Pieces", "Box"])
    unit_combobox.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Expiration Date", font=("Arial", 16)).grid(row=4, column=0, padx=10, pady=10)
    expiration_date_entry = DateEntry(input_frame, font=("Arial", 16), date_pattern='mm-dd-y', width=20)
    expiration_date_entry.grid(row=4, column=1, padx=10, pady=10)
    
    button_frame = tk.Frame(deposit_toplevel, bg=motif_color, pady=10)
    button_frame.grid(row=3, column=0, columnspan=2, sticky='ews')

    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(button_frame, text="Cancel", font=("Arial", 14), command=lambda: toplevel_destroy(deposit_toplevel), width=118, padx=10, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img)
    cancel_button.image = cancel_img
    cancel_button.grid(row=0, column=0, padx=79)

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(button_frame, text="Save", font=("Arial", 14), width=118, padx=10, relief="raised", bd=3, compound=tk.LEFT, image=save_img)
    save_button.image = save_img
    save_button.grid(row=0, column=1, padx=79)

#Function that creates the UI for medicine inventory in the content_frame
def show_medicine_supply():
    clear_frame()
    reset_button_colors()

    inventory_button.config(bg=active_bg_color)
    inventory_button.config(fg=active_fg_color)

    # Track the current active sort order and column
    global active_column, sort_order, search_term, active_column_logs, sort_order_logs
    active_column = "date_stored"  # Default sorting column
    sort_order = "ASC"  # Default sorting order
    active_column_logs = "date"  # Default sorting column
    sort_order_logs = "ASC"  # Default sorting order
    search_term = ""  # Store the search term globally
    search_term_logs = ""  # Store the search term globally

    # Create a custom style for the notebook tabs
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 14), padding=[20, 10])
    style.configure("TNotebook.Tab", background="white", foreground="black", borderwidth=1)
    style.map("TNotebook.Tab", background=[("selected", motif_color)], foreground=[("selected", "black")], borderwidth=[("selected", 1)])

    header_frame = tk.Frame(content_frame, bg=motif_color)
    header_frame.pack(fill="x", pady=10)

    def activate_button(clicked_button):
        for btn in buttons:
            btn.config(bg=motif_color, fg="white")
        clicked_button.config(bg="white", fg="black")

    def search_treeview():
        global search_term
        search_term = search_entry.get().lower()
        if search_term == "search here" or not search_term:
            search_term = ""
        populate_treeview()  # Repopulate with search filter

    def clear_placeholder(event=None):
        if search_entry.get() == 'Search here':
            search_entry.delete(0, tk.END)
            search_entry.config(fg='black')

    def add_placeholder(event):
        if not search_entry.get():
            search_entry.insert(0, 'Search here')
            search_entry.config(fg='grey')

    def clear_search():
        global search_term
        search_term = ""
        search_entry.delete(0, tk.END)
        search_entry.insert(0, 'Search here')
        search_entry.config(fg='grey')
        populate_treeview()

    def populate_treeview(order_by="date_stored", sort="ASC"):
        # Clear the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Fetch all data from the database first
        conn = sqlite3.connect('Medicine Cabinet.db')
        cursor = conn.cursor()
        query = f"SELECT name, type, quantity, unit, date_stored, expiration_date FROM medicine_inventory ORDER BY {order_by} {sort}"
        cursor.execute(query)
        medicine = cursor.fetchall()
        conn.close()

        # Filter data in Python based on the search term
        filtered_medicine = []
        search_term_lower = search_term.lower()

        for med in medicine:
            name, type, quantity, unit, date_stored, expiration_date = med
            # Generate both abbreviated and full month names for comparison
            date_stored_abbr = datetime.strptime(date_stored, "%Y-%m-%d").strftime("%b %d, %Y").lower()
            date_stored_full = datetime.strptime(date_stored, "%Y-%m-%d").strftime("%B %d, %Y").lower()
            expiration_date_abbr = datetime.strptime(expiration_date, "%Y-%m-%d").strftime("%b %d, %Y").lower()
            expiration_date_full = datetime.strptime(expiration_date, "%Y-%m-%d").strftime("%B %d, %Y").lower()

            # Check if the search term matches any of the fields
            if (
                search_term_lower in name.lower() or
                search_term_lower in type.lower() or
                search_term_lower in unit.lower() or
                search_term_lower in str(quantity).lower() or
                search_term_lower in date_stored_abbr or
                search_term_lower in date_stored_full or
                search_term_lower in expiration_date_abbr or
                search_term_lower in expiration_date_full
            ):
                filtered_medicine.append(med)

        # Use the filtered results to populate the Treeview
        for i, med in enumerate(filtered_medicine):
            name, type, quantity, unit, date_stored, expiration_date = med
            date_stored_str = datetime.strptime(date_stored, "%Y-%m-%d").strftime("%b %d, %Y")
            expiration_date_str = datetime.strptime(expiration_date, "%Y-%m-%d").strftime("%b %d, %Y")
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(name, type, quantity, unit, date_stored_str, expiration_date_str), tags=(tag,))


    def sort_treeview(column, clicked_button):
        global active_column, sort_order
        activate_button(clicked_button)

        # Set the active column and toggle sort order
        if active_column == column:
            sort_order = "DESC" if sort_order == "ASC" else "ASC"
        else:
            active_column = column
            sort_order = "ASC"

        # Repopulate the treeview with the current search term and sort order
        populate_treeview(order_by=active_column, sort=sort_order)

    # Load the search icon image
    search_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'search_icon.png')).resize((14, 14), Image.LANCZOS))

    # Create a Frame to hold the Entry and the search icon
    search_frame = tk.Frame(header_frame, bg='white')
    search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # Create the Entry widget (search bar)
    search_entry = tk.Entry(search_frame, width=25, fg='grey', font=('Arial', 12))
    search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    search_entry.insert(0, 'Search here')

    # Bind events to the search bar
    search_entry.bind("<FocusIn>", clear_placeholder)
    search_entry.bind("<FocusOut>", add_placeholder)
    search_entry.bind("<KeyPress>", clear_placeholder)
    search_entry.bind("<Return>", lambda event: search_treeview())

    # Add the search icon next to the Entry widget
    search_icon_label = tk.Label(search_frame, image=search_img, bg='white')
    search_icon_label.image = search_img  # Keep a reference to avoid garbage collection
    search_icon_label.pack(side=tk.RIGHT, padx=(0, 5))
    buttons = []

    #Sorting buttons
    sort_button_1 = tk.Button(header_frame, text="Sort by Name", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("name", sort_button_1), relief="raised", bd=4)
    sort_button_1.grid(row=0, column=2, padx=(110, 0), pady=10, sticky="e")
    buttons.append(sort_button_1)

    sort_button_2 = tk.Button(header_frame, text="Sort by Type", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("type", sort_button_2), relief="raised", bd=4)
    sort_button_2.grid(row=0, column=3, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_2)

    sort_button_3 = tk.Button(header_frame, text="Sort by Unit", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("unit", sort_button_3), relief="raised", bd=4)
    sort_button_3.grid(row=0, column=4, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_3)

    sort_button_4 = tk.Button(header_frame, text="Sort by Expiration Date", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("expiration_date", sort_button_4), relief="raised", bd=4)
    sort_button_4.grid(row=0, column=5, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_4)

    sort_button_5 = tk.Button(header_frame, text="Sort by Date Stored", bg="white", fg=motif_color, padx=10, pady=5,
                              command=lambda: sort_treeview("date_stored", sort_button_5), relief="raised", bd=4)
    sort_button_5.grid(row=0, column=6, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_5)

    activate_button(sort_button_5)

    tree_frame = tk.Frame(content_frame)
    tree_frame.pack(fill="both", expand=True)

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    columns = ("name", "type", "quantity", "unit", "date stored", "expiration date")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set, height=15)

    tree_scroll.config(command=tree.yview)

    tree.heading("name", text="Name")
    tree.heading("type", text="Type")
    tree.heading("quantity", text="Quantity")
    tree.heading("unit", text="Unit")
    tree.heading("date stored", text="Date Stored")
    tree.heading("expiration date", text="Expiration Date")

    tree.column("name", width=160)
    tree.column("type", width=170)
    tree.column("quantity", width=120)
    tree.column("unit", width=140)
    tree.column("date stored", width=150)
    tree.column("expiration date", width=150)

    conn = sqlite3.connect('Medicine Cabinet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, type, quantity, unit, date_stored, expiration_date FROM medicine_inventory ORDER BY date_stored")
    medicine = cursor.fetchall()
    conn.close()

    style.configure("Treeview", rowheight=30, font=('Arial', 12))
    style.configure("Treeview.Heading", font=('Arial', 14, 'bold'), padding=[10, 5])

    # Custom tag styles
    tree.tag_configure('oddrow', background="white")
    tree.tag_configure('evenrow', background="#ebebeb")
    style.map('Treeview', background=[('selected', motif_color)])

    for i, med in enumerate(medicine):
        name, type, quantity, unit, date_stored, expiration_date = med
        date_stored = datetime.strptime(date_stored, "%Y-%m-%d").strftime("%b %d, %Y")
        expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").strftime("%b %d, %Y")
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=(name, type, quantity, unit, date_stored, expiration_date), tags=(tag,))

    tree.pack(fill="both", expand=True)

    # Create a frame for the buttons below the Treeview
    button_frame = tk.Frame(content_frame, bg='white', padx=30)
    button_frame.pack(fill="x", anchor='e')  # Align to the right

    # Configure the columns in button_frame to distribute buttons evenly
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.columnconfigure(3, weight=1)

    # Add the first new button (e.g., 'Button 1')
    widthdraw_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'minus_icon.png')).resize((25, 25), Image.LANCZOS))
    withdraw_button = tk.Button(button_frame, text="Withdraw", padx=20, pady=10, font=('Arial', 15), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=widthdraw_icon, command=unlocked)
    withdraw_button.image = widthdraw_icon
    withdraw_button.grid(row=0, column=0, padx=20, pady=(12, ), sticky='ew')

    # Add the second new button (e.g., 'Button 2')
    deposit_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'add_icon.png')).resize((25, 25), Image.LANCZOS))
    deposit_button = tk.Button(button_frame, text="Deposit", padx=20, pady=10, font=('Arial', 15), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=deposit_icon,command=deposit_window)
    deposit_button.image = deposit_icon
    deposit_button.grid(row=0, column=1, padx=20, pady=(12, 7), sticky='ew')

    # Extract CSV button
    extract_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'extract_icon.png')).resize((25, 25), Image.LANCZOS))
    extract_button = tk.Button(button_frame, text="Extract CSV", padx=20, pady=10, font=('Arial', 15), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=extract_img)
    extract_button.image = extract_img
    extract_button.grid(row=0, column=2, padx=20, pady=(12, 7), sticky='ew')

    # Reload All button
    refresh_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'refresh_icon.png')).resize((25, 25), Image.LANCZOS))
    refresh_button = tk.Button(button_frame, text="Reload All", padx=20, pady=10, font=('Arial', 15), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=refresh_img, command=clear_search)
    refresh_button.image = refresh_img
    refresh_button.grid(row=0, column=3, padx=20, pady=(12, 7), sticky='ew')





#--------------------------------------------------------- DOOR FUNCTIONS -----------------------------------------------------------       

#Function that creates the UI for door function in the content_frame
def show_doorLog():
    clear_frame()
    reset_button_colors()
    doorLogs_button.config(bg=active_bg_color)
    doorLogs_button.config(fg=active_fg_color)
    tk.Label(content_frame, text="Door Logs Content", bg="#121212", fg="white").pack()
    doorLogs_label = tk.Label(content_frame, text="Door Logs Page", font=("Arial", 24))
    doorLogs_label.pack()




#--------------------------------------------------------- NOTIFICATION -----------------------------------------------------------       

#Function that creates the UI for notification in the content_frame
def show_notification():
    clear_frame()
    reset_button_colors()
    notification_button.config(bg=active_bg_color)
    notification_button.config(fg=active_fg_color)
    tk.Label(content_frame, text="Notification Content", bg="#121212", fg="white").pack()
    notification_label = tk.Label(content_frame, text="Notification Page", font=("Arial", 24))
    notification_label.pack()




#------------------------------------------------------ACCOUNT SETTINGS FRAME----------------------------------------------------------------------
image_refs = []
def show_account_setting():
    clear_frame()
    reset_button_colors()
    if account_setting_button:
        account_setting_button.config(bg=active_bg_color)
        account_setting_button.config(fg=active_fg_color)
    
    tk.Label(content_frame, text="ACCOUNT SETTINGS", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1).pack(fill='x')

    # Create a frame for the treeview
    tree_frame = tk.Frame(content_frame)
    tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Add styling for the treeview
    style = ttk.Style()
    style.configure("Treeview", rowheight=40, borderwidth=2, relief="solid")
    style.map('Treeview', 
              background=[('selected', motif_color)],
              foreground=[('selected', 'white')])

    # Define the treeview with a maximum height of 7 rows
    columns = ("username", "position", "accountType")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=7)
    
    # Define headings
    tree.heading("username", text="Username")
    tree.heading("position", text="Position")
    tree.heading("accountType", text="Account Type")

    # Define column widths
    tree.column("username", width=150)
    tree.column("position", width=150)
    tree.column("accountType", width=150)

    # Insert data into the treeview with alternating row colors
    conn = sqlite3.connect('Medicine Cabinet.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, position, accountType FROM users ORDER BY accountType ASC")
    users = cursor.fetchall()
    conn.close()

    for i, user in enumerate(users):
        username, position, accountType = user
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=(username, position, accountType), tags=(tag,))

    # Configure the row tags for alternating colors
    tree.tag_configure('evenrow', background='#ebebeb')
    tree.tag_configure('oddrow', background='white')

    # Pack the Treeview within the frame
    tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    # Create a frame for the buttons below the Treeview
    button_frame = tk.Frame(content_frame)
    button_frame.pack(padx=50, pady=10, fill=tk.X)  # Ensure this frame is packed below

    # Use grid layout for equally spaced buttons
    button_frame.columnconfigure([0, 1, 2], weight=1)  # Equal weight to all columns

    add_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'add_icon.png')).resize((25, 25), Image.LANCZOS))
    add_button = tk.Button(button_frame, text="Add User", font=("Arial", 15), pady=20, padx=25, bg=motif_color, fg='white', height=25, relief="raised", bd=3, compound=tk.LEFT, image=add_img, command=add_user)
    add_button.image = add_img
    add_button.grid(row=0, column=0, padx=30, pady=10, sticky="ew")

    edit_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'edit_icon.png')).resize((25, 25), Image.LANCZOS))
    edit_button = tk.Button(button_frame, text="Edit User", font=("Arial", 15), pady=20, padx=25, bg=motif_color, fg='white', height=25, relief="raised", bd=3, compound=tk.LEFT, image=edit_img, command=lambda: on_tree_select(tree))
    edit_button.image = edit_img
    edit_button.grid(row=0, column=1, padx=30, pady=10, sticky="ew")

    delete_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'delete_icon.png')).resize((25, 25), Image.LANCZOS))
    delete_button = tk.Button(button_frame, text="Delete User", font=("Arial", 15), pady=20, padx=25, bg=motif_color, fg='white', height=25, relief="raised", bd=3, compound=tk.LEFT, image=delete_img, command=lambda: delete_selected_user(tree))
    delete_button.image = delete_img
    delete_button.grid(row=0, column=2, padx=30, pady=10, sticky="ew")




def delete_selected_user(tree):
    selected_item = tree.selection()  # Get selected item
    if selected_item:
        username = tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the user '{username}'?"):
            conn = sqlite3.connect('Medicine Cabinet.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            show_account_setting()

def on_tree_select(tree):
    selected_item = tree.selection()  # Get selected item
    if selected_item:
        username = tree.item(selected_item, "values")[0]
        edit_user(username)
    else:
        messagebox.showwarning("Select a User", "Please select a user from the list to edit.")


def validate_all_fields_filled(*widgets):
    for widget in widgets:
        if isinstance(widget, tk.Entry):
            if not widget.get():
                return False
        elif isinstance(widget, ttk.Combobox):
            if not widget.get():
                return False
    return True

def validate_user_info(action, username, password, confirm_password, new_position, new_accountType):
    # Validate username uniqueness
    conn = sqlite3.connect('Medicine Cabinet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    username_exists = cursor.fetchone()[0] > 0
    cursor.execute("SELECT COUNT(*) FROM users WHERE accountType = 'Admin'")
    admin_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE accountType = 'Staff'")
    staff_count = cursor.fetchone()[0]
    conn.close()

    if action == 'edit':
        if new_accountType == 'Admin' and admin_count >= 2:
            messagebox.showerror("Error", "Maximum 2 admin accounts allowed.")
            return 
        elif new_accountType == 'Staff' and staff_count >= 5:
            messagebox.showerror("Error", "Maximum 5 staff accounts allowed.")
            return
        return True
    elif action == 'add':
        if username_exists:
            messagebox.showerror("Error", "Username already exists.")
            return False

    # Validate password strength
    if len(password) < 6 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        messagebox.showerror("Error", "Password must be at least 6 characters long and contain both letters and numbers.")
        return False

    # Validate password match
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return False
    
    # Check if adding another user exceeds the limit
    if new_accountType == 'Admin' and admin_count >= 2:
        messagebox.showerror("Error", "Maximum 2 admin accounts allowed.")
        return
    elif new_accountType == 'Staff' and staff_count >= 5:
        messagebox.showerror("Error", "Maximum 5 staff accounts allowed.")
        return
    return True

def toplevel_destroy(window):
        window.destroy()

def edit_user(username):
    edit_window = tk.Toplevel(relief='groove', bd=5)
    edit_window.overrideredirect(True)  # Remove the title bar
    edit_window.resizable(width=False, height=False)

    # Get the window dimensions
    edit_window.update_idletasks()  # Ensure the window size is calculated
    window_width = 620  # Adjust the width as needed
    window_height = 650  # Adjust the height as needed

    # Calculate the center position
    screen_width = edit_window.winfo_screenwidth()
    screen_height = edit_window.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the window position
    edit_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Bind activity events to the edit_window to reset the inactivity timer
    edit_window.bind("<Motion>", reset_timer)
    edit_window.bind("<KeyPress>", reset_timer)
    edit_window.bind("<ButtonPress>", reset_timer)

    # Ensure the inactivity timer starts when the edit_window is shown
    start_timer()
    
    conn = sqlite3.connect('Medicine Cabinet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT position, accountType, password, qr_code FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    # Title label
    title_label = tk.Label(edit_window, text="Edit User Information", font=("Arial", 18, "bold"), bg=motif_color, fg='white')
    title_label.grid(row=0, column=0, columnspan=2, sticky='new', padx=(0, 10))

    # Display QR code if it exists
    qr_code_image_label = tk.Label(edit_window)
    qr_code_image_label.grid(row=1, column=0, columnspan=2, pady=10)

    if user[3]:  # Check if qr_code is not None
        qr_image = ImageTk.PhotoImage(Image.open(io.BytesIO(user[3])))
        qr_code_image_label.config(image=qr_image)
        qr_code_image_label.image = qr_image    
    
    tk.Label(edit_window, text="Username", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10)
    username_entry = tk.Entry(edit_window, font=("Arial", 14))
    username_entry.grid(row=2, column=1, padx=10, pady=10)
    username_entry.insert(0, username)
    
    tk.Label(edit_window, text="Password", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)
    password_entry = tk.Entry(edit_window, show="*", font=("Arial", 14))
    password_entry.grid(row=3, column=1, padx=10, pady=10)
    password_entry.insert(0, user[2])
    
    tk.Label(edit_window, text="Confirm Password", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10)
    confirm_password_entry = tk.Entry(edit_window, show="*", font=("Arial", 14))
    confirm_password_entry.grid(row=4, column=1, padx=10, pady=10)
    
    tk.Label(edit_window, text="Position", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10)
    position_combobox = ttk.Combobox(edit_window, font=("Arial", 14), values=["Midwife", "BHW", "BNS"])  # Adjust values as needed
    position_combobox.grid(row=5, column=1, padx=10, pady=10)
    position_combobox.set(user[0])
    position_combobox.config(validate="key", validatecommand=(position_combobox.register(validate_combobox_input), '%d', '%S'))
    
    tk.Label(edit_window, text="Account Type", font=("Arial", 14)).grid(row=6, column=0, padx=10, pady=10)
    accountType_combobox = ttk.Combobox(edit_window, font=("Arial", 14), values=["Admin", "Staff"])  # Adjust values as needed
    accountType_combobox.grid(row=6, column=1, padx=10, pady=10)
    accountType_combobox.set(user[1])
    position_combobox.config(validate="key", validatecommand=(position_combobox.register(validate_combobox_input), '%d', '%S'))

    def save_changes():
        new_username = username_entry.get()
        new_password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        new_position = position_combobox.get()
        new_accountType = accountType_combobox.get()

        if validate_user_info('edit', new_username, new_password, confirm_password, new_position, new_accountType):
            conn = sqlite3.connect('Medicine Cabinet.db')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET username = ?, password = ?, position = ?, accountType = ?
                WHERE username = ?
            """, (new_username, new_password, new_position, new_accountType, username))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "User information updated successfully.")
            edit_window.destroy()
            show_account_setting()

    button_frame = tk.Frame(edit_window, bg=motif_color)

    # Cancel button (now on the right side)
    
    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(button_frame, text="Cancel", font=("Arial", 14), command=lambda: toplevel_destroy(edit_window), width=118, padx=10, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img)
    cancel_button.image = cancel_img
    cancel_button.grid(row=0, column=0, pady=10, padx=80)
    
    # Save button (now on the left side)
    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(button_frame, text="Save", font=("Arial", 14), command=save_changes, width=118, padx=10, relief="raised", bd=3, compound=tk.LEFT, image=save_img)
    save_button.image = save_img
    save_button.grid(row=0, column=1, pady=10, padx=80)

    button_frame.grid(row=7, column=0, columnspan=2, sticky="new", padx=(0,20), pady=(0, 50))


def add_user():
    add_window = tk.Toplevel(relief='raised', bd=3)
    add_window.overrideredirect(True)
    add_window.resizable(width=False, height=False)

    window_width = 600
    window_height = 600
    screen_width = add_window.winfo_screenwidth()
    screen_height = add_window.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))
    add_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    Add_User_header = tk.Label(add_window, bg=motif_color, text='Add User', font=('Arial', 18, 'bold'), fg='white')
    Add_User_header.grid(row=0, column=0, columnspan=2, sticky='new')

    default_image_path = os.path.join(os.path.dirname(__file__), 'images', 'image_icon.png')
    try:
        default_photo = ImageTk.PhotoImage(Image.open(default_image_path).resize((220, 220), Image.LANCZOS))
        image_label = tk.Label(add_window, image=default_photo)
        image_label.image = default_photo
        image_label.grid(row=1, column=0, columnspan=2, pady=10)
    except Exception as e:
        print(f"Error loading default image: {e}")

    tk.Label(add_window, text="Username", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=(29, 10))
    username_entry = tk.Entry(add_window, font=("Arial", 14), width=20)
    username_entry.grid(row=2, column=1, padx=10, pady=(29, 10))

    tk.Label(add_window, text="Password", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)
    password_entry = tk.Entry(add_window, show="*", font=("Arial", 14), width=20)
    password_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(add_window, text="Confirm Password", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10)
    confirm_password_entry = tk.Entry(add_window, show="*", font=("Arial", 14), width=20)
    confirm_password_entry.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(add_window, text="Position", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10)
    position_combobox = ttk.Combobox(add_window, font=("Arial", 14), values=["Midwife", "BHW", "BNS"], width=20)
    position_combobox.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(add_window, text="Account Type", font=("Arial", 14)).grid(row=6, column=0, padx=10, pady=10)
    accountType_combobox = ttk.Combobox(add_window, font=("Arial", 14), values=["Admin", "Staff"], width=20)
    accountType_combobox.grid(row=6, column=1, padx=10, pady=10)

    def generate_qr_code():
        new_username = username_entry.get().strip()
        new_position = position_combobox.get().strip()
        new_accountType = accountType_combobox.get().strip()

        if new_username and new_position and new_accountType:
            qr = qrcode.make(new_username)

            # Resize the QR code to match the default image size (220x220)
            qr = qr.resize((220, 220), Image.LANCZOS)
            qr_image = ImageTk.PhotoImage(qr)

            # Update the image label with the resized QR code image
            image_label.config(image=qr_image)
            image_label.image = qr_image
        else:
            # Reset to the default image if any field is empty
            image_label.config(image=default_photo)
            image_label.image = default_photo

    def on_field_update(event):
        generate_qr_code()

    username_entry.bind("<KeyRelease>", on_field_update)
    position_combobox.bind("<<ComboboxSelected>>", on_field_update)
    accountType_combobox.bind("<<ComboboxSelected>>", on_field_update)

    def add_new_user():
        new_username = username_entry.get()
        new_password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        new_position = position_combobox.get()
        new_accountType = accountType_combobox.get()
        qr_code = None

        if validate_all_fields_filled(username_entry, password_entry, confirm_password_entry, position_combobox, accountType_combobox):
            if validate_user_info('add', new_username, new_password, confirm_password, new_position, new_accountType):
                qr = qrcode.make(new_username)
                qr_bytes = io.BytesIO()
                qr.save(qr_bytes)
                qr_code = qr_bytes.getvalue()

                conn = sqlite3.connect('Medicine Cabinet.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, position, accountType, qr_code) VALUES (?, ?, ?, ?, ?)",
                               (new_username, new_password, new_position, new_accountType, qr_code))
                conn.commit()
                conn.close()

                add_window.destroy()
                show_account_setting()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    button_frame = tk.Frame(add_window, bg=motif_color)
    button_frame.grid(row=7, column=0, columnspan=2, sticky='ew')

    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(button_frame, text="Cancel", font=("Arial", 14), command=lambda: toplevel_destroy(add_window), width=118, padx=10, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img)
    cancel_button.image = cancel_img
    cancel_button.grid(row=0, column=0, pady=10, padx=79)

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(button_frame, text="Save", font=("Arial", 14), command=add_new_user, width=118, padx=10, relief="raised", bd=3, compound=tk.LEFT, image=save_img)
    save_button.image = save_img
    save_button.grid(row=0, column=1, pady=10, padx=79)




#-----------------------------------------------OTHER FUNCTIONS------------------------------------------------------
# Function that ensures users cannot type into the combobox  
def validate_combobox_input(action, value_if_allowed):
    return False
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

#Function for switching of Frames
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()

#Top Level Warning if door is not locked
def not_lock():
    lockStatus_window = tk.Toplevel(relief='groove', bd=5)
    lockStatus_window.overrideredirect(True)  # Remove the title bar
    lockStatus_window.resizable(width=False, height=False)

    # Get the window dimensions
    lockStatus_window.update_idletasks()  # Ensure the window size is calculated
    window_width = 620  # Adjust the width as needed
    window_height = 385  # Adjust the height as needed

    # Calculate the center position
    screen_width = lockStatus_window.winfo_screenwidth()
    screen_height = lockStatus_window.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the window position
    lockStatus_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Bind activity events to reset the inactivity timer
    lockStatus_window.bind("<Motion>", reset_timer)
    lockStatus_window.bind("<KeyPress>", reset_timer)
    lockStatus_window.bind("<ButtonPress>", reset_timer)

    # Start the inactivity timer
    start_timer()

    # Add the warning label with padding for better alignment
    tk.Label(lockStatus_window, text='WARNING', font=('Arial', 25, 'bold'), bg='red', fg='white', pady=12).pack(fill=tk.X)

    # Load and display the status image with a message
    status_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')).resize((150, 150), Image.LANCZOS))
    logo_label = tk.Label(lockStatus_window, text='Please close both doors properly before locking.', image=status_img, compound=tk.TOP, font=('Arial', 18))
    logo_label.image = status_img
    logo_label.pack(pady=(10, 20))

    button_frame = tk.Frame(lockStatus_window, bg='red')
    button_frame.pack(fill=tk.X)

    # Centering the button inside the frame
    button_frame.grid_columnconfigure(0, weight=1)  # Make the column stretch

    # Load and display the 'Okay' button with an icon, modern styling, and padding
    ok_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'okGrey_icon.png')).resize((35, 35), Image.LANCZOS))
    ok_button = tk.Button(button_frame, text="Okay", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, compound=tk.LEFT, image=ok_img, command=lambda: toplevel_destroy(lockStatus_window))
    ok_button.image = ok_img  # Keep a reference to avoid garbage collection

    # Add the button to the grid, center it with sticky and columnspan
    ok_button.grid(row=0, column=0, padx=90, pady=18, sticky="ew")

    # Configure the row and column to expand equally
    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)

def proceed_to_scan(window):
    """Close current window and proceed to scanning window."""
    toplevel_destroy(window)
    scanning()

def unlocked():
    unlocked_window = tk.Toplevel(relief='groove', bd=5)
    unlocked_window.overrideredirect(True)  # Remove the title bar
    unlocked_window.resizable(width=False, height=False)

    # Get the window dimensions
    unlocked_window.update_idletasks()  # Ensure the window size is calculated
    window_width = 620  # Adjust the width as needed
    window_height = 400  # Adjust the height as needed

    # Calculate the center position
    screen_width = unlocked_window.winfo_screenwidth()
    screen_height = unlocked_window.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the window position
    unlocked_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Bind activity events to reset the inactivity timer
    unlocked_window.bind("<Motion>", reset_timer)
    unlocked_window.bind("<KeyPress>", reset_timer)
    unlocked_window.bind("<ButtonPress>", reset_timer)

    # Start the inactivity timer
    start_timer()

    # Add the warning label with padding for better alignment
    tk.Label(unlocked_window, text='NOTICE', font=('Arial', 25, 'bold'), bg=motif_color, fg='white', pady=12).pack(fill=tk.X)

    # Load and display the status image with a message
    unlock_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png')).resize((150, 170), Image.LANCZOS))
    logo_label = tk.Label(unlocked_window, text='The door is finally unlocked, \nyou may now proceed to scan the QR code.', image=unlock_img, compound=tk.TOP, font=('Arial', 18), pady=7)
    logo_label.image = unlock_img
    logo_label.pack(pady=(10, 20))

    button_frame = tk.Frame(unlocked_window, bg=motif_color)
    button_frame.pack(fill=tk.X)

    # Centering the button inside the frame
    button_frame.grid_columnconfigure(0, weight=1)

    # Load and display the 'Okay' button with an icon, modern styling, and padding
    ok_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'okGrey_icon.png')).resize((30, 30), Image.LANCZOS))
    ok_button = tk.Button(button_frame, text="Okay", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=10, compound=tk.LEFT, image=ok_img, command=lambda: proceed_to_scan(unlocked_window))
    ok_button.image = ok_img  # Keep a reference to avoid garbage collection

    # Add the button to the grid, center it with sticky and columnspan
    ok_button.grid(row=0, column=0, padx=90, pady=5, sticky="ew")

    # Configure the row and column to expand equally
    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)

def scanning():
    scanning_window = tk.Toplevel(relief='groove', bd=5)
    scanning_window.overrideredirect(True)  # Remove the title bar
    scanning_window.resizable(width=False, height=False)

    # Get the window dimensions
    scanning_window.update_idletasks()  # Ensure the window size is calculated
    window_width = 620  # Adjust the width as needed
    window_height = 400  # Adjust the height as needed

    # Calculate the center position
    screen_width = scanning_window.winfo_screenwidth()
    screen_height = scanning_window.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the window position
    scanning_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Bind activity events to reset the inactivity timer
    scanning_window.bind("<Motion>", reset_timer)
    scanning_window.bind("<KeyPress>", reset_timer)
    scanning_window.bind("<ButtonPress>", reset_timer)

    # Start the inactivity timer
    start_timer()

    # Add the warning label with padding for better alignment
    tk.Label(scanning_window, text='NOTICE', font=('Arial', 25, 'bold'), bg=motif_color, fg='white', pady=12).pack(fill=tk.X)

    # Load and display the status image with a message
    scanner_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((150, 170), Image.LANCZOS))
    logo_label = tk.Label(scanning_window, text='Please scan the QR code of the desired medicine \n using the scanner at the right of the cabinet.', image=scanner_img, compound=tk.TOP, font=('Arial', 18))
    logo_label.image = scanner_img
    logo_label.pack(pady=(10, 20))

    button_frame = tk.Frame(scanning_window, bg=motif_color)
    button_frame.pack(fill=tk.X)

    # Centering the button inside the frame
    button_frame.grid_columnconfigure(0, weight=1)

    # Load and display the 'Okay' button with an icon, modern styling, and padding
    ok_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'okGrey_icon.png')).resize((35, 35), Image.LANCZOS))
    ok_button = tk.Button(button_frame, text="Okay", font=("Arial", 20), bg='white', fg='black', relief="raised", bd=3, padx=20, pady=7, compound=tk.LEFT, image=ok_img, command=lambda: toplevel_destroy(scanning_window))
    ok_button.image = ok_img  # Keep a reference to avoid garbage collection

    # Add the button to the grid, center it with sticky and columnspan
    ok_button.grid(row=0, column=0, padx=90, pady=5, sticky="ew")

    # Configure the row and column to expand equally
    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)



#-----------------------------------------------MAIN------------------------------------------------------
def main():
    global root

    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("Electronic Medicine Cabinet Control System")
    root.state("zoomed")  # Maximize the window to full screen

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    login_frame = create_login_frame(container)
    main_ui_frame = create_main_ui_frame(container)

    login_frame.tkraise()

    root.mainloop()

if __name__ == "__main__":
    main()