import tkinter as tk
from tkinter import messagebox, filedialog
from alchemy import Alchemy
from alchemy.types import AssetTransfersCategory

#from alchemy_sdk import Alchemy, Network, AssetTransfersCategory
import pandas as pd

# Alchemy configuration
api_key = "vhfS63Mbxdv6zgIHcrjl5zwvLyAD34B-"  # Replace with your actual Alchemy API key
alchemy = Alchemy(api_key=api_key, network="eth-mainnet")  # Connect to Ethereum mainnet

# Fetch transactions to analyze
def fetch_transactions(to_address):
    try:
        transactions = alchemy.core.get_asset_transfers(
            from_block="0x0",
            from_address="0x0000000000000000000000000000000000000000",  # Mint transactions
            to_address=to_address,
            exclude_zero_value=True,
            category=[AssetTransfersCategory.ERC721, AssetTransfersCategory.ERC1155]
        )
        return transactions['transfers']
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching transactions: {e}")
        return []

# Store data in Excel file
def save_to_excel(transactions):
    if transactions:
        df = pd.DataFrame(transactions)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Transactions saved to {file_path}.")
    else:
        messagebox.showwarning("Warning", "No transactions to save.")

# Fetch and display transactions in the GUI
def display_transactions():
    to_address = address_entry.get().strip()
    if not to_address:
        messagebox.showwarning("Warning", "Please enter a valid Ethereum address.")
        return

    transactions = fetch_transactions(to_address)
    if transactions:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Transactions for {to_address}:\n\n")
        for tx in transactions:
            result_text.insert(tk.END, f"{tx}\n\n")
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No transactions found.")

# GUI Setup
root = tk.Tk()
root.title("Cryptocurrency Transaction Fetcher")
root.geometry("600x500")
root.configure(bg="#2b2b2b")

# Title Label
title_label = tk.Label(root, text="Cryptocurrency Transaction Fetcher", font=("Arial", 18, "bold"), bg="#2b2b2b", fg="white")
title_label.pack(pady=10)

# Ethereum Address Entry
address_frame = tk.Frame(root, bg="#2b2b2b")
address_frame.pack(pady=10)
address_label = tk.Label(address_frame, text="Ethereum Address:", font=("Arial", 12), bg="#2b2b2b", fg="white")
address_label.pack(side=tk.LEFT, padx=5)
address_entry = tk.Entry(address_frame, font=("Arial", 12), width=40)
address_entry.pack(side=tk.LEFT, padx=5)

# Buttons Frame
buttons_frame = tk.Frame(root, bg="#2b2b2b")
buttons_frame.pack(pady=10)
fetch_button = tk.Button(buttons_frame, text="Fetch Transactions", command=display_transactions, bg="#4CAF50", fg="white", font=("Arial", 12), width=18)
fetch_button.grid(row=0, column=0, padx=10)
save_button = tk.Button(buttons_frame, text="Save to Excel", command=lambda: save_to_excel(fetch_transactions(address_entry.get())), bg="#2196F3", fg="white", font=("Arial", 12), width=18)
save_button.grid(row=0, column=1, padx=10)

# Result Text Box
result_text = tk.Text(root, wrap="word", font=("Arial", 10), bg="#1e1e1e", fg="white", height=15, width=70)
result_text.pack(pady=10)

# Start the GUI loop
root.mainloop()
