#!/usr/bin/env python3
"""Generate PWA icons"""
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install: pip3 install Pillow")
    exit(1)

for size in [192, 512]:
    img = Image.new('RGBA', (size, size), (8, 8, 14, 255))
    draw = ImageDraw.Draw(img)
    
    # Gradient-like effect with simple shapes
    box_margin = size // 6
    draw.rounded_rectangle(
        [box_margin, box_margin, size - box_margin, size - box_margin],
        radius=size // 5,
        fill=(74, 124, 255, 230)
    )
    
    # Inner accent
    inner = size // 3
    draw.rounded_rectangle(
        [inner, inner, size - inner, size - inner],
        radius=size // 8,
        fill=(124, 58, 237, 200)
    )
    
    # Text
    try:
        font_size = size // 3
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw "文" character
    draw.text((size // 2, size // 2), "文", fill=(255, 255, 255, 255),
              font=font, anchor="mm")
    
    path = f"/home/agentuser/.hermes/skills/novel-writing-workbench/static/icon-{size}.png"
    img.save(path)
    print(f"✅ Saved {path} ({size}x{size})")
