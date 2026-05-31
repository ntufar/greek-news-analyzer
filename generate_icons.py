#!/usr/bin/env python3
"""Generate PWA icons using the new logo design (SVG → PNG via cairosvg)"""

import os
import cairosvg

ICON_SIZES = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512]
TARGET_DIRS = ['static/icons', 'api/static/icons']

LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1e3c72"/>
      <stop offset="100%" stop-color="#2a5298"/>
    </linearGradient>
    <linearGradient id="gauge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ef4444"/>
      <stop offset="30%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#22c55e"/>
    </linearGradient>
  </defs>
  <rect x="10" y="10" width="300" height="300" rx="65" fill="url(#bg)"/>
  <path d="M50 240 A110 110 0 0 1 270 240" fill="none" stroke="url(#gauge)" stroke-width="14" stroke-linecap="round"/>
  <text x="160" y="170" text-anchor="middle" font-size="110" font-weight="900" fill="#fff" font-family="Georgia,'Times New Roman',serif">Α</text>
  <text x="252" y="135" text-anchor="middle" font-size="46" font-weight="900" fill="#22c55e" font-family="sans-serif">87</text>
  <text x="252" y="152" text-anchor="middle" font-size="11" font-weight="600" fill="#fff" font-family="sans-serif" opacity="0.5">ΒΑΘΜΟΣ</text>
  <path d="M195 216 L212 233 L255 188" fill="none" stroke="#22c55e" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="160" y="290" text-anchor="middle" font-size="16" font-weight="800" fill="#fbbf24" font-family="sans-serif" letter-spacing="2">ΑΝΑΛΥΣΗ ΕΙΔΗΣΕΩΝ</text>
</svg>'''


def generate_icons():
    for dir_path in TARGET_DIRS:
        os.makedirs(dir_path, exist_ok=True)

    for size in ICON_SIZES:
        png_bytes = cairosvg.svg2png(
            bytestring=LOGO_SVG.encode('utf-8'),
            output_width=size,
            output_height=size,
        )
        for dir_path in TARGET_DIRS:
            filename = f'{dir_path}/icon-{size}x{size}.png'
            with open(filename, 'wb') as f:
                f.write(png_bytes)
            print(f'  ✓ {filename} ({size}x{size})')

    print('\n✅ All icons generated successfully!')


if __name__ == '__main__':
    generate_icons()
