import subprocess
import sys

def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please make sure you have pip installed.")
        sys.exit(1)

# Install dependencies
install_dependencies()

import tkinter as tk
from tkinter import messagebox
import threading
import paramiko
import webbrowser
import re
from ctypes import windll

# Set DPI awareness (requires Windows 8.1 or later)
windll.shcore.SetProcessDpiAwareness(1)

class BackupBoxSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Box Setup v1.0")
        self.root.geometry("750x650")

        self.setup_frame = tk.Frame(self.root)
        self.setup_frame.pack(pady=20)

        self.label = tk.Label(self.setup_frame, text="Welcome to Backup Box Setup!", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.update_frame = tk.Frame(self.root)

        self.start_button = tk.Button(self.setup_frame, text="Start Setup", command=self.start_setup)
        self.start_button.pack(pady=10)

        # Initialize setup_complete_label
        self.setup_complete_label = tk.Label(self.root, text="", font=("Helvetica", 12))

    def close_program(self, event):
        self.root.destroy()

    def start_setup(self):
        confirm_message = "To start the setup, please make sure that your Backup Box is connected to power and is connected to your internet modem/switch/router with the included Ethernet cable. Refer to the included user manual."
        confirm_dialog = messagebox.askyesno("Confirm Setup", confirm_message)

        if confirm_dialog:
            self.label.config(text="Updating Backup Box...")
            self.start_button.config(state=tk.DISABLED)  # Disable the button after clicking

            self.update_frame.pack(pady=20)

            threading.Thread(target=self.update_backup_box).start()

    def update_backup_box(self):
        try:
            # SSH Connection
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname="backup-box", username="backup-box", password="backup-box#@")  # Replace with actual credentials

            # Update Backup Box
            self.update_text = tk.Text(self.update_frame, height=10, width=60, wrap=tk.WORD)
            self.update_text.pack(pady=10)
            stdin, stdout, stderr = client.exec_command("sudo apt update && sudo apt upgrade -y")
            line_count = 0
            for line in stdout:
                if line_count < 10:
                    self.update_text.insert(tk.END, line.strip() + "\n")
                    line_count += 1
                else:
                    self.update_text.delete(1.0, tk.END)
                    self.update_text.insert(tk.END, line.strip() + "\n")
                self.update_text.see(tk.END)

            # Successful update message
            self.label.config(text="Backup Box successfully updated!")

            # Remove update progress box
            self.update_frame.pack_forget()

            # Show Start Setup button again
            self.start_button.pack()

            # Ask for password
            self.ask_for_password(client)

        except Exception as e:
            # Error handling
            self.label.config(text="Error updating Backup Box. Please contact support.")
            error_message = f"Error: {str(e)}\nContact support at www.256bits.tech/contact"
            self.error_label = tk.Label(self.root, text=error_message, font=("Helvetica", 10), justify="left", fg="red", cursor="hand2")
            self.error_label.pack(pady=10)
            self.error_label.bind("<Button-1>", lambda event: webbrowser.open("https://256bits.tech/contact"))

    def ask_for_password(self, client):
        # Ask user for password
        self.label.config(text="It is now time to choose a password for your Backup Box.")
        self.label.config(wraplength=400)  # Set wrap length
        self.criteria_label = tk.Label(self.root, text="Please make sure that your password is secure and contains Capital and Lowercase letters as well as at least 1 special character [! & # $].", font=("Helvetica", 10), wraplength=400)
        self.criteria_label.pack(pady=5)
        self.password_entry_label = tk.Label(self.root, text="Enter Password:", font=("Helvetica", 10))
        self.password_entry_label.pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 10))
        self.password_entry.pack(pady=5)
        self.show_password_var = tk.IntVar()
        self.show_password_checkbox = tk.Checkbutton(self.root, text="Show password", variable=self.show_password_var, command=self.toggle_password_visibility)
        self.show_password_checkbox.pack(pady=5)
        self.confirm_password_label = tk.Label(self.root, text="Confirm Password:", font=("Helvetica", 10))
        self.confirm_password_label.pack(pady=5)
        self.confirm_password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 10))
        self.confirm_password_entry.pack(pady=5)
        self.confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.confirm_password(client))
        self.confirm_button.pack(pady=5)
    
        # Initialize the link label
        self.link = tk.Label(self.root, text="To learn how to connect your device, refer to your Setup Guide or www.256bits.tech/setup", font=("Helvetica", 10), fg="blue", cursor="hand2")
        self.link.pack(pady=5)
        self.link.bind("<Button-1>", lambda event: webbrowser.open("https://256bits.tech/setup"))

    def toggle_password_visibility(self):
        if self.show_password_var.get() == 1:
            self.password_entry.config(show="")
            self.confirm_password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            self.confirm_password_entry.config(show="*")

    def confirm_password(self, client):
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Password validation rules
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return
        if not re.search("[a-z]", password):
            messagebox.showerror("Error", "Password must contain at least one lowercase letter.")
            return
        if not re.search("[A-Z]", password):
            messagebox.showerror("Error", "Password must contain at least one uppercase letter.")
            return
        if not re.search("[!&#$]", password):
            messagebox.showerror("Error", "Password must contain at least one special character [! & # $].")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match. Please re-enter.")
            return

        confirm_message = f"Are you 100% sure that you would like to set this as the password? If you lose this password you will lose access to your Backup Box and all of its data!"
        confirm_dialog = messagebox.askyesno("Confirm Password", confirm_message)

        if confirm_dialog:
            try:
                # Change password
                stdin, stdout, stderr = client.exec_command(f'echo "backup-box:{password}" | sudo chpasswd')

                # Successful password change message
                self.label.config(text=f"Password successfully set! Please make sure that you write it down in a safe place!")
                messagebox.showinfo("Password Set", f"Password successfully set! Please make sure that you write it down in a safe place!")

                # Lock all aspects of the window
                self.root.attributes('-disabled', True)

                # Change setup completion message to green
                self.setup_complete_label.config(text="Setup Complete!", fg="green")

                # Display the link
                self.link.config(text="To learn how to connect your device, refer to your Setup Guide or www.256bits.tech/setup", fg="blue")
                self.link.bind("<Button-1>", lambda event: webbrowser.open("https://256bits.tech/setup"))

                # Disable password entry after setup completion
                self.password_entry.config(state=tk.DISABLED)
                self.confirm_password_entry.config(state=tk.DISABLED)
                self.confirm_button.config(state=tk.DISABLED)

                # Add label for closing instruction
                self.close_instruction_label = tk.Label(self.root, text="Press Enter to close the program", font=("Helvetica", 10))
                self.close_instruction_label.pack(pady=5)

                # Bind Enter key to close the program
                self.root.bind("<Return>", self.close_program)

            except Exception as e:
                # Error handling
                self.label.config(text="Error setting password. Please contact support.")
                error_message = f"Error: {str(e)}\nContact support at www.256bits.tech/contact"
                self.error_label = tk.Label(self.root, text=error_message, font=("Helvetica", 10), justify="left", fg="red", cursor="hand2")
                self.error_label.pack(pady=10)
                self.error_label.bind("<Button-1>", lambda event: webbrowser.open("https://256bits.tech/contact"))

                self.setup_complete_label.config(text="Setup incomplete", fg="red")

        else:
            self.label.config(text="Password setup cancelled.")
            self.setup_complete_label = tk.Label(self.root, text="Setup incomplete", font=("Helvetica", 12), fg="red")
            self.setup_complete_label.pack(pady=10)
            self.link.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupBoxSetup(root)
    root.mainloop()
