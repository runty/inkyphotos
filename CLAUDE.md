# inkyphotos

WiFi photo frame for the Pimoroni Inky Frame 7.3" (7-color ACeP e-ink display, 800x480, Raspberry Pi Pico W).

## How it works

MicroPython wake-fetch-display-sleep loop:
1. Wake from deep sleep (or machine.reset on USB power)
2. Connect WiFi (country code required, retries 3x)
3. Sync time via NTP
4. If quiet hours (10pm-6am), sleep until 6am
5. Fetch image from PHOTO_URL (set in secrets.py)
6. Save to SD card, render on e-ink display
7. Sleep for 1 hour, repeat

## Key files

- `main.py` — the main loop, deployed to the Pico as `main.py`
- `secrets.py` — user config (gitignored), see `secrets.py.example`
- `lib/trmnl_network.py` — WiFi with country code, PM_NONE, 3x retry
- `lib/trmnl_display.py` — image rendering (PNG/JPEG/BMP by magic bytes)
- `lib/trmnl_power.py` — battery ADC (before WiFi!) + deep sleep wrapper
- `lib/trmnl_storage.py` — SD card mount + JSON state persistence

## Pico W gotchas

- `WIFI_COUNTRY` is mandatory or connections silently fail
- Battery ADC (GPIO29) shares SPI with WiFi — read before wlan.active(True)
- `inky_frame.sleep_for()` on USB power just blocks then returns — need machine.reset() after
- WiFi can fail on first attempt after cold boot — retry logic handles this
- WPA2/WPA3 mixed mode on UniFi doesn't work — use WPA2 only
- NTP can timeout — skip quiet hours check if NTP fails
- Display constant is `DISPLAY_INKY_FRAME_7` (7-color ACeP), not `DISPLAY_INKY_FRAME_SPECTRA_7`

## Deploying to Pico

```bash
pipx install mpremote
mpremote cp secrets.py :secrets.py
mpremote cp main.py :main.py
mpremote mkdir lib
mpremote cp lib/trmnl_display.py :lib/trmnl_display.py
mpremote cp lib/trmnl_network.py :lib/trmnl_network.py
mpremote cp lib/trmnl_power.py :lib/trmnl_power.py
mpremote cp lib/trmnl_storage.py :lib/trmnl_storage.py
```

## Firmware

Pimoroni MicroPython: `pico_w_inky-*-with-filesystem.uf2` from https://github.com/pimoroni/inky-frame/releases
