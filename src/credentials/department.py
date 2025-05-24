import subprocess

def get_department():
    # Based on COMPUTERNAME split on '-'
    try:
        result = subprocess.run(
            ['cmd', '/C', 'echo', '%COMPUTERNAME%'],
            capture_output=True, text=True, check=True
        )
        name = result.stdout.strip()
        return name.split('-', 1)[0] if '-' in name else name
    except Exception:
        return "N/A"