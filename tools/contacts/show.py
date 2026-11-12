import sys, json
d = json.load(open(sys.argv[1], encoding='utf-8'))
C = {c['id']: c for c in d['contacts']}
for cid in sys.argv[2:]:
    c = C['CT-' + cid.zfill(4)]
    print(f"== {c['id']} {c['name']} | {c['city']} / {c['district']} / {c['address']} | tier {c['proximity_tier']} | pos {c['source_positions']}")
    for p in c['phones']: print(f"     {p['printed_number']:<16} -> {p['phone']} | {p['label']} | WA={p['whatsapp_marked']} | {p['source']} | {p['status']} | {p['usage']}")
    print(f"     primary={c['primary_phone']} wa={c['whatsapp_url']} emails={c['emails']} sites={c['sites']}")
    print(f"     makes={c['vehicle_makes']} models={c['vehicle_models']} cond={c['part_condition']} tags={c['service_tags']} market={c['market_coverage']}")
    print(f"     scope={c['scope_notes']} | flags={c['review_flags']} | notes={c['notes']}")
    if c['qr_links']: print('     qr:', [(q['type'], q['value'][:70], q['source_position']) for q in c['qr_links']])
