import psutil
import math

def get_total_ram():
    # Get memory info
    memory = psutil.virtual_memory()
    # Total RAM in bytes
    total_ram = memory.total
    # Convert to GB
    total_ram_gb = total_ram / (1024 ** 3)
    # Round up to the nearest whole number
    total_ram_rounded = math.ceil(total_ram_gb)
    return total_ram_rounded

def get_ram_type():
    try:
        import wmi
        ram_types = {
            20: "DDR",
            21: "DDR2",
            24: "DDR3",
            26: "DDR4"
        }
        c = wmi.WMI()
        types = set()
        for mem in c.Win32_PhysicalMemory():
            # Try SMBIOSMemoryType first, fallback to MemoryType
            t = int(getattr(mem, "SMBIOSMemoryType", 0) or 0)
            if t in ram_types:
                types.add(ram_types[t])
            else:
                # Fallback to MemoryType if SMBIOSMemoryType is not helpful
                t2 = int(getattr(mem, "MemoryType", 0) or 0)
                types.add(ram_types.get(t2, f"Unknown({t2})"))
        return list(types)[0] if types else "Unknown"
    except Exception:
        return "Unknown"

def get_ram_info():
    ram_size = get_total_ram()
    ram_type = get_ram_type()
    return f"Total Ram installed : {ram_size}GB Ram {ram_type}"


