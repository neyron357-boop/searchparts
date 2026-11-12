import sys, json, re, collections, openpyxl
d = json.load(open(sys.argv[1], encoding='utf-8'))
wb = openpyxl.load_workbook(sys.argv[2])
C = {c['id']: c for c in d['contacts']}
issues = []
def norm(p):
    x = re.sub(r'\D', '', p or '')
    if x.startswith('00971'): x = x[5:]
    elif x.startswith('971') and len(x) >= 11: x = x[3:]
    elif x.startswith('0'): x = x[1:]
    return x
mob = re.compile(r'^5[024568]\d{7}$'); land = re.compile(r'^[234679]\d{7}$'); toll = re.compile(r'^(800\d{2,9}|600\d{6})$')
kinds = collections.Counter(); status = collections.Counter(); usage = collections.Counter(); src = collections.Counter()
phone_owner = collections.defaultdict(set)
for c in d['contacts']:
    ph = c['phones']
    e164 = [p.get('phone') for p in ph]
    if c['primary_phone'] and c['primary_phone'] not in e164: issues.append((c['id'], 'primary_phone not in phones', c['primary_phone']))
    if not c['primary_phone'] and ph: issues.append((c['id'], 'no primary_phone though phones exist', [p['printed_number'] for p in ph]))
    if c['whatsapp_url']:
        m = re.search(r'wa\.me/(\d+)', c['whatsapp_url'])
        if m and ('+' + m.group(1)) not in e164: issues.append((c['id'], 'whatsapp_url number not in phones', c['whatsapp_url']))
        if m and not any(p.get('whatsapp_marked') for p in ph if p.get('phone') == '+' + m.group(1)): issues.append((c['id'], 'whatsapp_url number not marked WA on card', c['whatsapp_url']))
    for p in ph:
        status[p.get('status')] += 1; usage[p.get('usage')] += 1; src[p.get('source')] += 1
        n = norm(p['printed_number'])
        if p.get('phone'):
            if norm(p['phone']) != n: issues.append((c['id'], 'printed vs normalized mismatch', (p['printed_number'], p['phone'])))
            if not p['phone'].startswith('+971') and not toll.match(re.sub(r'\D', '', p['phone'])): issues.append((c['id'], 'non-UAE or odd phone', p['phone']))
        k = 'mobile' if mob.match(n) else 'landline' if land.match(n) else 'tollfree' if toll.match(n) else 'ODD'
        kinds[k] += 1
        if k == 'ODD': issues.append((c['id'], 'unusual number format', (p['printed_number'], p.get('phone'), p.get('status'), p.get('usage'))))
        phone_owner[n].add(c['id'])
print('contacts', len(C), '| phones', sum(kinds.values()), dict(kinds))
print('phone status', dict(status)); print('usage', dict(usage)); print('source', dict(src))
shared = {n: sorted(v) for n, v in phone_owner.items() if len(v) > 1}
print('numbers shared by >1 contact:', len(shared))
for n, v in sorted(shared.items()): print('   ', n, v, [C[i]['name'][:34] for i in v], [C[i]['group_id'] for i in v])
# positions <-> contacts
pos2c = {}
for s in d['sources']:
    stem = s['filename'][4:8]
    for pos, pd in s['positions'].items(): pos2c[stem + pos] = pd
print('positions', len(pos2c), 'obs:', dict(collections.Counter(o for pd in pos2c.values() for o in pd['observations'])))
print('positions without contact:', [k for k, v in pos2c.items() if not v['contact_ids']])
print('positions with >1 contact:', {k: v['contact_ids'] for k, v in pos2c.items() if len(v['contact_ids']) > 1})
for c in d['contacts']:
    for sp in c['source_positions']:
        if c['id'] not in pos2c.get(sp, {}).get('contact_ids', []): issues.append((c['id'], 'source_position not backed by sources', sp))
for k, v in pos2c.items():
    for cid in v['contact_ids']:
        if k not in C[cid]['source_positions']: issues.append((cid, 'sources position missing in contact', k))
print('contacts by #positions:', dict(collections.Counter(len(c['source_positions']) for c in d['contacts'])))
print('categories:', dict(collections.Counter(x for c in d['contacts'] for x in c['categories'])))
print('city:', dict(collections.Counter(c['city'] for c in d['contacts'])))
print('tier:', dict(collections.Counter(c['proximity_tier'] for c in d['contacts'])))
print('verification:', dict(collections.Counter(c['verification'] for c in d['contacts'])), 'batch:', dict(collections.Counter(c['source_batch'] for c in d['contacts'])))
print('contacts with review_flags:', sum(1 for c in d['contacts'] if c['review_flags']), '| flags:', dict(collections.Counter(f if isinstance(f, str) else json.dumps(f, ensure_ascii=False)[:40] for c in d['contacts'] for f in c['review_flags'])))
print('contacts without any phone:', [(c['id'], c['name'][:40]) for c in d['contacts'] if not c['phones']])
print('groups:', dict(collections.Counter(c['group_id'] for c in d['contacts'] if c['group_id'])))
# xlsx vs json
ws = wb['Контакты']; hdr = [c.value for c in ws[1]]; rows = {r[0]: dict(zip(hdr, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}
print('xlsx contacts', len(rows), 'ids equal:', set(rows) == set(C))
for i, c in C.items():
    r = rows.get(i)
    if not r: continue
    if (r['Основной телефон'] or None) != (c['primary_phone'] or None): issues.append((i, 'xlsx primary != json', (r['Основной телефон'], c['primary_phone'])))
    if (r['Компания / филиал'] or '') != c['name']: issues.append((i, 'xlsx name != json', (r['Компания / филиал'], c['name'])))
    xl_nums = set(re.findall(r'\+?\d{7,}', r['Все номера'] or '')); js = {p.get('phone') or p['printed_number'] for p in c['phones']}
    if {norm(x) for x in xl_nums} != {norm(x) for x in js}: issues.append((i, 'xlsx all-numbers != json', (r['Все номера'], sorted(js))))
ws = wb['Уточнить']; print('review sheet rows', ws.max_row - 1, dict(collections.Counter(r[0] for r in ws.iter_rows(min_row=2, values_only=True))), dict(collections.Counter(r[3] for r in ws.iter_rows(min_row=2, values_only=True))))
print('ISSUES', len(issues))
for i in issues: print('  ', i)
