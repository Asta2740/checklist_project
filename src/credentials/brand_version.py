import subprocess

def get_brand_and_version():
    # First attempt: WMIC csproduct get Name
    try:
        result = subprocess.run(
            ['wmic', 'csproduct', 'get', 'Name'],
            capture_output=True, text=True, check=True
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        brand = lines[1] if len(lines) >= 2 and lines[1].upper() != 'NAME' else "N/A"
    except Exception:
        brand = "N/A"

    # Fallback: WMIC csproduct get Version
    try:
        result = subprocess.run(
            ['wmic', 'csproduct', 'get', 'Version'],
            capture_output=True, text=True, check=True
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        version = lines[1] if len(lines) >= 2 and lines[1].upper() != 'VERSION' else "N/A"
    except Exception:
        version = "N/A"

    # Combine Brand and Version
    return f"{brand} {version}"