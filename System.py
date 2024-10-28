import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from tkinter import messagebox
from tkcalendar import DateEntry
import mysql.connector
from keyboard import *
from custom_messagebox import CustomMessageBox
from csv_exporter import *
from notification import *
from deposit import MedicineDeposit
from withdrawal import QRCodeScanner
from wifi_connect import WiFiConnectUI
import socket
import qrcode
from treeviewStyling import table_style
import serial
import time
from loginQrCode import QRLogin
from lockunlock import LockUnlock

conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="db_medicine_cabinet"
)
# Function to establish/re-establish MySQL connection
def establish_connection():
    global conn
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
        )
        print("MySQL connection established.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn = None  # Set to None if connection fails

INACTIVITY_PERIOD = 60000 #automatic logout timer in milliseconds
inactivity_timer = None #initialization of idle timer
root = None  # Global variable for root window

motif_color = '#42a7f5'
font_style = 'Arial'
font_size = 15

# Define the active and default background colors for Sidebar
active_bg_color = "#fff"  # Active background color
default_bg_color = motif_color  # Default background color
active_fg_color ='#000000' # Active foreground color
default_fg_color="#fff" # Default foreground color

#----------------------------------------------------LOGIN WINDOW--------------------------------------------------------

#function for authentication during the login frame
def authenticate_user(username, password):
    global Username, Password
    Username = username
    Password = password
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", [username, password])
    user = cursor.fetchone()
    if user:
        user_role = user[2]
        main_ui_frame = create_main_ui_frame(container) 
        main_ui_frame.tkraise()
        reset_timer()
        bind_activity_events()
        show_medicine_supply()
        configure_sidebar(user_role)
        # Check for soon-to-expire medicines on home page load
        notification_manager = NotificationManager(root, conn)
        notification_manager.check_soon_to_expire()  # Automatically check and pop-up notifications
    else:
        message_box = CustomMessageBox(
            root=login_frame,
            title="Login Error",
            message="Invalid username or password.",
            color="red",  # Background color for warning
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),  # Path to your icon
            sound_file="sounds/invalidLogin.mp3",
            page='Login'
        )

# Function that creates the UI for login frame
def create_login_frame(container):
    global login_frame
    login_frame = tk.Frame(container, bg=motif_color)
    box_frame = tk.Frame(login_frame, bg='#ffffff', bd=5, relief="ridge", padx=70, pady=30)
    box_frame.pack(expand=True, anchor='center')

    logo_path = os.path.join(os.path.dirname(__file__), 'images', 'SanMateoLogo.png')
    original_logo_img = Image.open(logo_path)
    resized_logo_img = original_logo_img.resize((150, 150), Image.LANCZOS)
    logo_img = ImageTk.PhotoImage(resized_logo_img)

    logo_label = tk.Label(box_frame, image=logo_img, bg='#ffffff')
    logo_label.image = logo_img
    logo_label.pack(pady=(0, 10))

    title = tk.Label(box_frame, text='ELECTRONIC\nMEDICINE CABINET', font=('Arial', 23, 'bold'), bg='white')
    title.pack()

    username_label = tk.Label(box_frame, text="Username", font=("Arial", 18), bg='#ffffff')
    username_label.pack(pady=10)

    # Create username entry
    global username_entry
    username_entry = tk.Entry(box_frame, font=("Arial", 16), relief='sunken', bd=3)
    username_entry.pack(pady=5, fill='x')

    password_label = tk.Label(box_frame, text="Password", font=("Arial", 18), bg='#ffffff')
    password_label.pack(pady=10)

    # Create password entry
    global password_entry
    password_entry = tk.Entry(box_frame, show="*", font=("Arial", 16), relief='sunken', bd=3)
    password_entry.pack(pady=5, fill='x')

    # Function to show/hide password based on Checkbutton state
    def toggle_password_visibility():
        if show_password_var.get():
            password_entry.config(show='')
        else:
            password_entry.config(show='*')

    # Variable to track the state of the Checkbutton
    show_password_var = tk.BooleanVar()
    show_password_checkbutton = tk.Checkbutton(box_frame, text="Show Password", variable=show_password_var,
                                                command=toggle_password_visibility, bg='#ffffff', font=("Arial", 14))
    show_password_checkbutton.pack(anchor='w', padx=(5, 0), pady=(5, 10))  # Align to the left with padding

    login_button = tk.Button(box_frame, text="Login", font=("Arial", 16), 
                             command=lambda: authenticate_user(username_entry.get(), password_entry.get()), 
                             fg='#ffffff', bg='#2c3e50', width=20)
    login_button.pack(pady=(20, 10))

    login_frame.grid(row=0, column=0, sticky='news')


    qrlogin= tk.Button(box_frame, text="or Login using QR code", fg="black", cursor="hand2", bg='white', relief="flat", font=('Arial', 13), command=lambda: QRLogin(login_frame, callback=authenticate_user))
    qrlogin.pack()

    # Create an instance of OnScreenKeyboard and bind it to entry widgets
    on_screen_keyboard = OnScreenKeyboard(login_frame)
    on_screen_keyboard.hide_keyboard()

    # Bind focus events to show/hide the on-screen keyboard
    def show_keyboard(event):
        on_screen_keyboard.show_keyboard()

    def hide_keyboard(event):
        on_screen_keyboard.hide_keyboard()

    # Bind the FocusIn event to show the keyboard when focused
    username_entry.bind("<FocusIn>", show_keyboard)
    password_entry.bind("<FocusIn>", show_keyboard)

    # Optional: Bind FocusOut to hide the keyboard when losing focus (optional, can be removed if not needed)
    username_entry.bind("<FocusOut>", hide_keyboard)
    password_entry.bind("<FocusOut>", hide_keyboard)


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
    inventory_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'inventory_icon.png')).resize((50, 50), Image.LANCZOS))
    global inventory_button
    inventory_button = tk.Button(sidebar_frame, height=100, width=350, text="Medicine Inventory", command=show_medicine_supply, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=inventory_img, padx=10, anchor='w')
    inventory_button.image = inventory_img
    inventory_button.grid(row=1, column=0, sticky="w", columnspan=2)
    doorLogs_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cabinet_Icon.png')).resize((50, 50), Image.LANCZOS))
    global doorLogs_button
    doorLogs_button = tk.Button(sidebar_frame, height=100, width=350, text="Door Functions", command=show_doorLog, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=doorLogs_img, padx=10, anchor='w')
    doorLogs_button.image = doorLogs_img
    doorLogs_button.grid(row=2, column=0, sticky="we", columnspan=2)
    notification_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'notification_Icon.png')).resize((50, 50), Image.LANCZOS))
    global notification_button
    notification_button = tk.Button(sidebar_frame, height=100, width=350, text="Notification", command=show_notification, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=notification_img, justify="left", padx=10, anchor='w')
    notification_button.image = notification_img
    notification_button.grid(row=4, column=0, sticky="we", columnspan=2)
    
    account_setting_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'accountSetting_Icon.png')).resize((50, 50), Image.LANCZOS))
    global account_setting_button
    account_setting_button = None
    
    logout_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'logout_icon.png')).resize((40, 40), Image.LANCZOS))
    logout_button = tk.Button(sidebar_frame, height=100, width=350, text="Log Out", command=lambda: logout('manual logout'), font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=logout_img, padx=10, anchor='w')
    logout_button.image = logout_img
    logout_button.grid(row=6, column=0, sticky="we", columnspan=2)
    content_frame = tk.Frame(main_ui_frame, bg='#ecf0f1')
    content_frame.pack(expand=True, fill='both', side='top')
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
            account_setting_button = tk.Button(sidebar_frame, height=100, width=350, text="Account Settings", command=show_account_setting, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="groove", compound=tk.LEFT, image=account_setting_img, padx=10, anchor='w')
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
        message_box = CustomMessageBox(
            root=login_frame,
            title="Session Expired",
            message="You have been logged-out due to inactivity.",
            color='red',  # Background color for warning
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'logout_icon.png'),
            sound_file ="sounds/automaticLogout.mp3",
        )
        OnScreenKeyboard(content_frame).hide_keyboard()

def on_ok_pressed():
    print("Custom OK action triggered!")

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
    print("\nUser has been automatically logged out due to inactivity.")
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

def deposit_window():
    clear_frame()

    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_medicine_cabinet"
    )
    # Fetch data from the database
    def fetch_medicine_data():
        cursor = db_connection.cursor()

        # Fetch distinct names
        cursor.execute("SELECT DISTINCT name FROM medicine_list")
        names = [row[0] for row in cursor.fetchall()]

        # Fetch distinct types
        cursor.execute("SELECT DISTINCT type FROM medicine_list")
        types = [row[0] for row in cursor.fetchall()]

        # Fetch distinct units
        cursor.execute("SELECT DISTINCT unit FROM medicine_list")
        units = [row[0] for row in cursor.fetchall()]

        cursor.close()
        return names, types, units

    # Retrieve data from the database
    names, types, units = fetch_medicine_data()

    # Ensure content_frame expands to fill the available width
    content_frame.grid_columnconfigure(0, weight=1)

    title_label = tk.Label(content_frame, text="DEPOSIT MEDICINE", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1)
    title_label.pack(fill='both')

    # Create input frame and ensure it expands horizontally
    input_frame = tk.LabelFrame(content_frame, text='Fill out all the necessary information below', font=('Arial', 14), pady=20, padx=5, relief='raised', bd=5)
    input_frame.pack(fill='x', pady=30, padx=300)

    # Instantiate OnScreenKeyboard and NumericKeyboard
    keyboard = OnScreenKeyboard(content_frame)
    keyboard.create_keyboard()
    keyboard.hide_keyboard()  # Initially hide the keyboard

    numKeyboard = NumericKeyboard(content_frame)
    numKeyboard.create_keyboard()
    numKeyboard.hide()

    # Name Combobox
    tk.Label(input_frame, text="Name of Medicine", font=("Arial", 16)).grid(row=0, column=0, padx=(30, 10), pady=10, sticky='w')
    name_combobox = ttk.Combobox(input_frame, font=("Arial", 16), width=20, values=names)
    name_combobox.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    # Type Combobox
    tk.Label(input_frame, text="Type", font=("Arial", 16)).grid(row=1, column=0, padx=(30, 10), pady=10, sticky='w')
    type_combobox = ttk.Combobox(input_frame, font=("Arial", 16), width=20, values=types)
    type_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    tk.Label(input_frame, text="Quantity", font=("Arial", 16)).grid(row=2, column=0, padx=(30, 10), pady=10, sticky='w')
    quantity_spinbox = tk.Spinbox(input_frame, from_=0, to=100, font=("Arial", 16), width=20)
    quantity_spinbox.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

    # Unit Combobox
    tk.Label(input_frame, text="Unit", font=("Arial", 16)).grid(row=3, column=0, padx=(30, 10), pady=10, sticky='w')
    unit_combobox = ttk.Combobox(input_frame, font=("Arial", 16), width=20, values=units)
    unit_combobox.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

    tk.Label(input_frame, text="Expiration Date", font=("Arial", 16)).grid(row=4, column=0, padx=(30, 10), pady=10, sticky='w')
    expiration_date_entry = DateEntry(input_frame, font=("Arial", 16), date_pattern='mm-dd-y', width=20)
    expiration_date_entry.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

    # Bind focus events to show/hide the keyboard for each widget
    for widget in [name_combobox, type_combobox, unit_combobox, expiration_date_entry]:
        widget.bind("<FocusIn>", lambda e: keyboard.show_keyboard())
        widget.bind("<FocusOut>", lambda e: keyboard.hide_keyboard())
    quantity_spinbox.bind("<FocusIn>", lambda e: numKeyboard.show())
    quantity_spinbox.bind("<FocusOut>", lambda e: numKeyboard.hide())

    # Save button logic
    def save_medicine():
        name = name_combobox.get()
        type_ = type_combobox.get()
        quantity = quantity_spinbox.get()
        unit = unit_combobox.get()
        expiration_date = expiration_date_entry.get_date()

        deposit = MedicineDeposit(name, type_, quantity, unit, expiration_date, conn, main_ui_frame)

        if deposit.validate_inputs():
            deposit.save_to_database()
            show_medicine_supply()

    # Cancel and Save buttons
    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(input_frame, text="Cancel", font=("Arial", 16), bg=motif_color, fg='white', command=show_medicine_supply, width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img, pady=5)
    cancel_button.image = cancel_img
    cancel_button.grid(row=5, column=0, padx=(40, 60), pady=(50, 0))

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(input_frame, text="Save", font=("Arial", 16), bg=motif_color, fg='white', width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=save_img, pady=5, command=save_medicine)
    save_button.image = save_img
    save_button.grid(row=5, column=1, padx=(60, 40), pady=(50, 0))



# Function that creates the UI for medicine inventory in the content_frame
def show_medicine_supply():
    clear_frame()
    reset_button_colors()

    inventory_button.config(bg=active_bg_color)
    inventory_button.config(fg=active_fg_color)

    # Initialize the On-Screen Keyboard
    keyboard = OnScreenKeyboard(content_frame)
    keyboard.create_keyboard()
    keyboard.hide_keyboard()  # Initially hide the keyboard

    # Track the current active sort order and column
    global active_column, sort_order, search_term
    active_column = "date_stored"  # Default sorting column
    sort_order = "ASC"  # Default sorting order
    search_term = ""  # Store the search term globally

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
        global latest_timestamp
        # Clear the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Fetch all data from the database first
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
        )
        cursor = conn.cursor()
        query = f"SELECT name, type, quantity, unit, date_stored, expiration_date FROM medicine_inventory WHERE quantity <> 0 ORDER BY {order_by} {sort}"
        cursor.execute(query)
        medicine = cursor.fetchall()

        # Filter data in Python based on the search term
        filtered_medicine = []
        search_term_lower = search_term.lower()

        for med in medicine:
            name, type, quantity, unit, date_stored, expiration_date = med

            # Convert date objects to strings (handling NoneType)
            date_stored_str = date_stored.strftime("%b %d, %Y").lower() if date_stored else "N/A"
            expiration_date_str = expiration_date.strftime("%b %d, %Y").lower() if expiration_date else "N/A"

            # Check if the search term matches any of the fields
            if (
                search_term_lower in name.lower() or
                search_term_lower in type.lower() or
                search_term_lower in unit.lower() or
                search_term_lower in str(quantity).lower() or
                search_term_lower in date_stored_str or
                search_term_lower in expiration_date_str
            ):
                filtered_medicine.append(med)

        # Use the filtered results to populate the Treeview
        for i, med in enumerate(filtered_medicine):
            name, type, quantity, unit, date_stored, expiration_date = med
            date_stored_str = date_stored.strftime("%b %d, %Y") if date_stored else "N/A"
            expiration_date_str = expiration_date.strftime("%b %d, %Y") if expiration_date else "N/A"
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
    search_entry = tk.Entry(search_frame, width=20, fg='grey', font=('Arial', 17))
    search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    search_entry.insert(0, 'Search here')

    # Bind events to the search_entry to show/hide the keyboard
    def focus_in_search(event):
        clear_placeholder()
        keyboard.show_keyboard()  # Always show the keyboard on focus

    def focus_out_search(event):
        if not search_entry.get():
            search_entry.insert(0, 'Search here')
            search_entry.config(fg='grey')
        # No need to hide keyboard on focus out, it will be hidden by pressing Enter

    def handle_enter_key(event):
        keyboard.hide_keyboard()  # Hide the on-screen keyboard
        search_treeview()  # Trigger the search functionality
        add_placeholder(None)
        return "break"  # Prevent default behavior of Enter key

    # Bindings for the search_entry widget
    search_entry.bind("<FocusIn>", focus_in_search)  # Show keyboard when focused
    search_entry.bind("<FocusOut>", focus_out_search)  # Add placeholder when out of focus
    search_entry.bind("<Return>", handle_enter_key)  # Hide keyboard and search on Enter
    
    # Bind events to the search_entry to show/hide the keyboard
    search_entry.bind("<KeyPress>", clear_placeholder)
    search_entry.bind("<FocusOut>", lambda event: (keyboard.hide_keyboard(), add_placeholder(None)))

    # Add the search icon next to the Entry widget
    search_icon_label = tk.Button(search_frame, image=search_img, bg='white', command=search_treeview, relief='flat')
    search_icon_label.image = search_img  # Keep a reference to avoid garbage collection
    search_icon_label.pack(side=tk.RIGHT, fill='both')

    buttons = []

    # Sorting buttons
    sort_button_1 = tk.Button(header_frame, text="Sort by Name", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("name", sort_button_1), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_1.grid(row=0, column=2, padx=(110, 0), pady=10, sticky="e")
    buttons.append(sort_button_1)

    sort_button_2 = tk.Button(header_frame, text="Sort by Type", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("type", sort_button_2), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_2.grid(row=0, column=3, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_2)

    sort_button_3 = tk.Button(header_frame, text="Sort by Unit", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("unit", sort_button_3), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_3.grid(row=0, column=4, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_3)

    sort_button_4 = tk.Button(header_frame, text="Sort by Expiration Date", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("expiration_date", sort_button_4), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_4.grid(row=0, column=5, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_4)

    sort_button_5 = tk.Button(header_frame, text="Sort by Date Stored", bg="white", fg=motif_color, padx=10, pady=5,
                              command=lambda: sort_treeview("date_stored", sort_button_5), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_5.grid(row=0, column=6, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_5)

    activate_button(sort_button_5)

    # Frame for the treeview
    tree_frame = tk.Frame(content_frame, bg="#f0f0f0")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Custom scrollbar for the treeview
    tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    table_style()

    # Define columns
    columns = ("name", "type", "quantity", "unit", "date stored", "expiration date")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set, height=10)

    tree_scroll.config(command=tree.yview)

    # Column headings
    for col in columns:
        tree.heading(col, text=col.capitalize())

    # Column configurations
    for col in columns:
        tree.column(col, anchor=tk.CENTER, width=100)

    # Row styling
    tree.tag_configure('oddrow', background="white")
    tree.tag_configure('evenrow', background="#f2f2f2")

    # Mouse wheel support
    def on_mouse_wheel(event):
        tree.yview_scroll(int(-1*(event.delta/120)), "units")

    tree.bind_all("<MouseWheel>", on_mouse_wheel)

    # Populate treeview for the first time
    populate_treeview()

    tree.pack(side=tk.LEFT, fill="both", expand=True)

    # Create a frame for the buttons below the Treeview
    button_frame = tk.Frame(content_frame, bg='white', padx=30)
    button_frame.pack(fill="x", anchor='e')  # Align to the right

    # Configure the columns in button_frame to distribute buttons evenly
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.columnconfigure(3, weight=1)


    widthdraw_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'minus_icon.png')).resize((25, 25), Image.LANCZOS))
    withdraw_button = tk.Button(button_frame, text="Withdraw", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=widthdraw_icon, command=lambda: LockUnlock(content_frame, content_frame, Username, Password, ser, "withdraw"))
    withdraw_button.image = widthdraw_icon
    withdraw_button.grid(row=0, column=0, padx=20, pady=(12, ), sticky='ew')


    deposit_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'add_icon.png')).resize((25, 25), Image.LANCZOS))
    deposit_button = tk.Button(button_frame, text="Deposit", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=deposit_icon,command=deposit_window)
    deposit_button.image = deposit_icon
    deposit_button.grid(row=0, column=1, padx=20, pady=(12, 7), sticky='ew')

    # Extract CSV button
    extract_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'extract_icon.png')).resize((25, 25), Image.LANCZOS))
    extract_button = tk.Button(button_frame, text="Extract CSV", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=extract_img, command=lambda: export_to_csv(root,'medicine_inventory'))
    extract_button.image = extract_img
    extract_button.grid(row=0, column=2, padx=20, pady=(12, 7), sticky='ew')

    # Reload All button
    refresh_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'refresh_icon.png')).resize((25, 25), Image.LANCZOS))
    refresh_button = tk.Button(button_frame, text="Reload All", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=refresh_img, command=clear_search)
    refresh_button.image = refresh_img
    refresh_button.grid(row=0, column=3, padx=20, pady=(12, 7), sticky='ew')

#--------------------------------------------------------- DOOR FUNCTIONS -----------------------------------------------------------       

#Function that creates the UI for door function in the content_frame
def show_doorLog():
    clear_frame()
    reset_button_colors()
    doorLogs_button.config(bg=active_bg_color)
    doorLogs_button.config(fg=active_fg_color)

    # Initialize the On-Screen Keyboard
    keyboard = OnScreenKeyboard(content_frame)
    keyboard.create_keyboard()
    keyboard.hide_keyboard()  # Initially hide the keyboard

    # Local variables to track sorting and search for door logs
    active_column = "date"  # Default sorting column for door logs
    sort_order = "ASC"  # Default sorting order
    search_term = ""  # Store the search term locally

    def activate_button(clicked_button):
        # Reset all buttons to default color
        for btn in buttons:
            btn.config(bg=motif_color, fg='white')
        # Highlight the clicked button
        clicked_button.config(bg="white", fg="black")

    def search_treeview():
        nonlocal search_term
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
        nonlocal search_term
        search_term = ""
        search_entry.delete(0, tk.END)
        search_entry.insert(0, 'Search here')
        search_entry.config(fg='grey')
        populate_treeview()

    def populate_treeview(order_by="date", sort="DESC"):
        # Clear the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Fetch all data from the database first
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
        )
        cursor = conn.cursor()
        query = f"SELECT username, accountType, position, date, time, action_taken FROM door_logs ORDER BY {order_by} {sort}"
        cursor.execute(query)
        logs = cursor.fetchall()

        cursor.close()  # Close the cursor
        conn.close()  # Close the connection

        # Filter data in Python based on the search term
        filtered_logs = []
        search_term_lower = search_term.lower()

        for log in logs:
            username, accountType, position, date, time, action_taken = log

            # Convert date to string
            date_str = date.strftime("%b %d, %Y").lower() if date else "N/A"

            # Convert time (timedelta) to hours, minutes, and seconds
            if time:
                total_seconds = int(time.total_seconds())  # Convert timedelta to total seconds
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                time_str = "N/A"

            # Check if the search term matches any of the fields
            if (
                search_term_lower in username.lower() or
                search_term_lower in accountType.lower() or
                search_term_lower in position.lower() or
                search_term_lower in date_str or
                search_term_lower in time_str or
                search_term_lower in action_taken.lower()
            ):
                filtered_logs.append(log)

        # Populate the Treeview with the filtered results
        for i, log in enumerate(filtered_logs):
            username, accountType, position, date, time, action_taken = log
            
            # Convert date and time again for displaying
            date_str = date.strftime("%b %d, %Y") if date else "N/A"
            if time:
                total_seconds = int(time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                time_str = "N/A"

            # Alternate row colors using tags
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(date_str, time_str, username, accountType, position, action_taken), tags=(tag,))

    def sort_treeview(column, clicked_button):
        nonlocal active_column, sort_order
        activate_button(clicked_button)

        # Set the active column and toggle sort order
        if active_column == column:
            sort_order = "DESC" if sort_order == "ASC" else "ASC"
        else:
            active_column = column
            sort_order = "ASC"

        # Modify the column to handle combined Date & Time sorting
        if column == "date_time":
            # Sort by both date and time
            populate_treeview(order_by="date, time", sort=sort_order)
        else:
            # Regular sorting by a single column
            populate_treeview(order_by=active_column, sort=sort_order)


    # Header frame for sorting buttons and search bar
    header_frame = tk.Frame(content_frame, bg=motif_color)
    header_frame.pack(fill="x", pady=10)

    # Load the search icon image
    search_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'search_icon.png')).resize((14, 14), Image.LANCZOS))

    # Create a Frame to hold the Entry and the search icon
    search_frame = tk.Frame(header_frame, bg='white')
    search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # Create the Entry widget (search bar)
    search_entry = tk.Entry(search_frame, width=20, fg='grey', font=('Arial', 18))
    search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    search_entry.insert(0, 'Search here')

    # Add the search icon next to the Entry widget
    search_icon_label = tk.Button(search_frame, image=search_img, bg='white', command=search_treeview, relief='flat')
    search_icon_label.image = search_img  # Keep a reference to avoid garbage collection
    search_icon_label.pack(side=tk.RIGHT, fill='both')

    # Bind events to the search_entry to show/hide the keyboard
    def focus_in_search(event):
        clear_placeholder()
        keyboard.show_keyboard()  # Always show the keyboard on focus

    def focus_out_search(event):
        if not search_entry.get():
            search_entry.insert(0, 'Search here')
            search_entry.config(fg='grey')
        # No need to hide keyboard on focus out, it will be hidden by pressing Enter

    def handle_enter_key(event):
        keyboard.hide_keyboard()  # Hide the on-screen keyboard
        search_treeview()  # Trigger the search functionality
        add_placeholder(None)
        return "break"  # Prevent default behavior of Enter key

    # Bindings for the search_entry widget
    search_entry.bind("<FocusIn>", focus_in_search)  # Show keyboard when focused
    search_entry.bind("<FocusOut>", focus_out_search)  # Add placeholder when out of focus
    search_entry.bind("<Return>", handle_enter_key)  # Hide keyboard and search on Enter
    
    # Bind events to the search_entry to show/hide the keyboard
    search_entry.bind("<KeyPress>", clear_placeholder)
    search_entry.bind("<FocusOut>", lambda event: (keyboard.hide_keyboard(), add_placeholder(None)))

    search_icon_label.bind("<KeyPress>", search_treeview)

    buttons = []

    # Combined Sorting Button for Date & Time
    sort_button_date_time = tk.Button(header_frame, text="Sort by Date & Time", bg="white", fg='black', padx=10, pady=5,
                                    command=lambda: sort_treeview("date_time", sort_button_date_time), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_date_time.grid(row=0, column=2, padx=(110, 0), pady=10, sticky="e")
    buttons.append(sort_button_date_time)

    sort_button_1 = tk.Button(header_frame, text="Sort by Username", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("username", sort_button_1), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_1.grid(row=0, column=3, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_1)

    sort_button_2 = tk.Button(header_frame, text="Sort by Account Type", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("accountType", sort_button_2), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_2.grid(row=0, column=4, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_2)

    sort_button_3 = tk.Button(header_frame, text="Sort by Position", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("position", sort_button_3), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_3.grid(row=0, column=5, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_3)

    sort_button_6 = tk.Button(header_frame, text="Sort by Action Taken", bg=motif_color, fg='white', padx=10, pady=5,
                              command=lambda: sort_treeview("action_taken", sort_button_6), relief="raised", bd=4, font=(font_style, font_size))
    sort_button_6.grid(row=0, column=6, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_6)

    tree_frame = tk.Frame(content_frame, bg="#f0f0f0")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Custom scrollbar for the treeview
    tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    table_style()

     # Create the Treeview to display the door logs
    columns = ("Date", "Time", "Username", "Account Type", "Position", "Action Taken")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

    # Define columns
    tree_scroll.config(command=tree.yview)

    # Column headings
    for col in columns:
        tree.heading(col, text=col.capitalize())

    # Column configurations    for col in columns:
    for col in columns:
        tree.column(col, anchor=tk.CENTER, width=100)

    # Row styling
    tree.tag_configure('oddrow', background="white")
    tree.tag_configure('evenrow', background="#f2f2f2")

    # Mouse wheel support
    def on_mouse_wheel(event):
        tree.yview_scroll(int(-1*(event.delta/120)), "units")

    tree.bind_all("<MouseWheel>", on_mouse_wheel)

    populate_treeview()

    tree.pack(side=tk.LEFT, fill="both", expand=True)

    # Create a frame for the buttons below the Treeview
    button_frame = tk.Frame(content_frame, bg='white', padx=30)
    button_frame.pack(fill="x", anchor='e')  # Align to the right

    # Configure the columns in button_frame to distribute buttons evenly
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.columnconfigure(3, weight=1)

    # Add the first new button (e.g., 'Button 1')
    lock_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'lockWhite_icon.png')).resize((25, 25), Image.LANCZOS))
    lock_button = tk.Button(button_frame, text="Lock", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=lock_icon, command=lambda: LockUnlock(content_frame, content_frame, Username, Password, ser, "lock"))
    lock_button.image = lock_icon
    lock_button.grid(row=0, column=0, padx=20, pady=(12, ), sticky='ew')

    # Add the second new button (e.g., 'Button 2')
    unlock_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'unlockWhite_icon.png')).resize((35, 35), Image.LANCZOS))
    unlock_button = tk.Button(button_frame, text="Unlock", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=unlock_icon, command=lambda: LockUnlock(content_frame, content_frame, Username, Password, ser, "unlock"))
    unlock_button.image = unlock_icon
    unlock_button.grid(row=0, column=1, padx=20, pady=(12, 7), sticky='ew')

    # Extract CSV button
    extract_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'extract_icon.png')).resize((25, 25), Image.LANCZOS))
    extract_button = tk.Button(button_frame, text="Extract CSV", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=extract_img, command=lambda: export_to_csv(root, 'door_logs'))
    extract_button.image = extract_img
    extract_button.grid(row=0, column=2, padx=20, pady=(12, 7), sticky='ew')

    # Reload All button
    refresh_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'refresh_icon.png')).resize((25, 25), Image.LANCZOS))
    refresh_button = tk.Button(button_frame, text="Reload All", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=refresh_img, command=clear_search)
    refresh_button.image = refresh_img
    refresh_button.grid(row=0, column=3, padx=20, pady=(12, 7), sticky='ew')


#--------------------------------------------------------- NOTIFICATION -----------------------------------------------------------       

# Function to display selected row's data in a Toplevel window
def on_row_select(event):
    # Get the selected item
    selected_item = tree.focus()
    row_data = tree.item(selected_item, 'values')
    
    # Create a new Toplevel window to show the selected row's data
    if row_data:  # Only if a row is selected
        text=f"A medicine is about to expire!\n\nMedicine Name: {row_data[0]}\nExpiration Date: {row_data[1]}\nNotification Date: {row_data[2]}\nDays Until Expiration: {row_data[3]}"
        CustomMessageBox(root=content_frame,
                        title="Medicine Expiration",
                        color='red',
                        message=text,
                        icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'))


# Function that creates the UI for notification logs in the content_frame
def show_notification():
    clear_frame()
    reset_button_colors()
    notification_button.config(bg=active_bg_color)
    notification_button.config(fg=active_fg_color)

    # Add a header
    tk.Label(content_frame, text="NOTIFICATION LOGS", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1).pack(fill='x')

    # Create a Treeview to display the logs
    columns = ("Medicine Name", "Expiration Date", "Notification Date", "Days Until Expiration")
    global tree  # Make the tree global so it can be accessed in the on_row_select function
    tree = ttk.Treeview(content_frame, columns=columns, show="headings")

    table_style('Notification')

    # Define headings for the columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # Create an instance of NotificationManager
    notification_manager = NotificationManager(root, conn)

    # Fetch notification logs from the database
    notification_manager.cursor.execute("SELECT medicine_name, expiration_date, notification_date, days_until_expiration FROM notification_logs")
    logs = notification_manager.cursor.fetchall()

    # Insert the logs into the Treeview
    if logs:
        for log in logs:
            tree.insert("", tk.END, values=log)
    else:
        # Display a message if there are no logs
        tk.Label(content_frame, text="No notifications found.", font=('Arial', 14), pady=10).pack()

    # Bind the <<TreeviewSelect>> event to trigger the on_row_select function
    tree.bind('<<TreeviewSelect>>', on_row_select)


#------------------------------------------------------ACCOUNT SETTINGS FRAME----------------------------------------------------------------------
image_refs = []
def show_account_setting():
    global conn
    try:
        # Ensure the connection is active
        if conn.is_connected() == False:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="db_medicine_cabinet"
            )
    except mysql.connector.Error as err:
        print(f"Error reconnecting to the database: {err}")
        message_box = CustomMessageBox(
            root=root,
            title="ERROR",
            message="Database connection lost. Reconnecting...",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        return
    
    cursor = conn.cursor()

    clear_frame()
    reset_button_colors()
    if account_setting_button:
        account_setting_button.config(bg=active_bg_color)
        account_setting_button.config(fg=active_fg_color)
    
    tk.Label(content_frame, text="ACCOUNT SETTINGS", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1).pack(fill='x')

    # Create a frame for the treeview
    tree_frame = tk.Frame(content_frame)
    tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    table_style() #Call the function for styling the treeview

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
    # conn = sqlite3.connect('Medicine Cabinet.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, position, accountType FROM users ORDER BY accountType ASC")
    users = cursor.fetchall()

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

        def yes_delete():
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", [username])
            conn.commit()
            # Refresh the table after deleting
            show_account_setting()

        def no_delete():
            print("\nUser deletion canceled.")

        CustomMessageBox(
            root=tree, 
            title="Confirm Delete", 
            message=f"Are you sure you want to delete the user '{username}'?", 
            color="red", 
            yes_callback=yes_delete, 
            no_callback=no_delete,
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
            sound_file="sounds/confirmDelete.mp3"
        )

def add_user():
    global conn
    try:
        if not conn.is_connected():
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="db_medicine_cabinet"
            )
    except mysql.connector.Error as err:
        print(f"\nError reconnecting to the database: {err}")
        message_box = CustomMessageBox(
            root=root,
            title="ERROR",
            message="Database connection lost. Reconnecting...",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        return
    
    clear_frame()
    content_frame.grid_columnconfigure(0, weight=1)

    title_label = tk.Label(content_frame, text="ACCOUNT SETTINGS", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1)
    title_label.pack(fill='both')

    input_frame = tk.LabelFrame(content_frame, text='ADD NEW USER ACCOUNT', font=('Arial', 14), pady=20, padx=15, relief='raised', bd=5)
    input_frame.pack(pady=30, padx=20, anchor='center')

    keyboard = OnScreenKeyboard(content_frame)
    keyboard.create_keyboard()
    keyboard.hide_keyboard()

    tk.Label(input_frame, text="Username", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)
    username_entry = tk.Entry(input_frame, font=("Arial", 14), width=20)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Password", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10)
    password_entry = tk.Entry(input_frame, show="*", font=("Arial", 14), width=20)
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Confirm Password", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)
    confirm_password_entry = tk.Entry(input_frame, show="*", font=("Arial", 14), width=20)
    confirm_password_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Position", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10)
    position_combobox = ttk.Combobox(input_frame, font=("Arial", 14), values=["Midwife", "BHW", "BNS"], width=20)
    position_combobox.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Account Type", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10)
    accountType_combobox = ttk.Combobox(input_frame, font=("Arial", 14), values=["Admin", "Staff"], width=20)
    accountType_combobox.grid(row=5, column=1, padx=10, pady=10)

    for widget in [username_entry, password_entry, confirm_password_entry, position_combobox, accountType_combobox]:
        widget.bind("<FocusIn>", lambda e: keyboard.show_keyboard())
        widget.bind("<FocusOut>", lambda e: keyboard.hide_keyboard())

    def add_new_user():
        try:
            new_username = username_entry.get()
            new_password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            new_position = position_combobox.get()
            new_accountType = accountType_combobox.get()

            if validate_all_fields_filled(username_entry, password_entry, confirm_password_entry, position_combobox, accountType_combobox):
                if validate_user_info('add', new_username, new_password, confirm_password, new_position, new_accountType):

                    # Generate the QR code data string
                    qr_code_data = f"{new_username} - {new_position}"

                    # Insert the user into the database with qrcode_data
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO users (username, password, position, accountType, qrcode_data)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (new_username, new_password, new_position, new_accountType, qr_code_data))
                    conn.commit()

                    # Generate and save QR code image temporarily
                    qr_path = generate_qrcode(qr_code_data)

                    # Display success message with QR code
                    message_box = CustomMessageBox(
                        root=root,
                        title="SUCCESS",
                        message=f'Successfully added new user {new_username}',
                        icon_path=qr_path,
                    )
                    show_account_setting()

                else:
                    message_box = CustomMessageBox(
                        root=root,
                        title="ERROR",
                        message="Please fill in all the fields.",
                        color="red",
                        icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                        sound_file="sounds/FillAllFields.mp3"
                    )
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def generate_qrcode(qr_data):
        # Ensure the 'users' directory exists
        qr_dir = os.path.join(os.path.dirname(__file__), 'users')
        os.makedirs(qr_dir, exist_ok=True)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_img = qr.make_image(fill='black', back_color='white')
        
        # Save the QR code image temporarily for display
        qr_path = os.path.join(qr_dir, f"{qr_data.split(' - ')[0]}_qrcode.png")
        qr_img.save(qr_path)
        
        return qr_path

    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(input_frame, text="Cancel", font=("Arial", 16), bg=motif_color, fg='white', command=show_account_setting, width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img, pady=5)
    cancel_button.image = cancel_img
    cancel_button.grid(row=7, column=0, padx=(40, 60), pady=(50, 0))

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(input_frame, text="Save", font=("Arial", 16), bg=motif_color, fg='white', width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=save_img, pady=5, command=add_new_user)
    save_button.image = save_img
    save_button.grid(row=7, column=1, padx=(60, 40), pady=(50, 0))    

def on_tree_select(tree):
    selected_item = tree.selection()  # Get selected item
    if selected_item:
        username = tree.item(selected_item, "values")[0]
        edit_user(username)
    else:
        message_box = CustomMessageBox(
            root=root,
            title="WARNING",
            message="Please select a user to edit.",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
    )

def validate_all_fields_filled(*widgets):
    for widget in widgets:
        if isinstance(widget, tk.Entry):
            if not widget.get():
                return False
        elif isinstance(widget, ttk.Combobox):
            if not widget.get():
                return False
    return True

def validate_user_info(mode, username, password, confirm_password, position, accountType):
    # Check if passwords match
    if password != confirm_password:
        message_box = CustomMessageBox(
            root=root,
            title="ERROR",
            message="Passwords do not match.",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        return False

    # Check if username already exists
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s", [username])
    user_exists = cursor.fetchone()

    if mode == 'add' and user_exists:
        message_box = CustomMessageBox(
            root=root,
            title="ERROR",
            message="Username already exists.",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        return False

    # Check if accountType is Admin and if there are already 2 Admins
    if accountType == 'Admin':
        cursor.execute("SELECT COUNT(*) FROM users WHERE accountType = 'Admin'")
        admin_count = cursor.fetchone()[0]

        if admin_count >= 2:
            message_box = CustomMessageBox(
                root=root,
                title="ERROR",
                message="There are already 2 admin accounts. You cannot add more.",
                color="red",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

    # All validations passed
    return True


def toplevel_destroy(window):
        window.destroy()

def edit_user(username):
    # Clear the content_frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Retrieve the user information from the database
    cursor = conn.cursor()
    cursor.execute("SELECT position, accountType, password, qrcode_data FROM users WHERE username = %s", [username])
    user = cursor.fetchone()

    title_label = tk.Label(content_frame, text="ACCOUNT SETTINGS", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1)
    title_label.pack(fill='both')

    # Create input frame and ensure it expands horizontally
    input_frame = tk.LabelFrame(content_frame, text='Edit User Account', font=('Arial', 14), pady=20, padx=10, relief='raised', bd=5)
    input_frame.pack(pady=30, padx=20, anchor='center')

    # Instantiate OnScreenKeyboard
    keyboard = OnScreenKeyboard(content_frame)
    keyboard.create_keyboard()
    keyboard.hide_keyboard()  # Initially hide the keyboard
  

    # Username entry
    tk.Label(input_frame, text="Username", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(input_frame, font=("Arial", 14))
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    username_entry.insert(0, username)
    
    # Password entry
    tk.Label(input_frame, text="Password", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(input_frame, show="*", font=("Arial", 14))
    password_entry.grid(row=1, column=1, padx=10, pady=10)
    password_entry.insert(0, user[2])
    
    # Position combobox
    tk.Label(input_frame, text="Position", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10)
    position_combobox = ttk.Combobox(input_frame, font=("Arial", 14), values=["Midwife", "BHW", "BNS"])
    position_combobox.grid(row=2, column=1, padx=10, pady=10)
    position_combobox.set(user[0])
    position_combobox.config(validate="key", validatecommand=(position_combobox.register(validate_combobox_input), '%d', '%S'))

    # Account Type combobox
    tk.Label(input_frame, text="Account Type", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)
    accountType_combobox = ttk.Combobox(input_frame, font=("Arial", 14), values=["Admin", "Staff"])
    accountType_combobox.grid(row=3, column=1, padx=10, pady=10)
    accountType_combobox.set(user[1])
    accountType_combobox.config(validate="key", validatecommand=(position_combobox.register(validate_combobox_input), '%d', '%S'))

    # Save changes button
    def save_changes():
        new_username = username_entry.get()
        new_password = password_entry.get()
        new_position = position_combobox.get()
        new_accountType = accountType_combobox.get()

        if validate_user_info('edit', new_username, new_password, new_password, new_position, new_accountType):
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET username = %s, password = %s, position = %s, accountType = %s
                WHERE username = %s
            """, [new_username, new_password, new_position, new_accountType, username])
            conn.commit()

            # Success message
            message_box = CustomMessageBox(
                root=root,
                title="SUCCESS",
                message="User account successfully configured.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'accountSetting_Icon.png'),
            )
            show_account_setting()  # Refresh the user table
    
    # Cancel and Save buttons
    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(input_frame, text="Cancel", font=("Arial", 16), bg=motif_color, fg='white', command=show_account_setting, width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img, pady=5)
    cancel_button.image = cancel_img
    cancel_button.grid(row=5, column=0, padx=(40, 60), pady=(50, 0))

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(input_frame, text="Save", font=("Arial", 16), bg=motif_color, fg='white', width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=save_img, pady=5, command=save_changes)
    save_button.image = save_img
    save_button.grid(row=5, column=1, padx=(60, 40), pady=(50, 0))

    # Bind the focus events to show/hide the keyboard for each widget
    for widget in [username_entry, password_entry, position_combobox, accountType_combobox]:
        widget.bind("<FocusIn>", lambda e: keyboard.show_keyboard())
        widget.bind("<FocusOut>", lambda e: keyboard.hide_keyboard())

#-----------------------------------------------OTHER FUNCTIONS------------------------------------------------------
# Function that ensures users cannot type into the combobox  
def validate_combobox_input(action, value_if_allowed):
    return False


#Function for switching of Frames
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()

CHECK_INTERVAL = 15000  # Interval for checking the internet in milliseconds (e.g., 15000ms = 15 seconds)
wifi_ui_open = False  # Flag to track if the WiFiConnectUI is open

def check_internet(host="8.8.8.8", port=53, timeout=3):
    """Check if the system has an internet connection."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def periodic_internet_check(root):
    """Periodically checks for an internet connection and opens WiFiConnectUI if no connection is found."""
    global wifi_ui_open  # We use this flag to control the periodic check

    # Only run if WiFiConnectUI is not open
    if not wifi_ui_open:
        if not check_internet():
            # If the internet is lost, open WiFiConnectUI
            message_box = CustomMessageBox(
                root=root,
                title="Error",
                message="No internet connection.",
                color="red",  # Background color for warning
                ok_callback=lambda: show_wifi_connect(message_box),  # Open the WiFiConnect UI for network selection
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'noInternet_icon.png')  # Path to your icon
            )

    # Schedule the next check only if the WiFi UI is not open
    if not wifi_ui_open:
        root.after(CHECK_INTERVAL, lambda: periodic_internet_check(root))

def show_wifi_connect(message_box):
    """Opens the WiFi connection UI and pauses periodic checks."""
    global wifi_ui_open

    # Set flag to indicate WiFiConnectUI is open
    wifi_ui_open = True

    # Destroy the message box first
    message_box.destroy()

    # Open the WiFi connection UI
    wifi_ui = WiFiConnectUI(root)

    # When WiFiConnectUI is closed, resume the periodic check
    wifi_ui.protocol("WM_DELETE_WINDOW", on_wifi_ui_close)

def on_wifi_ui_close():
    """Callback to handle the closing of WiFiConnectUI and resume the periodic checks."""
    global wifi_ui_open

    # Reset the flag when WiFiConnectUI is closed
    wifi_ui_open = False

    # Restart the periodic check after WiFi UI is closed
    periodic_internet_check(root)

# Function to send the lock command
def lock_door():
    ser.write(b'lock\n')  # Send the "lock" command to the Arduino
    print("\nLock command sent")

# Function to send the unlock command
def unlock_door():
    ser.write(b'unlock\n')  # Send the "unlock" command to the Arduino
    print("\nUnlock command sent")


#-----------------------------------------------MAIN------------------------------------------------------
def main():
    global root, ser, container

    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("Electronic Medicine Cabinet Control System")
    root.state("zoomed")  # Maximize the window to full screen

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    global login_frame, loading_frame

    # Create a "Loading" frame
    loading_frame = tk.Frame(container, bg=motif_color)
    loading_label = tk.Label(loading_frame, text="Loading...", font=("Arial", 24), fg='white', bg=motif_color)
    loading_label.pack(expand=True)  # Center the "Loading" message
    loading_frame.grid(row=0, column=0, sticky="nsew")  # Fill the container

    # Show the loading frame initially
    loading_frame.tkraise()

    # Delay creation of login and main UI frames until Arduino connection is done
    def connect_to_arduino():
        global ser
        try:
            ser = serial.Serial('COM5', 9600)  # Port of the Arduino
            time.sleep(2)  # Wait for the connection to establish
            print("\nSerial connection established")
            # Once connected, proceed to show login_frame
            login_frame = create_login_frame(container)
        
            login_frame.tkraise()
        except serial.SerialException as e:
            print(f"\nError opening serial port: {e}")
            ser = None  # Set to None if the connection fails
            show_retry_window()  # Show retry window if connection fails

    # Create a Toplevel window for retrying the connection
    def show_retry_window():
        message_box = CustomMessageBox(
            root=loading_frame,
            title="Connection Error",
            message="Failed to connect to Arduino.\nPlease retry.",
            color="red",  # Background color for warning
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),  # Path to your icon
            ok_callback=lambda: retry_connection(message_box)
        )

    # Retry the connection when the button is clicked
    def retry_connection(frame):
        frame.destroy()
        loading_frame.tkraise()  # Show the loading frame again while retrying
        root.after(100, connect_to_arduino)  # Retry the connection

    # Call the function to connect to Arduino after showing the "Loading" screen
    root.after(100, connect_to_arduino)  # Introduce a slight delay before connecting

    # Initial internet check before showing any UI
    if not check_internet():
        wifi_window = WiFiConnectUI(root)
        root.wait_window(wifi_window)  # Pause the main UI until WiFi window is closed

    # Start periodic internet checking
    root.after(CHECK_INTERVAL, lambda: periodic_internet_check(root))

    root.mainloop()

    # Close the serial connection when the application exits, if it's open
    if ser is not None:
        ser.close()
        print("\nSerial connection closed")

if __name__ == "__main__":
    main()

