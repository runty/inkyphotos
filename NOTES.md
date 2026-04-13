# Build notes

## Pico W WiFi gotchas

### Country code is mandatory

The Pico W CYW43 WiFi chip will silently fail to connect without `rp2.country('CA')` (or your country code). Connections return status -2 (NO_NET) even when the AP is visible in scans. Set via `WIFI_COUNTRY` in `secrets.py`.

### Power management causes drops

Disable with `wlan.config(pm=network.WLAN.PM_NONE)` after activating the interface.

### Flaky on cold boot

The WiFi chip sometimes fails to connect on the first attempt right after a machine.reset(). The connect function waits 1 second after activating the radio and retries up to 3 times with 2-second gaps. On total failure, sleeps 5 minutes then the full cycle restarts.

### WPA3/WPA2 mixed mode doesn't work

UniFi APs defaulting to WPA2/WPA3 (auth type 5 in scan results) cause connection failures. Must set the SSID to WPA2-only in the UniFi controller. This showed up as status -1 (CONNECT_FAIL) or -2 (NO_NET).

## Hardware gotchas

### Battery ADC conflicts with WiFi

GPIO29 (ADC3) shares the SPI clock with the wireless chip. Reading battery voltage while WiFi is active hangs the device. Must read before calling `wlan.active(True)`.

### sleep_for() doesn't loop on USB power

`inky_frame.sleep_for(minutes)` on USB power internally calls `time.sleep()` then returns — it doesn't reset the device. Added `machine.reset()` after the sleep call so `main.py` re-runs for the next cycle. On battery power, `sleep_for()` sets an RTC alarm and powers down, then the device cold-boots on wake.

## Software gotchas

### NTP timeout crashes the run if not caught

NTP can fail with ETIMEDOUT. If not caught, the RTC defaults to 2000-01-01 00:00 which looks like midnight to the quiet hours check, causing an immediate sleep until 6am. Fixed by only checking quiet hours when NTP succeeds.

### pngdec.decode() has no dither parameter on v1.26.1

The `dither=False` keyword argument isn't supported on this firmware version. If your image server pre-dithers to exact ACeP palette colors, the default dithering has no visible effect (zero error = nothing to diffuse).

### Display constant

Use `DISPLAY_INKY_FRAME_7` for the 7-color ACeP panel, not `DISPLAY_INKY_FRAME_SPECTRA_7` (which is for 6-color Spectra 6).
