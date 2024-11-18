import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from tkinter import messagebox
from tkcalendar import DateEntry
import mysql.connector
from keyboard import *
from custom_messagebox import CustomMessageBox
from csv_exporter import *
from notification import *
from wifi_connect import WiFiConnectUI
import socket
import qrcode
from treeviewStyling import table_style
import serial
import time
from loginQrCode import QRLogin
# from lockunlock import LockUnlock
import threading
import datetime
import pygame
from notification import NotificationManager

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

INACTIVITY_PERIOD = 300000 #automatic logout timer in milliseconds
inactivity_timer = 0 #initialization of idle timer
root = None  # Global variable for root window

motif_color = '#42a7f5'
font_style = 'Arial'
font_size = 15

# Define the active and default background colors for Sidebar
active_bg_color = "#fff"  # Active background color
default_bg_color = motif_color  # Default background color
active_fg_color ='#000000' # Active foreground color
default_fg_color="#fff" # Default foreground color

# Create a path to store the file in a 'door_status' folder within the current directory
file_path = os.path.join(os.getcwd(), "door_status", "door_status.txt")

# Ensure the folder exists before writing the file
os.makedirs(os.path.dirname(file_path), exist_ok=True)



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
        user_role = user[3]
        main_ui_frame = create_main_ui_frame(container) 
        main_ui_frame.tkraise()
        reset_timer()
        bind_activity_events()
        show_medicine_supply()
        configure_sidebar(user_role)
        update_datetime()
        # Check for soon-to-expire medicines on home page load
        notification_manager = NotificationManager(root, asap=True)
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
    global main_ui_frame, date_time_label
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
    notification_button = tk.Button(sidebar_frame, height=100, width=350, text="Notification", command=show_notification_table, font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=notification_img, justify="left", padx=10, anchor='w')
    notification_button.image = notification_img
    notification_button.grid(row=4, column=0, sticky="we", columnspan=2)
    
    account_setting_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'accountSetting_Icon.png')).resize((50, 50), Image.LANCZOS))
    global account_setting_button
    account_setting_button = None
    
    logout_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'logout_icon.png')).resize((40, 40), Image.LANCZOS))
    logout_button = tk.Button(sidebar_frame, height=100, width=350, text="Log Out", command=lambda: logout_with_sensor_check('manual logout'), font=("Arial", 16), bg=motif_color, fg="white", bd=1, relief="sunken", compound=tk.LEFT, image=logout_img, padx=10, anchor='w')
    logout_button.image = logout_img
    logout_button.grid(row=6, column=0, sticky="we", columnspan=2)
    # Assuming main_ui_frame is already defined as part of your Tkinter window
    user_and_datetime_label = tk.Frame(main_ui_frame)
    user_and_datetime_label.pack(fill='x', side='top')

    # Configure grid to expand columns appropriately
    user_and_datetime_label.grid_columnconfigure(0, weight=1)  # Left side (user label)
    user_and_datetime_label.grid_columnconfigure(1, weight=1)  # Right side (datetime label)

    # User label
    user = tk.Label(user_and_datetime_label, text=f'Welcome user, {Username}', anchor='w', padx=20, font=('Arial', 18, 'bold italic'))
    user.grid(row=0, column=0, sticky='w')  # Align to the left

    # Date and time label
    date_time_label = tk.Label(user_and_datetime_label, text=get_current_datetime(), anchor='e', padx=20, font=('Arial', 18, 'bold'))
    date_time_label.grid(row=0, column=1, sticky='e')  # Align to the right
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
    if reason == 'delete own':
        message_box = CustomMessageBox(
            root=login_frame,
            title="Session Expired",
            message="You deleted your own account.\nPlease log-in again using other account.",
            color='red',  # Background color for warning
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'logout_icon.png')
        )
        OnScreenKeyboard(content_frame).hide_keyboard()

def logout_with_sensor_check(logout_type):
    data = load_data()
    # Step 1: Check sensors before logging out
    arduino.write(b'check_sensors\n')
    time.sleep(0.1)  # Small delay for Arduino to respond

    # Step 2: Read Arduino's response
    if arduino.in_waiting > 0:
        response = arduino.readline().decode().strip()

        # Step 3: Proceed based on the sensor check response
        if data == "Unlocked" and response == "Object detected":
            # Destroy warning and proceed with logout
            print("Door detected but the data is unlocked")
            for widget in root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            LockUnlock(content_frame, Username, Password, arduino, "automatic_logout", "medicine inventory", container=root, exit_callback=lambda: logout(logout_type))
        
        elif data == "Locked" and response == "Object detected":
            logout(logout_type)
            print("Logged Out and data is locked")
        else:
            for widget in root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            # Recursive function to recheck the sensors
            def recheck_sensors(warning_box):
                arduino.write(b'check_sensors\n')
                time.sleep(0.1)
                
                if arduino.in_waiting > 0:
                    response = arduino.readline().decode().strip()
                    
                    if response == "Object detected" and data == "Unlocked":
                        # Destroy warning and proceed with logout
                        print("Door detected but the data is unlocked")
                        warning_box.destroy()
                        LockUnlock(content_frame, Username, Password, arduino, "automatic_logout", "medicine inventory", container=root, exit_callback=lambda: logout(logout_type))
                    elif response == "Object detected" and data == "Locked":
                        logout(logout_type)
                        print("Logged Out and data is locked")
                    else:
                        # Show warning again and recheck sensors
                        warning_box = CustomMessageBox(
                            root=content_frame,
                            title="Warning",
                            color='red',
                            message="Doors are not properly closed.\nPlease close the doors properly before you automatically logged out.",
                            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                            ok_callback=lambda: recheck_sensors(warning_box),
                            close_state=True
                        )
                        print("Rechecking sensors: No object detected.")

            # Show initial warning if sensors do not detect an object
            warning_box = CustomMessageBox(
                root=content_frame,
                title="Warning",
                color='red',
                message="Doors are not properly closed.\nPlease close the doors properly before you automatically logged out.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                ok_callback=lambda: recheck_sensors(warning_box),
                close_state=True
            )
            print("Logout command aborted: No object detected.")

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
    logout_with_sensor_check('inactivity')

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
def center_toplevel(toplevel):
    # Get the screen width and height
    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    # Get the dimensions of the Toplevel window
    window_width = toplevel.winfo_width()
    window_height = toplevel.winfo_height()

    # Calculate the x and y coordinates to center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the new position of the Toplevel window
    toplevel.geometry(f"+{x}+{y}")

#Function that creates the UI for deposit toplevel
def deposit_window(permission):
    deposit_Toplevel = tk.Toplevel(root, relief='raised', bd=5)
    deposit_Toplevel.attributes('-topmost', True)
    deposit_Toplevel.overrideredirect(True)  # Remove the title bar
    deposit_Toplevel.resizable(width=False, height=False)
    deposit_Toplevel.focus_set()
    deposit_Toplevel.grab_set()

    # Center the Toplevel window when it's created
    center_toplevel(deposit_Toplevel)

    # Bind the <Configure> event to the centering function
    deposit_Toplevel.bind("<Configure>", lambda e: center_toplevel(deposit_Toplevel))

    deposit_Toplevel.bind("<Motion>", reset_timer)
    deposit_Toplevel.bind("<KeyPress>", reset_timer)
    deposit_Toplevel.bind("<ButtonPress>", reset_timer)


    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_medicine_cabinet"
    )

    title_label = tk.Label(deposit_Toplevel, text="DEPOSIT MEDICINE", bg=motif_color, fg="white", font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1)
    title_label.pack(fill='both')

    # Create input frame and ensure it expands horizontally
    input_frame = tk.LabelFrame(deposit_Toplevel, text='Fill out all the necessary information below', font=('Arial', 14), pady=20, padx=5, relief='raised', bd=5)
    input_frame.pack(fill='x', pady=30, padx=300)

    # Instantiate OnScreenKeyboard and NumericKeyboard
    keyboard = OnScreenKeyboard(deposit_Toplevel)
    keyboard.create_keyboard()
    keyboard.hide_keyboard()  # Initially hide the keyboard

    numKeyboard = NumericKeyboard(deposit_Toplevel)
    numKeyboard.create_keyboard()
    numKeyboard.hide()

    # Type Combobox
    tk.Label(input_frame, text="Generic Name: ", font=("Arial", 16)).grid(row=0, column=0, padx=(30, 20), pady=10, sticky='e')
    type_combobox = tk.Entry(input_frame, font=("Arial", 16), width=2)
    type_combobox.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    # Name Combobox
    tk.Label(input_frame, text="Brand Name: ", font=("Arial", 16)).grid(row=1, column=0, padx=(30, 20), pady=10, sticky='e')
    name_combobox = tk.Entry(input_frame, font=("Arial", 16), width=20)
    name_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    # Unit Combobox
    tk.Label(input_frame, text="Dosage: ", font=("Arial", 16)).grid(row=2, column=0, padx=(30, 20), pady=10, sticky='e')
    dosage_spinbox= tk.Spinbox(input_frame, from_=0, to=1000, font=("Arial", 16), width=5)
    dosage_spinbox.grid(row=2, column=1, padx=(10, 10), pady=10, sticky='ew')
    dosage_spinbox.delete(0, tk.END)

    # Unit OptionMenu
    tk.Label(input_frame, text="Unit: ", font=("Arial", 16)).grid(row=3, column=0, padx=(30, 20), pady=10, sticky='e')

    # Define units and set the placeholder as the initial value
    units = ["Syrup", "Capsule", "Tablet"]
    selected_unit = tk.StringVar(value="Select a unit")  # Set placeholder value

    # Create OptionMenu with placeholder
    unit_option_menu = tk.OptionMenu(input_frame, selected_unit, *units)
    unit_option_menu.config(font=("Arial", 16), width=20, bg='white')
    unit_option_menu.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

    # Optional: Add validation to check if a valid unit is selected (i.e., placeholder is removed)
    def validate_selection(*args):
        if selected_unit.get() == "Select a unit":
            selected_unit.set(units[0])  # You could set it to units[0] or keep the placeholder for invalid selection feedback

    # Track changes in the selected unit to enforce valid selection if needed
    selected_unit.trace_add("write", validate_selection)

    # Customize the dropdown menu styling
    menu = unit_option_menu["menu"]
    menu.config(font=("Arial", 18), activebackground="blue") 

    tk.Label(input_frame, text="Quantity: ", font=("Arial", 16)).grid(row=4, column=0, padx=(30, 20), pady=10, sticky='e')
    quantity_spinbox = tk.Spinbox(input_frame, from_=0, to=100, font=("Arial", 16), width=20)
    quantity_spinbox.grid(row=4, column=1, padx=10, pady=(10, 1), sticky='ew')
    quantity_spinbox.delete(0, tk.END)

    tk.Label(input_frame, text="For capsule or tablet box, input the pieces of blisters present in the box.\nFor syrup box, input the pieces of box/es to be deposited.", font=("Arial", 13), justify="center").grid(row=5, column=0, padx=(30, 10), pady=(0, 10), sticky='w', columnspan=2)

    tk.Label(input_frame, text="Expiration Date: ", font=("Arial", 16)).grid(row=6, column=0, padx=(30, 20), pady=(5, 1), sticky='e')
    expiration_date_entry = DateEntry(input_frame, font=("Arial", 16), date_pattern='mm-dd-y', width=20)
    expiration_date_entry.grid(row=6, column=1, padx=10, pady=10, sticky='ew')


    # Bind focus events to show/hide the keyboard for each widget
    for widget in [name_combobox, type_combobox, expiration_date_entry]:
        widget.bind("<FocusIn>", lambda e: keyboard.show_keyboard())
        widget.bind("<FocusOut>", lambda e: keyboard.hide_keyboard())

    for widgetz in [quantity_spinbox, dosage_spinbox]:
        widgetz.bind("<FocusIn>", lambda e: numKeyboard.show())
        widgetz.bind("<FocusOut>", lambda e: numKeyboard.hide())

    # Save button logic
    def save_medicine():
        name = name_combobox.get()
        type_ = type_combobox.get()
        dosage = dosage_spinbox.get()
        quantity = quantity_spinbox.get()
        unit = selected_unit.get()
        expiration_date = expiration_date_entry.get_date()
        keyboard.hide_keyboard()

        deposit = MedicineDeposit(name, type_,  quantity, unit, expiration_date, dosage, conn, root, root, content_frame, Username, Password, arduino, action="unlock", yes_callback=lambda: (print("Calling deposit_window with 'deposit_again'"), deposit_window(permission), deposit_Toplevel.destroy()))

        if deposit.validate_inputs():
            deposit_Toplevel.destroy()
            message_box = CustomMessageBox(root=root,
                             title="Deposit Medicine",
                             message=f"Adding Medicine:\n\nGeneric Name: {deposit.generic_name}\nBrand Name: {deposit.name}\nQuantity: {deposit.quantity}\nUnit: {deposit.unit}\nDosage: {deposit.dosage_for_db}\nExpiration Date: {deposit.expiration_date}\n\nClick 'Yes' to confirm medicine.",
                             icon_path=os.path.join(os.path.dirname(__file__), 'images', 'drugs_icon.png'),
                             yes_callback=lambda: (proceed_depositing(), message_box.destroy()),
                             no_callback=lambda: (message_box.destroy(), deposit_Toplevel.destroy()))
            def proceed_depositing():
                deposit.save_to_database()
                deposit_Toplevel.destroy()
                show_medicine_supply()

    # Cancel and Save buttons
    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(input_frame, text="Cancel", font=("Arial", 16), bg=motif_color, fg='white', width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img, pady=5)
    cancel_button.image = cancel_img
    cancel_button.grid(row=7, column=0, padx=(40, 60), pady=(50, 0))

    if permission == 'deposit_again':
        cancel_button.config(command=lambda: (LockUnlock(root, Username, Password, arduino, "lock", "medicine inventory", container=root), deposit_Toplevel.destroy()))
    else:
        cancel_button.config(command=lambda: (show_medicine_supply(), deposit_Toplevel.destroy()))

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(input_frame, text="Save", font=("Arial", 16), bg=motif_color, fg='white', width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=save_img, pady=5, command=save_medicine)
    save_button.image = save_img
    save_button.grid(row=7, column=1, padx=(60, 40), pady=(50, 0))

def check_sensor(toplevel):
    print("Checking sensors...")
    # Step 1: Check sensors
    arduino.write(b'check_sensors\n')
    time.sleep(0.1)  # Small delay for Arduino to respond

    # Step 2: Read Arduino's response
    if arduino.in_waiting > 0:
        response = arduino.readline().decode().strip()

        # Step 3: Proceed based on the sensor check response
        if response == "Object detected":
            # Proceed with logout if sensors detect an object
            toplevel.destroy()
            arduino.write(b'lock\n')
            print("Locked the door successfully")

        else:
            # Recursive function to recheck the sensors
            def recheck_sensors(warning_box):
                arduino.write(b'check_sensors\n')
                time.sleep(0.1)
                
                if arduino.in_waiting > 0:
                    response = arduino.readline().decode().strip()
                    
                    if response == "Object detected":
                        # Destroy warning and proceed with logout
                        warning_box.destroy()
                        arduino.write(b'lock\n')
                        toplevel.destroy()
                        success_box = CustomMessageBox(
                            root=content_frame,
                            title="Warning",
                            color=motif_color,
                            message="Doors are not properly closed.",
                            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                            ok_callback=lambda: recheck_sensors(warning_box)
                        )
                        success_box.bind("<Motion>", reset_timer)
                        success_box.bind("<KeyPress>", reset_timer)
                        success_box.bind("<ButtonPress>", reset_timer)
                        print("Locked the Door Successfully")
                    else:
                        # Show warning again and recheck sensors
                        warning_box = CustomMessageBox(
                            root=content_frame,
                            title="Warning",
                            color='red',
                            message="Doors are not properly closed.",
                            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                            ok_callback=lambda: recheck_sensors(warning_box)
                        )
                        warning_box.bind("<Motion>", reset_timer)
                        warning_box.bind("<KeyPress>", reset_timer)
                        warning_box.bind("<ButtonPress>", reset_timer)
                        print("Rechecking sensors: No object detected.")

            # Show initial warning if sensors do not detect an object
            warning_box = CustomMessageBox(
                root=content_frame,
                title="Warning",
                color='red',
                message="Doors are not properly close.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                ok_callback=lambda: recheck_sensors(warning_box)
            )
            warning_box.bind("<Motion>", reset_timer)
            warning_box.bind("<KeyPress>", reset_timer)
            warning_box.bind("<ButtonPress>", reset_timer)
            print("Door is not properly closed")


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
    header_frame.pack(fill="x", pady=(0, 10))

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

    def populate_treeview(order_by="name", sort="ASC"):
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
        query = f"SELECT name, type, dosage, quantity, unit, date_stored, expiration_date FROM medicine_inventory WHERE quantity <> 0 ORDER BY {order_by} {sort}"
        cursor.execute(query)
        medicine = cursor.fetchall()

        # Find the maximum length of data for each column
        column_lengths = [len(col) for col in columns]  # Start with header lengths
        for med in medicine:
            for i, value in enumerate(med):
                value_str = str(value)
                column_lengths[i] = max(column_lengths[i], len(value_str))

        # Set the width of each column based on its maximum length
        char_width = 8  # Approximate width of a character in pixels
        padding = 20    # Add padding to each column
        for i, col in enumerate(columns):
            column_width = (column_lengths[i] * char_width) + padding
            tree.column(col, width=column_width, anchor=tk.CENTER)

        # Filter data in Python based on the search term
        filtered_medicine = []
        search_term_lower = search_term.lower()

        for med in medicine:
            name, type, dosage, quantity, unit, date_stored, expiration_date = med

            # Convert date objects to strings (handling NoneType)
            date_stored_str = date_stored.strftime("%b %d, %Y").lower() if date_stored else "N/A"
            expiration_date_str = expiration_date.strftime("%b %d, %Y").lower() if expiration_date else "N/A"

            # Check if the search term matches any of the fields
            if (
                search_term_lower in name.lower() or
                search_term_lower in type.lower() or
                search_term_lower in unit.lower() or
                search_term_lower in dosage.lower() or
                search_term_lower in str(quantity).lower() or
                search_term_lower in date_stored_str or
                search_term_lower in expiration_date_str
            ):
                filtered_medicine.append(med)

        # Use the filtered results to populate the Treeview
        if filtered_medicine:
            for i, med in enumerate(filtered_medicine):
                name, type, dosage, quantity, unit, date_stored, expiration_date = med
                date_stored_str = date_stored.strftime("%b %d, %Y") if date_stored else "N/A"
                expiration_date_str = expiration_date.strftime("%b %d, %Y") if expiration_date else "N/A"
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                tree.insert("", "end", values=(name, type, dosage, quantity, unit, date_stored_str, expiration_date_str), tags=(tag,))
        else:
            # Insert a placeholder row if no matches are found
            tree.insert("", "end", values=("", "", "", "No Search Match", "", "", ""), tags=('no_match',))

        # Style the 'no match' row
        tree.tag_configure('no_match', background="#f5c6cb", foreground="#721c24")



    def sort_treeview(column, clicked_button):
        global active_column, sort_order

        # Enable all buttons first
        for btn in buttons:
            btn.config(bg=motif_color, fg="white", state="normal")

        # Set the clicked button to active style and disable it
        clicked_button.config(bg="white", fg="black", state="disabled")

        # Check if we're clicking the same column to toggle sort order
        if active_column == column:
            # Toggle the sort order if the same button is clicked again
            sort_order = "DESC" if sort_order == "ASC" else "ASC"
        else:
            # Set active column and reset sort order to ascending
            active_column = column
            sort_order = "ASC"

        # Repopulate the treeview with the current sorting
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
    tk.Label(header_frame, text="Sort by:", bg=motif_color, fg='white', padx=10, pady=5, font=(font_style, font_size)).grid(row=0, column=2, padx=(50, 5), pady=10, sticky="e")

    sort_button_1 = tk.Button(header_frame, text="Brand Name", bg='white', fg=motif_color, padx=10, pady=5,
                              command=lambda: sort_treeview("name", sort_button_1), relief="raised", bd=4, font=(font_style, font_size), state="disabled", width=10)
    sort_button_1.grid(row=0, column=3, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_1)

    sort_button_2 = tk.Button(header_frame, text="Generic Name", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("type", sort_button_2), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_2.grid(row=0, column=4, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_2)

    sort_button_3 = tk.Button(header_frame, text="Unit", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("unit", sort_button_3), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_3.grid(row=0, column=5, padx=6, pady=10, sticky="e")
    buttons.append(sort_button_3)

    sort_button_4 = tk.Button(header_frame, text="Date Stored", bg=motif_color, fg='white', padx=10, pady=5,
                              command=lambda: sort_treeview("date_stored", sort_button_4), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_4.grid(row=0, column=6, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_4)

    sort_button_5 = tk.Button(header_frame, text="Expiration Date", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("expiration_date", sort_button_5), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_5.grid(row=0, column=7, padx=6, pady=10, sticky="e")
    buttons.append(sort_button_5)

    activate_button(sort_button_1)

    # Frame for the treeview
    tree_frame = tk.Frame(content_frame, bg="#f0f0f0")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Custom scrollbar for the treeview
    tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    table_style()

    # Define columns
    columns = ("brand name", "generic name", "dosage", "quantity", "unit", "date stored", "expiration date")
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
    withdraw_button = tk.Button(button_frame, text="Withdraw", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=widthdraw_icon, command=lambda: LockUnlock(root, Username, Password, arduino, "unlock", "medicine inventory", container=root, type="withdraw"))
    withdraw_button.image = widthdraw_icon
    withdraw_button.grid(row=0, column=0, padx=20, pady=(12, ), sticky='ew')


    deposit_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'add_icon.png')).resize((25, 25), Image.LANCZOS))
    deposit_button = tk.Button(button_frame, text="Deposit", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=deposit_icon,command=lambda: deposit_window('normal'))
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

    def populate_treeview(order_by="username", sort="ASC"):
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

        # If no matches are found, display a "No search match" message
        if not filtered_logs:
            tree.insert("", "end", values=("    ", "    ", "        No search match", "", "", ""), tags=('nomatch',))
            tree.tag_configure('nomatch', background="#f5c6cb", foreground="#721c24")  # Styling for the no match row
            return

        # Populate the Treeview with the filtered results
        for i, log in enumerate(filtered_logs):
            username, accountType, position, date, time, action_taken = log
            
            # Convert date and time again for displaying
            date_str = date.strftime("%b %d, %Y") if date else "N/A"
            # Convert time (timedelta) to a 12-hour format with AM/PM
            if time:
                total_seconds = int(time.total_seconds())  # Convert timedelta to total seconds
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Convert to 12-hour format
                period = "AM" if hours < 12 else "PM"
                hours = hours % 12 or 12  # Convert 0 to 12 for midnight
                time_str = f"{hours:02}:{minutes:02}:{seconds:02} {period}"
            else:
                time_str = "N/A"

            # Alternate row colors using tags
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(username, date_str, time_str, accountType, position, action_taken), tags=(tag,))

    def sort_treeview(column, clicked_button):
        global active_column, sort_order

        # Enable all buttons first
        for btn in buttons:
            btn.config(bg=motif_color, fg="white", state="normal")

        # Set the clicked button to active style and disable it
        clicked_button.config(bg="white", fg="black", state="disabled")

        if column == 'date':
            sort_order = 'DESC'
        else:
            sort_order = 'ASC'

        # Check if we're clicking the same column to toggle sort order
        if active_column == column:
            # Toggle the sort order if the same button is clicked again
            sort_order = "DESC" if sort_order == "ASC" else "ASC"
            if active_column == 'date':
                sort_order = "DESC"
        else:
            # Set active column and reset sort order to ascending
            active_column = column
            sort_order = "ASC"

        # Repopulate the treeview with the current sorting
        populate_treeview(order_by=active_column, sort=sort_order)


    # Header frame for sorting buttons and search bar
    header_frame = tk.Frame(content_frame, bg=motif_color)
    header_frame.pack(fill="x", pady=(0, 10))

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
    tk.Label(header_frame, text="Sort by:", bg=motif_color, fg='white', padx=10, pady=5, font=(font_style, font_size)).grid(row=0, column=1, padx=(50, 5), pady=10, sticky="e")

    sort_button_date_time = tk.Button(header_frame, text="Date & Time", bg="white", fg='black', padx=10, pady=5,
                                    command=lambda: sort_treeview("date", sort_button_date_time), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_date_time.grid(row=0, column=3, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_date_time)

    sort_button_1 = tk.Button(header_frame, text="Username", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("username", sort_button_1), relief="raised", bd=4, font=(font_style, font_size), width=10, state="disabled")
    sort_button_1.grid(row=0, column=2, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_1)

    sort_button_2 = tk.Button(header_frame, text="Account Type", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("accountType", sort_button_2), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_2.grid(row=0, column=4, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_2)

    sort_button_3 = tk.Button(header_frame, text="Position", bg=motif_color, fg="white", padx=10, pady=5,
                              command=lambda: sort_treeview("position", sort_button_3), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_3.grid(row=0, column=5, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_3)

    sort_button_6 = tk.Button(header_frame, text="Action Taken", bg=motif_color, fg='white', padx=10, pady=5,
                              command=lambda: sort_treeview("action_taken", sort_button_6), relief="raised", bd=4, font=(font_style, font_size), width=10)
    sort_button_6.grid(row=0, column=6, padx=5, pady=10, sticky="e")
    buttons.append(sort_button_6)

    activate_button(sort_button_1)

    tree_frame = tk.Frame(content_frame, bg="#f0f0f0")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Custom scrollbar for the treeview
    tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    table_style()

     # Create the Treeview to display the door logs
    columns = ("Username", "Date", "Time", "Account Type", "Position", "Action Taken")
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
    lock_button = tk.Button(button_frame, text="Lock", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=lock_icon, command=lambda: LockUnlock(root, Username, Password, arduino, "lock", "medicine inventory", container=root, type="disable"))
    lock_button.image = lock_icon
    lock_button.grid(row=0, column=0, padx=20, pady=(12, ), sticky='ew')

    # Add the second new button (e.g., 'Button 2')
    unlock_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'unlockWhite_icon.png')).resize((35, 35), Image.LANCZOS))
    unlock_button = tk.Button(button_frame, text="Disable lock", padx=20, pady=10, font=('Arial', 18), bg=motif_color, fg="white", relief="raised", bd=4, compound=tk.LEFT, image=unlock_icon, command=display_disable_unlock)
    unlock_button.image = unlock_icon
    unlock_button.grid(row=0, column=1, padx=20, pady=(12, 7), sticky='ew')


    
    if load_data() == 'Locked':
        lock_button.config(state='disabled')
    elif load_data == 'Unlocked':
        unlock_button.config(state='disabled')

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

def display_disable_unlock():
    message_box = CustomMessageBox(root=root, title="Disable Unlock", color='red', message="Are you sure to disable lock mechanism?\n\nNOTE: This feauture is dedicated only for power interruptions.", yes_callback=disable_unlock, no_callback=lambda: print("Dsestroyed"), icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'))


def disable_unlock():
    LockUnlock(root, Username, Password, arduino, "unlock", "medicine inventory", container=root, type="disable", exit_callback=logout('disable-unlock'))


#--------------------------------------------------------- NOTIFICATION -----------------------------------------------------------       

# Define the refresh interval in milliseconds 
REFRESH_INTERVAL = 50000

# Function to display selected row's data in a Toplevel window
def on_row_select(event):
    # Get the selected item
    selected_item = tree_notif.focus()
    row_data = tree_notif.item(selected_item, 'values')

    # Row styling
    tree_notif.tag_configure('oddrow', background="white")
    tree_notif.tag_configure('evenrow', background="#f2f2f2")
    
    # Create a new Toplevel window to show the selected row's data
    if row_data:  # Only if a row is selected
        text = (f"A medicine is about to expire!\n\n"
                f"Medicine Name: {row_data[0]}\nExpiration Date: {row_data[1]}\n"
                f"Notification Date: {row_data[2]}\nDays Until Expiration: {row_data[3]}")
        message_box = CustomMessageBox(
            root=content_frame,
            title="Medicine Expiration",
            color='red',
            message=text,
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)

def fetch_notifications():
    """Fetch notifications from the notification_logs table."""
    notifications = []
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Replace with your MySQL password
            database="db_medicine_cabinet"
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Fetch data from notification_logs table
            query = ("SELECT medicine_name, expiration_date, notification_date, days_until_expiration "
                     "FROM notification_logs "
                     "ORDER BY notification_date DESC, notification_time DESC")
            cursor.execute(query)
            notifications = cursor.fetchall()

    except mysql.connector.Error as e:
        print("Error while connecting to MySQL:", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

    return notifications

def update_notification_logs():
    """Fetches updated notification logs and refreshes the Treeview."""
    # Clear existing rows in the Treeview
    for item in tree_notif.get_children():
        tree_notif.delete(item)

    # Fetch new notification logs from the database
    logs = fetch_notifications()

    # Insert the new logs into the Treeview with alternating row colors
    if logs:
        for index, log in enumerate(logs):
            tag = 'oddrow' if index % 2 == 0 else 'evenrow'
            tree_notif.insert("", tk.END, values=(
                log['medicine_name'], log['expiration_date'], log['notification_date'], log['days_until_expiration']),
                tags=(tag,))
    else:
        # Display a message if there are no logs (optional)
        tk.Label(content_frame, text="No notifications found.", font=('Arial', 14), pady=10).pack()

    # Schedule the next update after the specified interval
    content_frame.after(REFRESH_INTERVAL, update_notification_logs)

def show_notification_table():
    # Apply table style
    table_style()
    global tree_notif
    notify = NotificationManager(root, asap=False)
    notify.check_soon_to_expire()

    """Display the notification logs table in the Treeview."""
    clear_frame()
    reset_button_colors()
    notification_button.config(bg=active_bg_color, fg=active_fg_color)

    # Add a header
    tk.Label(content_frame, text="NOTIFICATION LOGS", bg=motif_color, fg="white",
             font=('Arial', 25, 'bold'), height=2, relief='groove', bd=1).pack(fill='x')

    tree_frame = tk.Frame(content_frame, bg="#f0f0f0")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Custom scrollbar for the treeview
    tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    table_style()

     # Create the Treeview to display the door logs
    columns = ("Medicine Name", "Expiration Date", "Notification Time", "Days Until Exp")
    tree_notif = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

    # Define columns
    tree_scroll.config(command=tree_notif.yview)

    # Column headings
    for col in columns:
        tree_notif.heading(col, text=col.capitalize())

    # Column configurations    for col in columns:
    for col in columns:
        tree_notif.column(col, anchor=tk.CENTER, width=100)

    # Row styling
    tree_notif.tag_configure('oddrow', background="white")
    tree_notif.tag_configure('evenrow', background="#f2f2f2")

    # Mouse wheel support
    def on_mouse_wheel(event):
        tree_notif.yview_scroll(int(-1*(event.delta/120)), "units")

    tree_notif.bind("<<TreeviewSelect>>", on_row_select)

    tree_notif.bind_all("<MouseWheel>", on_mouse_wheel)

    tree_notif.pack(side=tk.LEFT, fill="both", expand=True)

    # Initial fetch and start automatic refresh
    update_notification_logs()

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
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)
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
    tree.column("username", width=150, anchor=tk.CENTER)
    tree.column("position", width=150, anchor=tk.CENTER)
    tree.column("accountType", width=150, anchor=tk.CENTER)

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
    delete_button = tk.Button(button_frame, text="Delete User", font=("Arial", 15), pady=20, padx=25, bg=motif_color, fg='white', height=25, relief="raised", bd=3, compound=tk.LEFT, image=delete_img, command=lambda: delete_selected_user(tree, Username, conn))
    delete_button.image = delete_img
    delete_button.grid(row=0, column=2, padx=30, pady=10, sticky="ew")


def delete_selected_user(tree, authenticated_user, conn):
    selected_item = tree.selection()  # Get selected item
    if not selected_item:
        return

    username = tree.item(selected_item, "values")[0]
    account_type = tree.item(selected_item, "values")[2]  # Account type for the selected user
    cursor = conn.cursor()

    # Check the number of admin accounts
    cursor.execute("SELECT COUNT(*) FROM users WHERE accountType = 'Admin'")
    admin_count = cursor.fetchone()[0]

    # Define callbacks for deletion confirmation
    def yes_delete():
        # If user confirms deleting own account, check if it’s the last admin
        if username == authenticated_user and account_type == "Admin" and admin_count <= 1:
            message_box = CustomMessageBox(
                root=tree, 
                title="Action Denied", 
                message="Cannot delete the last admin account.", 
                color="red",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            return
        
        # Proceed with deletion
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        if username == authenticated_user:
            logout_with_sensor_check("delete own")
        else:
            show_account_setting()  # Refresh the account settings

    def no_delete():
        print("User deletion canceled.")

    # Check if the selected account is the user’s own account
    if username == authenticated_user:
        # Ask for confirmation to delete own account
        message_box = CustomMessageBox(
            root=tree, 
            title="Confirm Delete", 
            message=f"Are you sure you want to delete your own account '{username}'?", 
            color="red", 
            yes_callback=yes_delete, 
            no_callback=no_delete,
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)
    else:
        # If it's another user, check if they're the last admin and confirm deletion
        if account_type == "Admin" and admin_count <= 1:
            message_box = CustomMessageBox(
                root=tree, 
                title="Action Denied", 
                message="Cannot delete the last admin account.", 
                color="red",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            return

        # Ask for confirmation to delete other user's account
        message_box = CustomMessageBox(
            root=tree, 
            title="Confirm Delete", 
            message=f"Are you sure you want to delete the user '{username}'?", 
            color="red", 
            yes_callback=yes_delete, 
            no_callback=no_delete,
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
            sound_file=os.path.join(os.path.dirname(__file__), 'sounds', 'confirmDelete.mp3')
        )
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)

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

    # Position OptionMenu
    tk.Label(input_frame, text="Position", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10)

    # Define positions and set placeholder
    positions = ["Midwife", "BHW", "BNS", "BHC"]
    selected_position = tk.StringVar(value="Select Position")  # Placeholder

    position_option_menu = tk.OptionMenu(input_frame, selected_position, *positions)
    position_option_menu.config(font=("Arial", 16), width=20, bg='white')
    position_option_menu.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

    # Account Type OptionMenu
    tk.Label(input_frame, text="Account Type", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10)

    # Define account types and set placeholder
    account_types = ["Admin", "Staff"]
    selected_account_type = tk.StringVar(value="Select Account Type")  # Placeholder

    account_type_option_menu = tk.OptionMenu(input_frame, selected_account_type, *account_types)
    account_type_option_menu.config(font=("Arial", 16), width=20, bg='white')
    account_type_option_menu.grid(row=5, column=1, padx=10, pady=10, sticky='ew')


    # Optional: Function to ensure a valid selection (not the placeholder)
    def validate_selection(var, placeholder, valid_values):
        if var.get() == placeholder:
            var.set(valid_values[0])  # Set to a default valid value if needed

    # Customize the dropdown menu styling
    menu0 = position_option_menu["menu"]
    menu0.config(font=("Arial", 18), activebackground="blue") 
    menu1 = account_type_option_menu["menu"]
    menu1.config(font=("Arial", 18), activebackground="blue")


    # Track selection for Position and Account Type
    selected_position.trace_add("write", lambda *args: validate_selection(selected_position, "Select Position", positions))
    selected_account_type.trace_add("write", lambda *args: validate_selection(selected_account_type, "Select Account Type", account_types))


    for widget in [username_entry, password_entry, confirm_password_entry]:
        widget.bind("<FocusIn>", lambda e: keyboard.show_keyboard())
        widget.bind("<FocusOut>", lambda e: keyboard.hide_keyboard())

    def add_new_user():
        try:
            new_username = username_entry.get()
            new_password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            new_position = selected_position.get()
            new_accountType = selected_account_type.get()

            if validate_all_fields_filled(username_entry, password_entry, confirm_password_entry, selected_position, selected_account_type):
                if validate_user_info('add', new_username, new_password, confirm_password, new_position, new_accountType, new_accountType, new_position):

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
                    qr_path = generate_qrcode(qr_code_data, 'add', new_username)

            else:
                message_box = CustomMessageBox(
                    root=root,
                    title="ERROR",
                    message="Please fill in all the fields.",
                    color="red",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
                    sound_file="sounds/FillAllFields.mp3"
                )
                message_box.window.bind("<Motion>", reset_timer)
                message_box.window.bind("<KeyPress>", reset_timer)
                message_box.window.bind("<ButtonPress>", reset_timer)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(input_frame, text="Cancel", font=("Arial", 16), bg=motif_color, fg='white', command=show_account_setting, width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img, pady=5)
    cancel_button.image = cancel_img
    cancel_button.grid(row=7, column=0, padx=(40, 60), pady=(50, 0))

    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(input_frame, text="Save", font=("Arial", 16), bg=motif_color, fg='white', width=130, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=save_img, pady=5, command=add_new_user)
    save_button.image = save_img
    save_button.grid(row=7, column=1, padx=(60, 40), pady=(50, 0))

def edit_user(username):
    # Clear the content_frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Retrieve the user information from the database
    cursor = conn.cursor()
    cursor.execute("SELECT id, position, accountType, password, qrcode_data, username FROM users WHERE username = %s", [username])
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
    password_entry.insert(0, user[3])
    
    #Position OptionMenu
    tk.Label(input_frame, text="Position", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10)

    # Define the positions and initialize with database value or placeholder
    positions = ["Midwife", "BHW", "BNS", "BHC"]
    selected_position = tk.StringVar(value=user[1] if user[1] in positions else "Select Position")  # Set from DB or placeholder

    position_option_menu = tk.OptionMenu(input_frame, selected_position, *positions)
    position_option_menu.config(font=("Arial", 16), width=20, bg='white')
    position_option_menu.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

    # Account Type OptionMenu
    tk.Label(input_frame, text="Account Type", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)

    # Define account types and initialize with database value or placeholder
    account_types = ["Admin", "Staff"]
    selected_account_type = tk.StringVar(value=user[2] if user[2] in account_types else "Select Account Type")  # Set from DB or placeholder

    account_type_option_menu = tk.OptionMenu(input_frame, selected_account_type, *account_types)
    account_type_option_menu.config(font=("Arial", 16), width=20, bg='white')
    account_type_option_menu.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

    # Customize the dropdown menu styling
    menu0 = position_option_menu["menu"]
    menu0.config(font=("Arial", 18), activebackground="blue") 
    menu1 = account_type_option_menu["menu"]
    menu1.config(font=("Arial", 18), activebackground="blue")


    # Optional validation to ensure user does not submit with a placeholder selected
    def validate_selection(var, placeholder, valid_values):
        if var.get() == placeholder:
            var.set(valid_values[0])  # Set to a default valid value if needed


    # Track changes to enforce valid selection for both fields
    selected_position.trace_add("write", lambda *args: validate_selection(selected_position, "Select Position", positions))
    selected_account_type.trace_add("write", lambda *args: validate_selection(selected_account_type, "Select Account Type", account_types))

    # Save changes button
    def save_changes():
        new_username = username_entry.get()
        new_password = password_entry.get()
        new_position = selected_position.get()
        new_accountType = selected_account_type.get()

        if validate_user_info('edit', new_username, new_password, new_password, new_position, new_accountType, user[2], user[1]):
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
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            show_account_setting()  # Refresh the user table

        # New "Decode QR" button to generate QR based on existing QR data
    def decode_and_generate_qr():
        # Retrieve the qrcode_data from the database (it is stored as a string)
        qr_data = user[4]  # Assuming `qrcode_data` is at index 3
        
        # Generate QR code with the decoded data (this is already a string)
        qr_path = generate_qrcode(qr_data, 'edit', user[5])
        
        # You can optionally display or log the generated QR code path
        print(f"QR code generated and saved at: {qr_path}")
    
    # Cancel button
    cancel_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'cancelBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    cancel_button = tk.Button(input_frame, text="Cancel", font=("Arial", 16), bg=motif_color, fg='white', command=show_account_setting, padx=20, relief="raised", bd=3, compound=tk.LEFT, image=cancel_img, pady=5)
    cancel_button.image = cancel_img
    cancel_button.grid(row=5, column=0, pady=(50, 0))

    # New "Decode QR" button between Cancel and Save
    decode_qr_button = tk.Button(input_frame, text="Print QR", font=("Arial", 16), bg=motif_color, fg='white', command=decode_and_generate_qr, padx=20, relief="raised", bd=3, compound=tk.LEFT, pady=5)
    decode_qr_button.grid(row=5, column=1, pady=(50, 0))  # Position the new button between Cancel and Save

    # Save button
    save_img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'images', 'saveBlack_icon.png')).resize((25, 25), Image.LANCZOS))
    save_button = tk.Button(input_frame, text="Save", font=("Arial", 16), bg=motif_color, fg='white', padx=20, relief="raised", bd=3, compound=tk.LEFT, image=save_img, pady=5, command=save_changes)
    save_button.image = save_img
    save_button.grid(row=5, column=2, pady=(50, 0))

    # Bind the focus events to show/hide the keyboard for each widget
    for widget in [username_entry, password_entry]:
        widget.bind("<FocusIn>", lambda e: keyboard.show_keyboard())
        widget.bind("<FocusOut>", lambda e: keyboard.hide_keyboard())

def generate_qrcode(qr_data, mode, username):
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
    qr_path = os.path.join(qr_dir, f"{qr_data.split(' - ')[0]}_qrcode.png")
    qr_img.save(qr_path)

    # Combine QR with text
    print_qr_code_with_text(qr_path, username, mode)

    return qr_path

def print_qr_code_with_text(qr_image_path, username, mode):
    # Create a Toplevel window for "Printing..."
    printing_window = tk.Toplevel(relief='raised', bd=3, bg=motif_color)
    printing_window.overrideredirect(True)  # Remove the title bar

    # Get the screen width and height
    screen_width = printing_window.winfo_screenwidth()
    screen_height = printing_window.winfo_screenheight()

    # Set the dimensions of the Toplevel window
    window_width = 400
    window_height = 150

    # Calculate the position to center the window
    position_top = int((screen_height / 2) - (window_height / 2))
    position_left = int((screen_width / 2) - (window_width / 2))

    # Set the geometry of the window to center it
    printing_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")
    printing_window.resizable(False, False)

    # Label to show the printing status
    printing_label = tk.Label(printing_window, text="Loading, please wait...", font=("Arial", 18, 'bold'), fg='white', bg=motif_color)
    printing_label.pack(expand=True)

    # Call the function to print in a separate thread to keep the GUI responsive
    print_thread = threading.Thread(target=perform_printing, args=(qr_image_path, username, printing_window, username, mode))
    print_thread.start()


def perform_printing(qr_image_path, username, printing_window, userName, mode):
    try:
        # Simulate the QR code printing process
        qr_image = Image.open(qr_image_path)
        qr_image = qr_image.resize((200, 200))

        font_path = "C:/Windows/Fonts/arialbd.ttf"  # Adjust path as needed
        font = ImageFont.truetype(font_path, 35)
        text_width, text_height = font.getbbox(username)[2:]

        padding = 12
        total_width = qr_image.width + padding + text_width
        extra_space_below = 60
        total_height = max(qr_image.height, text_height) + extra_space_below

        combined_image = Image.new('L', (total_width, total_height), 255)
        combined_image.paste(qr_image, (padding + text_width, 0))

        draw = ImageDraw.Draw(combined_image)
        draw.text((padding, (total_height - text_height) // 2), username, font=font, fill=0)
        combined_image = combined_image.convert('1')

        img_data = image_to_escpos_data(combined_image)

        # Send the data to the printer
        SERIAL_PORT = 'COM4'
        BAUD_RATE = 9600
        TIMEOUT = 1

        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as printer:
            printer.write(img_data)
            printer.flush()
            printer.write(b'\x1d\x56\x42\x00')  # ESC/POS cut command
            printer.flush()

        if mode == 'add':
            # Display success message with QR code
            message_box = CustomMessageBox(
                root=root,
                title="Added User",
                message=f'Successfully added new user {userName}.\nPlease carefully tear off the QR code sticker.',
                icon_path=qr_image_path
            )
            show_account_setting()
        elif mode == 'edit':
            # Display success message with QR code
            message_box = CustomMessageBox(
                root=root,
                title="User QR Code",
                message=f'Printed the QR code for {userName}.\nPlease carefully tear off the QR code sticker.',
                icon_path=qr_image_path
            )
            show_account_setting()
        print("QR code and username printed successfully.")

    except Exception as e:
        print(f"Printing failed: {e}")
    finally:
        # Close the Toplevel window after printing is finished
        printing_window.destroy()


def image_to_escpos_data(img):
    width, height = img.size
    bytes_per_row = (width + 7) // 8  
    img_data = b'\x1d\x76\x30\x00' + bytes([bytes_per_row % 256, bytes_per_row // 256, height % 256, height // 256])

    for y in range(height):
        byte = 0
        row_data = b''
        for x in range(width):
            if img.getpixel((x, y)) == 0:  # Black pixel
                byte |= (1 << (7 - (x % 8)))
            if x % 8 == 7:
                row_data += bytes([byte])
                byte = 0
        if width % 8 != 0:
            row_data += bytes([byte])
        img_data += row_data

    return img_data    

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
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)

def validate_all_fields_filled(*widgets):
    for widget in widgets:
        if isinstance(widget, tk.Entry):
            if not widget.get():
                return False
        elif isinstance(widget, ttk.Combobox):
            if not widget.get():
                return False
        elif isinstance(widget, tk.StringVar):
            # Check if the StringVar is holding a placeholder value
            if widget.get() in ["Select Position", "Select Account Type"]:
                return False
    return True

def validate_user_info(mode, username, password, confirm_password, position, accountType, current_accountType, current_position):
    # Check if passwords match
    if password != confirm_password:
        message_box = CustomMessageBox(
            root=root,
            title="ERROR",
            message="Passwords do not match.",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)
        return False

    # Check if username already exists (for adding users only)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s", [username])
    user_exists = cursor.fetchone()

    # If mode is 'add' and the username exists, show error
    if mode == 'add' and user_exists:
        message_box = CustomMessageBox(
            root=root,
            title="ERROR",
            message="Username already exists.",
            color="red",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
        )
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)
        return False

    # Check if accountType is Admin and if there are already 2 Admins (Only for 'add' mode)
    if mode == 'add' and accountType == 'Admin':
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
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            return False
        
    if mode == 'add' and position == 'BHC':
        cursor.execute("SELECT COUNT(*) FROM users WHERE position = 'BHC'")
        councilor_count = cursor.fetchone()[0]

        if councilor_count >= 1:
            message_box = CustomMessageBox(
                root=root,
                title="ERROR",
                message="Can't add more Brgy Health Councilor account",
                color="red",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            return False

    # Check if position is being changed to "Admin" and there are already 2 Admins (Only for 'edit' mode)
    if mode == 'edit' and accountType == 'Admin' and current_accountType != 'Admin':
        cursor.execute("SELECT COUNT(*) FROM users WHERE accountType = 'Admin'")
        admin_count = cursor.fetchone()[0]

        if admin_count >= 2:
            message_box = CustomMessageBox(
                root=root,
                title="ERROR",
                message="There are already 2 admin accounts. You cannot make more admins.",
                color="red",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            return False
        
    if mode == 'edit' and position == 'BHC':
        cursor.execute("SELECT COUNT(*) FROM users WHERE position = 'BHC'")
        councilor_count = cursor.fetchone()[0]

        if councilor_count >= 1:
            message_box = CustomMessageBox(
                root=root,
                title="ERROR",
                message="Can't add more account for Brgy Health Councilor.",
                color="red",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)
            return False
        
    
    # All validations passed
    return True

def toplevel_destroy(window):
        window.destroy()

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
    arduino.write(b'lock\n')  # Send the "lock" command to the Arduino
    print("\nLock command sent")

# Function to send the unlock command
def unlock_door():
    arduino.write(b'unlock\n')  # Send the "unlock" command to the Arduino
    print("\nUnlock command sent")

def get_current_datetime():
    # Format date as "Nov 7, 2024" and time as "hh:mm:ss AM/PM"
    now = datetime.datetime.now()
    date_str = now.strftime("%b %d, %Y")   # "Nov 7, 2024"
    time_str = now.strftime("%I:%M:%S %p") # "hh:mm:ss AM/PM"
    return f"{date_str}     {time_str}"

def update_datetime():
    date_time_label.config(text=get_current_datetime())
    root.after(1000, update_datetime)

def load_data():
    try:
        with open(file_path, "r") as file:  # Use file_path here to load from the correct location
            return file.read().strip()  # Use strip() to remove any extra whitespace or newline
    except FileNotFoundError:
        return None
    

class LockUnlock:
    def __init__(self, root, userName, passWord, arduino, action, parentHeader, exit_callback=None, container=None, type=None, color=motif_color):
        self.user_Username = userName
        self.user_Password = passWord

        self.arduino = arduino
        self.action = action

        self.exit_callback = exit_callback

        # Initialize the Toplevel window
        self.window = tk.Toplevel(root, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)
        # self.window.attributes('-topmost', True)
        self.window.focus_set()

        self.window.bind("<Motion>", reset_timer)
        self.window.bind("<ButtonPress>", reset_timer)
        self.window.bind("<KeyPress>", reset_timer)

        self.reference_window = root

        self.warning_box = None

        # Update the window to get its correct size
        self.window.update_idletasks()

        # Center the Toplevel window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.window.geometry(f"+{x}+{y}")

        # Make the window modal (prevents interaction with other windows)
        self.window.grab_set()

        self.parentHeader = parentHeader
        self.container = container
        self.keyboardFrame = root
        self.type = type
        
        for widget in self.window.winfo_children():
            widget.destroy()

        # Add the close button icon at the top-right corner
        self.close_icon_path = os.path.join(os.path.dirname(__file__), 'images', 'cancel_icon.png')
        if self.close_icon_path:
            self.close_img = ImageTk.PhotoImage(Image.open(self.close_icon_path).resize((14, 14), Image.LANCZOS))
        else:
            self.close_img = None

            # Center the Toplevel window when it's created
        self._center_toplevel(self.window)

        # Bind the <Configure> event to the centering function
        self.window.bind("<Configure>", lambda e: self._center_toplevel(self.window))
        self.warning_box = None
        
        self._create_ui()

    def _center_toplevel(self, toplevel):
        # Get the screen width and height
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()

        # Get the dimensions of the Toplevel window
        window_width = toplevel.winfo_width()
        window_height = toplevel.winfo_height()

        # Calculate the x and y coordinates to center the window
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Set the new position of the Toplevel window
        toplevel.geometry(f"+{x}+{y}")


    def _create_ui(self):
        
        # Title frame
        title_frame = tk.Frame(self.window, bg=motif_color)
        title_frame.pack(fill='both')
        
        title_label = tk.Label(title_frame, text=self.action, font=('Arial', 15, 'bold'), fg='white', bg=motif_color, pady=12)
        title_label.pack(side=tk.LEFT, padx=(10, 20))

        if self.action == 'successful_close' or self.action == 'automatic_logout' or self.action == 'lock':
            title_label.config(text="Lock")
        elif self.action == 'unlock':
            title_label.config(text="Unlock")

        close_button = tk.Button(title_frame, image=self.close_img, command=self._exit_action, bg=motif_color, relief=tk.FLAT, bd=0)
        close_button.image = self.close_img  # Keep a reference to avoid garbage collection
        close_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 5))

        # Create a Notebook widget
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True)
        
         # Create a custom style for the Notebook tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 18, 'bold'), padding=[20, 17])  # Adjust font size and padding

        global tab1, tab2

        # Create frames for each tab
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)

        self.keyboard = OnScreenKeyboard(self.window)
        self.keyboard.create_keyboard()
        self.keyboard.hide_keyboard()  # Initially hide the keyboar
        

        # Add frames to the notebook with titles
        notebook.add(tab1, text="Manual")
        notebook.add(tab2, text="QR Code")

        if self.type == "withdraw":
            manual_instruction = tk.Label(tab1, text=f'Enter your username and password manually\nto unlock the door before proceeding to {self.type} medicine.', font=('Arial', 18))
        elif self.type == "deposit":
            manual_instruction = tk.Label(tab1, text=f'Enter your username and password manually\nto unlock the door before proceeding to {self.type} medicine.', font=('Arial', 18))
        else:
            manual_instruction = tk.Label(tab1, text=f'Enter your username and password manually\nto lock the door.', font=('Arial', 18))
        if self.type == "withdraw" and self.action == 'lock':
            manual_instruction = tk.Label(tab1, text=f'Enter your username and password manually\nto unlock the door before proceeding to lock the door.', font=('Arial', 18))
        if self.action == 'automatic_logout':
            manual_instruction = tk.Label(tab1, text="Please enter your username and password to lock the door now.", font=('Arial', 18))
            title_frame.config(bg='red')
            close_button.config(bg='red')
            title_label.config(bg='red')
        manual_instruction.pack(pady=10, anchor='center')

        username_label = tk.Label(tab1, text="Username", font=("Arial", 18))
        username_label.pack(pady=10)

        self.username_entry = tk.Entry(tab1, font=("Arial", 16), relief='sunken', bd=3, width=50)
        self.username_entry.pack(pady=5, padx=20)

        password_label = tk.Label(tab1, text="Password", font=("Arial", 18))
        password_label.pack(pady=10)

        self.password_entry = tk.Entry(tab1, show="*", font=("Arial", 16), relief='sunken', bd=3, width=50)
        self.password_entry.pack(pady=5, padx=20)

        # Function to show/hide password based on Checkbutton state
        def toggle_password_visibility():
            if show_password_var.get():
                self.password_entry.config(show='')
            else:
                self.password_entry.config(show='*')

        # Variable to track the state of the Checkbutton
        show_password_var = tk.BooleanVar()
        show_password_checkbutton = tk.Checkbutton(tab1, text="Show Password", variable=show_password_var,
                                                    command=toggle_password_visibility, font=("Arial", 14))
        show_password_checkbutton.pack(anchor='center', pady=(5, 10))  # Align to the left with padding

        enter_button = tk.Button(tab1, text="Enter", font=("Arial", 18, 'bold'), bg=motif_color, fg='white', relief="raised", bd=3, pady=7, padx=40, command=self._validate_credentials)
        enter_button.pack(anchor='center', pady=(0, 10))
        if self.action == 'automatic_logout':
            enter_button.config(bg='red')

        # Bind the FocusIn event to show the keyboard when focused
        self.username_entry.bind("<FocusIn>", lambda event : self._show_keyboard())
        self.password_entry.bind("<FocusIn>", lambda event : self._show_keyboard())


        #TAB 2 - QR SCANNING TO LOCK OUR UNLOCK THE DOOR

        # QR Code Scanner Icon
        original_logo_img = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((170, 170), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(original_logo_img)
        logo_label = tk.Label(tab2, image=logo_img)
        logo_label.image = logo_img  # Keep reference to avoid garbage collection
        logo_label.pack(side=tk.TOP, pady=(10, 10))

        # Instruction Message
        if self.action == 'unlock':
            instruction_label = tk.Label(tab2, text=f"Please scan your qrcode\nto lock or unlock the door.", font=("Arial", 18), fg='black')
        elif self.action == 'lock' or self.action == 'successful_close':
            instruction_label = tk.Label(tab2, text=f"Please scan your qrcode\nto lock the door.", font=("Arial", 18), fg='black')
        elif self.action == 'automatic_logout':
            instruction_label = tk.Label(tab2, text=f"Please scan your qrcode\nto lock the door now.", font=("Arial", 18), fg='black')
        instruction_label.pack(pady=10)

        # QR Code Entry Frame
        entry_frame = tk.Frame(tab2)
        entry_frame.pack(pady=(5, 3))

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(tab2, font=("Arial", 14), justify='center', width=35, relief='flat', bd=3)
        self.qr_entry.pack(pady=(10, 5))
        self.qr_entry.focus_set()

        # Label to display the contents corresponding to qrcode
        self.result_label = tk.Label(tab2, text="", font=("Arial", 15), fg='green', pady=2, height=5)
        self.result_label.pack()

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self._process_qrcode)

        # Bind the tab change event
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)



    #Function that validates user login credentials manually
    def _validate_credentials(self):
        from datetime import datetime
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
            )
        cursor = conn.cursor()

        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == self.user_Username and password == self.user_Password:

            search_query = "SELECT username, accountType, position FROM users WHERE username = %s AND password = %s"
            cursor.execute(search_query, (username, password))
            result = cursor.fetchone()
            userName, accountType, position = result

            insert_query = """
                INSERT INTO door_logs (username, accountType, position, date, time, action_taken)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            if self.action == 'successful_close' or self.action == 'automatic_logout':
                cursor.execute(insert_query, (userName, accountType, position, datetime.now().date(), datetime.now().time(), 'Lock'))
            else: 
                cursor.execute(insert_query, (userName, accountType, position, datetime.now().date(), datetime.now().time(), self.action))
            conn.commit()
            self._exit_action()
            if self.action == "unlock" and self.type == "deposit":
                self.window.destroy()
                self._unlock_door()
                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Success",
                    message="Door is now unlocked.\nPlease insert your medicine inside the Cabinet.\nPress ok if your finished inserting medicine to proceed on\nlocking the door.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                    ok_callback=lambda: (message_box.destroy(), self._lock_door())
                )
                message_box.window.bind("<KeyPress>", reset_timer)
                message_box.window.bind("<Motion>", reset_timer)
                message_box.window.bind("<ButtonPress>", reset_timer)
            elif self.type== "withdraw" and self.action == "unlock":
                self._unlock_door()
                self.window.destroy()
                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Success",
                    message="Door is now unlocked\nYou may now proceed to withdraw medicine.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                    ok_callback= lambda: (message_box.destroy(), QRCodeScanner(self.keyboardFrame, self.user_Username, self.user_Password, self.arduino, 'lock'), self.window.destroy())
                )
                message_box.window.bind("<KeyPress>", reset_timer)
                message_box.window.bind("<Motion>", reset_timer)
                message_box.window.bind("<ButtonPress>", reset_timer)
                

            elif self.action == "successful_close":
                self.arduino.write(b'lock\n')
                with open(file_path, "w") as file:
                    file.write("Locked")
                self.window.destroy()
                message_box = CustomMessageBox(
                    root=root,
                    title="Success",
                    message="Door is now locked.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'lock_icon.png'),
                    ok_callback=lambda: message_box.destroy()
                )
                message_box.window.bind("<KeyPress>", reset_timer)
                message_box.window.bind("<Motion>", reset_timer)
                message_box.window.bind("<ButtonPress>", reset_timer)
            elif self.action == "lock":
                self.window.destroy()
                self._lock_door()

            elif self.action == 'automatic_logout':
                with open(file_path, "w") as file:
                    file.write("Locked")
                self.window.destroy()
                self.arduino.write(b'lock\n')
                self.exit_callback()
                
            if self.action == "unlock" and self.type == "disable":
                self.window.destroy()
                self._unlock_door()
                message_box = CustomMessageBox(
                    root=self.keyboardFrame,
                    title="Disable Lock",
                    message="Lock functionality is now disabled temporarily",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                    ok_callback=lambda: (message_box.destroy(), self._exit_action()),
                )
                message_box.window.bind("<KeyPress>", reset_timer)
                message_box.window.bind("<Motion>", reset_timer)
                message_box.window.bind("<ButtonPress>", reset_timer)

        else:
            message_box = CustomMessageBox(
                root=self.keyboardFrame,
                title="Error",
                message="Invalid username or password.",
                color="red",  # Background color for warning
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),  # Path to your icon
                sound_file="sounds/invalidLogin.mp3"
            )
            message_box.window.bind("<KeyPress>", reset_timer)
            message_box.window.bind("<Motion>", reset_timer)
            message_box.window.bind("<ButtonPress>", reset_timer)


    def _on_tab_change(self, event):
        # Check if the selected tab is tab2 and hide the keyboard
        notebook = event.widget
        if notebook.index(notebook.select()) == 1:  # Index 1 for tab2
            self._hide_keyboard()


    def _show_keyboard(self):
        """Show the keyboard and move the window up."""
        self.keyboard.show_keyboard()

    def _hide_keyboard(self):
        """Hide the keyboard and restore the window position."""
        self.keyboard.hide_keyboard()

    #Function that validates user login credentials via QR code
    def _process_qrcode(self, event):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_medicine_cabinet"
            )
        cursor = conn.cursor()

        if self.qr_entry.winfo_exists():
            scanned_qr_code = self.qr_entry.get().strip()
            print(f"Final scanned QR code: {scanned_qr_code}")  # Debugging statement

            if scanned_qr_code:
                # Clear the Entry widget for the next scan
                self.qr_entry.delete(0, tk.END)

                # Connect to the MySQL database
                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",  # Adjust according to your MySQL setup
                        database="db_medicine_cabinet"
                    )
                    cursor = conn.cursor()

                    # Check if the scanned QR code matches any user in the database
                    query = "SELECT username, password FROM users WHERE username = %s AND password = %s"
                    cursor.execute(query, (self.user_Username, self.user_Password))
                    result = cursor.fetchone()

                    if result:
                        search_query = "SELECT username, accountType, position FROM users WHERE qrcode_data = %s"
                        cursor.execute(search_query, (scanned_qr_code,))
                        user_result = cursor.fetchone()
                        userName, accountType, position = user_result
                        self._exit_action()
                        insert_query = """
                            INSERT INTO door_logs (username, accountType, position, date, time, action_taken)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        if self.action == 'successful_close':
                            cursor.execute(insert_query, (userName, accountType, position, datetime.now().date(), datetime.now().time(), 'Lock'))
                        else: 
                            cursor.execute(insert_query, (userName, accountType, position, datetime.now().date(), datetime.now().time(), self.action))
                        conn.commit()
                        if self.action == "unlock" and self.type == "deposit":
                            self.window.destroy()
                            self._unlock_door()
                            message_box = CustomMessageBox(
                                root=self.keyboardFrame,
                                title="Success",
                                message="Door is now unlocked.\nPlease insert your medicine inside the Cabinet.\nPress ok if your finished inserting medicine to proceed on\nlocking the door.",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                                ok_callback=lambda: (message_box.destroy(), self._lock_door())
                            )
                            message_box.window.bind("<KeyPress>", reset_timer)
                            message_box.window.bind("<Motion>", reset_timer)
                            message_box.window.bind("<ButtonPress>", reset_timer)
                        elif self.type== "withdraw" and self.action == "unlock":
                            self._unlock_door()
                            self.window.destroy()
                            message_box = CustomMessageBox(
                                root=self.keyboardFrame,
                                title="Success",
                                message="Door is now unlocked\nYou may now proceed to withdraw medicine.",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                                ok_callback= lambda: (message_box.destroy(), QRCodeScanner(self.keyboardFrame, self.user_Username, self.user_Password, self.arduino, 'lock'), self.window.destroy())
                            )
                            message_box.window.bind("<KeyPress>", reset_timer)
                            message_box.window.bind("<Motion>", reset_timer)
                            message_box.window.bind("<ButtonPress>", reset_timer)
                        elif self.action == "successful_close":
                            self.arduino.write(b'lock\n')
                            with open(file_path, "w") as file:
                                file.write("Locked")
                            self.window.destroy()
                            message_box = CustomMessageBox(
                                root=root,
                                title="Success",
                                message="Door is now locked.",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'lock_icon.png'),
                                ok_callback=lambda: message_box.destroy()
                            )
                            message_box.window.bind("<KeyPress>", reset_timer)
                            message_box.window.bind("<Motion>", reset_timer)
                            message_box.window.bind("<ButtonPress>", reset_timer)
                        elif self.action == "lock":
                            self.window.destroy()
                            self._lock_door()

                        elif self.action == 'automatic_logout':
                            with open(file_path, "w") as file:
                                file.write("Locked")
                            self.window.destroy()
                            self.arduino.write(b'lock\n')
                            self.exit_callback()
                            
                        if self.action == "unlock" and self.type == "disable":
                            self.window.destroy()
                            self._unlock_door()
                            message_box = CustomMessageBox(
                                root=self.keyboardFrame,
                                title="Disable Lock",
                                message="Lock functionality is now disabled temporarily",
                                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'unlock_icon.png'),
                                ok_callback=lambda: (message_box.destroy(), self._exit_action()),
                            )
                            message_box.window.bind("<KeyPress>", reset_timer)
                            message_box.window.bind("<Motion>", reset_timer)
                            message_box.window.bind("<ButtonPress>", reset_timer)

                    else:
                        # If no match found, show an error
                        self.result_label.config(text="Invalid QR code or credentials.", fg="red")

                except mysql.connector.Error as err:
                    print(f"Error: {err}")
                    messagebox.showerror("Database Error", "Could not connect to the database.")

                finally:
                    # Close the cursor and connection
                    cursor.close()
                    conn.close()
            else:
                self.result_label.config(text="No QR code data scanned.", fg="red")

    # Function to send the lock command
    def _lock_door(self):
        # Step 1: Check the sensors before sending the lock command
        self.arduino.write(b'check_sensors\n')
        time.sleep(0.1)  # Brief delay to allow Arduino to process and respond

        # Step 2: Read Arduino's response
        if self.arduino.in_waiting > 0:
            response = self.arduino.readline().decode().strip()

            # Step 3: Proceed based on the sensor check response
            if response == "Object detected" and self.type == "deposit":
                self._show_success_message("Door is now properly closed and ready to lock.\nPlease click 'Ok' to process locking the door.")
                # Trigger further action for a successful close (for deposit type)
                LockUnlock(self.reference_window, self.user_Username, self.user_Password, self.arduino, 'successful_close', self.parentHeader)
            
            elif response == "Object detected" and self.type == "withdraw":
                # Send lock command and update lock status for withdraw type
                self.arduino.write(b'lock\n')
                self._update_lock_status()
                self._show_success_message("Door is now locked.")

            else:
                # If sensors indicate an issue, display warning and recheck sensors
                self._show_warning_and_recheck()

    def _show_success_message(self, message):
        """Display a success message and close relevant windows."""
        self._close_existing_windows()
        message_box = CustomMessageBox(
            root=root,
            title="Success", 
            message=message,
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'lock_icon.png'),
            ok_callback=lambda: message_box.destroy()
        )
        message_box.window.bind("<KeyPress>", reset_timer)
        message_box.window.bind("<Motion>", reset_timer)
        message_box.window.bind("<ButtonPress>", reset_timer)

    def _show_warning_and_recheck(self):
        """Display a warning message box if doors are not closed properly and recheck sensors."""
        # Destroy any existing warning box to avoid duplicates
        if hasattr(self, 'warning_box') and self.warning_box:
            self.warning_box.destroy()
            self.warning_box = None

        self.warning_box = CustomMessageBox(
            root=root,
            title="Warning",
            color='red',
            message="Doors are not properly closed\nPlease close both the doors properly before locking the door.",
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
            ok_callback=lambda: (self.warning_box.destroy(), self._recheck_sensors())
        )
        self.warning_box.window.bind("<KeyPress>", reset_timer)
        self.warning_box.window.bind("<Motion>", reset_timer)
        self.warning_box.window.bind("<ButtonPress>", reset_timer)

    def _recheck_sensors(self):
        """Rechecks sensors by sending the 'check_sensors' command to Arduino and responds accordingly."""
        self.arduino.write(b'check_sensors\n')
        time.sleep(0.1)
        if self.arduino.in_waiting > 0:
            response = self.arduino.readline().decode().strip()

            if response == "Object detected" and self.type == "deposit":
                self._close_existing_windows()
                message_box = CustomMessageBox(
                    root=root,
                    title="Success", 
                    message="Door is now properly closed and ready to lock.\nPlease click 'Ok' to process locking the door.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'lock_icon.png'),
                    ok_callback=lambda: (message_box.destroy(), LockUnlock(root, self.user_Username, self.user_Password, self.arduino, 'successful_close', self.parentHeader))
                )
                message_box.window.bind("<KeyPress>", reset_timer)
                message_box.window.bind("<Motion>", reset_timer)
                message_box.window.bind("<ButtonPress>", reset_timer)

            elif response == "Object detected" and self.type == "withdraw":
                self.arduino.write(b'lock\n')
                self._update_lock_status()
                self._show_success_message("Door is now locked.")
            
            else:
                # Show warning if sensors still indicate an issue
                self._show_warning_and_recheck()

    def _update_lock_status(self):
        """Update the lock status and perform cleanup."""
        with open(file_path, "w") as file:
            file.write("Locked")
        self._close_existing_windows()

    def _close_existing_windows(self):
        """Closes the main window and any top-level windows."""
        self.window.destroy()



    # Function to send the unlock command
    def _unlock_door(self):
        print("Unlock command sent")
        with open(file_path, "w") as file:
            file.write("Unlocked")
        self.arduino.write(b'unlock\n')  # Send the "unlock" command to the Arduino

    def _exit_action(self):
        """Trigger the no callback and close the window."""
        if self.exit_callback:
            self.exit_callback()

class QRCodeScanner:
    def __init__(self, parent, username, password, arduino, lock):
        from System import reset_timer
        print("QRCodeScanner initialized")  # Debugging statement
        # Create a new Toplevel window
        self.top = tk.Toplevel(parent, relief='raised', bd=5)

        self.top.overrideredirect(True)  # Remove the title bar
        self.top.resizable(width=False, height=False)
        self.top.attributes('-topmost', True)

        self.top.bind("<ButtonPress>", reset_timer)
        self.top.bind("<KeyPress>", reset_timer)
        self.top.bind("<Motion>", reset_timer)

        self.parent = parent

        self.username = username
        self.password = password
        self.arduino = arduino
        self.lock = lock

        self.top.focus_set()
        self.top.grab_set()

        # Title Frame
        self.title_frame = tk.Frame(self.top, bg=motif_color)
        self.title_frame.pack(fill=tk.X, expand=True, pady=(0, 10))

        # Title Label
        title_label = tk.Label(self.title_frame, text="  Withdraw Medicine", font=('Arial', 15, 'bold'), fg='white', bg=motif_color, pady=12)
        title_label.pack(side=tk.LEFT)

        # Add the close button icon at the top-right corner
        self.close_icon_path = os.path.join(os.path.dirname(__file__), 'images', 'cancel_icon.png')
        if os.path.exists(self.close_icon_path):
            self.close_img = ImageTk.PhotoImage(Image.open(self.close_icon_path).resize((18, 18), Image.LANCZOS))
        else:
            self.close_img = None

        close_button = tk.Button(self.title_frame, image=self.close_img, command=self.ask_lock, relief=tk.FLAT, bd=0, bg=motif_color, activebackground=motif_color)
        close_button.image = self.close_img  # Keep a reference to avoid garbage collection
        close_button.pack(side=tk.RIGHT, padx=(0, 5))

        # Content Frame
        content_frame = tk.Frame(self.top)
        content_frame.pack(pady=(10, 2))

        # QR Code Scanner Icon
        original_logo_img = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'scanning_icon.png')).resize((170, 170), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(original_logo_img)
        logo_label = tk.Label(content_frame, image=logo_img)
        logo_label.image = logo_img  # Keep reference to avoid garbage collection
        logo_label.pack(side=tk.TOP, pady=(10, 10))

        # Instruction Message
        instruction_label = tk.Label(content_frame, text="Please scan the medicine QR code to withdraw", font=("Arial", 14), fg='black')
        instruction_label.pack(pady=10)

        # QR Code Entry Frame
        entry_frame = tk.Frame(self.top)
        entry_frame.pack(pady=(5, 3))

        # Entry widget to capture QR code input
        self.qr_entry = tk.Entry(content_frame, font=("Arial", 14), justify='center', width=35, relief='sunken', bd=3)
        self.qr_entry.pack(pady=(10, 5))
        self.qr_entry.focus_set()

        # Label to display the medicine withdrawn
        self.result_label = tk.Label(self.top, text="", font=("Arial", 15), fg='green', pady=2, height=5)
        self.result_label.pack()

        # Bind the Enter key to process the QR code when scanned
        self.qr_entry.bind("<Return>", self.process_qrcode)

        self._adjust_window_height()

    def _adjust_window_height(self):
        """Adjust window height based on the message length while keeping the width fixed."""
        # Fixed width, dynamic height
        window_width = 450  # Adjusted width to fit better
        self.top.update_idletasks()

        required_height = self.top.winfo_reqheight()

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()

        # Calculate the position to center the window
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (required_height / 2))

        # Set the new geometry with fixed width and dynamic height
        self.top.geometry(f"{window_width}x{required_height}+{position_x}+{position_y}")

    def process_qrcode(self, event):
        if self.qr_entry.winfo_exists():
            scanned_qr_code = self.qr_entry.get().strip()
            print(f"Final scanned QR code: {scanned_qr_code}")  # Debugging statement

            if scanned_qr_code:
                # Clear the Entry widget for the next scan
                self.qr_entry.delete(0, tk.END)
                # Proceed with withdrawal process if the QR code is scanned
                self.withdraw_medicine(scanned_qr_code)
            else:
                self.result_label.config(text="No QR code data scanned.", fg="red")

    def withdraw_medicine(self, qr_code):
        print(f"Withdrawing medicine with QR code: {qr_code}")

        try:
            # Connect to the MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Your MySQL password
                database="db_medicine_cabinet"
            )
            cursor = conn.cursor()

            # Query to check if the medicine exists and retrieve name, quantity, type, and unit
            cursor.execute("SELECT name, quantity, type, unit FROM medicine_inventory WHERE qr_code = %s", (qr_code,))
            result = cursor.fetchone()

            if result:
                medicine_name, current_quantity, medicine_type, medicine_unit = result
                if current_quantity > 0:
                    # Deduct 1 from quantity
                    new_quantity = current_quantity - 1
                    cursor.execute("UPDATE medicine_inventory SET quantity = %s WHERE qr_code = %s", (new_quantity, qr_code))
                    conn.commit()

                    # Update the result label with the new multi-line format
                    self.result_label.config(text=f"You Withdrawn:\nMedicine: {medicine_name}\nType: {medicine_type}\nNew Quantity: {new_quantity}\nUnit: {medicine_unit}", fg="green", height=20, pady=2)
                else:
                    self.result_label.config(text=f"No more {medicine_name} ({medicine_type})\navailable to withdraw.", fg="red", height=5)
                    cursor.execute("DELETE FROM medicine_inventory WHERE qr_code = %s", (qr_code,))
                    conn.commit()
            else:
                self.result_label.config(text="QR code not found in the database.", fg="red")

        except mysql.connector.Error as err:
            self.result_label.config(text=f"Database Error: {err}", fg="red")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
    def ask_lock(self):
        from custom_messagebox import CustomMessageBox
        self.top.destroy()
        message_box = CustomMessageBox(
            root=root,
            title="Proceed Lock",
            message="Are you finished withdrawing and wants\nto proceed on locking the door?.",
            color="red",  # Background color for warning
            icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png'),
            yes_callback=lambda: (LockUnlock(root, self.username, self.password, self.arduino, 'lock', 'lock', type="withdraw"), message_box.destroy()),
            no_callback=lambda: (message_box.destroy(), QRCodeScanner(self.parent, self.username, self.password, self.arduino, 'lock'))
        )

SERIAL_PORT = 'COM4'  # Update to your printer's COM port if different
BAUD_RATE = 9600
TIMEOUT = 1

motif_color = '#42a7f5'


class MedicineDeposit:
    def __init__(self, name, generic_name, quantity, unit, expiration_date, dosage, db_connection, root, content_frame, keyboardFrame, Username, Password, arduino, action="unlock", yes_callback=None):
        self.root = root
        self.name = name.lower()
        self.generic_name = generic_name.lower()
        self.quantity = int(quantity)
        self.unit = unit.lower()
        self.expiration_date = expiration_date
        self.dosage = int(dosage)
        self.db_connection = db_connection
        self.content_frame = content_frame
        self.keyboardFrame = keyboardFrame
        self.Username = Username
        self.Password = Password
        self.arduino = arduino
        self.action = action
        self.yes_callback = yes_callback

        self.reference_window = root 
        if self.unit == 'capsule' or self.unit == 'tablet':
            self.dosage_for_db = f"{self.dosage} mg"
        elif self.unit == 'syrup':
            self.dosage_for_db = f"{self.dosage} ml"
        
        


    def validate_inputs(self):
        # Check if all fields are filled
        if not all([self.name, self.generic_name, self.quantity, self.unit, self.expiration_date, self.dosage]):
            global message_box
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message='Please fill-out all the fields',
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False
        
        # Check length of name and generic_name
        if len(self.name) > 20:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message="Brand name cannot exceed 20 characters.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        if len(self.generic_name) > 20:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message="Generic name cannot exceed 20 characters.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        # Check if quantity and dosage are numeric and greater than 0
        try:
            self.quantity = int(self.quantity)
            self.dosage = int(self.dosage)
            if self.quantity <= 0:
                message_box = CustomMessageBox(
                    root=self.root,
                    title='Error',
                    color='red',
                    message="Quantity must be greater than 0.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
                )
                return False
            if self.dosage <= 0:
                message_box = CustomMessageBox(
                    root=self.root,
                    title='Error',
                    color='red',
                    message="Dosage must be greater than 0.",
                    icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
                )
                return False
        except ValueError:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message="Quantity and Dosage must be numeric values greater than 0.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        # Check if expiration date is in the future
        today = datetime.datetime.now().date()
        if self.expiration_date <= today:
            message_box = CustomMessageBox(
                root=self.root,
                title='Error',
                color='red',
                message="Expiration date must be later than today.",
                icon_path=os.path.join(os.path.dirname(__file__), 'images', 'warningGrey_icon.png')
            )
            return False

        return True

    def generate_qr_code(self):
        # Combine name and expiration date to create a unique identifier for the QR code
        qr_code_data = f"{self.name}_{self.dosage_for_db}_{self.expiration_date}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill='black', back_color='white')

        # Save the generated QR code image
        qr_code_filename = f"qr_{self.name}_{self.expiration_date}.png"
        qr_code_filepath = os.path.join(os.path.dirname(__file__), 'qr_codes', qr_code_filename)
        qr_image.save(qr_code_filepath)

        # Update the QR code label in the UI
        self.update_qr_code_image(qr_code_filepath)

        return qr_code_filepath

    def update_qr_code_image(self, qr_code_filepath):
        # Load the new QR code image
        qr_image = Image.open(qr_code_filepath)
        qr_image_resized = qr_image.resize((450, 450), Image.LANCZOS)
        qr_image_tk = ImageTk.PhotoImage(qr_image_resized)
        # Add code here to update the label widget if necessary

    def show_loading_window(self):
        """Display a Toplevel window with a 'Loading...' message."""
        self.loading_window = tk.Toplevel(self.root, relief='raised', bd=5)
        self.loading_window.title("Printing")
        self.loading_window.geometry("500x300")
        self.loading_window.resizable(False, False)
        self.loading_window.attributes('-topmost', True)
        self.loading_window.focus_set()
        self.loading_window.grab_set()  # Make it modal (disable interaction with main window)
        self.loading_window.overrideredirect(True)  # Remove the title bar
        
        # Center the loading window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 100
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 50
        self.loading_window.geometry(f"+{x}+{y}")

        loading_label = tk.Label(self.loading_window, text="Loading...", font=("Arial", 18, 'bold'), bg=motif_color, fg='white')
        loading_label.pack(expand=True, fill='both')

    def close_loading_window(self):
        """Close the loading window."""
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

    def print_qr_code(self, expiration_date):
        """Prints the QR code and expiration date on the thermal printer,
        repeating the print if the unit is 'syrup' based on quantity,
        and showing a loading window during the process."""
        try:
            # Show the loading window before starting the print task
            self.show_loading_window()

            # Generate QR code image
            qr_code_filepath = self.generate_qr_code()
            qr_image = Image.open(qr_code_filepath)

            # Resize QR code to fit with text beside it (adjust as needed)
            qr_image = qr_image.resize((170, 170), Image.LANCZOS)

            # Prepare expiration date text as an image with a larger, bold font
            expiration_text = f"{expiration_date.strftime('%Y-%m-%d')}"

            # Load a bold TrueType font (adjust the path as needed for your system)
            font_path = "C:/Windows/Fonts/arialbd.ttf"  # Arial Bold on Windows
            font = ImageFont.truetype(font_path, 33)  # 33px for larger text
            text_width, text_height = font.getbbox(expiration_text)[2:]

            # Create a new blank image with space for both the QR and expiration text
            combined_width = qr_image.width + text_width + 20  # 20px padding between QR and text
            combined_height = max(qr_image.height, text_height)
            combined_image = Image.new('1', (combined_width, combined_height + 60), 255)  # Add 30px padding below

            # Place the QR code on the left
            combined_image.paste(qr_image, (0, 0))

            # Add the expiration date text to the right of the QR code
            draw = ImageDraw.Draw(combined_image)
            text_x_position = qr_image.width + 18  # Adjust padding here if needed
            draw.text((text_x_position, (combined_height - text_height) // 2), expiration_text, font=font, fill=0)

            # Convert the combined image to ESC/POS format for printing
            img_data = self.image_to_escpos_data(combined_image)

            # Define the print task in a separate thread to prevent UI freezing
            def print_task():
                try:
                    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as printer:
                        # If the unit is 'syrup', repeat printing based on quantity
                        if self.unit == 'syrup':
                            for _ in range(self.quantity):
                                printer.write(img_data)
                                printer.flush()
                                # Optional cut command if printer supports it
                                printer.write(b'\x1d\x56\x42\x00')  # ESC i - Cut paper
                                printer.flush()
                                time.sleep(1)  # Slight delay if needed between prints
                        else:
                            # Print only once for 'capsule' or 'tablet'
                            printer.write(img_data)
                            printer.flush()
                            # Optional cut command if printer supports it
                            printer.write(b'\x1d\x56\x42\x00')  # ESC i - Cut paper
                            printer.flush()

                        print("QR code and expiration date printed with spacing successfully.")
                except serial.SerialException as e:
                    print(f"Printer communication error: {e}")
                finally:
                    # Ensure both the loading window is closed and success message is shown after printing
                    self.close_loading_window()
                    self.show_success_message(qr_code_filepath)

            # Start the print task in a new thread
            threading.Thread(target=print_task).start()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.close_loading_window()  # Ensure loading window is closed in case of error



    def save_to_database(self):
        # Generate QR code and get the image file path
        qr_code_filepath = self.generate_qr_code()
        qr_code_data = f"{self.name}_{self.dosage_for_db}_{self.expiration_date}"

        # Convert name and type to Title Case for database insertion
        name_for_db = self.name.capitalize()
        type_for_db = self.generic_name.capitalize()
        
        # Save the medicine data to the database
        try:
            cursor = self.db_connection.cursor()
            insert_query = """
                INSERT INTO medicine_inventory (name, type, quantity, unit, dosage, expiration_date, date_stored, qr_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name_for_db, type_for_db, self.quantity, self.unit.capitalize(), self.dosage_for_db,
                                        self.expiration_date, datetime.datetime.now().date(), qr_code_data))
            self.db_connection.commit()

            # Start printing process after database save
            print("Attempting to print expiration date on thermal printer...")
            self.print_qr_code(self.expiration_date)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            cursor.close()

    def image_to_escpos_data(self, img):
        """Converts a monochrome image to ESC/POS format."""
        width, height = img.size
        bytes_per_row = (width + 7) // 8  # 1 bit per pixel, so 8 pixels per byte
        img_data = b''

        # ESC/POS command for image printing
        img_data += b'\x1d\x76\x30\x00' + bytes([bytes_per_row % 256, bytes_per_row // 256, height % 256, height // 256])

        # Loop through pixels and convert to ESC/POS data
        for y in range(height):
            row_data = 0
            byte = 0
            for x in range(width):
                if img.getpixel((x, y)) == 0:  # Pixel is black
                    byte |= (1 << (7 - row_data))
                row_data += 1
                if row_data == 8:
                    img_data += bytes([byte])
                    row_data = 0
                    byte = 0
            if row_data > 0:  # Remaining bits in the row
                img_data += bytes([byte])

        return img_data


    def show_success_message(self, qr_code_filepath):
        """Display the custom messagebox after successfully adding the medicine."""
        self.close_loading_window()
        self.message_box = CustomMessageBox(
            root=root,
            title="Medicine Deposited",
            message=f"Adding medicine: '{self.name.capitalize()}'\nPlease attach the printed QR Code with Exp. Date to the medicine.\n\nDo you want to add more medicine?",
            icon_path=qr_code_filepath,
            no_callback=lambda: (LockUnlock(root, self.Username, self.Password, self.arduino,"unlock", "medicine inventory", type="deposit"), self.message_box.destroy()),
            yes_callback=lambda: (self._yes_action(), self.message_box.destroy(), deposit_window(permission='deposit_again'))
        )

    def _yes_action(self):
        """Trigger the yes callback and close the window."""
        print("yes Callback called")
        if self.yes_callback:
            self.yes_callback()



class CustomMessageBox:
    def __init__(self, root, title, message, color=motif_color, icon_path=None, sound_file=None, ok_callback=None, yes_callback=None, no_callback=None, close_icon_path=None, page='Home', close_state=None):
        self.window = tk.Toplevel(root, relief='raised', bd=5)
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.resizable(width=False, height=False)

        # self.window.bind("<ButtonPress>", reset_timer)
        # self.window.bind("<Motion>", reset_timer)
        # self.window.bind("<KeyPress>", reset_timer)

        self.window.attributes('-topmost', True)
        self.window.focus_set()

        # Make the window modal (prevents interaction with other windows)
        self.window.grab_set()

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
        self.close_state = close_state

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

        if self.close_state:
            close_button.config(state='disabled')

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


#-----------------------------------------------MAIN------------------------------------------------------
def main():
    global root, arduino, container
    root = tk.Tk()
    root.resizable(width=False, height=False)
    # root.overrideredirect(True)
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
        global arduino
        try:
            arduino = serial.Serial('COM5', 9600)  # Port of the Arduino
            time.sleep(2)  # Wait for the connection to establish
            print("\nSerial connection established")
            # Once connected, proceed to show login_frame
            login_frame = create_login_frame(container)
        
            login_frame.tkraise()
        except serial.SerialException as e:
            print(f"\nError opening serial port: {e}")
            arduino = None  # Set to None if the connection fails
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
    if arduino is not None:
        arduino.close()
        print("\nSerial connection closed")

if __name__ == "__main__":
    main()

