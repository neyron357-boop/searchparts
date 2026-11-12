import sys, os, json, hashlib
from PIL import Image, ImageOps
import pillow_heif
pillow_heif.register_heif_opener()
src, full, prev, basejson = sys.argv[1:5]
base = json.load(open(basejson, encoding='utf-8'))
srcs = {s['filename']: s for s in base['sources']}
rows = []
for fn in sorted(os.listdir(src)):
    if not fn.upper().endswith('.HEIC'): continue
    p = os.path.join(src, fn)
    raw = open(p, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    b = srcs.get(fn)
    im = Image.open(p)
    exif_o = im.getexif().get(0x0112)
    size_raw = im.size
    im2 = ImageOps.exif_transpose(im).convert('RGB')
    stem = fn.split('.')[0]
    im2.save(os.path.join(full, stem + '.jpg'), quality=95)
    pv = im2.copy(); pv.thumbnail((1600, 1600)); pv.save(os.path.join(prev, stem + '.jpg'), quality=85)
    rows.append((fn, size_raw, exif_o, im2.size, len(raw), sha == (b or {}).get('sha256'), len(raw) == (b or {}).get('bytes'), (b or {}).get('rotation_clockwise'), (b or {}).get('status')))
for r in rows: print(*r, sep=' | ')
print('files', len(rows), 'sha_match', sum(1 for r in rows if r[5]), 'bytes_match', sum(1 for r in rows if r[6]))
print('base sources not in folder:', sorted(set(srcs) - {r[0] for r in rows}))
print('folder files not in base:', sorted({r[0] for r in rows} - set(srcs)))
