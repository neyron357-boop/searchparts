import sys, json
d = json.load(open(sys.argv[1], encoding='utf-8'))
for c in d['contacts']:
    mk = ','.join(c['vehicle_makes'][:8]) + ('…' if len(c['vehicle_makes']) > 8 else '')
    print(f"{c['id'][3:]}|{c['name'][:44]}|{'/'.join(c['categories'])}|{(c['city'] or '?')[:7]}:{(c['district'] or '?')[:26]}|t{c['proximity_tier']}|{mk}|{'/'.join(c['source_positions'])}|{','.join(c['review_flags'])}")
