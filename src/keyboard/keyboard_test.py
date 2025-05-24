import os
import subprocess
import time
import tkinter as tk
import os
import sys
import clr

# Global variable to store the keyboard response
Keyboard_response = None

def prompt_user_gui():
    def on_yes():
        global Keyboard_response
        Keyboard_response = "yes"
        if root:
            root.destroy()

    def on_no():
        global Keyboard_response
        Keyboard_response = "no"
        if root:
            root.destroy()

    def on_timeout():
        global Keyboard_response
        Keyboard_response = "no"  # Default to "no" if timeout occurs
        if root:
            root.destroy()

    root = tk.Tk()
    root.title("Problem Check")
    root.geometry("300x150")
    root.resizable(False, False)

    # Add a label
    label = tk.Label(root, text="Is there a problem?", font=("Arial", 12))
    label.pack(pady=20)

    # Add Yes and No buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    yes_button = tk.Button(button_frame, text="Yes", width=10, command=on_yes)
    yes_button.pack(side="left", padx=10)

    no_button = tk.Button(button_frame, text="No", width=10, command=on_no)
    no_button.pack(side="right", padx=10)

    # Set a timeout to close the window automatically
    root.after(10000, on_timeout)

    # Run the main event loop
    root.mainloop()

def run_aqua_key_test():
    # Define the absolute path to AquaKeyTest.exe
    # Detect if running from a PyInstaller bundle
    # Detect if running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
    # When running from a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
    # When running from source (e.g., in VSCode)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    support_path = os.path.join(base_path, 'Support')

    aqua_key_test_path = os.path.join(support_path, 'AquaKeyTest.exe')

    # Run the AquaKeyTest.exe
    try:
        process = subprocess.Popen(aqua_key_test_path, shell=True)
    except FileNotFoundError:
        print(f"Error: The file '{aqua_key_test_path}' was not found.")
        exit(1)

    # Wait for 60 seconds
    time.sleep(60)

    # Prompt the user using GUI
    prompt_user_gui()
    print(Keyboard_response)

    # Print the response at the end
    if Keyboard_response == "yes":
        return "Problem Detected in the Keyboard"
    elif Keyboard_response == "no":
        return "Keyboard is working fine"
    else:
        return "Keyboard is working fine."