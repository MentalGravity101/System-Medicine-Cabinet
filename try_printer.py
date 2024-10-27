import win32print
import win32ui
from PIL import Image, ImageWin

printer_name = win32print.GetDefaultPrinter()
hprinter = win32print.OpenPrinter(printer_name)

# Load image or text to print
hdc = win32ui.CreateDC()
hdc.CreatePrinterDC(printer_name)

hdc.StartDoc("Test print job")
hdc.StartPage()

# Example: Sending text to the printer
hdc.TextOut(100, 100, "Hello, world!")

hdc.EndPage()
hdc.EndDoc()
hdc.DeleteDC()
