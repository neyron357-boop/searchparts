#!/usr/bin/env python3
"""Enhanced zoom: zoomx.py IMG_6276 x0 y0 x1 y1 [rot] -> contrast-stretched, upscaled crop (fractions of upright full photo)."""
import sys, os
from PIL import Image, ImageOps, ImageFilter
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
stem = sys.argv[1]; x0, y0, x1, y1 = map(float, sys.argv[2:6]); rot = int(sys.argv[6]) if len(sys.argv) > 6 else 0
im = Image.open(os.path.join(root, 'crops', stem + '_upright.jpg')); W, H = im.size
c = im.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H)))
if rot: c = c.rotate(-rot, expand=True)
scale = min(6.0, 1568 / max(c.size))
c = c.resize((int(c.size[0]*scale), int(c.size[1]*scale)), Image.LANCZOS)
c = ImageOps.autocontrast(c, cutoff=1).filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
os.makedirs(os.path.join(root, 'zoom'), exist_ok=True)
p = os.path.join(root, 'zoom', f'{stem}_x_{x0:.3f}_{y0:.3f}_{x1:.3f}_{y1:.3f}_r{rot}.jpg'); c.save(p, quality=94); print(p, c.size)
