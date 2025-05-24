import psutil
import win32com.client

# Initialize the Results variable
Battery_results = ""

def get_battery_wear_level_windows():
    global Battery_results
    try:
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\WMI")
        try:
            batteries = service.ExecQuery("Select * from BatteryFullChargedCapacity")
            for battery in batteries:
                full_charge = battery.FullChargedCapacity
        except Exception:
            full_charge = None
            Battery_results += "Could not retrieve full charge capacity.\n"

        try:
            batteries = service.ExecQuery("Select * from BatteryStaticData")
            for battery in batteries:
                designed_capacity = battery.DesignedCapacity
        except Exception:
            designed_capacity = None
            Battery_results += "Could not retrieve designed capacity.\n"

        if full_charge is not None and designed_capacity is not None:
            try:
                wear_level = 100 - ((full_charge / designed_capacity) * 100)
                Battery_results += f"Wear Level: {wear_level:.2f}%\n"
            except Exception:
                Battery_results += "Could not calculate wear level.\n"
        else:
            Battery_results += "Wear level calculation skipped due to missing data.\n"
        return Battery_results
    except Exception:
        Battery_results += "Could not retrieve battery wear level.\n"
        return Battery_results
