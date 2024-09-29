import serial
import mysql.connector

# Setup the serial connection to the QR scanner
ser = serial.Serial('COM4', 9600, timeout=1)  # Adjust 'COM3' to your scanner's port

# Setup MySQL connection

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_medicine_cabinet"
)

def check_qr_code_in_database(scanned_qr):
    try:
        cursor = conn.cursor()
        # Query the database to find if the scanned QR code exists
        query = "SELECT username, position, accountType FROM users WHERE username = %s"
        cursor.execute(query, (scanned_qr,))
        result = cursor.fetchone()

        if result:
            username, position, account_type = result
            print(f"QR Code matched!\nUsername: {username}, Position: {position}, Account Type: {account_type}")
        else:
            print("No match found in the database for the scanned QR code.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()

def scan_qr_code():
    while True:
        qr_data = ser.readline().decode('utf-8').strip()  # Read from scanner
        if qr_data:
            print(f"Scanned QR Code: {qr_data}")
            check_qr_code_in_database(qr_data)

if __name__ == "__main__":
    print("Starting QR code scanning...")
    scan_qr_code()
