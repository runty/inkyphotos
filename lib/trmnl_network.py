import network
import time
import ubinascii
import rp2


_wlan = None


def _get_wlan():
    global _wlan
    if _wlan is None:
        _wlan = network.WLAN(network.STA_IF)
    return _wlan


def set_country(code="CA"):
    """Set WiFi regulatory country code. Must be called before connect()."""
    rp2.country(code)


def get_mac_address():
    """Return MAC address as colon-separated uppercase hex string.
    Can be called before connect() — only needs the interface activated."""
    wlan = _get_wlan()
    was_active = wlan.active()
    if not was_active:
        wlan.active(True)
    mac = ubinascii.hexlify(wlan.config('mac'), ':').decode().upper()
    if not was_active:
        wlan.active(False)
    return mac


def connect(ssid, password, timeout=20, retries=3):
    """Connect to WiFi with retries. Returns True on success, False on failure."""
    wlan = _get_wlan()
    wlan.active(True)
    time.sleep(1)
    wlan.config(pm=network.WLAN.PM_NONE)

    if wlan.isconnected():
        return True

    for attempt in range(retries):
        wlan.connect(ssid, password)
        deadline = time.time() + timeout
        while not wlan.isconnected():
            if time.time() >= deadline:
                break
            status = wlan.status()
            if status < 0:
                break
            time.sleep(0.5)

        if wlan.isconnected():
            return True

        wlan.disconnect()
        time.sleep(2)

    return False


def disconnect():
    """Disconnect WiFi and deactivate interface to save power."""
    wlan = _get_wlan()
    try:
        wlan.disconnect()
    except Exception:
        pass
    wlan.active(False)


def get_rssi():
    """Return WiFi signal strength (RSSI) as int. Only valid when connected."""
    wlan = _get_wlan()
    if wlan.isconnected():
        return wlan.status('rssi')
    return 0


def is_connected():
    """Check if WiFi is currently connected."""
    return _get_wlan().isconnected()
