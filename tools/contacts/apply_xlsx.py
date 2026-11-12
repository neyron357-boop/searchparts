# Patch the existing workbook in place (keeps its layout, styles and tables). Executed from apply.py.
from copy import copy as _cp
wb = openpyxl.load_workbook(BASE_XLSX)
LINK_COLOR = 'FF075C9A'
FLAG_RU = {'area_unspecified': 'Район не указан', 'handwritten_phone': 'Рукописный номер', 'see_notes': 'См. примечание',
           'make_unspecified': 'Марки не указаны', 'phone_not_listed': 'Нет рабочего номера на визитке',
           'make_pair_to_verify': 'Связку сторон с марками стоит подтвердить', 'invalid_printed_number': 'Неверный формат номера',
           'phone_digit_uncertain': 'Цифра номера под сомнением'}
def style_like(dst, src):
    dst.font = _cp(src.font); dst.alignment = _cp(src.alignment); dst.border = _cp(src.border); dst.fill = _cp(src.fill); dst.number_format = src.number_format
def put(cell, value, link=None, tmpl=None):
    cell.value = value
    if tmpl is not None: style_like(cell, tmpl)
    if link:
        cell.hyperlink = link; f = _cp(cell.font); f.color = LINK_COLOR; cell.font = f
    else:
        cell.hyperlink = None
        if cell.font and cell.font.color is not None and cell.font.color.rgb == LINK_COLOR:
            f = _cp(cell.font); f.color = 'FF263B4D'; cell.font = f
# ---- Контакты
ws = wb['Контакты']; H = {c.value: i + 1 for i, c in enumerate(ws[1])}
rows = {ws.cell(r, 1).value: r for r in range(2, ws.max_row + 1)}
tmpl_text = ws.cell(2, H['ID'])
for cid in sorted(changed):
    c = C[cid]; r = rows[cid]
    put(ws.cell(r, H['Основной телефон']), c['primary_phone'], tmpl=tmpl_text)
    put(ws.cell(r, H['WhatsApp']), 'Открыть чат' if c['whatsapp_url'] else None, c['whatsapp_url'], tmpl=tmpl_text)
    if c['map_links_from_card']: put(ws.cell(r, H['Карта']), 'QR с визитки', c['map_links_from_card'][0], tmpl=tmpl_text)
    put(ws.cell(r, H['Email']), ' · '.join(c['emails']) or None, tmpl=tmpl_text)
    put(ws.cell(r, H['Сайты / соцсети']), ' · '.join(c['sites']) or None, tmpl=tmpl_text)
    put(ws.cell(r, H['Все номера']), all_numbers(c), tmpl=tmpl_text)
    put(ws.cell(r, H['Примечания']), c['notes'], tmpl=tmpl_text)
# ---- Индекс марок (phone / WhatsApp columns follow the contact)
wm = wb['Индекс марок']; HM = {c.value: i + 1 for i, c in enumerate(wm[1])}
for r in range(2, wm.max_row + 1):
    cid = wm.cell(r, HM['ID']).value
    if cid in changed:
        c = C[cid]; put(wm.cell(r, HM['Телефон']), c['primary_phone'], tmpl=tmpl_text)
        put(wm.cell(r, HM['WhatsApp']), 'Открыть чат' if c['whatsapp_url'] else None, c['whatsapp_url'], tmpl=tmpl_text)
# ---- Журнал фото (QR counters)
wp = wb['Журнал фото']; HP = {c.value: i + 1 for i, c in enumerate(wp[1])}
for r in range(2, wp.max_row + 1):
    ph = str(wp.cell(r, 1).value)[4:8]
    if ph in qr_photos or ph in photos_changed:
        for i, pos in enumerate(['TL', 'TR', 'BL', 'BR']): wp.cell(r, 3 + i).value = photo_cell(SRC[ph]['positions'][pos])
        s = SRC[ph]; dec = sum(p['qr_decoded_count'] for p in s['positions'].values()); vis = sum(p['qr_visible_count'] for p in s['positions'].values())
        old = wp.cell(r, HP['QR прочитано']).value
        wp.cell(r, HP['QR прочитано']).value = str(dec) if isinstance(old, str) else dec
        wp.cell(r, HP['QR в кадре']).value = str(vis) if isinstance(old, str) else vis
# ---- Уточнить: rebuild data rows
wr = wb['Уточнить']; HR = [c.value for c in wr[1]]
data = []
for r in range(2, wr.max_row + 1):
    vals = [wr.cell(r, i + 1).value for i in range(len(HR))]; link = wr.cell(r, len(HR)).hyperlink.target if wr.cell(r, len(HR)).hyperlink else None
    data.append([vals, link])
def drive_url(pos): return SRC[pos[:4]]['drive_url']
out = []; done_contacts = set()
for vals, link in data:
    typ, cid = vals[0], vals[1]
    if typ == 'QR':
        ph = str(vals[2])[4:8]; pos = vals[5]; pd = SRC[ph]['positions'][pos]
        if pd['qr_decoded_count'] >= pd['qr_visible_count']: continue      # now fully decoded
        out.append([vals, link]); continue
    if typ == 'Контакт' and cid in changed:
        done_contacts.add(cid); c = C[cid]
        if not c['review_flags']: continue
        vals = [typ, cid, c['name'], ' · '.join(FLAG_RU.get(f, f) for f in c['review_flags']), c['notes'], ' · '.join(c['source_positions']), 'Открыть']
        link = drive_url(c['source_positions'][0])
    out.append([vals, link])
# contacts that got review flags only now
first_qr = next((i for i, (v, _) in enumerate(out) if v[0] == 'QR'), len(out))
for cid in sorted(changed - done_contacts):
    c = C[cid]
    if not c['review_flags']: continue
    out.insert(first_qr, [['Контакт', cid, c['name'], ' · '.join(FLAG_RU.get(f, f) for f in c['review_flags']), c['notes'], ' · '.join(c['source_positions']), 'Открыть'], drive_url(c['source_positions'][0])]); first_qr += 1
tmpl_row = [_cp(wr.cell(2, i + 1)) for i in range(len(HR))]
height = wr.row_dimensions[2].height
for r in range(2, max(wr.max_row, len(out) + 1) + 1):
    for i in range(len(HR)): wr.cell(r, i + 1).value = None; wr.cell(r, i + 1).hyperlink = None
for k, (vals, link) in enumerate(out):
    r = k + 2
    for i, v in enumerate(vals):
        cell = wr.cell(r, i + 1); style_like(cell, tmpl_row[i]); cell.value = v
    lc = wr.cell(r, len(HR))
    if link: lc.hyperlink = link; f = _cp(lc.font); f.color = LINK_COLOR; lc.font = f
    wr.row_dimensions[r].height = height
last = len(out) + 1
for r in range(last + 1, wr.max_row + 1): wr.row_dimensions[r].height = None
wr.tables['UaeReview'].ref = f'A1:{openpyxl.utils.get_column_letter(len(HR))}{last}'
if wr.max_row > last: wr.delete_rows(last + 1, wr.max_row - last)
# ---- Журнал правок (new sheet, same look)
if 'Журнал правок' in wb.sheetnames: del wb['Журнал правок']
wl = wb.create_sheet('Журнал правок')
hdr = ['Дата', 'ID', 'Компания', 'Поле', 'Было', 'Стало', 'Основание']
for i, h in enumerate(hdr, 1): style_like(wl.cell(1, i), ws.cell(1, 1)); wl.cell(1, i).value = h
for k, e in enumerate(log, 2):
    vals = [e['date'], e['contact_id'], C[e['contact_id']]['name'], e['field'], None if e['old'] is None else str(e['old']), None if e['new'] is None else str(e['new']), e['evidence']]
    for i, v in enumerate(vals, 1): style_like(wl.cell(k, i), tmpl_text); wl.cell(k, i).value = v
    wl.row_dimensions[k].height = 33
wl.row_dimensions[1].height = ws.row_dimensions[1].height
for col, w in zip('ABCDEFG', (11, 10, 30, 26, 24, 24, 46)): wl.column_dimensions[col].width = w
wl.freeze_panes = 'A2'
t = Table(displayName='UaeAudit', ref=f'A1:G{max(2, len(log) + 1)}'); t.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showRowStripes=True); wl.add_table(t)
# ---- Как пользоваться: date line, control line, audit line
wh = wb['Как пользоваться']
for row in wh.iter_rows():
    for cell in row:
        v = cell.value
        if isinstance(v, str) and v.startswith('База визиток'):
            cell.value = v.replace('7 ноября 2026', '7 ноября 2026, сверка 12 ноября 2026')
        if isinstance(v, str) and v.startswith('Контроль партии'):
            cell.value = re.sub(r'(\d+) марок и (\d+) из (\d+) видимых QR', f"{st['brands']} марок и {st['qr_decoded']} из {st['qr_visible']} видимых QR", v)
            ctrl = cell
r0 = ctrl.row + 1
# move the folder link (row r0+1) one row down so the audit line keeps a spacer before the link
lk = wh.cell(r0 + 1, 1)
if lk.hyperlink is not None:
    rng = next((m for m in list(wh.merged_cells.ranges) if m.min_row == r0 + 1), None)
    if rng: wh.unmerge_cells(str(rng))
    dst = wh.cell(r0 + 2, 1); style_like(dst, lk); dst.value = lk.value; dst.hyperlink = lk.hyperlink.target
    wh.row_dimensions[r0 + 2].height = wh.row_dimensions[r0 + 1].height
    lk.value = None; lk.hyperlink = None; wh.row_dimensions[r0 + 1].height = None
    if rng: wh.merge_cells(start_row=r0 + 2, start_column=rng.min_col, end_row=r0 + 2, end_column=rng.max_col)
style_like(wh.cell(r0, 1), ctrl); wh.cell(r0, 1).value = ('Сверка 12.11.2026. Все 200 позиций перечитаны независимо и сверены с базой. '
    f'Без изменений — {len(C) - len(changed)}, с правками — {len(changed)} (из {len(C)}). Подробности — лист «Журнал правок».')
if ctrl.row in [m.min_row for m in wh.merged_cells.ranges]:
    rng = next(m for m in wh.merged_cells.ranges if m.min_row == ctrl.row); wh.merge_cells(start_row=r0, start_column=rng.min_col, end_row=r0, end_column=rng.max_col)
wh.row_dimensions[r0].height = wh.row_dimensions[ctrl.row].height
wb.save(OUT_XLSX); print('XLSX written', OUT_XLSX, '| review rows', len(out), '| audit rows', len(log))
