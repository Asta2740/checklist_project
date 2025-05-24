import asyncio
from bleak import BleakScanner

async def _ble_scan(timeout: float = 5.0):
    """
    Perform a BLE scan for `timeout` seconds and return a list of devices.
    """
    return await BleakScanner.discover(timeout)

def check_bluetooth_scan(timeout: float = 5.0):
    """
    Check if the local Bluetooth adapter can scan for BLE devices.

    Returns:
        (bool, list|str):
          - True, [(address, name), …] on success
          - False, error message on failure
    """
    try:
        devices = asyncio.run(_ble_scan(timeout))
        # Format results as (address, name) tuples
        found = [(d.address, d.name or "<unknown>") for d in devices]
        return True, found
    except Exception as e:
        # e.g. adapter off, permissions, backend issues
        return False, str(e)

