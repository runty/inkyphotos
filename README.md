# inkyphotos

A WiFi photo frame for the [Pimoroni Inky Frame 7.3"](https://shop.pimoroni.com/products/inky-frame-7-3) color e-ink display.

Fetches images from a configurable URL, renders them on the 7-color ACeP e-ink panel (800x480, 5:3), and sleeps for an hour before fetching the next one. Quiet hours (10pm-6am) are respected — no updates overnight.

Designed to work with [trmnl-photos](https://github.com/runty/trmnl-photos), which serves pre-dithered photos sized for this display.

## Hardware

- Pimoroni Inky Frame 7.3" — 7-color ACeP (black, white, red, green, blue, yellow, orange)
- Raspberry Pi Pico W (RP2040) with 8MB PSRAM
- FAT-formatted microSD card (required)

## Setup

### 1. Flash firmware

Download the latest Pimoroni MicroPython firmware from [pimoroni/inky-frame releases](https://github.com/pimoroni/inky-frame/releases). Use the `pico_w_inky-*-with-filesystem.uf2` build.

Hold BOOT, tap RESET, copy the `.uf2` to the `RPI-RP2` drive.

### 2. Configure

Copy `secrets.py.example` to `secrets.py` and fill in your details:

```python
WIFI_SSID = "your_network"
WIFI_PASSWORD = "your_password"
WIFI_COUNTRY = "CA"  # required for Pico W
PHOTO_URL = "http://your-server:8099/random?w=800&h=480&palette=7color"
```

### 3. Deploy

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

Insert a FAT-formatted microSD card and press reset.

## How it works

On each cycle the device:

1. Reads battery voltage (before WiFi — GPIO29 shares SPI with the radio)
2. Connects to WiFi (with retry, up to 3 attempts)
3. Syncs time via NTP
4. Checks quiet hours (10pm-6am) — if so, sleeps until 6am
5. Downloads image from `PHOTO_URL` to the SD card
6. Renders image on the 7-color e-ink display
7. Sleeps for 1 hour, then resets and repeats

## Notes

See [NOTES.md](NOTES.md) for Pico W gotchas discovered during development (WiFi country codes, WPA3 issues, ADC conflicts, sleep behavior, etc).

## License

MIT
