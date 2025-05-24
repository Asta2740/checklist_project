import pyaudio
import wave
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from threading import Timer
import os
import os
import sys
import clr


# Audio configuration
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1              # Mono audio
RATE = 44100              # Sample rate (Hz)
CHUNK = 1024              # Frames per buffer
RECORD_SECONDS = 10     # Duration of recording
OUTPUT_FILENAME = "mic_test.wav"

# Initialize PyAudio
try:
    audio = pyaudio.PyAudio()
except Exception as e:
    print(f"Error initializing PyAudio: {e}")
    exit()

def record_microphone_test():
    frames = []
    try:
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"Error opening audio stream: {e}")
        return False

    print("Recording for 10 seconds... Speak into the microphone.")
    try:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("Recording finished.")
    except Exception as e:
        print(f"Error during recording: {e}")
        stream.stop_stream()
        stream.close()
        return False

    try:
        stream.stop_stream()
        stream.close()
    except Exception as e:
        print(f"Error stopping or closing the stream: {e}")

    # Save the recorded audio to a WAV file
    try:
        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    except Exception as e:
        print(f"Error saving the WAV file: {e}")
        return False

    return True


# Initialize global variables to store test results
microphone_test_result = "There is no problem with the microphone."
audio_channel_test_result = "There is no Problem with the Speakers."

# Prompt the user with a custom UI
def prompt_user():
    global microphone_test_result
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window

        # Create a custom dialog
        dialog = tk.Toplevel(root)
        dialog.title("Microphone Test")
        dialog.geometry("300x150")
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable manual closing

        label = tk.Label(dialog, text="Is there a problem with the microphone?")
        label.pack(pady=20)

        response = {"value": None}

        def on_yes():
            response["value"] = True
            dialog.destroy()

        def on_no():
            response["value"] = False
            dialog.destroy()

        yes_button = tk.Button(dialog, text="Yes", command=on_yes)
        yes_button.pack(side=tk.LEFT, padx=20, pady=20)

        no_button = tk.Button(dialog, text="No", command=on_no)
        no_button.pack(side=tk.RIGHT, padx=20, pady=20)

        # Timeout mechanism
        def timeout():
            if response["value"] is None:
                print("There is no problem with the microphone.")
                dialog.destroy()

        root.after(10000, timeout)  # 10 seconds timeout
        root.wait_window(dialog)

        if response["value"] is None:
            print("There is no problem with the microphone.")
            root.destroy()
            return "There is no problem with the microphone."
        elif response["value"]:
            microphone_test_result = "There is a problem with the microphone."
            root.destroy()
            return microphone_test_result
        else:
            microphone_test_result = "There is no problem with the microphone."
            root.destroy()
            return microphone_test_result
        
    except Exception as e:
        print(f"Error during user prompt: {e}")
        return "Microphone test failed."

# Play the Audio-test.wav file and prompt the user
def play_audio_test():
    global audio_channel_test_result
    try:
        print("Playing Audio-test.wav...")
        # Detect if running from a PyInstaller bundle
        if getattr(sys, 'frozen', False):
        # When running from a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
        # When running from source (e.g., in VSCode)
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        support_path = os.path.join(base_path, 'Support')
        audio_path = os.path.join(support_path, 'Audio-test.wav')

        wf = wave.open(audio_path, 'rb')
        stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

        # Read and play the audio data
        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        # Clean up
        stream.stop_stream()
        stream.close()
        print("Audio-test.wav playback finished.")

        # Prompt the user for feedback
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window

        # Create a custom dialog
        dialog = tk.Toplevel(root)
        dialog.title("Audio Channel Test")
        dialog.geometry("300x150")
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable manual closing

        label = tk.Label(dialog, text="Is there a problem with the audio?\nOptions: left, right, none")
        label.pack(pady=20)

        response = {"value": None}

        def on_submit():
            response["value"] = entry.get()
            dialog.destroy()

        entry = tk.Entry(dialog)
        entry.pack(pady=10)

        submit_button = tk.Button(dialog, text="Submit", command=on_submit)
        submit_button.pack(pady=10)

        # Timeout mechanism
        def timeout():
            if response["value"] is None:
                print("There is no Problem with the Speakers.")
                dialog.destroy()

        root.after(10000, timeout)  # 10 seconds timeout
        root.wait_window(dialog)

        if response["value"] is None:
            print("There is no Problem with the Speakers.")
            root.destroy()
            return "There is no Problem with the Speakers."
        elif response["value"].lower() == "none":
            print("There is no Problem with the Speakers.")
            root.destroy()
            return "There is no Problem with the Speakers."
        else:
            audio_channel_test_result = f"There is  a problem with: {response['value']} Side"
            root.destroy()
            return audio_channel_test_result

    except Exception as e:
        print(f"An error occurred during audio channel test: {e}")
        return "Audio channel test failed."
