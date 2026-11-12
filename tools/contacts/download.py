import sys, json, os, subprocess, time
lst = json.load(open(sys.argv[1])); out = sys.argv[2]
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
res = []
for e in lst:
    dst = os.path.join(out, e['title'])
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        res.append((e['title'], 'cached', os.path.getsize(dst))); continue
    url = f"https://drive.usercontent.google.com/download?id={e['id']}&export=download&confirm=t"
    code = '?'
    for attempt in range(4):
        r = subprocess.run(['curl', '-sS', '-L', '-A', UA, '-o', dst, '-w', '%{http_code} %{content_type}', url],
                           capture_output=True, text=True)
        code = r.stdout.strip() or r.stderr.strip()[:80]
        if code.startswith('200') and os.path.exists(dst) and os.path.getsize(dst) > 2000 and 'text/html' not in code:
            break
        time.sleep(2 * (attempt + 1))
    res.append((e['title'], code, os.path.getsize(dst) if os.path.exists(dst) else 0))
for r in res: print(*r, sep=' | ')
print('total', len(res), 'ok', sum(1 for r in res if r[1] == 'cached' or (r[1].startswith('200') and 'text/html' not in r[1])))
