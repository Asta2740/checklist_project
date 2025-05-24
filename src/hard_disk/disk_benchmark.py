import time
import os
import statistics
import shutil
import platform
import ctypes
import struct
import psutil  # For drive type detection (install with `pip install psutil`)

def init_benchmark_config():
    """Initialize and return benchmark configuration."""
    file_size = 1024 * 1024 * 1024  # 1 GiB
    block_size = 4 * 1024 * 1024    # 4 MiB block for NVMe/SATA
    num_passes = 5                  # Match CrystalDiskMark
    results_dir = 'C:\\benchmark_results'

    # Ensure the directory exists
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    file_path = os.path.join(results_dir, 'test_file.dat')
    print(f"Test file path: {file_path}")

    # Windows-specific flags
    FILE_FLAG_NO_BUFFERING = None
    FILE_FLAG_WRITE_THROUGH = None
    kernel32 = None
    if platform.system() == "Windows":
        FILE_FLAG_NO_BUFFERING = 0x20000000
        FILE_FLAG_WRITE_THROUGH = 0x80000000
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    return {
        "file_size": file_size,
        "block_size": block_size,
        "num_passes": num_passes,
        "results_dir": results_dir,
        "file_path": file_path,
        "FILE_FLAG_NO_BUFFERING": FILE_FLAG_NO_BUFFERING,
        "FILE_FLAG_WRITE_THROUGH": FILE_FLAG_WRITE_THROUGH,
        "kernel32": kernel32
    }

# Update all functions to use config
def check_disk_space(drive_path, file_size, num_passes):
    """Check if there's enough free space on the disk."""
    total, used, free = shutil.disk_usage(os.path.dirname(drive_path))
    if free < file_size * num_passes:
        raise RuntimeError(f"Not enough disk space. Required: {file_size * num_passes / (1024**3):.2f} GiB, Available: {free / (1024**3):.2f} GiB")
    return free / (1024**3)

def get_drive_type(drive_path):
    """Detect drive type (simplified)."""
    if platform.system() != "Windows":
        return "Unknown (Non-Windows)"
    drive = os.path.splitdrive(drive_path)[0]
    for partition in psutil.disk_partitions():
        if partition.device.startswith(drive):
            return partition.fstype
    return "Unknown"

def align_buffer(size):
    """Create a buffer aligned to sector size (4096 bytes)."""
    sector_size = 4096
    aligned_size = ((size + sector_size - 1) // sector_size) * sector_size
    return ctypes.create_string_buffer(aligned_size)

def write_test_windows(config):
    """Write test using direct I/O on Windows."""
    hFile = config["kernel32"].CreateFileW(
        config["file_path"],
        0x40000000,  # GENERIC_WRITE
        0,           # No sharing
        None,
        2,           # CREATE_ALWAYS
        config["FILE_FLAG_NO_BUFFERING"] | config["FILE_FLAG_WRITE_THROUGH"],
        None
    )
    if hFile == -1:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        buffer = align_buffer(config["block_size"])
        bytes_written = ctypes.c_uint32()
        start_time = time.perf_counter()
        for _ in range(config["file_size"] // config["block_size"]):
            config["kernel32"].WriteFile(hFile, buffer, config["block_size"], ctypes.byref(bytes_written), None)
            if bytes_written.value != config["block_size"]:
                raise RuntimeError("Incomplete write")
        config["kernel32"].FlushFileBuffers(hFile)
        end_time = time.perf_counter()
        return config["file_size"] / (end_time - start_time) / (1024 * 1024)
    finally:
        config["kernel32"].CloseHandle(hFile)

def read_test_windows(config):
    """Read test using direct I/O on Windows."""
    hFile = config["kernel32"].CreateFileW(
        config["file_path"],
        0x80000000,  # GENERIC_READ
        0,
        None,
        3,           # OPEN_EXISTING
        config["FILE_FLAG_NO_BUFFERING"],
        None
    )
    if hFile == -1:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        buffer = align_buffer(config["block_size"])
        bytes_read = ctypes.c_uint32()
        start_time = time.perf_counter()
        for _ in range(config["file_size"] // config["block_size"]):
            config["kernel32"].ReadFile(hFile, buffer, config["block_size"], ctypes.byref(bytes_read), None)
            if bytes_read.value != config["block_size"]:
                raise RuntimeError("Incomplete read")
        end_time = time.perf_counter()
        return config["file_size"] / (end_time - start_time) / (1024 * 1024)
    finally:
        config["kernel32"].CloseHandle(hFile)

def write_test_fallback(config):
    """Fallback write test for non-Windows."""
    start_time = time.perf_counter()
    with open(config["file_path"], 'wb') as f:
        buffer = b'\0' * config["block_size"]
        for _ in range(config["file_size"] // config["block_size"]):
            f.write(buffer)
        f.flush()
        os.fsync(f.fileno())
    end_time = time.perf_counter()
    return config["file_size"] / (end_time - start_time) / (1024 * 1024)

def read_test_fallback(config):
    """Fallback read test for non-Windows."""
    start_time = time.perf_counter()
    with open(config["file_path"], 'rb') as f:
        while f.read(config["block_size"]):
            pass
    end_time = time.perf_counter()
    return config["file_size"] / (end_time - start_time) / (1024 * 1024)

def run_benchmark():
    """Run benchmark and return average speeds as a single string."""
    config = init_benchmark_config()
    check_disk_space(config["file_path"], config["file_size"], config["num_passes"])
    write_speeds = []
    read_speeds = []

    print(f"Running {config['num_passes']} passes with {config['file_size'] / (1024**3):.2f} GiB file...")
    
    for i in range(config["num_passes"]):
        current_file = f"{config['file_path']}.{i}"
        config["file_path"] = current_file  # Update file_path for this pass
        print(f"Pass {i+1}/{config['num_passes']}: Write test...")
        try:
            if platform.system() == "Windows":
                write_speed = write_test_windows(config)
            else:
                write_speed = write_test_fallback(config)
            write_speeds.append(write_speed)
            print(f"Write speed: {write_speed:.2f} MB/s")
        except Exception as e:
            print(f"Write test failed: {e}")
            return None

        print(f"Pass {i+1}/{config['num_passes']}: Read test...")
        try:
            if platform.system() == "Windows":
                read_speed = read_test_windows(config)
            else:
                read_speed = read_test_fallback(config)
            read_speeds.append(read_speed)
            print(f"Read speed: {read_speed:.2f} MB/s")
        except Exception as e:
            print(f"Read test failed: {e}")
            return None

        if os.path.exists(current_file):
            os.remove(current_file)

    avg_write = statistics.mean(write_speeds) if write_speeds else 0
    avg_read = statistics.mean(read_speeds) if read_speeds else 0
    return f"Average Write Speed: {avg_write:.2f} MB/s\nAverage Read Speed: {avg_read:.2f} MB/s"

def Hard_Disk_check():
    config = init_benchmark_config()
    if not os.path.exists(config["results_dir"]):
        os.makedirs(config["results_dir"])

    print("Disk Benchmark (Sequential Read/Write)")
    print(f"Test file: {config['file_path']}")
    print(f"File size: {config['file_size'] / (1024**3):.2f} GiB")
    print(f"Block size: {config['block_size'] / (1024**2):.2f} MiB")
    print(f"Number of passes: {config['num_passes']}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Drive type: {get_drive_type(config['file_path'])}")
    print(f"Free space: {check_disk_space(config['file_path'], config['file_size'], config['num_passes']):.2f} GiB\n")

    try:
        result = run_benchmark()
        if result:
            return result  # Return the single string
        else:
            return "Benchmark failed."
    except Exception as e:
        return f"Benchmark failed: {e}"
    finally:
        if os.path.exists(config["results_dir"]) and not os.listdir(config["results_dir"]):
            os.rmdir(config["results_dir"])