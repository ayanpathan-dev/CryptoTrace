import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import hashlib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Hashing function to convert Ethereum address to a numeric value
def hash_address(address):
    return int(hashlib.sha256(address.encode('utf-8')).hexdigest(), 16)

# Main function to execute the ML pipeline and display results
def run_pipeline():
    try:
        # Load dataset
        data = pd.read_csv('transaction_dataset_updated.csv')

        # Handle missing values
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())
        non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
        data[non_numeric_cols] = data[non_numeric_cols].fillna('Unknown')

        # Replace infinite values in numeric columns
        data[numeric_cols] = data[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(data[numeric_cols].median())

        # Add a hashed column for Ethereum address
        data['address_hash'] = data['Address'].apply(hash_address)

        # Define features and target variable
        selected_features = [
            'Avg min between sent tnx', 'Avg min between received tnx',
            'Time Diff between first and last (Mins)', 'Sent tnx', 'Received Tnx',
            'Number of Created Contracts', 'Unique Received From Addresses',
            'Unique Sent To Addresses', 'total transactions (including tnx to create contract)',
            'total Ether sent', 'total ether received', 'Total ERC20 tnxs', 'address_hash'
        ]
        X = data[selected_features]
        y = data['FLAG']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Standardize features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train the model
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train_scaled, y_train)

        # Save the model and scaler
        joblib.dump(model, 'trained_model.pkl')
        joblib.dump(scaler, 'scaler.pkl')

        # Evaluate the model
        y_pred = model.predict(X_test_scaled)
        report = classification_report(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        acc = "Accuracy Score: {:.2f}%".format(accuracy_score(y_test, y_pred) * 100)


        # Display classification report
        report_text.delete("1.0", tk.END)
        report_text.insert(tk.END, f"Classification Report:\n\n{report}\n{acc}")

        # Plot and display confusion matrix
        conf_matrix = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots(figsize=(7, 7))  # Adjusting the size to approximately 500x500 pixels
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Not Fraud', 'Fraud'], yticklabels=['Not Fraud', 'Fraud'], ax=ax)
        ax.set_title('Confusion Matrix', fontsize=16)
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        
        # Embed confusion matrix plot in the GUI
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Tkinter GUI
root = tk.Tk()
root.title("CryptoTrace - ML Evaluation")
root.geometry("1000x600")
root.configure(bg="#e8f1fa")

# Main frames for layout
left_frame = tk.Frame(root, bg="#e8f1fa", width=500, height=600)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(root, bg="#e8f1fa", width=500, height=600)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Title
title_label = tk.Label(left_frame, text="CryptoTrace ML Evaluation", font=("Arial", 20, "bold"), fg="#003366", bg="#e8f1fa")
title_label.pack(pady=20)

# Classification report section
report_text = tk.Text(left_frame, font=("Arial", 12), wrap=tk.WORD, bg="#f5f5f5", fg="#333333", height=20, width=50)
report_text.pack(pady=10, padx=10)

# Button to run pipeline
run_button = tk.Button(left_frame, text="Run Machine Learning Model", font=("Arial", 14), bg="#0056b3", fg="white",
                       activebackground="#003366", activeforeground="white", command=run_pipeline)
run_button.pack(pady=10)

# Confusion matrix plot area
plot_frame = tk.Frame(right_frame, bg="#e8f1fa")
plot_frame.pack(fill=tk.BOTH, expand=True)

# Footer
footer_label = tk.Label(root, text="© 2025 CryptoTrace Inc.", font=("Arial", 10), fg="#6c757d", bg="#e8f1fa")
footer_label.pack(side="bottom", pady=10)

root.mainloop()
