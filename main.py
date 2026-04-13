import gc
import machine
import time
import inky_frame

gc.collect()

from lib.trmnl_power import read_battery_voltage, deep_sleep
battery_voltage = read_battery_voltage()

from lib.trmnl_network import connect, disconnect, set_country
from lib.trmnl_storage import mount, MOUNT_POINT
from lib.trmnl_display import show_image, show_status

gc.collect()

REFRESH_SECONDS = 3600  # 1 hour
IMG_PATH = MOUNT_POINT + "/photo.img"
QUIET_START = 22  # 10pm
QUIET_END = 6     # 6am
UTC_OFFSET = -7   # PDT (adjust for your timezone)


def _seconds_until_quiet_ends():
    """Calculate seconds from now until QUIET_END. Assumes RTC is set to UTC."""
    _, _, _, hour, minute, _, _, _ = time.localtime()
    local_hour = (hour + UTC_OFFSET) % 24
    if local_hour < QUIET_END:
        return (QUIET_END - local_hour) * 3600 - minute * 60
    # Past quiet end already (shouldn't be called), return 1 hour
    return 3600


def _in_quiet_hours():
    """Check if current local time is in quiet hours (10pm-6am)."""
    _, _, _, hour, minute, _, _, _ = time.localtime()
    local_hour = (hour + UTC_OFFSET) % 24
    if QUIET_START <= local_hour or local_hour < QUIET_END:
        return True
    return False


def run():
    try:
        import secrets
        ssid = secrets.WIFI_SSID
        password = secrets.WIFI_PASSWORD
        country = getattr(secrets, "WIFI_COUNTRY", "")
        photo_url = getattr(secrets, "PHOTO_URL", "")
    except ImportError:
        show_status(["Missing secrets.py!"])
        return

    if not photo_url:
        show_status(["Missing PHOTO_URL", "in secrets.py!"])
        return

    if not mount():
        show_status(["SD card error!", "", "Insert a FAT-formatted", "microSD card and reset."])
        return

    if country:
        set_country(country)

    # Connect WiFi (need NTP for time check)
    inky_frame.led_wifi.on()
    if not connect(ssid, password, timeout=20):
        inky_frame.led_wifi.off()
        show_status(["WiFi connection failed!"])
        deep_sleep(300)
        return

    # Sync time via NTP
    ntp_ok = False
    try:
        import ntptime
        ntptime.settime()
        ntp_ok = True
    except Exception:
        pass

    inky_frame.led_wifi.off()

    # Skip update during quiet hours (10pm-6am), only if we have valid time
    if ntp_ok and _in_quiet_hours():
        disconnect()
        sleep_secs = _seconds_until_quiet_ends()
        deep_sleep(max(sleep_secs, 60))
        return

    inky_frame.led_busy.on()
    import urequests
    try:
        r = urequests.get(photo_url)
        with open(IMG_PATH, "wb") as f:
            f.write(r.content)
        r.close()
        gc.collect()
        ok = True
    except Exception:
        ok = False
    gc.collect()

    disconnect()

    if ok:
        show_image(IMG_PATH)
    else:
        show_status(["Download failed!", "", "Retrying in 5 min..."])
        inky_frame.led_busy.off()
        deep_sleep(300)
        return

    inky_frame.led_busy.off()
    deep_sleep(REFRESH_SECONDS)


try:
    run()
except Exception as e:
    import sys, io
    buf = io.StringIO()
    sys.print_exception(e, buf)
    lines = ["ERROR:", ""] + buf.getvalue().split("\n")[:8]
    try:
        show_status(lines)
    except Exception:
        pass
    deep_sleep(900)
