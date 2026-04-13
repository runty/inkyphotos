import machine
import time


def read_battery_voltage():
    """Read battery voltage via ADC3 (GPIO29).
    MUST be called BEFORE WiFi is activated — GPIO29 shares the SPI clock
    with the wireless chip, so reading it while WiFi is active will hang.
    Returns voltage as float (typical: 3.0-4.2V LiPo, ~4.5V 3xAA)."""
    adc = machine.ADC(3)
    raw = adc.read_u16()
    # VSYS is divided by 3 before reaching the ADC
    voltage = raw * 3.0 * 3.3 / 65535
    voltage = round(voltage, 2)
    # On USB power with no battery, ADC reads near 0.
    # Report 5.0V to avoid triggering low-battery screens.
    if voltage < 1.0:
        return 5.0
    return voltage


def deep_sleep(seconds):
    """Enter deep sleep for the given number of seconds.
    Converts to minutes for inky_frame.sleep_for() (1-minute resolution).
    On USB power, sleep_for() falls back to time.sleep() automatically."""
    import inky_frame

    if seconds < 60:
        # Sub-minute: use blocking sleep (only works on USB power;
        # on battery, minimum is 1 minute via RTC)
        time.sleep(seconds)
        machine.reset()
    else:
        minutes = seconds // 60
        minutes = max(1, min(minutes, 40320))  # 1 min to 28 days
        inky_frame.sleep_for(minutes)
        # On USB power, sleep_for() blocks via time.sleep() then returns.
        # Reset to re-run main.py for the next cycle.
        machine.reset()
