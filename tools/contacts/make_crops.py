# Rotate each photo upright (rotation from the existing base) and cut 4 overlapping quadrant crops.
import sys, os, json
from PIL import Image
full, out, basejson = sys.argv[1:4]
base = json.load(open(basejson, encoding='utf-8'))
F = 0.56  # each quadrant covers 56% of width/height, so cards crossing the midline are not cut
n = 0
for s in base['sources']:
    stem = s['filename'].split('.')[0]
    im = Image.open(os.path.join(full, stem + '.jpg'))
    rot = s['rotation_clockwise']
    if rot: im = im.rotate(-rot, expand=True)
    W, H = im.size
    im.save(os.path.join(out, f'{stem}_upright.jpg'), quality=92)
    boxes = {'TL': (0, 0, int(W*F), int(H*F)), 'TR': (int(W*(1-F)), 0, W, int(H*F)),
             'BL': (0, int(H*(1-F)), int(W*F), H), 'BR': (int(W*(1-F)), int(H*(1-F)), W, H)}
    for pos, b in boxes.items():
        c = im.crop(b)
        c.save(os.path.join(out, f'{stem}_{pos}.jpg'), quality=92); n += 1
print('crops', n, 'example size', c.size)
