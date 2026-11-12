# Diff the blind transcriptions against the existing base, position by position and contact by contact.
import sys, json, re, glob, os, difflib, collections
basejson, blinddir = sys.argv[1:3]
d = json.load(open(basejson, encoding='utf-8'))
C = {c['id']: c for c in d['contacts']}
blind = {}
for f in sorted(glob.glob(os.path.join(blinddir, 'batch_*.json'))):
    for e in json.load(open(f, encoding='utf-8')):
        blind[e['photo'][4:8] + e['pos']] = e
def norm(p):
    x = re.sub(r'[^\d?]', '', p or '')
    if x.startswith('00971'): x = x[5:]
    elif x.startswith('971') and len(x) >= 11: x = x[3:]
    elif x.startswith('0'): x = x[1:]
    return x
def nsite(s):
    s = (s or '').lower().strip(); s = re.sub(r'^https?://', '', s); s = re.sub(r'^www\.', '', s); return s.rstrip('/')
def ham(a, b):
    if len(a) != len(b): return 99
    return sum(1 for x, y in zip(a, b) if x != y)
pos2c = {}
for s in d['sources']:
    for pos, pd in s['positions'].items(): pos2c[s['filename'][4:8] + pos] = pd
print('blind positions', len(blind), 'of', len(pos2c), '| missing:', sorted(set(pos2c) - set(blind)))
out = collections.defaultdict(list)
# ---- per contact
skipped = []
for cid, c in C.items():
    if any(sp not in blind for sp in c['source_positions']):
        skipped.append(cid); continue
    bph = {}; bem = set(); bst = set(); bnames = []; unc = []
    for sp in c['source_positions']:
        e = blind.get(sp)
        if not e: continue
        for p in e.get('phones') or []:
            bph.setdefault(norm(p.get('printed')), []).append((sp, p.get('printed'), p.get('kind'), p.get('label'), p.get('whatsapp')))
        bem |= {x.lower().strip() for x in (e.get('emails') or [])}
        bst |= {nsite(x) for x in (e.get('websites') or [])}
        if e.get('company'): bnames.append((sp, e['company']))
        for u in e.get('uncertain') or []: unc.append((sp, u))
    base_ph = {norm(p['printed_number']): p for p in c['phones']}
    only_base = [n for n in base_ph if n not in bph]
    only_blind = [n for n in bph if n not in base_ph]
    # positions shared with other contacts: phone may belong to the other contact at that position
    shared_other = set()
    for sp in c['source_positions']:
        for oc in pos2c[sp]['contact_ids']:
            if oc != cid: shared_other |= {norm(p['printed_number']) for p in C[oc]['phones']}
    for n in list(only_blind):
        if n in shared_other: only_blind.remove(n)
    used = set()
    for nb in only_base:
        best = min(only_blind, key=lambda x: ham(nb, x), default=None)
        if best is not None and ham(nb, best) <= 3:
            out[cid].append(('DIGIT', f"base {base_ph[nb]['printed_number']!r} vs blind {[x[1] for x in bph[best]]} at {[x[0] for x in bph[best]]} (hamming {ham(nb, best)})")); used.add(best)
        else:
            out[cid].append(('BASE_ONLY_PHONE', f"{base_ph[nb]['printed_number']!r} ({base_ph[nb].get('label')}, {base_ph[nb].get('source')}, {base_ph[nb].get('status')}) not seen by blind read; blind phones: {sorted(bph)}"))
    for n in only_blind:
        if n in used: continue
        out[cid].append(('BLIND_ONLY_PHONE', f"{[(x[0], x[1], x[2], x[3]) for x in bph[n]]} not in base; base phones: {[p['printed_number'] for p in c['phones']]}"))
    # whatsapp marks
    for n, p in base_ph.items():
        if n in bph:
            bw = any(x[4] for x in bph[n])
            if bool(p.get('whatsapp_marked')) != bw: out[cid].append(('WA_MARK', f"{p['printed_number']}: base whatsapp_marked={p.get('whatsapp_marked')} blind={[(x[0], x[4]) for x in bph[n]]}"))
    be = {x.lower() for x in c['emails']}
    if be != bem: out[cid].append(('EMAIL', f"base {sorted(be)} vs blind {sorted(bem)}"))
    bs = {nsite(x) for x in c['sites']}
    if bs != bst: out[cid].append(('SITE', f"base {sorted(bs)} vs blind {sorted(bst)}"))
    if bnames:
        r = max(difflib.SequenceMatcher(None, re.sub(r'\W+', ' ', c['name'].lower()), re.sub(r'\W+', ' ', n.lower())).ratio() for _, n in bnames)
        if r < 0.72: out[cid].append(('NAME', f"base {c['name']!r} vs blind {bnames} (ratio {r:.2f})"))
    for u in unc: out[cid].append(('BLIND_UNCERTAIN', f"{u[0]}: {u[1]}"))
# ---- per position: content type vs observation
for k, pd in sorted(pos2c.items()):
    e = blind.get(k)
    if not e: continue
    obs = pd['observations']
    if e.get('content') in ('blank', 'no_card') and 'blank_back' not in obs: out['POS'].append(('CONTENT', f"{k}: blind={e.get('content')} base obs={obs} ids={pd['contact_ids']}"))
    if 'blank_back' in obs and e.get('content') not in ('blank', 'no_card'): out['POS'].append(('CONTENT', f"{k}: base says blank_back, blind={e.get('content')} company={e.get('company')!r} phones={[p.get('printed') for p in e.get('phones') or []]}"))
    if (e.get('qr_codes') or 0) != pd.get('qr_visible_count', 0): out['POS'].append(('QR_COUNT', f"{k}: blind sees {e.get('qr_codes')} QR, base visible={pd.get('qr_visible_count')} decoded={pd.get('qr_decoded_count')}"))
print('contacts skipped (not fully read yet):', len(skipped))
cnt = collections.Counter(t for v in out.values() for t, _ in v)
print('FLAGS:', dict(cnt), '| contacts with flags:', len([k for k in out if k != 'POS']), 'of', len(C))
order = ['DIGIT', 'BLIND_ONLY_PHONE', 'BASE_ONLY_PHONE', 'EMAIL', 'SITE', 'NAME', 'WA_MARK', 'BLIND_UNCERTAIN', 'CONTENT', 'QR_COUNT']
only = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else set(order)
for cid in sorted(out):
    rows = [(t, m) for t, m in out[cid] if t in only]
    if not rows: continue
    print(f"--- {cid} {C[cid]['name'][:50] if cid in C else ''} {C[cid]['source_positions'] if cid in C else ''}")
    for t, m in sorted(rows, key=lambda x: order.index(x[0])): print(f"   [{t}] {m[:420]}")
