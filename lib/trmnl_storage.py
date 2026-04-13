import machine
import os
import json


MOUNT_POINT = "/sd"
STATE_FILE = MOUNT_POINT + "/state.json"

_sd = None
_mounted = False

# Inky Frame 7.3 SD card SPI pins
_SD_SPI_ID = 0
_SD_SCK = 18
_SD_MOSI = 19
_SD_MISO = 16
_SD_CS = 22

DEFAULT_STATE = {
    "api_key": "",
    "friendly_id": "",
    "last_image_name": "",
    "refresh_rate": 900,
    "error_count": 0,
}


def mount():
    """Mount SD card. Returns True on success."""
    global _sd, _mounted
    if _mounted:
        return True
    try:
        import sdcard
        sd_spi = machine.SPI(
            _SD_SPI_ID,
            sck=machine.Pin(_SD_SCK),
            mosi=machine.Pin(_SD_MOSI),
            miso=machine.Pin(_SD_MISO),
        )
        _sd = sdcard.SDCard(sd_spi, machine.Pin(_SD_CS))
        os.mount(_sd, MOUNT_POINT)
        _mounted = True
        return True
    except Exception:
        _mounted = False
        return False


def unmount():
    """Unmount SD card."""
    global _mounted
    try:
        os.umount(MOUNT_POINT)
    except Exception:
        pass
    _mounted = False


def is_mounted():
    return _mounted


def load_state():
    """Load persisted state from SD card. Returns dict with defaults for missing keys."""
    state = dict(DEFAULT_STATE)
    try:
        with open(STATE_FILE, "r") as f:
            saved = json.load(f)
        state.update(saved)
    except (OSError, ValueError):
        pass
    return state


def save_state(state):
    """Persist device state as JSON to SD card."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def file_exists(path):
    """Check if a file exists."""
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def rename_file(src, dst):
    """Rename/move a file. Removes dst first if it exists."""
    try:
        os.remove(dst)
    except OSError:
        pass
    try:
        os.rename(src, dst)
    except OSError:
        pass
