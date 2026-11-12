#!/usr/bin/env python3
"""Zoom helper. Usage: zoom.py IMG_6231 x0 y0 x1 y1 [rotate_cw_degrees] -> writes a zoomed JPEG and prints its path.
Coordinates are FRACTIONS (0..1) of the upright full photo (crops/IMG_xxxx_upright.jpg): x left->right, y top->bottom.
The TL crop covers x 0-0.56, y 0-0.56; TR x 0.44-1, y 0-0.56; BL x 0-0.56, y 0.44-1; BR x 0.44-1, y 0.44-1."""
import sys, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
crops = os.path.join(os.path.dirname(here), 'crops'); out = os.path.join(os.path.dirname(here), 'zoom'); os.makedirs(out, exist_ok=True)
stem = sys.argv[1]; x0, y0, x1, y1 = map(float, sys.argv[2:6]); rot = int(sys.argv[6]) if len(sys.argv) > 6 else 0
im = Image.open(os.path.join(crops, stem + '_upright.jpg')); W, H = im.size
c = im.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H)))
if rot: c = c.rotate(-rot, expand=True)
scale = min(4.0, 1568 / max(c.size))
if scale > 1.05: c = c.resize((int(c.size[0]*scale), int(c.size[1]*scale)), Image.LANCZOS)
p = os.path.join(out, f'{stem}_{x0:.3f}_{y0:.3f}_{x1:.3f}_{y1:.3f}_r{rot}.jpg'); c.save(p, quality=93); print(p, c.size)
