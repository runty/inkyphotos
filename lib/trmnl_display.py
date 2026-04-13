import gc
import struct

# 7-color ACeP display (black, white, red, green, blue, yellow, orange)
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_7 as DISPLAY


_graphics = None


def _get_graphics():
    global _graphics
    if _graphics is None:
        _graphics = PicoGraphics(DISPLAY)
        gc.collect()
    return _graphics


def _detect_format(filepath):
    """Detect image format by reading magic bytes from file header."""
    with open(filepath, "rb") as f:
        header = f.read(4)
    if header[:2] == b'BM':
        return "bmp"
    if header[:3] == b'\xff\xd8\xff':
        return "jpeg"
    # PNG magic: 0x89 P N G
    if header[:4] == b'\x89PNG':
        return "png"
    return "png"  # default fallback


def show_image(filepath):
    """Decode and display an image file from SD card.
    Supports PNG, JPEG, and 1-bit BMP. Detects format by magic bytes."""
    graphics = _get_graphics()
    fmt = _detect_format(filepath)

    if fmt == "png":
        from pngdec import PNG
        p = PNG(graphics)
        p.open_file(filepath)
        p.decode(0, 0)
    elif fmt == "jpeg":
        from jpegdec import JPEG
        j = JPEG(graphics)
        j.open_file(filepath)
        j.decode(0, 0)
    elif fmt == "bmp":
        _render_bmp(graphics, filepath)

    graphics.update()
    gc.collect()


def _render_bmp(graphics, filepath):
    """Manual parser for 1-bit monochrome BMP3 files (TRMNL standard format).
    Reads row-by-row to conserve RAM. BMP stores rows bottom-to-top."""
    WHITE = 15  # PicoGraphics pen index for white
    BLACK = 0   # PicoGraphics pen index for black

    with open(filepath, "rb") as f:
        # Read BMP file header (14 bytes)
        file_header = f.read(14)
        if file_header[0:2] != b'BM':
            return

        # Read DIB header (at least 40 bytes for BITMAPINFOHEADER)
        dib_header = f.read(40)
        width = struct.unpack('<i', dib_header[4:8])[0]
        height = struct.unpack('<i', dib_header[8:12])[0]
        bpp = struct.unpack('<H', dib_header[14:16])[0]

        # We only handle 1-bit BMPs
        if bpp != 1:
            return

        # Pixel data offset from file header
        pixel_offset = struct.unpack('<I', file_header[10:14])[0]
        f.seek(pixel_offset)

        # BMP rows are padded to 4-byte boundaries
        row_bytes = ((width + 31) // 32) * 4
        row_buf = bytearray(row_bytes)

        # Height can be negative (top-down) or positive (bottom-up)
        top_down = height < 0
        abs_height = abs(height)

        # Clear display to white
        graphics.set_pen(WHITE)
        graphics.clear()
        graphics.set_pen(BLACK)

        for row_idx in range(abs_height):
            f.readinto(row_buf)
            y = row_idx if top_down else (abs_height - 1 - row_idx)

            for x in range(width):
                byte_idx = x >> 3
                bit_idx = 7 - (x & 7)
                pixel_white = (row_buf[byte_idx] >> bit_idx) & 1
                if not pixel_white:
                    graphics.pixel(x, y)


def show_status(lines):
    """Display text lines on screen (for status/error messages)."""
    graphics = _get_graphics()
    graphics.set_pen(15)  # white
    graphics.clear()
    graphics.set_pen(0)   # black
    graphics.set_font("bitmap8")

    y = 20
    for line in lines:
        graphics.text(line, 10, y, scale=2)
        y += 30

    graphics.update()
    gc.collect()


def show_setup_screen(mac_address):
    """Display registration instructions with the device MAC address."""
    show_status([
        "TRMNL - Inky Frame 7.3",
        "",
        "Register this device at:",
        "  trmnl.com/claim-a-device",
        "",
        "Device MAC address:",
        "  " + mac_address,
        "",
        "Then press any button",
        "to continue.",
    ])
