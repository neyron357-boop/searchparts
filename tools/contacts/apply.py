# Build v2 of the contacts base: apply verified corrections to JSON and patch the existing XLSX in place.
import sys, os, json, copy, re, collections, datetime
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmt import all_numbers, photo_cell
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_JSON = os.path.join(root, 'drive_files', 'UAE_Contacts_AI.json'); BASE_XLSX = os.path.join(root, 'drive_files', 'UAE_Contacts.xlsx')
OUT_JSON = os.path.join(root, 'out', 'UAE_Contacts_AI.json'); OUT_XLSX = os.path.join(root, 'out', 'UAE_Contacts.xlsx')
TODAY = '2026-11-12'; BATCH = '2026-11-12-audit-01'
d = json.load(open(BASE_JSON, encoding='utf-8')); C = {c['id']: c for c in d['contacts']}
SRC = {s['filename'][4:8]: s for s in d['sources']}
log = []          # audit log rows
changed = set()   # contact ids whose xlsx row must be rewritten
photos_changed = set()
def L(cid, field, old, new, evidence):
    log.append({'date': TODAY, 'contact_id': cid, 'field': field, 'old': old, 'new': new, 'evidence': evidence}); changed.add(cid)
def phone(cid, printed):
    for p in C[cid]['phones']:
        if p['printed_number'] == printed: return p
    raise KeyError((cid, printed))
def add_flag(cid, f):
    if f not in C[cid]['review_flags']: C[cid]['review_flags'].append(f)
def set_notes(cid, text):
    old = C[cid]['notes']; C[cid]['notes'] = text; L(cid, 'notes', old, text, 'обновлено по итогам сверки')
def set_wa(cid, printed, ev):
    p = phone(cid, printed)
    if not p['whatsapp_marked']:
        L(cid, f'phones[{printed}].whatsapp_marked', False, True, ev); p['whatsapp_marked'] = True
    if not C[cid]['whatsapp_url']:
        url = 'https://wa.me/' + p['phone'].lstrip('+'); L(cid, 'whatsapp_url', None, url, ev); C[cid]['whatsapp_url'] = url
def add_phone(cid, entry, ev):
    C[cid]['phones'].append(entry); L(cid, 'phones', None, entry['printed_number'], ev)

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corrections.py'), encoding='utf-8').read())

# ---------- QR values already decoded in this session (no further decoding was done) ----------
NEW_QR = globals().get('NEW_QR', [])  # (photo, pos, value, contact, type, x, y) — defined in corrections.py
qr_photos = set()
for ph, pos, val, cid, typ, x, y in NEW_QR:
    pd = SRC[ph]['positions'][pos]
    assert cid in pd['contact_ids'], (ph, pos, cid, pd['contact_ids'])
    if any(q['value'] == val for q in pd['qr_values']): continue
    pd['qr_values'].append({'value': val, 'x': x, 'y': y}); pd['qr_decoded_count'] += 1
    pd['qr_visible_count'] = max(pd['qr_visible_count'], pd['qr_decoded_count']); qr_photos.add(ph)
    c = C[cid]
    if not any(q['value'] == val for q in c['qr_links']):
        c['qr_links'].append({'value': val, 'type': typ, 'source_position': ph + pos})
        L(cid, 'qr_links', None, val[:80], f'QR на {ph}{pos} расшифрован при сверке')
    if typ == 'whatsapp':
        num = '+' + re.sub(r'\D', '', val.split('wa.me/')[1].split('?')[0])
        for p in c['phones']:
            if p.get('phone') == num and not p['whatsapp_marked']:
                p['whatsapp_marked'] = True; L(cid, f'phones[{p["printed_number"]}].whatsapp_marked', False, True, f'QR WhatsApp на {ph}{pos} ведёт на этот номер')
        if not c['whatsapp_url']:
            c['whatsapp_url'] = 'https://wa.me/' + num.lstrip('+'); L(cid, 'whatsapp_url', None, c['whatsapp_url'], f'QR WhatsApp на {ph}{pos}')
    if typ == 'map' and not c['map_links_from_card']:
        c['map_links_from_card'].append(val); L(cid, 'map_links_from_card', None, val, f'QR карты на {ph}{pos}')
    if typ == 'social' and val not in c['sites']:
        c['sites'].append(val.replace('https://', '')); L(cid, 'sites', None, val, f'QR на {ph}{pos}')

# ---------- stats, indexes, handoff ----------
for c in d['contacts']:
    if c['id'] in changed: c.setdefault('audit', {})
    c['audit'] = {'blind_reread': TODAY, 'result': 'corrected' if c['id'] in changed else 'confirmed'}
st = d['stats']
st['qr_decoded'] = sum(pd['qr_decoded_count'] for s in d['sources'] for pd in s['positions'].values())
st['qr_visible'] = sum(pd['qr_visible_count'] for s in d['sources'] for pd in s['positions'].values())
idx = collections.defaultdict(list)
for c in d['contacts']:
    for m in c['vehicle_makes']: idx[m].append(c['id'])
d['vehicle_make_index'] = {k: sorted(v) for k, v in sorted(idx.items())}
st['brands'] = len(d['vehicle_make_index'])
d['updated_on'] = TODAY; d['schema_version'] = '1.1'
d['handoff']['audit'] = ('2026-11-12: все 200 позиций независимо перечитаны вслепую (без доступа к базе) и сверены скриптом по номерам, '
    'email, сайтам, названиям и отметкам WhatsApp; каждое расхождение проверено по увеличенному фото. Правки — в audit_log; '
    'поле audit у каждого контакта: confirmed (совпало) или corrected. Расшифровка QR дополнительно не проводилась по просьбе пользователя; '
    'внесены только 7 значений, уже полученных в ходе сверки.')
d['audit_log'] = d.get('audit_log', []) + log
json.dump(d, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('JSON written; log entries', len(log), '| changed contacts', len(changed), sorted(changed))
print('stats', st)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apply_xlsx.py'), encoding='utf-8').read())
