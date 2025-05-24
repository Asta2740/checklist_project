import os
import platform
import psutil
import os
import subprocess
import re
import os
import sys
import clr



import os
import platform
import psutil

def get_disk_info():
    """
    Returns a list of dictionaries with information about each physical disk:
    - name: Disk model name (e.g., 'CT500P3SSD8')
    - size_gb: Size in GB
    - type: 'SSD' or 'HDD' if detectable, else 'Unknown'
    """
    disks = []
    system = platform.system()

    if system == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                name = disk.Model.strip() if hasattr(disk, 'Model') else disk.DeviceID
                size_gb = round(int(disk.Size) / (1024**3), 2)
                if hasattr(disk, 'MediaType') and disk.MediaType:
                    if 'ssd' in disk.Model.lower() or 'ssd' in disk.MediaType.lower():
                        disk_type = 'SSD'
                    elif 'hdd' in disk.Model.lower() or 'hard' in disk.MediaType.lower():
                        disk_type = 'HDD'
                    else:
                        disk_type = 'Unknown'
                else:
                    disk_type = 'Unknown'
                disks.append({
                    'name': name,
                    'size_gb': size_gb,
                    'type': disk_type
                })
        except ImportError:
            print("wmi module not installed. Run 'pip install wmi' to get detailed disk info.")
    else:
        # Linux/Mac
        for disk in os.listdir("/sys/block/"):
            if disk.startswith("loop") or disk.startswith("ram"):
                continue  # Skip loop and ram disks

            model_path = f"/sys/block/{disk}/device/model"
            size_path = f"/sys/block/{disk}/size"
            sector_size_path = f"/sys/block/{disk}/queue/hw_sector_size"

            try:
                with open(model_path, 'r') as f:
                    model = f.read().strip()
            except Exception:
                model = disk  # fallback to disk name

            try:
                with open(size_path, 'r') as f:
                    num_sectors = int(f.read().strip())
                with open(sector_size_path, 'r') as f:
                    sector_size = int(f.read().strip())
                size_gb = round((num_sectors * sector_size) / (1024**3), 2)
            except Exception:
                size_gb = 0.0

            if 'nvme' in disk.lower() or 'ssd' in model.lower():
                disk_type = 'SSD'
            elif 'sd' in disk.lower() or 'hdd' in model.lower():
                disk_type = 'HDD'
            else:
                disk_type = 'Unknown'

            disks.append({
                'name': model,
                'size_gb': size_gb,
                'type': disk_type
            })

    return disks


# Example usage:


def get_local_smartctl_path():
    if getattr(sys, 'frozen', False):
    # When running from a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # When running from source (e.g., in VSCode)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    support_path = os.path.join(base_path, 'Support')
    smartctl_path = os.path.join(support_path, 'smartctl.exe')

    return smartctl_path

def parse_smart_health_percent(device, smartctl_path):
    try:
        output = subprocess.check_output(
            [smartctl_path, "-A", device],
            encoding='utf-8',
            stderr=subprocess.DEVNULL
        )
        health = 100

        if "No SMART support" in output:
            return "No SMART support"

        # Penalty weights for attributes that degrade health
        penalty_attrs = {
            "Reallocated_Sector_Ct": 10,
            "Reported_Uncorrect": 10,
            "Offline_Uncorrectable": 10,
            "Current_Pending_Sector": 10,
            "Uncorrectable_Error_Cnt": 10,
            "Media_Wearout_Indicator": 1,
            "Percentage_Used": 1,
        }

        for line in output.splitlines():
            for attr, weight in penalty_attrs.items():
                if attr in line:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 10:
                        try:
                            raw_value = int(parts[-1])
                            if raw_value > 0:
                                health -= min(raw_value * weight, 100)
                        except ValueError:
                            pass

        return max(0, health)

    except Exception as e:
        return f"Error reading SMART: {e}"

def get_all_disk_health_percent():
    smartctl_path = get_local_smartctl_path()
    health_map = {}
    try:
        output = subprocess.check_output([smartctl_path, "--scan"], encoding='utf-8')
        devices = [line.split()[0] for line in output.strip().split('\n')]
        for dev in devices:
            percent = parse_smart_health_percent(dev, smartctl_path)
            health_map[dev] = percent
    except Exception as e:
        print(f"smartctl scan failed: {e}")
    return health_map




print(get_disk_info())