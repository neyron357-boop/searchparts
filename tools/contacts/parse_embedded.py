import sys, re, html, json
p = sys.argv[1]
t = open(p, encoding='utf-8', errors='replace').read()
print('title:', re.findall(r'<title>(.*?)</title>', t, re.S)[:1])
# entries
entries = re.findall(r'<div class="flip-entry" id="entry-([^"]+)"(.*?)</div></div></a></div>', t, re.S)
print('entries (regex1):', len(entries))
ids = re.findall(r'id="entry-([A-Za-z0-9_-]+)"', t)
print('entry ids:', len(ids), 'unique', len(set(ids)))
titles = re.findall(r'<div class="flip-entry-title">(.*?)</div>', t, re.S)
print('titles:', len(titles))
hrefs = re.findall(r'<a href="([^"]+)" target="_blank"', t)
print('hrefs:', len(hrefs))
dates = re.findall(r'<div class="flip-entry-last-modified"><div>(.*?)</div>', t, re.S)
print('dates:', len(dates))
out = []
for i, eid in enumerate(ids):
    out.append({'n': i+1, 'id': eid, 'title': html.unescape(titles[i]) if i < len(titles) else None,
                'href': html.unescape(hrefs[i]) if i < len(hrefs) else None,
                'date': dates[i] if i < len(dates) else None})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
for e in out:
    print(e['n'], '|', e['title'], '|', e['id'], '|', e['date'], '|', (e['href'] or '')[:60])
