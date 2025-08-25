#!/usr/bin/env python3
"""
Wedding QR Code Generator

Create a stylish QR code that links to a Google Photos album (or any URL).

Features
- High error correction (for reliability when printed)
- Custom colors (foreground + background)
- Optional centered logo (PNG/JPG with automatic rounding mask)
- Optional caption strip (e.g., names + date)
- Auto-detect dominant colors from logo
- Export both PNG and PDF

Dependencies
    pip install qrcode[pil] pillow

Usage
    python wedding_qr.py \
        --url "https://photos.app.goo.gl/YOUR_GOOGLE_PHOTOS_LINK" \
        --output qr_wedding.png \
        --fg "#222222" --bg "#fff9f2" \
        --logo path/to/logo.png \
        --caption "Nali & Kioni • 18 Aug 2025"

Tip: Print at 300 DPI. For an A6 card (105×148 mm), export at ~1240×1748 px or higher.
"""

from __future__ import annotations

import argparse
import sys
from typing import Tuple

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
except Exception as e:
    sys.stderr.write(
        "\nThis script requires the 'qrcode' package with Pillow support.\n"
        "Install with:  pip install qrcode[pil] pillow\n\n"
    )
    raise

from PIL import Image, ImageDraw, ImageFont


def parse_color(c: str) -> Tuple[int, int, int]:
    """Convert hex or rgb string to RGB tuple."""
    c = c.strip()
    if c.startswith("#"):
        c = c[1:]
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        if len(c) != 6:
            raise ValueError("Invalid hex color")
        return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
    if "," in c:
        parts = [int(x) for x in c.split(",")]
        if len(parts) != 3:
            raise ValueError("RGB must have 3 comma-separated numbers")
        return tuple(parts)
    raise ValueError("Use #RRGGBB or R,G,B format for colors")


def generate_qr(
    url: str,
    size: int = 1200,
    border: int = 4,
    fg: Tuple[int, int, int] = (0, 0, 0),
    bg: Tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """Generate a QR code image with given settings."""
    qr = qrcode.QRCode(
        version=None,  # let library choose minimal version that fits
        error_correction=ERROR_CORRECT_H,  # robust for logo overlay
        box_size=10,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg, back_color=bg).convert("RGBA")

    # Resize to requested size (exact square)
    img = img.resize((size, size), Image.LANCZOS)
    return img


def get_dominant_colors(img: Image.Image, num_colors: int = 3):
    """Return top N dominant colors from image."""
    small = img.resize((150, 150))
    result = small.convert("RGBA").quantize(colors=num_colors, method=2)
    palette = result.getpalette()
    color_counts = sorted(result.getcolors(), reverse=True)
    colors = []
    for count, idx in color_counts:
        r, g, b = palette[idx*3:idx*3+3]
        colors.append((r, g, b))
    return colors[:num_colors]


def add_logo(base: Image.Image, logo_path: str, scale: float = 0.2, round_ratio: float = 0.25) -> Image.Image:
    """Overlay a centered logo, scale down only if larger than fraction."""
    logo = Image.open(logo_path).convert("RGBA")

    # Extract dominant colors for later use
    dom_colors = get_dominant_colors(logo, 3)
    print("Dominant colors:", dom_colors)

    # compute target size
    target_w = int(base.width * scale)
    aspect = logo.width / logo.height

    # only shrink if logo is larger
    if logo.width > target_w:
        new_w = target_w
        new_h = int(target_w / aspect)
        logo = logo.resize((new_w, new_h), Image.LANCZOS)

    new_w, new_h = logo.size

    # rounded corners mask
    radius = int(min(new_w, new_h) * round_ratio)
    if radius > 0:
        mask = Image.new("L", (new_w, new_h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, new_w, new_h), radius=radius, fill=255)
        logo.putalpha(mask)

    # optional white pad behind logo
    pad = int(min(new_w, new_h) * 0.08)
    bg = Image.new("RGBA", (new_w + 2 * pad, new_h + 2 * pad), (255, 255, 255, 230))
    bg_mask = Image.new("L", bg.size, 0)
    ImageDraw.Draw(bg_mask).rounded_rectangle((0, 0, *bg.size), radius=radius + pad//2, fill=255)

    # center positions
    cx = (base.width - bg.width) // 2
    cy = (base.height - bg.height) // 2

    base.paste(bg, (cx, cy), bg_mask)
    base.paste(logo, (cx + pad, cy + pad), logo)
    return base


def add_caption_strip(
    base: Image.Image,
    caption: str,
    strip_height_ratio: float = 0.18,
    strip_bg: Tuple[int, int, int] = (255, 255, 255),
    text_color: Tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """Add a caption strip below the QR (names/date)."""
    w, h = base.size
    strip_h = int(h * strip_height_ratio)

    canvas = Image.new("RGBA", (w, h + strip_h), (*strip_bg, 255))
    canvas.paste(base, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Try to load a nice font; fall back to default if not available
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Avenir.ttc",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    font = None
    for path in font_candidates:
        try:
            font = ImageFont.truetype(path, size=int(strip_h * 0.38))
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Draw text centered
    text = caption
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    tx = (w - tw) // 2
    ty = h + (strip_h - th) // 2
    draw.line([(int(w*0.12), h), (int(w*0.88), h)], fill=(0, 0, 0, 40), width=2)
    draw.text((tx, ty), text, fill=text_color, font=font)

    return canvas


def main():
    p = argparse.ArgumentParser(description="Generate a wedding QR code for a Google Photos album (or any URL).")
    p.add_argument('--url', required=True, help='Link to Google Photos album (or any URL).')
    p.add_argument('--output', default='qr_wedding.png', help='Output image file (PNG recommended).')
    p.add_argument('--size', type=int, default=1200, help='Final square size in pixels (e.g., 1200, 2000).')
    p.add_argument('--border', type=int, default=4, help='Quiet zone border modules (default 4).')
    p.add_argument('--fg', default='#222222', help='Foreground color (#RRGGBB or R,G,B).')
    p.add_argument('--bg', default='#FFFFFF', help='Background color (#RRGGBB or R,G,B).')
    p.add_argument('--logo', default=None, help='Optional path to a logo image for the center.')
    p.add_argument('--caption', default=None, help='Optional caption (e.g., "Nali & Kioni • 18 Aug 2025").')
    p.add_argument('--strip-bg', default='#FFFFFF', help='Caption strip background color.')
    p.add_argument('--text-color', default='#000000', help='Caption text color.')
    p.add_argument('--logo-scale', type=float, default=0.20, help='Logo width as fraction of QR size (0.10–0.30 recommended).')
    p.add_argument('--logo-round', type=float, default=0.25, help='Logo corner rounding ratio (0–0.5).')

    args = p.parse_args()

    try:
        fg = parse_color(args.fg)
        bg = parse_color(args.bg)
        strip_bg = parse_color(args.strip_bg)
        text_color = parse_color(args.text_color)
    except Exception as e:
        p.error(str(e))

    img = generate_qr(args.url, size=args.size, border=args.border, fg=fg, bg=bg)

    if args.logo:
        img = add_logo(img, args.logo, scale=args.logo_scale, round_ratio=args.logo_round)

    if args.caption:
        img = add_caption_strip(img, args.caption, strip_bg=strip_bg, text_color=text_color)

    # Save PNG
    img.save(args.output, format='PNG')
    print(f"Saved: {args.output}")

    # Also export to PDF
    pdf_out = args.output.rsplit('.', 1)[0] + ".pdf"
    rgb_img = img.convert("RGB")
    rgb_img.save(pdf_out, "PDF", resolution=300.0)
    print(f"Saved PDF: {pdf_out}")


if __name__ == '__main__':
    main()
