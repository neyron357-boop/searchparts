# Pass 1: zxing on the full frame + quadrants (2x). Pass 2 (only where the base says a QR is visible but undecoded): heavy preprocessing on that quadrant.
import sys, os, json, itertools
import numpy as np, cv2, zxingcpp
crops, basejson, outjson = sys.argv[1:4]
base = json.load(open(basejson, encoding='utf-8'))
QUAD = {'TL': (0, 0, .56, .56), 'TR': (.44, 0, 1, .56), 'BL': (0, .44, .56, 1), 'BR': (.44, .44, 1, 1)}
def zx(img, sc=1.0, ox=0, oy=0, W=1, H=1, found=None):
    for r in zxingcpp.read_barcodes(img):
        if not r.text: continue
        p = r.position
        cx = ((p.top_left.x + p.bottom_right.x) / 2 / sc + ox) / W; cy = ((p.top_left.y + p.bottom_right.y) / 2 / sc + oy) / H
        found.setdefault(r.text, (round(cx, 3), round(cy, 3)))
def variants(g):
    yield g
    yield cv2.createCLAHE(3.0, (8, 8)).apply(g)
    yield cv2.GaussianBlur(g, (0, 0), 1.2)
    sharp = cv2.addWeighted(g, 1.8, cv2.GaussianBlur(g, (0, 0), 3), -0.8, 0); yield sharp
    for bs, c in ((31, 5), (51, 8), (91, 10), (151, 12)):
        yield cv2.adaptiveThreshold(cv2.GaussianBlur(g, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bs, c)
    _, o = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU); yield o
    for gm in (0.5, 0.7, 1.5, 2.2):
        yield (255 * (g / 255.0) ** gm).astype(np.uint8)
    yield 255 - g
    yield cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    yield cv2.medianBlur(g, 5)
res = {}; T = dict(base=0, now=0, new=0, missing=0)
for s in base['sources']:
    stem = s['filename'].split('.')[0]
    img = cv2.imread(os.path.join(crops, stem + '_upright.jpg')); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); H, W = gray.shape
    found = {}
    zx(gray, 1, 0, 0, W, H, found)
    for pos, (a, b, c, d) in QUAD.items():
        x0, y0, x1, y1 = int(a * W), int(b * H), int(c * W), int(d * H); t = gray[y0:y1, x0:x1]
        zx(cv2.resize(t, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), 2, x0, y0, W, H, found)
        zx(cv2.createCLAHE(3.0, (8, 8)).apply(t), 1, x0, y0, W, H, found)
    basevals = {}; vis = 0; heavy = []
    for pos, pd in s['positions'].items():
        vis += pd.get('qr_visible_count', 0)
        for q in pd.get('qr_values', []): basevals[q['value']] = pos
        if pd.get('qr_visible_count', 0) > pd.get('qr_decoded_count', 0): heavy.append(pos)
    for pos in heavy:
        a, b, c, d = QUAD[pos]; x0, y0, x1, y1 = int(a * W), int(b * H), int(c * W), int(d * H); t = gray[y0:y1, x0:x1]
        before = len(found)
        for sc in (1.0, 1.5, 2.0, 3.0, 0.75, 0.5):
            tt = cv2.resize(t, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC if sc > 1 else cv2.INTER_AREA) if sc != 1.0 else t
            for v in variants(tt):
                zx(v, sc, x0, y0, W, H, found)
                for ang in (90, 180):  # zxing is rotation tolerant, but perspective cases sometimes pass after rotating
                    pass
        print(f'  heavy pass {stem} {pos}: +{len(found) - before}')
    new = sorted(set(found) - set(basevals)); missing = sorted(set(basevals) - set(found))
    T['base'] += len(basevals); T['now'] += len(found); T['new'] += len(new); T['missing'] += len(missing)
    res[stem] = {'found': {k: list(v) for k, v in found.items()}, 'base': basevals, 'base_visible': vis, 'new': new, 'missing': missing}
    if new or missing:
        print(stem, 'visible(base)=', vis, 'decoded(base)=', len(basevals), 'decoded(now)=', len(found))
        for n in new: print('   NEW   ', found[n], repr(n)[:200])
        for m in missing: print('   NOT REDECODED', basevals[m], repr(m)[:120])
json.dump(res, open(outjson, 'w'), ensure_ascii=False, indent=1)
print('TOTAL', T)
