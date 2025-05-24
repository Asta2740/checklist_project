import subprocess

def get_serial_number():
    # First attempt: WMIC
    try:
        result = subprocess.run(
            ['wmic', 'bios', 'get', 'SerialNumber'],
            capture_output=True, text=True, check=True
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        if len(lines) >= 2 and lines[1].upper() != 'SERIALNUMBER':
            return lines[1]
    except Exception:
        pass

    # Fallback: PowerShell Get-CimInstance
    try:
        ps_cmd = [
            'powershell', '-NoProfile', '-Command',
            "Get-CimInstance -ClassName Win32_BIOS | Select-Object -ExpandProperty SerialNumber"
        ]
        result = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
        serial = result.stdout.strip()
        if serial:
            return serial
    except Exception:
        pass

    return "N/A"