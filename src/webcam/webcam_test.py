from screeninfo import get_monitors
import cv2
import os
import platform
import subprocess
import time
import threading
import tkinter as tk

import os
import subprocess
import time
import tkinter as tk

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

def try_enable_camera():
    os_name = platform.system()
    print(f"Attempting to enable webcam on {os_name}...")

    if os_name == "Windows":
        cmd = [
            "powershell",
            "-Command",
            "Get-PnpDevice -Class Camera | Where-Object { $_.Status -eq 'Disabled' } "
            "| Enable-PnpDevice -Confirm:$false"
        ]
    elif os_name == "Linux":
        cmd = ["sudo", "modprobe", "-r", "uvcvideo", "&&", "sudo", "modprobe", "uvcvideo"]
    else:
        print("Automatic enabling not supported on this OS.")
        return False

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Enable command output:", result.stdout.strip())
        print("Enable command error (if any):", result.stderr.strip())
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to enable webcam. Command output:", e.stdout.strip())
        print("Command error:", e.stderr.strip())
        return False

def camera_test():
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            cap.release()
            break
    else:
        print("No camera found.")
        return "No camera found."

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam is not available.")
        if try_enable_camera():
            time.sleep(2)
            cap = cv2.VideoCapture(0)
        else:
            print("Could not enable the webcam automatically.")
            return "Could not enable the webcam automatically."

    if not cap.isOpened():
        print("Webcam is still not available after attempting to enable.")
        return "Webcam is still not available after attempting to enable."

    print("Webcam is available. Showing feed for 10 seconds...")



    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from webcam.")
            return "Failed to read from webcam."

        cv2.imshow("Webcam Test - Press 'q' to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("User closed the window.")
            break

        if time.time() - start_time > 10:
            break

    cap.release()
    cv2.destroyAllWindows()

    prompt_user_gui()
    print(Keyboard_response)

       # Print the response at the end
    if Keyboard_response == "yes":
        return "User reported a problem with the webcam."
    elif Keyboard_response == "no":
        return "Webcam is working fine."
    else:
        return "Webcam is working fine."