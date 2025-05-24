import psutil
import math
from screeninfo import get_monitors
import math

def get_screen_size():
    """
    Get the screen size of the primary monitor in inches.
    The function calculates the diagonal size based on the width and height in millimeters.
    """
    ScreenSize = "Screen Size: Unknown"
    
    # Check if the screeninfo library is available
    try:
        # Get list of all connected monitors
        monitors = get_monitors()
        # Find the primary monitor (typically the laptop's built-in screen)
        primary_monitor = next((m for m in monitors if m.x == 0 and m.y == 0), None)
        
        if primary_monitor:
            # Get physical width and height in millimeters
            width_mm = primary_monitor.width_mm
            height_mm = primary_monitor.height_mm
            
            # Convert millimeters to inches (1 inch = 25.4 mm)
            width_inch = width_mm / 25.4
            height_inch = height_mm / 25.4
            
            # Calculate diagonal size using the Pythagorean theorem
            diagonal_inch = math.sqrt(width_inch**2 + height_inch**2)
            
            # Round up to the nearest whole number
            rounded_diagonal = math.ceil(diagonal_inch)
            
            # Output both the precise and rounded-up results
            ScreenSize = f"Screen Size: {diagonal_inch:.2f} inch (precise)"
            return f"Screen Size: {rounded_diagonal} inch (rounded up)"
        else:
            print("Could not find the primary monitor.")
            return "Screen Size: Unknown"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Screen Size: Unknown"

