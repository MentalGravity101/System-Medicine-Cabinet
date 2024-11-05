import serial
import time

# Set the correct COM port for your printer
SERIAL_PORT = 'COM4'  # Replace 'COM3' with your actual COM port
BAUD_RATE = 9600      # Check and update as needed
TIMEOUT = 1           # 1 second timeout

# ESC/POS Commands
ESC = b'\x1b'
INITIALIZE_PRINTER = ESC + b'@'  # Resets the printer
NEWLINE = b'\n'
CUT_PAPER = ESC + b'd\x04'  # Feeds paper before cutting (may vary by model)

# Define a function to send each character with a delay
def send_with_delay(printer, message, delay=0.1):
    for char in message:
        printer.write(char.encode())  # Encode each character
        time.sleep(delay)  # Delay between characters

try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as printer:
        # Allow some time for the printer to initialize
        time.sleep(2)
        
        # Send initialization command
        printer.write(INITIALIZE_PRINTER)
        time.sleep(0.1)  # Small delay for command processing

        # Send "Hello World" with delay between characters
        send_with_delay(printer, "Hello World!", delay=0.05)
        
        # Send newline and cut command (optional)
        printer.write(NEWLINE)
        printer.write(CUT_PAPER)

        # Flush to ensure all data is sent
        printer.flush()
        
    print("Print job sent successfully.")
except serial.SerialException as e:
    print(f"Error communicating with printer: {e}")
