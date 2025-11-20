import tkinter as tk
from tkinter import messagebox
import sqlite3
from PIL import Image, ImageTk
import socket
import platform
from logger import logger 
 



# Root window setup
root = tk.Tk()
root.title("CryptoTrace - Login")
root.geometry("500x700")
root.configure(bg="#f5fafd")

# Variables for user input
username = tk.StringVar()
password = tk.StringVar()

# Helper functions+
def get_ip_address():
    """Get the IP address of the current machine."""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        logger.error("Error fetching IP address", extra={"Error": str(e)})
        return "Unknown"

def get_device_info():
    """Get basic device information."""
    try:
        system = platform.system()  # E.g., Windows, Linux, macOS
        release = platform.release()  # OS version
        machine = platform.machine()  # Architecture (e.g., x86_64)
        return f"{system} {release} ({machine})"
    except Exception as e:
        logger.error("Error fetching device information", extra={"Error": str(e)})
        return "Unknown Device"



# Database setup and login function
def login():
    user_ip = get_ip_address()
    device_info = get_device_info()
    try:
        with sqlite3.connect('evaluation.db') as db:
            c = db.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS registration 
                         (username TEXT, Email TEXT, password TEXT)''')
            db.commit()
            find_entry = 'SELECT * FROM registration WHERE username = ? AND password = ?'
            c.execute(find_entry, (username.get(), password.get()))
            result = c.fetchall()

        if result:
            messagebox.showinfo("Success", "Login Successful!")
            logger.info(
                "Login successful",
                extra={"Username": username.get(), "IP": user_ip, "Device": device_info}
            )
            root.destroy()
            from subprocess import call
            call(['python', 'ui.py'])
        else:
            logger.warning(
                "Login failed",
                extra={"Username": username.get(), "IP": user_ip, "Device": device_info}
            )
            messagebox.showerror("Error", "Invalid username or password.")
    except Exception as e:
        logger.error(
            "Error during login",
            extra={"Username": username.get(), "IP": user_ip, "Device": device_info, "Error": str(e)}
        )
        messagebox.showerror("Error", "An unexpected error occurred. Please try again.")

def forgot_password():
    logger.info("Forgot password accessed", extra={"IP": get_ip_address(), "Device": get_device_info()})
    messagebox.showinfo("Forgot Password", "Please contact support@cryptotrace.com to reset your password.")

def sign_up():
    logger.info("Sign-up page accessed", extra={"IP": get_ip_address(), "Device": get_device_info()})
    messagebox.showinfo("Sign Up", "Redirecting to the sign-up page...")
    root.destroy()
    from subprocess import call
    call(['python', 'register.py'])

# Load and display the logo
try:
    logo_img = Image.open("cryptotrace_logo.png")
    logo_img = logo_img.resize((150, 150), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo, bg="#f5fafd")
    logo_label.pack(pady=20)
except Exception as e:
    print(f"Error loading logo: {e}")

# Title and subtitle
title_label = tk.Label(root, text="CryptoTrace", font=("Arial", 30, "bold"), fg="#003366", bg="#f5fafd")
title_label.pack(pady=5)

subtitle_label = tk.Label(root, text="Trace the Untraceable", font=("Arial", 16), fg="#C59E01", bg="#f5fafd")
subtitle_label.pack(pady=10)

# Input frame for fields
input_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="raised")
input_frame.pack(pady=30, padx=30)

# Username field
username_label = tk.Label(input_frame, text="Username", font=("Arial", 12), bg="#ffffff", fg="#333333")
username_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

username_entry = tk.Entry(input_frame, textvariable=username, font=("Arial", 12), width=30, bd=1, relief="solid")
username_entry.grid(row=0, column=1, pady=10, padx=10)

# Password field
password_label = tk.Label(input_frame, text="Password", font=("Arial", 12), bg="#ffffff", fg="#333333")
password_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

password_entry = tk.Entry(input_frame, textvariable=password, font=("Arial", 12), width=30, show="*", bd=1, relief="solid")
password_entry.grid(row=1, column=1, pady=10, padx=10)

# Login button
login_button = tk.Button(root, text="Login", command=login, font=("Arial", 14, "bold"), bg="#003366", fg="white",
                         activebackground="#0056b3", activeforeground="white", width=20, relief="flat", cursor="hand2")
login_button.pack(pady=20)

# Forgot password and sign-up links
options_frame = tk.Frame(root, bg="#f5fafd")
options_frame.pack(pady=10)

forgot_password_button = tk.Button(options_frame, text="Forgot Password?", command=forgot_password,
                                   font=("Arial", 10, "underline"), bg="#f5fafd", fg="#007bff",
                                   activebackground="#f5fafd", activeforeground="#0056b3", relief="flat", cursor="hand2")
forgot_password_button.grid(row=0, column=0, padx=20)

sign_up_button = tk.Button(options_frame, text="Sign Up", command=sign_up, font=("Arial", 10, "underline"),
                           bg="#f5fafd", fg="#007bff", activebackground="#f5fafd", activeforeground="#0056b3",
                           relief="flat", cursor="hand2")
sign_up_button.grid(row=0, column=1, padx=20)

# Footer
footer_label = tk.Label(root, text="© 2025 CryptoTrace Inc.", font=("Arial", 10), fg="#6c757d", bg="#f5fafd")
footer_label.pack(side="bottom", pady=10)

# Run the application
root.mainloop()