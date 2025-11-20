import tkinter as tk
import sqlite3
from tkinter import messagebox as ms
from PIL import Image, ImageTk
from logger import logger
import re

# Initialize the main window
root = tk.Tk()
root.title("CryptoTrace - Registration")
root.geometry("600x700")
root.configure(bg="#f7f9fc")

# Database setup
db = sqlite3.connect('evaluation.db')
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS registration (username TEXT, Email TEXT, password TEXT)")
db.commit()

# Variables for user input
username = tk.StringVar()
email = tk.StringVar()
password = tk.StringVar()
password1 = tk.StringVar()

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

# Email validation function
def validate_email(email_address):
    """
    Validate email address using regex pattern
    Returns True if valid, False otherwise
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email_address) is not None

# Password validation function
def password_check(passwd):
    special_chars = ['$', '@', '#', '%']
    if (len(passwd) < 6 or len(passwd) > 20 or
            not any(char.isdigit() for char in passwd) or
            not any(char.isupper() for char in passwd) or
            not any(char.islower() for char in passwd) or
            not any(char in special_chars for char in passwd)):
        return False
    return True

# Registration function with audit logs
def register():
    fname = username.get()
    user_email = email.get()
    pwd = password.get()
    cnpwd = password1.get()

    user_ip = get_ip_address()  # Fetch IP dynamically
    device_info = get_device_info()  # Fetch device information dynamically

    try:
        if fname.isdigit() or fname == "":
            ms.showinfo("Error", "Please enter a valid username.")
            logger.warning(
                "Registration failed",
                extra={"Username": fname or "N/A", "IP": user_ip, "Device": device_info}
            )
        elif user_email == "" or not validate_email(user_email):
            ms.showinfo("Error", "Please enter a valid email address (e.g., user@example.com).")
            logger.warning(
                "Registration failed",
                extra={"Username": fname, "Email": user_email, "Reason": "Invalid email", "IP": user_ip, "Device": device_info}
            )
        elif not password_check(pwd):
            ms.showinfo("Error", "Password must include an uppercase letter, a lowercase letter, a number, and a special symbol.")
            logger.warning(
                "Registration failed",
                extra={"Username": fname, "Reason": "Weak password", "IP": user_ip, "Device": device_info}
            )
        elif pwd != cnpwd:
            ms.showinfo("Error", "Passwords do not match.")
            logger.warning(
                "Registration failed",
                extra={"Username": fname, "Reason": "Password mismatch", "IP": user_ip, "Device": device_info}
            )
        else:
            with sqlite3.connect('evaluation.db') as db:
                cursor = db.cursor()
                cursor.execute('INSERT INTO registration (username, Email, password) VALUES (?, ?, ?)', (fname, user_email, pwd))
                db.commit()
            ms.showinfo("Success", "Account created successfully!")
            logger.info(
                "Registration successful",
                extra={"Username": fname, "Email": user_email, "IP": user_ip, "Device": device_info}
            )
            root.destroy()
            # Navigate to the login page
            from subprocess import call
            call(['python', 'login.py'])
    except Exception as e:
        logger.error(
            "Error during registration",
            extra={"Username": fname, "Reason": str(e), "IP": user_ip, "Device": device_info}
        )
        ms.showerror("Error", "An unexpected error occurred. Please try again.")


# Load and display the logo
try:
    logo_img = Image.open("cryptotrace_logo.png")
    logo_img = logo_img.resize((150, 150), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo, bg="#f7f9fc")
    logo_label.pack(pady=20)
except Exception as e:
    print(f"Error loading logo: {e}")

# Title
title_label = tk.Label(root, text="Create Your CryptoTrace Account", font=("Arial", 20, "bold"), bg="#f7f9fc", fg="#003366")
title_label.pack(pady=10)

# Form frame for user inputs
form_frame = tk.Frame(root, bg="#ffffff", relief="raised", bd=2)
form_frame.pack(pady=20, padx=20)

# Input fields
fields = [
    ("Username", username),
    ("Email", email),
    ("Password", password),
    ("Confirm Password", password1)
]

for i, (label_text, var) in enumerate(fields):
    label = tk.Label(form_frame, text=label_text, font=("Arial", 12), bg="#ffffff", fg="#333333")
    label.grid(row=i, column=0, padx=10, pady=10, sticky="e")
    entry = tk.Entry(form_frame, font=("Arial", 12), width=25, textvariable=var)
    if "Password" in label_text:
        entry.config(show="*")  # Hide password input
    entry.grid(row=i, column=1, padx=10, pady=10)

def login():
    root.destroy()
    from subprocess import call
    call(['python', 'login.py'])

# Register button
register_button = tk.Button(root, text="Sign Up", command=register, font=("Arial", 14, "bold"),
                            bg="#003366", fg="#ffffff", width=15, relief="flat", cursor="hand2")
register_button.pack(pady=20)

# Footer
footer_frame = tk.Frame(root, bg="#f7f9fc")
footer_frame.pack(pady=10)

footer_label = tk.Label(footer_frame, text="Already have an account?", font=("Arial", 10), bg="#f7f9fc", fg="#333333")
footer_label.pack(side="left", padx=5)

login_link = tk.Button(footer_frame, text="Log in here", font=("Arial", 10, "bold"), bg="#f7f9fc", fg="#007bff",
                       command=login, cursor="hand2")
login_link.pack(side="left")

login_link.bind("<Button-1>", lambda e: print("Navigate to login page."))  # Replace with actual login navigation

# Footer
footer_label = tk.Label(
    root,
    text="© 2025 CryptoTrace Inc.",
    font=("Arial", 10),
    fg="#4a4a4a",
    bg="#f7f9fc"
)
footer_label.pack(side="bottom", pady=10)

# Run the application
root.mainloop()