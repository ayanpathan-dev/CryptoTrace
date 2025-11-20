import tkinter as tk
from tkinter import messagebox, Text, filedialog, ttk
import pandas as pd
import numpy as np
import joblib  # For loading the trained model
from sklearn.preprocessing import StandardScaler
import hashlib
import pyperclip  # To handle clipboard copying

# Function to hash Ethereum addresses
def hash_address(address):
    return int(hashlib.sha256(address.encode('utf-8')).hexdigest(), 16)

# Load the trained model and scaler
model = joblib.load('C:/Users/Admin/CryptoTrace1/Model/trained_model.pkl')  # Replace with your .pkl file path
scaler = joblib.load('C:/Users/Admin/CryptoTrace1/Model/scaler.pkl')  # Replace with your scaler .pkl file path

# Features used for prediction (keeping the original features from the first code)
selected_features = [
    'Avg min between sent tnx', 'Avg min between received tnx', 
    'Time Diff between first and last (Mins)', 'Sent tnx', 'Received Tnx', 
    'Number of Created Contracts', 'Unique Received From Addresses',
]
selected_features2 = [
    'Unique Sent To Addresses', 'total transactions (including tnx to create contract)',
    'total Ether sent', 'total ether received', 'Total ERC20 tnxs', 'Address'
]

# GUI Application Class
class FraudDetectionForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptocurrency Fraud Detection (Ethereum)")
        self.root.geometry("1200x750")  # Increased window size

        self.dataset = None  # Placeholder for dataset
        self.feature_inputs = {}

        self.setup_main_layout()

    def setup_main_layout(self):
        self.setup_header_frame()
        self.setup_input_frame()
        self.setup_button_frame()
        self.setup_result_frame()
        self.setup_data_display_frame()

    def setup_header_frame(self):
        header_frame = tk.Frame(self.root, bg="#333", pady=10)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(header_frame, text="Cryptocurrency Fraud Detection (Ethereum)",
                                font=("Arial", 20, "bold"), fg="white", bg="#333")
        header_label.pack()

    def setup_input_frame(self):
        input_frame = tk.Frame(self.root, bg="#f5f5f5")
        input_frame.pack(fill=tk.X, pady=10)

        left_frame = tk.Frame(input_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        right_frame = tk.Frame(input_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        for feature in selected_features:
            row_frame = tk.Frame(left_frame, bg="#f5f5f5")
            row_frame.pack(pady=5)

            label = tk.Label(row_frame, text=f"{feature}:", width=35, anchor="w", font=("Arial", 10))
            label.pack(side="left")

            entry = tk.Entry(row_frame, width=30, font=("Arial", 12))
            entry.pack(side="right")

            self.feature_inputs[feature] = entry

        for feature in selected_features2:
            row_frame = tk.Frame(right_frame, bg="#f5f5f5")
            row_frame.pack(pady=5)

            label = tk.Label(row_frame, text=f"{feature}:", width=35, anchor="w", font=("Arial", 10))
            label.pack(side="left")

            entry = tk.Entry(row_frame, width=30, font=("Arial", 12))
            entry.pack(side="right")

            self.feature_inputs[feature] = entry

    def setup_button_frame(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        import_button = tk.Button(button_frame, text="Import CSV", command=self.import_csv,
                                  font=("Arial", 14), bg="#007bff", fg="white", padx=20, pady=10)
        import_button.pack(side="left", padx=10)

        search_button = tk.Button(button_frame, text="Search Address", command=self.search_address,
                                  font=("Arial", 14), bg="#ffc107", fg="black", padx=20, pady=10)
        search_button.pack(side="left", padx=10)

        predict_button = tk.Button(button_frame, text="Predict Fraud", command=self.predict_fraud,
                                   font=("Arial", 14), bg="#28a745", fg="white", padx=20, pady=10)
        predict_button.pack(side="left", padx=10)

        reset_button = tk.Button(button_frame, text="Reset Fields", command=self.reset_fields,
                                 font=("Arial", 14), bg="#dc3545", fg="white", padx=20, pady=10)
        reset_button.pack(side="left", padx=10)

        hide_button = tk.Button(button_frame, text="Hide/Unhide Data", command=self.toggle_data_display,
                                 font=("Arial", 14), bg="#6c757d", fg="white", padx=20, pady=10)
        hide_button.pack(side="left", padx=10)

    def setup_result_frame(self):
        result_frame = tk.Frame(self.root, bg="#f5f5f5")
        result_frame.pack(fill="both", expand=True, pady=20)

        tk.Label(result_frame, text="Prediction Result", font=("Arial", 14, "bold"),
                 bg="#f5f5f5", fg="#333").pack(pady=10)

        self.result_text = Text(result_frame, height=5, width=80, font=("Arial", 12),
                                bg="#e6f7ff", fg="#333", wrap="word")
        self.result_text.pack(pady=10)

        result_frame.pack_propagate(False)

    def setup_data_display_frame(self):
        self.data_frame = tk.Frame(self.root)
        self.data_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.treeview = ttk.Treeview(self.data_frame, show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Bind the right-click event to the Treeview
        self.treeview.bind("<Button-3>", self.show_context_menu)

        # Create a context menu (right-click menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy Address", command=self.copy_address)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.dataset = pd.read_csv(file_path)
            self.display_data_in_treeview()

    def display_data_in_treeview(self):
        if self.dataset is not None:
            # Clear existing data in the Treeview
            for item in self.treeview.get_children():
                self.treeview.delete(item)

            # Set the column headers based on the dataset columns
            self.treeview["columns"] = list(self.dataset.columns)
            for col in self.dataset.columns:
                self.treeview.heading(col, text=col)

            # Insert the rows into the Treeview
            for _, row in self.dataset.iterrows():
                self.treeview.insert("", "end", values=list(row))

    def search_address(self):
        if self.dataset is None:
            messagebox.showerror("Error", "Please import a CSV file first!")
            return

        search_window = tk.Toplevel(self.root)
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
            for feature in selected_features + selected_features2:
                if feature == 'Address':
                    address = self.feature_inputs[feature].get()
                    input_data.append(hash_address(address))
                else:
                    value = float(self.feature_inputs[feature].get())
                    input_data.append(value)

            input_data = np.array([input_data])
            input_data_scaled = scaler.transform(input_data)

            probabilities = model.predict_proba(input_data_scaled)[0]
            predicted_class_index = np.argmax(probabilities)
            classes = ['Illicit(Fraud)', 'Licit(Normal)']  # Removed 'Unknown(Fraud)'
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

    def save_report(self, predicted_class, probabilities, file_path="Ethereum_Prediction_Report.txt"):
        """Save a comprehensive prediction report to a file."""
        # Project Name and Description
        report_content = "==================================================\n"
        report_content += "          Cryptocurrency Fraud Detection (Ethereum)      \n"
        report_content += "==================================================\n"
        report_content += "\nProject Description:\n"
        report_content += "This project utilizes machine learning to predict fraudulent activity in\n"
        report_content += "Ethereum transactions based on user-provided input data. The model outputs\n"
        report_content += "the likelihood of the transaction being categorized as illicit or normal.\n\n"

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
        report_content += f"  Licit(Normal): {probabilities[1] * 100:.2f}%\n\n"

        # Add Short Description Based on the Predicted Class
        report_content += "Short Description:\n"
        if predicted_class == 'Illicit(Fraud)':
            report_content += "The prediction indicates that the input data is most likely associated\n"
            report_content += "with fraudulent activity. Immediate investigation is recommended.\n"
        elif predicted_class == 'Licit(Normal)':
            report_content += "The prediction indicates that the input data is most likely normal and\n"
            report_content += "not associated with fraud. No action required.\n"

        # Footer
        report_content += "\n==================================================\n"
        report_content += "Generated Report\n"
        report_content += "==================================================\n"
        report_content += "This report was generated using the ETH Fraud Detection Model.\n"
        report_content += "Report Date: {}\n".format(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Save the report to a file
        with open(file_path, "w") as report_file:
            report_file.write(report_content)

        # Notify the user
        messagebox.showinfo("Report Saved", f"Report saved to {file_path}")

    def toggle_data_display(self):
        # Toggle the visibility of the data frame (Treeview)
        if self.data_frame.winfo_ismapped():
            self.data_frame.pack_forget()  # Hide the data frame
        else:
            self.data_frame.pack(fill=tk.BOTH, expand=True, pady=10)  # Show the data frame

    def show_context_menu(self, event):
        # Show the right-click menu
        item = self.treeview.identify('item', event.x, event.y)
        if item:
            self.context_menu.post(event.x_root, event.y_root)

    def copy_address(self):
        selected_item = self.treeview.selection()
        if selected_item:
            selected_address = self.treeview.item(selected_item[0], "values")[0]
            pyperclip.copy(selected_address)
            messagebox.showinfo("Copied", f"Address '{selected_address}' copied to clipboard.")
        else:
            messagebox.showerror("Error", "No address selected.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FraudDetectionForm(root)
    root.mainloop()