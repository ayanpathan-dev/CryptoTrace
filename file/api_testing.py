import tkinter as tk
from tkinter import messagebox, filedialog
from alchemy import Alchemy
from alchemy.types import AssetTransfersCategory
import pandas as pd
import joblib
from datetime import datetime

# Alchemy configuration
API_KEY = "vhfS63Mbxdv6zgIHcrjl5zwvLyAD34B-"  # Replace with your Alchemy API key
alchemy = Alchemy(api_key=API_KEY, network="eth-mainnet")  # Connect to Ethereum mainnet

# Load trained model and scaler
MODEL_PATH = "trained_model_old.pkl"  # Replace with your model file path
SCALER_PATH = "scaler_old.pkl"  # Replace with your scaler file path
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Fetch transactions for an Ethereum address
def fetch_transactions(to_address):
    try:
        transactions = alchemy.core.get_asset_transfers(
            from_block="0x0",
            to_address=to_address,
            exclude_zero_value=True,
            category=[AssetTransfersCategory.ERC20, AssetTransfersCategory.EXTERNAL]
        )
        return transactions['transfers']
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching transactions: {e}")
        return []

from datetime import datetime

def calculate_features(transactions):
    if not transactions:
        return {}

    sent_tx_times = []
    received_tx_times = []
    unique_sent_to = set()
    unique_received_from = set()
    total_erc20_tnxs = 0
    total_sent_value = 0
    total_received_value = 0

    for tx in transactions:
        try:
            # Accessing transaction attributes
            block_num = int(tx.blockNum, 16) if hasattr(tx, 'blockNum') else None
            timestamp = datetime.fromtimestamp(block_num) if block_num else None
            value = float(tx.value) if hasattr(tx, 'value') and tx.value else 0.0

            if hasattr(tx, 'fromAddress') and tx.fromAddress != '0x0000000000000000000000000000000000000000':
                # Sent transaction
                sent_tx_times.append(timestamp)
                unique_sent_to.add(tx.toAddress)
                total_sent_value += value

            if hasattr(tx, 'toAddress') and tx.toAddress != '0x0000000000000000000000000000000000000000':
                # Received transaction
                received_tx_times.append(timestamp)
                unique_received_from.add(tx.fromAddress)
                total_received_value += value

            if hasattr(tx, 'category') and tx.category == AssetTransfersCategory.ERC20:
                total_erc20_tnxs += 1
        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue

    # Feature calculations
    avg_min_between_sent = (
        (max(sent_tx_times) - min(sent_tx_times)).total_seconds() / 60 / len(sent_tx_times)
        if sent_tx_times else 0
    )
    avg_min_between_received = (
        (max(received_tx_times) - min(received_tx_times)).total_seconds() / 60 / len(received_tx_times)
        if received_tx_times else 0
    )
    time_diff_first_last = (
        (max(sent_tx_times + received_tx_times) - min(sent_tx_times + received_tx_times)).total_seconds() / 60
        if sent_tx_times or received_tx_times else 0
    )

    return {
        'Avg min between sent tnx': avg_min_between_sent,
        'Avg min between received tnx': avg_min_between_received,
        'Time Diff between first and last (Mins)': time_diff_first_last,
        'Sent tnx': len(sent_tx_times),
        'Received Tnx': len(received_tx_times),
        'Unique Sent To Addresses': len(unique_sent_to),
        'Unique Received From Addresses': len(unique_received_from),
        'Total ERC20 tnxs': total_erc20_tnxs,
        'Total Ether sent': total_sent_value,
        'Total Ether received': total_received_value
    }

# Predict fraud using the trained model
def predict_fraud(features):
    try:
        features_df = pd.DataFrame([features])
        scaled_features = scaler.transform(features_df)
        prediction = model.predict(scaled_features)
        return "Fraud" if prediction[0] == 1 else "Not Fraud"
    except Exception as e:
        return f"Error during prediction: {e}"

# GUI: Analyze transactions and predict fraud
def analyze_and_predict():
    to_address = address_entry.get().strip()
    if not to_address:
        messagebox.showwarning("Warning", "Please enter a valid Ethereum address.")
        return

    transactions = fetch_transactions(to_address)
    features = calculate_features(transactions)
    
    if features:
        result = predict_fraud(features)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Prediction for {to_address}: {result}\n\nFeatures:\n{features}")
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No transactions found or insufficient data for analysis.")

# Save transaction data to Excel
def save_to_excel(transactions):
    if transactions:
        df = pd.DataFrame(transactions)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Transactions saved to {file_path}.")
    else:
        messagebox.showwarning("Warning", "No transactions to save.")

# GUI Setup
root = tk.Tk()
root.title("Cryptocurrency Fraud Detection")
root.geometry("700x600")
root.configure(bg="#2b2b2b")

# Title Label
title_label = tk.Label(root, text="Cryptocurrency Fraud Detection", font=("Arial", 18, "bold"), bg="#2b2b2b", fg="white")
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
analyze_button = tk.Button(buttons_frame, text="Analyze Transactions", command=analyze_and_predict, bg="#4CAF50", fg="white", font=("Arial", 12), width=18)
analyze_button.grid(row=0, column=0, padx=10)
save_button = tk.Button(buttons_frame, text="Save to Excel", command=lambda: save_to_excel(fetch_transactions(address_entry.get())), bg="#2196F3", fg="white", font=("Arial", 12), width=18)
save_button.grid(row=0, column=1, padx=10)

# Result Text Box
result_text = tk.Text(root, wrap="word", font=("Arial", 10), bg="#1e1e1e", fg="white", height=20, width=80)
result_text.pack(pady=10)

# Start the GUI loop
root.mainloop()
