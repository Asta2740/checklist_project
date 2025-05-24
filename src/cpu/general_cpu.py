import threading
import time
import multiprocessing
import numpy as np
import time
import clr  # pythonnet
import sys
import os
import psutil
import time
import platform
import sys
import queue

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def matrix_workload(stop_event, intensity=0.9):
    """Perform intensive matrix multiplication with adjustable intensity."""
    matrix_size = 500  # Size of square matrices
    while not stop_event.is_set():
        # Generate random matrices
        a = np.random.rand(matrix_size, matrix_size)
        b = np.random.rand(matrix_size, matrix_size)
        # Perform matrix multiplication
        _ = np.dot(a, b)
        # Sleep to adjust CPU usage (tune intensity)
        time.sleep(0.01 * (1 - intensity))

def monitor_cpu(stop_event, target_usage=90):
    """Monitor CPU usage and temperature with live updates and stats.
    Returns:
        summary (dict): Contains CPU usage stats and per-sensor temp stats.
    """
    print("Monitoring CPU usage and temperature (press Ctrl+C to stop)...")
    start_time = time.time()
    usages = []
    min_usage = float('inf')
    max_usage = float('-inf')
    temp_records = {}  # {sensor_name: [list of temps]}
    try:
        while not stop_event.is_set():
            if PSUTIL_AVAILABLE:
                cpu_percents = psutil.cpu_percent(interval=1, percpu=True)
                avg_usage = sum(cpu_percents) / len(cpu_percents)
                usages.append(avg_usage)
                min_usage = min(min_usage, avg_usage)
                max_usage = max(max_usage, avg_usage)
                core_str = " | ".join([f"Core {i}: {p:.1f}%" for i, p in enumerate(cpu_percents)])
                # Get CPU temps
                temps = get_cpu_temps()
                if temps:
                    temp_strs = []
                    for name, value in temps:
                        if value is not None:
                            temp_records.setdefault(name, []).append(value)
                            temp_strs.append(f"{name}: {value:.1f}°C")
                    temp_str = " | ".join(temp_strs)
                else:
                    temp_str = "No temp data"
                print(f"\rCPU Usage: {avg_usage:.1f}% (min: {min_usage:.1f}%, max: {max_usage:.1f}%) | {core_str} | Temps: {temp_str}   ", end='', flush=True)
            else:
                print("\rCPU usage monitoring unavailable (psutil not installed).", end='', flush=True)
                time.sleep(1)
            # Stop after 60 seconds for safety
            if time.time() - start_time > 60:
                stop_event.set()
                print("\nTest duration reached 60 seconds, stopping...")
                break
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
    finally:
        if usages:
            avg_usage = sum(usages) / len(usages)
            print(f"\nAverage CPU Usage: {avg_usage:.1f}%")
            print(f"Min CPU Usage: {min_usage:.1f}%")
            print(f"Max CPU Usage: {max_usage:.1f}%")
        else:
            avg_usage = 0.0
        # Print and collect temperature stats
        temp_stats = {}
        if temp_records:
            for name, values in temp_records.items():
                max_temp = max(values)
                avg_temp = sum(values) / len(values)
                temp_stats[name] = {"max": max_temp, "avg": avg_temp}
                print(f"{name}:  Maximum : {max_temp:.1f} °C  Average : {avg_temp:.1f} °C")
        else:
            print("No temperature data collected.")
        # Return all stats in a dictionary
        return {
            "avg_usage": avg_usage,
            "min_usage": min_usage,
            "max_usage": max_usage,
            "temps": temp_stats
        }

def stress_cpu(target_usage=90):
    """Stress CPU to approximately target_usage% using all cores and return monitoring results."""
    num_cores = multiprocessing.cpu_count()
    print(f"Detected {num_cores} CPU cores. Starting stress test...")

    stop_event = threading.Event()
    result_queue = queue.Queue()  # For returning monitor_cpu result

    # Wrap monitor_cpu to put its result in the queue
    def monitor_wrapper(stop_event, target_usage, result_queue):
        result = monitor_cpu(stop_event, target_usage)
        result_queue.put(result)

    monitor_thread = threading.Thread(target=monitor_wrapper, args=(stop_event, target_usage, result_queue))
    monitor_thread.daemon = True
    monitor_thread.start()

    threads = []
    intensity = 1
    for _ in range(num_cores):
        t = threading.Thread(target=matrix_workload, args=(stop_event, intensity))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping stress test...")
    finally:
        stop_event.set()
        for t in threads:
            t.join()
        monitor_thread.join(timeout=2)
        print("Stress test completed.")

    # Get the result from the queue (if available)
    if not result_queue.empty():
        return result_queue.get()
    else:
        return None


# Path to the OpenHardwareMonitorLib.dll
# Detect if running from a PyInstaller bundle
if getattr(sys, 'frozen', False):
# When running from a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # When running from source (e.g., in VSCode)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

support_path = os.path.join(base_path, 'Support')
dll_path = os.path.join(support_path, 'OpenHardwareMonitorLib.dll')
print(dll_path)

# Load the assembly
sys.path.append(os.path.dirname(dll_path))
clr.AddReference("OpenHardwareMonitorLib")

from OpenHardwareMonitor import Hardware ## ignore

# Initialize computer
computer = Hardware.Computer()
computer.CPUEnabled = True
computer.Open()

import time


def get_cpu_temps():
    temps = []
    for hw in computer.Hardware:
        hw.Update()  # Required to get the latest data
        if hw.HardwareType == Hardware.HardwareType.CPU:
            for sensor in hw.Sensors:
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    temps.append((sensor.Name, sensor.Value))
    return temps




# Import winreg only if on Windows
if platform.system() == 'Windows':
    import winreg

def get_cpu_name():
    os_name = platform.system()
    if os_name == 'Windows':
        # Access the Windows registry to get the CPU name
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        value, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        return value
    elif os_name == 'Linux':
        # Read /proc/cpuinfo on Linux to find the model name
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('model name'):
                    return line.split(':')[1].strip()
    elif os_name == 'Darwin':  # macOS
        # Use sysctl command on macOS to get the CPU brand string
        import subprocess
        output = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
        return output
    else:
        return "Unknown OS"