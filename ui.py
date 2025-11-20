import tkinter as tk
from ttkbootstrap import Style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import random
import uuid
from tkinter import ttk, messagebox, filedialog
from alchemy import Alchemy
from alchemy.types import AssetTransfersCategory

from loggger import logger 

# Alchemy configuration
api_key = "vhfS63Mbxdv6zgIHcrjl5zwvLyAD34B-"  # Replace with your actual Alchemy API key
alchemy = Alchemy(api_key=api_key, network="eth-mainnet")  # Connect to Ethereum mainnet

# Global variable to store enriched transaction data
fetched_transaction_data = []

import socket

def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        logger.error("Error fetching IP address", extra={"Error": str(e)})
        return "Unknown"

import platform

def get_device_info():
    try:
        system = platform.system()  # E.g., Windows, Linux, macOS
        release = platform.release()  # OS version
        machine = platform.machine()  # Architecture (e.g., x86_64)
        return f"{system} {release} ({machine})"
    except Exception as e:
        logger.error("Error fetching device information", extra={"Error": str(e)})
        return "Unknown Device"

# Function to fetch transactions
def fetch_transactions(to_address):
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info()  # Fetch device information dynamically
    try:
        transactions = alchemy.core.get_asset_transfers(
            from_block="0x0",
            from_address="0x0000000000000000000000000000000000000000",  # Mint transactions
            to_address=to_address,
            exclude_zero_value=True,
            category=[AssetTransfersCategory.ERC721, AssetTransfersCategory.ERC1155]
        )
        logger.info(
            "Transaction Successfully",
            extra={"IP": user_ip, "Device": device_info}
        )
        return transactions['transfers']
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching transactions: {e}")
        logger.info(
            "Transaction Failed",
            extra={"IP": user_ip, "Device": device_info}
        )
        return []
    
def display_transactions():
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info() 
    """
    Fetch and display Ethereum transactions along with unique IP and geolocation data.
    """
    global fetched_transaction_data
    fetched_transaction_data = []  # Clear previous data

    to_address = address_entry.get().strip()
    if not to_address:
        messagebox.showwarning("Warning", "Please enter a valid Ethereum address.")
        return

    transactions = fetch_transactions(to_address)
    if transactions:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Transactions for {to_address}:\n\n")

        for tx in transactions:
            # Access transaction details using attributes
            try:
                from_address = getattr(tx, 'from_', 'Unknown')
                to_address = getattr(tx, 'to', 'Unknown')
                tx_hash = getattr(tx, 'transaction_hash', 'N/A')
            except AttributeError:
                result_text.insert(tk.END, "Error: Invalid transaction format.\n")
                continue

            # Generate new dummy IPs and geolocations for each transaction
            from_ip, from_location = get_realistic_ip_and_location()
            to_ip, to_location = get_realistic_ip_and_location()

            # If any field is "Unknown", replace with dummy data
            if from_address.upper() == "UNKNOWN":
                from_address = generate_dummy_ethereum_address()
            if to_address.upper() == "UNKNOWN":
                to_address = generate_dummy_ethereum_address()
            if tx_hash.upper() in ["UNKNOWN", "N/A"]:
                tx_hash = generate_random_tx_hash()

            # Add enriched data to the global list
            fetched_transaction_data.append({
                "Transaction Hash": tx_hash,
                "From Address": from_address,
                "From IP": from_ip,
                "From Location": from_location,
                "To Address": to_address,
                "To IP": to_ip,
                "To Location": to_location,
            })

            # Display transaction details in the GUI
            result_text.insert(tk.END, f"Transaction Hash: {tx_hash}\n")
            result_text.insert(tk.END, f"From: {from_address} (IP: {from_ip}, Location: {from_location})\n")
            result_text.insert(tk.END, f"To: {to_address} (IP: {to_ip}, Location: {to_location})\n")
            result_text.insert(tk.END, "-" * 50 + "\n")

            logger.info(
                "Displayed Transaction",
                extra={"IP": user_ip, "Device": device_info}
            )

        root.update()
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No transactions found.")

used_ips = set()  # To track used IPs

def get_realistic_ip_and_location():
    def ip_to_int(ip):
        parts = map(int, ip.split('.'))
        return sum(part << (8 * (3 - i)) for i, part in enumerate(parts))

    def int_to_ip(value):
        return '.'.join(str((value >> (8 * (3 - i))) & 0xFF) for i in range(4))

    REAL_IP_LOCATION_MAPPING = [
        {"ip_range_start": "8.8.8.0", "ip_range_end": "8.8.8.255", "location": "Mountain View, California, USA"},
        {"ip_range_start": "13.229.0.0", "ip_range_end": "13.229.255.255", "location": "Singapore, Singapore"},
        {"ip_range_start": "52.95.0.0", "ip_range_end": "52.95.255.255", "location": "Sydney, New South Wales, Australia"},
        {"ip_range_start": "31.13.0.0", "ip_range_end": "31.13.255.255", "location": "Dublin, Leinster, Ireland"},
        {"ip_range_start": "91.198.174.0", "ip_range_end": "91.198.174.255", "location": "Amsterdam, North Holland, Netherlands"},
        {"ip_range_start": "123.176.0.0", "ip_range_end": "123.176.255.255", "location": "Mumbai, Maharashtra, India"},
        {"ip_range_start": "172.217.0.0", "ip_range_end": "172.217.255.255", "location": "Los Angeles, California, USA"},
        {"ip_range_start": "202.56.0.0", "ip_range_end": "202.56.255.255", "location": "Tokyo, Tokyo Prefecture, Japan"},
        {"ip_range_start": "186.233.0.0", "ip_range_end": "186.233.255.255", "location": "São Paulo, São Paulo, Brazil"},
        {"ip_range_start": "41.191.0.0", "ip_range_end": "41.191.255.255", "location": "Cape Town, Western Cape, South Africa"},
    ]

    while True:
        entry = random.choice(REAL_IP_LOCATION_MAPPING)
        start = ip_to_int(entry["ip_range_start"])
        end = ip_to_int(entry["ip_range_end"])
        random_ip_int = random.randint(start, end)
        random_ip = int_to_ip(random_ip_int)

        if random_ip not in used_ips:  # Ensure the IP is unique
            used_ips.add(random_ip)
            return random_ip, entry["location"]

# Generate from and to IPs, locations, and MAC addresses (used in some parts of the code)
from_ip, from_location = get_realistic_ip_and_location()
to_ip, to_location = get_realistic_ip_and_location()

# --- Modified Save to Excel Function with Metadata ---
def save_to_excel_with_dummy_data(transactions):
    """
    Save transactions to an Excel file with additional dummy IP, geolocation, and metadata.
    Also, replace any 'UNKNOWN' or missing values with randomized dummy data.
    """
    if transactions:
        enriched_data = []
        for tx in transactions:
            # Retrieve transaction details; if missing or 'UNKNOWN', generate dummy values
            try:
                from_address = getattr(tx, 'from_', None)
            except:
                from_address = None
            if not from_address or from_address.upper() == "UNKNOWN":
                from_address = generate_dummy_ethereum_address()

            try:
                to_address = getattr(tx, 'to', None)
            except:
                to_address = None
            if not to_address or to_address.upper() == "UNKNOWN":
                to_address = generate_dummy_ethereum_address()

            try:
                tx_hash = getattr(tx, 'transaction_hash', None)
            except:
                tx_hash = None
            if not tx_hash or tx_hash.upper() in ["UNKNOWN", "N/A"]:
                tx_hash = generate_random_tx_hash()
                
            # Generate dummy IP and geolocation values for both sender and receiver
            from_ip, from_geo = get_realistic_ip_and_location()
            to_ip, to_geo = get_realistic_ip_and_location()

            if from_geo.upper() == "UNKNOWN":
                from_geo = get_dummy_geolocation(from_ip)
            if to_geo.upper() == "UNKNOWN":
                to_geo = get_dummy_geolocation(to_ip)
            
            # --- New: Extract and enrich metadata ---
            block_number = getattr(tx, 'block_number', 'Unknown')
            if str(block_number).upper() == "UNKNOWN":
                block_number = random.randint(1000000, 9999999)  # Dummy block number
            category = getattr(tx, 'category', 'Unknown')
            if str(category).upper() == "UNKNOWN":
                category = random.choice(["ERC721", "ERC1155", "ERC20"])
            token_id = getattr(tx, 'token_id', 'Unknown')
            if str(token_id).upper() == "UNKNOWN":
                token_id = str(random.randint(1, 100000))
            
            enriched_data.append({
                "Transaction Hash": tx_hash,
                "From Address": from_address,
                "From IP": from_ip,
                "From Location": from_geo,
                "To Address": to_address,
                "To IP": to_ip,
                "To Location": to_geo,
                "Block Number": block_number,
                "Category": category,
                "Token ID": token_id
            })

        df = pd.DataFrame(enriched_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Transactions saved to {file_path}.")
    else:
        messagebox.showwarning("Warning", "No transactions to save.")

def generate_random_tx_hash():
    """
    Generate a random hexadecimal string to simulate a transaction hash.
    """
    return "0x" + uuid.uuid4().hex[:64]

def generate_dummy_ethereum_address():
    """
    Generate a dummy Ethereum address.
    """
    return "0x" + uuid.uuid4().hex[:40]

def get_dummy_ip_address():
    """
    Generate a random dummy IP address in the 192.168.0.0/16 range.
    """
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

def get_dummy_geolocation(ip_address):
    """
    Assign a random geolocation based on a predefined list of locations.
    """
    locations = ["New York, USA", "London, UK", "Tokyo, Japan", "Berlin, Germany",
                 "Paris, France", "Mumbai, India", "Sydney, Australia", "Cape Town, South Africa"]
    return random.choice(locations)

# Note: The display_transactions functions below are preserved as in your original code.
def display_transactions():
    """
    Fetch and display Ethereum transactions along with dummy IP and geolocation data.
    """
    to_address = address_entry.get().strip()
    if not to_address:
        messagebox.showwarning("Warning", "Please enter a valid Ethereum address.")
        return

    transactions = fetch_transactions(to_address)
    if transactions:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Transactions for {to_address}:\n\n")

        for tx in transactions:
            try:
                from_address = getattr(tx, 'from_', 'Unknown')
                to_address = getattr(tx, 'to', 'Unknown')
                tx_hash = getattr(tx, 'transaction_hash', 'N/A')
            except AttributeError:
                result_text.insert(tk.END, "Error: Invalid transaction format.\n")
                continue

            from_ip, _ = get_realistic_ip_and_location()
            to_ip, _ = get_realistic_ip_and_location()
            from_location = get_dummy_geolocation(from_ip)
            to_location = get_dummy_geolocation(to_ip)

            result_text.insert(tk.END, f"Transaction Hash: {tx_hash}\n")
            result_text.insert(tk.END, f"From: {from_address} (IP: {from_ip}, Location: {from_location})\n")
            result_text.insert(tk.END, f"To: {to_address} (IP: {to_ip}, Location: {to_location})\n")
            result_text.insert(tk.END, "-" * 50 + "\n")

        root.update()
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No transactions found.")


def TestingEthereum():
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info() 
    confirm = messagebox.askyesno("Testing", "Are you sure you want to Testing?")
    if confirm:
        logger.info(
            "Ethereum Testing",
            extra={"IP": user_ip, "Device": device_info}
        )
        from subprocess import call
        call(['python', 'test_file.py'])

def TestingBTC():
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info() 
    confirm = messagebox.askyesno("Testing", "Are you sure you want to Testing?")
    if confirm:
        logger.info(
            "TestingBTC",
            extra={"IP": user_ip, "Device": device_info}
        )
        from subprocess import call
        call(['python', 'BTC-testing.py'])

def traineth():
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info() 
    confirm = messagebox.askyesno("Training", "Are you sure you want to Train?")
    if confirm:
        logger.info(
            "Ethereum Training",
            extra={"IP": user_ip, "Device": device_info}
        )
        from subprocess import call
        call(['python', 'Eth_training.py'])
    
def trainBTC():
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info() 
    confirm = messagebox.askyesno("Training", "Are you sure you want to Train?")
    if confirm:
        logger.info(
            "Training BTC",
            extra={"IP": user_ip, "Device": device_info}
        )
        from subprocess import call
        call(['python', 'BTC_training.py'])
    
# Function to handle logout
def logout():
    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info() 
    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    logger.info(
        "Logout",
        extra={"IP": user_ip, "Device": device_info}
    )
    
    if confirm:
        root.destroy()

# Initialize main window with Ttkbootstrap style
style = Style(theme='cosmo')  # You can choose other themes like 'flatly', 'darkly', etc.
root = style.master
root.title("CryptoTrace - Transaction Tracker")
root.state('zoomed')  # Maximize window to full screen

# Create a PanedWindow to divide the sidebar and main content
paned_window = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# Sidebar Frame
sidebar = ttk.Frame(paned_window, width=200, relief='raised')
paned_window.add(sidebar, weight=1)

# Sidebar Buttons
def select_tab(tab_name):
    notebook.select(tab_name)

tabs = ['Home', 'Transactions', 'Training', 'Testing']
for tab in tabs:
    btn = ttk.Button(sidebar, text=tab, command=lambda t=tab: select_tab(t))
    btn.pack(fill='x', pady=5, padx=10)

# Main Content Frame
main_content = ttk.Frame(paned_window, relief='sunken')
paned_window.add(main_content, weight=4)

# Notebook for tabbed interface
notebook = ttk.Notebook(main_content)
notebook.pack(fill='both', expand=True)

# Home Tab
home_frame = ttk.Frame(notebook)
notebook.add(home_frame, text='Home')

# Add logo to the Home tab
try:
    logo_img = tk.PhotoImage(file=r"cryptotrace_logo.png")
    resized_logo = logo_img.subsample(3, 3)  # Adjust scaling factor as needed
    logo_label = tk.Label(home_frame, image=resized_logo)
    logo_label.pack(pady=20)
except Exception as e:
    print(f"Error loading logo: {e}")

home_label = ttk.Label(home_frame, text="Welcome to CryptoTrace", font=("Helvetica", 18, "bold"))
home_label.pack(pady=10)

home_description = ttk.Label(home_frame, text=(
    "CryptoTrace is a real-time cryptocurrency tracking solution designed to monitor, detect, "
    "and flag suspicious activities in blockchain transactions. Utilize the sidebar to navigate through different sections."
), wraplength=600, justify="center")
home_description.pack(pady=10)

# Transactions Tab
transactions_frame = ttk.Frame(notebook)
notebook.add(transactions_frame, text='Transactions')

# Transactions tab widgets
address_label = ttk.Label(transactions_frame, text="Enter Ethereum Address:", font=("Helvetica", 12))
address_label.pack(pady=10)
address_entry = ttk.Entry(transactions_frame, font=("Helvetica", 12), width=50)
address_entry.pack(pady=10)

fetch_button = ttk.Button(transactions_frame, text="Fetch Transactions", command=display_transactions)
fetch_button.pack(pady=5)
# --- Modified Save Button to use the enriched Excel saving function with metadata ---
save_button = ttk.Button(transactions_frame, text="Save to Excel", command=lambda: save_to_excel_with_dummy_data(fetch_transactions(address_entry.get())))
save_button.pack(pady=5)

result_text = tk.Text(transactions_frame, wrap="word", font=("Helvetica", 10), height=15, width=70)
result_text.pack(pady=10)

# Training Tab
training_frame = ttk.Frame(notebook)
notebook.add(training_frame, text='Training')

training_button = ttk.Button(training_frame, text="Load Training-Eth", command=traineth)
training_button.pack(pady=10)

training_button1 = ttk.Button(training_frame, text="Load Training-BTC", command=trainBTC)
training_button1.pack(pady=10)

# Testing Tab
testing_frame = ttk.Frame(notebook)
notebook.add(testing_frame, text='Testing')

testing_button = ttk.Button(testing_frame, text="Cryptocurrency Testing Ethereum Data", command=TestingEthereum)
testing_button.pack(pady=50)

testing_button = ttk.Button(testing_frame, text="Cryptocurrency Testing BTC Data", command=TestingBTC)
testing_button.pack(pady=5)

# Footer with Logout Button
footer = ttk.Frame(root)
footer.pack(side='bottom', fill='x')

footer_label = ttk.Label(footer, text="© 2025 CryptoTrace - All Rights Reserved", anchor='center')
footer_label.pack(side='left', pady=10, padx=20)

logout_button = ttk.Button(footer, text="Log Out", command=logout)
logout_button.pack(side='right', pady=10, padx=20)

# Run the application
root.mainloop()
