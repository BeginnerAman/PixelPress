"""
generate_icon.py
================
Generates the official Aperture / Shutter Camera Lens icon.ico for PixelPress.
Matches the in-app branding logo 100%.
"""

import os
import math
from PIL import Image, ImageDraw

SIZES = [256, 128, 64, 48, 32, 16]

def make_aperture_frame(size):
    """Draw a high-resolution antialiased aperture icon frame at a given size."""
    # Render at 4x resolution for super crisp antialiasing, then downsample
    scale = 4
    canvas_size = size * scale
    img = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = int(canvas_size * 0.08)
    radius = int(canvas_size * 0.22)
    box = [pad, pad, canvas_size - pad, canvas_size - pad]

    # Background rounded container: Dark sleek aesthetic (#111218)
    bg_color = (17, 18, 26, 255)
    border_color = (124, 106, 255, 120)
    border_width = max(2, int(canvas_size * 0.02))

    try:
        draw.rounded_rectangle(box, radius=radius, fill=bg_color, outline=border_color, width=border_width)
    except AttributeError:
        draw.rectangle(box, fill=bg_color, outline=border_color, width=border_width)

    # Center coordinates and radius for the aperture
    cx = canvas_size / 2.0
    cy = canvas_size / 2.0
    r = (canvas_size - 2 * pad) * 0.38
    stroke_w = max(2, int(canvas_size * 0.045))
    accent_color = (124, 106, 255, 255)
    accent_glow = (160, 145, 255, 255)

    # Outer circle of aperture
    circle_box = [cx - r, cy - r, cx + r, cy + r]
    draw.ellipse(circle_box, outline=accent_color, width=stroke_w)

    # 6 Aperture Shutter Blades (geometry matching the SVG aperture symbol)
    # The SVG points scaled to circle of radius r:
    # 6 lines tangent/offset from a central hexagon
    num_blades = 6
    inner_r = r * 0.42
    for i in range(num_blades):
        angle = (i * 2.0 * math.pi / num_blades) - (math.pi / 6.0)
        # Inner vertex
        x1 = cx + inner_r * math.cos(angle)
        y1 = cy + inner_r * math.sin(angle)
        # Outer intersection with the outer circle
        outer_angle = angle + 0.95
        x2 = cx + r * math.cos(outer_angle)
        y2 = cy + r * math.sin(outer_angle)
        draw.line([(x1, y1), (x2, y2)], fill=accent_color, width=stroke_w)

    # Center dot / lens shine
    dot_r = max(2, int(canvas_size * 0.035))
    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=(34, 197, 94, 255))

    # Downsample with high-quality LANCZOS to final icon frame size
    return img.resize((size, size), Image.LANCZOS)


def generate_icon(output_path='icon.ico'):
    frames = [make_aperture_frame(s) for s in SIZES]
    frames[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in SIZES],
        append_images=frames[1:],
    )
    print(f"✓ Official Aperture Icon saved: {os.path.abspath(output_path)}")
    print(f"  Generated sizes: {SIZES}")


if __name__ == '__main__':
    generate_icon()
