#!/usr/bin/env python3
"""
Simple icon generator for PWA
Creates basic icons from a simple text-based design
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the specified size"""
    # Create a new image with a gradient background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for i in range(size):
        color_ratio = i / size
        r = int(30 + (102 - 30) * color_ratio)  # 1e3c72 to 667eea
        g = int(60 + (126 - 60) * color_ratio)
        b = int(114 + (234 - 114) * color_ratio)
        draw.line([(0, i), (size, i)], fill=(r, g, b, 255))
    
    # Draw a simple newspaper icon
    # Main rectangle
    margin = size // 8
    draw.rectangle([margin, margin, size-margin, size-margin], 
                   fill=(255, 255, 255, 200), outline=(0, 0, 0, 255), width=2)
    
    # Text lines
    line_height = size // 12
    for i in range(3):
        y = margin + size // 6 + i * line_height
        draw.rectangle([margin + size // 10, y, size - margin - size // 10, y + line_height // 3], 
                       fill=(0, 0, 0, 255))
    
    # Add a small "GR" text
    try:
        font_size = size // 8
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "GR"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = size - margin - text_height
    draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Generate all required icon sizes"""
    # Create icons directory if it doesn't exist
    os.makedirs('static/icons', exist_ok=True)
    
    # Generate all required icon sizes
    sizes = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        filename = f'static/icons/icon-{size}x{size}.png'
        create_icon(size, filename)
    
    print("✅ All icons generated successfully!")
    print("📱 Your app is now ready for mobile installation!")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
        main()
    except ImportError:
        print("❌ PIL (Pillow) is required to generate icons")
        print("Install it with: pip install Pillow")
        print("Or create simple placeholder icons manually")
