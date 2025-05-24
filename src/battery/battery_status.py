import psutil
import win32com.client

# Initialize the Results variable
Battery_results = ""

def get_battery_status():
    global Battery_results
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            Battery_results += "No battery information available.\n"
            return

        try:
            percent = battery.percent
        except Exception:
            percent = "Unknown"
            Battery_results += "Could not retrieve battery percentage.\n"

        try:
            plugged = battery.power_plugged
        except Exception:
            plugged = "Unknown"
            Battery_results += "Could not retrieve plugged-in status.\n"

        try:
            secs_left = battery.secsleft
            if secs_left == psutil.POWER_TIME_UNLIMITED:
                time_left = "Unlimited (Plugged In)"
                total_time = "Unlimited"
            elif secs_left == psutil.POWER_TIME_UNKNOWN or secs_left < 0:
                time_left = "Unknown (System can't estimate time)"
                total_time = "Unknown"
            else:
                hours = secs_left // 3600
                minutes = round((secs_left % 3600) / 60)
                if minutes == 60:
                    hours += 1
                    minutes = 0
                time_left = f"{hours}h {minutes}m"
                # Calculate total time if percent is known and not zero
                if isinstance(percent, (int, float)) and percent > 0:
                    total_secs = secs_left / (percent / 100)
                    total_hours = int(total_secs // 3600)
                    total_minutes = int(round((total_secs % 3600) / 60))
                    if total_minutes == 60:
                        total_hours += 1
                        total_minutes = 0
                    total_time = f"{total_hours}h {total_minutes}m"
                else:
                    total_time = "Unknown"
        except Exception:
            time_left = "Unknown"
            total_time = "Unknown"
            Battery_results += "Could not retrieve estimated time left.\n"

        Battery_results += f"Battery: {percent}%\n"
        Battery_results += f"Plugged In: {'Yes' if plugged else 'No'}\n"
        Battery_results += f"Estimated Time Left: {time_left}\n"
        Battery_results += f"Total Time (Full Discharge): {total_time}\n"
        return Battery_results
    except Exception:
        Battery_results += "Could not retrieve battery status.\n"
        return Battery_results



