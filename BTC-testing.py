import tkinter as tk
from tkinter import messagebox, Text, filedialog, ttk
import pandas as pd
import numpy as np
import joblib
import hashlib
import pyperclip

# Function to hash BTC addresses
def hash_address(address):
    return int(hashlib.sha256(address.encode('utf-8')).hexdigest(), 16)

class FraudDetectionForm:
    def __init__(self, master):
        self.master = master
        self.master.title("Cryptocurrency Fraud Detection")
        self.master.geometry("1200x900")
        self.selected_features = [
            'Address', 'Time step', 'first_block_appeared_in', 'last_block_appeared_in', 'lifetime_in_blocks',
            'total_txs', 'first_sent_block', 'first_received_block', 'btc_transacted_total', 'btc_sent_total',
            'btc_received_total', 'fees_total', 'fees_as_share_total', 'blocks_btwn_txs_total',
            'blocks_btwn_input_txs_total', 'blocks_btwn_output_txs_total', 'num_addr_transacted_multiple',
            'transacted_w_address_total'
        ]
        self.feature_inputs = {}
        self.dataset = None

        try:
            # Load the trained model and scaler
            self.model = joblib.load("C:/Users/Admin/CryptoTrace1/Model/BTC-trained_model.pkl")
            self.scaler = joblib.load("C:/Users/Admin/CryptoTrace1/Model/BTC-scaler.pkl")
        except Exception as e:
            messagebox.showerror("Error", f"Model or Scaler loading failed: {str(e)}")

        self.setup_main_layout()

    def setup_main_layout(self):
        self.setup_header_frame()
        self.setup_input_frame()
        self.setup_button_frame()
        self.setup_result_frame()
        self.setup_data_display_frame()

    def setup_header_frame(self):
        header_frame = tk.Frame(self.master, bg="#333", pady=10)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(header_frame, text="BTC Fraud Detection Tool",
                                font=("Arial", 20, "bold"), fg="white", bg="#333")
        header_label.pack()

    def setup_input_frame(self):
        input_frame = tk.Frame(self.master, bg="#f5f5f5")
        input_frame.pack(fill=tk.X, pady=10)

        left_frame = tk.Frame(input_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        right_frame = tk.Frame(input_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        half = len(self.selected_features) // 2
        for idx, feature in enumerate(self.selected_features):
            parent_frame = left_frame if idx < half else right_frame
            row_frame = tk.Frame(parent_frame, bg="#f5f5f5")
            row_frame.pack(pady=5)

            label = tk.Label(row_frame, text=f"{feature}:", width=25, anchor="w", font=("Arial", 10))
            label.pack(side="left")

            entry = tk.Entry(row_frame, width=30, font=("Arial", 12))
            entry.pack(side="right")

            self.feature_inputs[feature] = entry

    def setup_button_frame(self):
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Import CSV", command=self.import_csv,
                  font=("Arial", 14), bg="#007bff", fg="white", padx=20, pady=10).pack(side="left", padx=10)

        tk.Button(button_frame, text="Search Address", command=self.search_address,
                  font=("Arial", 14), bg="#ffc107", fg="black", padx=20, pady=10).pack(side="left", padx=10)

        tk.Button(button_frame, text="Predict Fraud", command=self.predict_fraud,
                  font=("Arial", 14), bg="#28a745", fg="white", padx=20, pady=10).pack(side="left", padx=10)

        tk.Button(button_frame, text="Reset Fields", command=self.reset_fields,
                  font=("Arial", 14), bg="#dc3545", fg="white", padx=20, pady=10).pack(side="left", padx=10)

        tk.Button(button_frame, text="Hide/Unhide Data", command=self.toggle_data_display,
                  font=("Arial", 14), bg="#6c757d", fg="white", padx=20, pady=10).pack(side="left", padx=10)

    def setup_result_frame(self):
        result_frame = tk.Frame(self.master, bg="#f5f5f5")
        result_frame.pack(fill="both", expand=True, pady=20)

        tk.Label(result_frame, text="Prediction Result", font=("Arial", 14, "bold"),
                 bg="#f5f5f5", fg="#333").pack(pady=10)

        self.result_text = Text(result_frame, height=5, width=80, font=("Arial", 12),
                                bg="#e6f7ff", fg="#333", wrap="word")
        self.result_text.pack(pady=10)

    def setup_data_display_frame(self):
        self.data_frame = tk.Frame(self.master)
        self.data_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.treeview = ttk.Treeview(self.data_frame, show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar for the treeview
        self.treeview_scrollbar = tk.Scrollbar(self.data_frame, orient="vertical", command=self.treeview.yview)
        self.treeview_scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=self.treeview_scrollbar.set)

        # Add a horizontal scrollbar for the treeview
        self.treeview_scrollbar_x = tk.Scrollbar(self.data_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview_scrollbar_x.pack(side="bottom", fill="x")
        self.treeview.configure(xscrollcommand=self.treeview_scrollbar_x.set)

        self.treeview.bind("<Button-3>", self.on_right_click)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.dataset = pd.read_csv(file_path)
            self.display_data_in_treeview()

    def display_data_in_treeview(self):
        if self.dataset is not None:
            for item in self.treeview.get_children():
                self.treeview.delete(item)

            self.treeview["columns"] = list(self.dataset.columns)
            for col in self.dataset.columns:
                self.treeview.heading(col, text=col)

            for _, row in self.dataset.iterrows():
                self.treeview.insert("", "end", values=list(row))

    def on_right_click(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            selected_item = self.treeview.item(item)
            address = selected_item['values'][0]  # Assuming 'Address' is the first column
            pyperclip.copy(address)
            messagebox.showinfo("Copied", f"Address '{address}' copied to clipboard!")

    def search_address(self):
        if self.dataset is None:
            messagebox.showerror("Error", "Please import a CSV file first!")
            return

        search_window = tk.Toplevel(self.master)
        search_window.title("Search Address")
        search_window.geometry("400x200")

        tk.Label(search_window, text="Enter Address to Search:", font=("Arial", 12)).pack(pady=10)

        address_entry = tk.Entry(search_window, width=40, font=("Arial", 12))
        address_entry.pack(pady=10)

        def search():
            address = address_entry.get()
            if address in self.dataset['Address'].values:
                row = self.dataset[self.dataset['Address'] == address].iloc[0]
                for feature in self.feature_inputs:
                    if feature in row:
                        self.feature_inputs[feature].delete(0, tk.END)
                        self.feature_inputs[feature].insert(0, row[feature])
                messagebox.showinfo("Success", f"Address '{address}' found and loaded!")
            else:
                messagebox.showerror("Not Found", f"Address '{address}' not found in dataset.")
            search_window.destroy()

        tk.Button(search_window, text="Search", command=search, font=("Arial", 12), bg="#007bff", fg="white").pack(pady=10)

    def reset_fields(self):
        for feature in self.feature_inputs:
            self.feature_inputs[feature].delete(0, tk.END)
        self.result_text.delete('1.0', tk.END)

    def predict_fraud(self):
        try:
            input_data = []

            # Validate and collect input data
            for feature in self.selected_features:
                value = self.feature_inputs[feature].get()
                if not value.strip():
                    raise ValueError(f"Feature '{feature}' is empty.")
                if feature == 'Address':
                    input_data.append(hash_address(value))
                else:
                    input_data.append(float(value))

            # Prepare input data for prediction
            input_data = np.array([input_data])
            input_data_scaled = self.scaler.transform(input_data)
            probabilities = self.model.predict_proba(input_data_scaled)[0]
            predicted_class_index = np.argmax(probabilities)
            classes = ['Illicit(Fraud)', 'Licit(Normal)', 'Unknown(Fraud)']
            predicted_class = classes[predicted_class_index]

            # Display results in the text box
            self.display_results(predicted_class, probabilities)

            # Save results to a file
            self.save_report(predicted_class, probabilities)

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def display_results(self, predicted_class, probabilities):
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f"Predicted Class: {predicted_class}\n")
        self.result_text.insert(tk.END, "--------------------------------------------------------\n")
        self.result_text.insert(tk.END, "Probabilities:\n")
        self.result_text.insert(tk.END, f"  Illicit(Fraud): {probabilities[0] * 100:.2f}%\n")
        self.result_text.insert(tk.END, f"  Licit(Normal): {probabilities[1] * 100:.2f}%\n")
        self.result_text.insert(tk.END, f"  Unknown(Fraud): {probabilities[2] * 100:.2f}%\n")

    def save_report(self, predicted_class, probabilities, file_path="BTC_Prediction_Report.txt"):
        """Save a comprehensive prediction report to a file."""
        # Project Name and Description
        report_content = "==================================================\n"
        report_content += "          Cryptocurrency Fraud Detection (BTC)      \n"
        report_content += "==================================================\n"
        report_content += "\nProject Description:\n"
        report_content += "This project utilizes machine learning to predict fraudulent activity in\n"
        report_content += "Bitcoin transactions based on user-provided input data. The model outputs\n"
        report_content += "the likelihood of the transaction being categorized as illicit, normal,\n"
        report_content += "or unknown.\n\n"

        # Input Details
        report_content += "--------------------------------------------------\n"
        report_content += "Input Details:\n"
        report_content += "--------------------------------------------------\n"
        for feature, entry in self.feature_inputs.items():
            value = entry.get()
            report_content += f"{feature:40}: {value}\n"

        # Output Details
        report_content += "\n--------------------------------------------------\n"
        report_content += "Prediction Output:\n"
        report_content += "--------------------------------------------------\n"
        report_content += f"Predicted Class: {predicted_class}\n\n"
        report_content += "Probabilities:\n"
        report_content += f"  Illicit(Fraud): {probabilities[0] * 100:.2f}%\n"
        report_content += f"  Licit(Normal): {probabilities[1] * 100:.2f}%\n"
        report_content += f"  Unknown(Fraud): {probabilities[2] * 100:.2f}%\n\n"

        # Add Short Description Based on the Predicted Class
        report_content += "Short Description:\n"
        if predicted_class == 'Illicit(Fraud)':
            report_content += "The prediction indicates that the input data is most likely associated\n"
            report_content += "with fraudulent activity. Immediate investigation is recommended.\n"
        elif predicted_class == 'Licit(Normal)':
            report_content += "The prediction indicates that the input data is most likely normal and\n"
            report_content += "not associated with fraud. No action required.\n"
        elif predicted_class == 'Unknown(Fraud)':
            report_content += "The prediction is uncertain but leans towards fraudulent activity.\n"
            report_content += "Further investigation may be needed.\n"

        # Footer
        report_content += "\n==================================================\n"
        report_content += "Generated Report\n"
        report_content += "==================================================\n"
        report_content += "This report was generated using the BTC Fraud Detection Model.\n"
        report_content += "Report Date: {}\n".format(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Save the report to a file
        with open(file_path, "w") as report_file:
            report_file.write(report_content)

        # Notify the user
        messagebox.showinfo("Report Saved", f"Report saved to {file_path}")

    def toggle_data_display(self):
        if self.data_frame.winfo_ismapped():
            self.data_frame.pack_forget()
        else:
            self.data_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Main application launcher
def main():
    root = tk.Tk()
    app = FraudDetectionForm(root)
    root.mainloop()

if __name__ == "__main__":
    main()