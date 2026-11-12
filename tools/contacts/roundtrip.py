import sys, json, openpyxl
sys.path.insert(0, sys.argv[3]); from fmt import all_numbers
wb = openpyxl.load_workbook(sys.argv[1]); d = json.load(open(sys.argv[2], encoding='utf-8'))
C = {c['id']: c for c in d['contacts']}; ws = wb['Контакты']; hdr = [c.value for c in ws[1]]
bad = 0
for r in range(2, ws.max_row + 1):
    row = {h: ws.cell(r, i + 1).value for i, h in enumerate(hdr)}; c = C[row['ID']]
    checks = {'Все номера': all_numbers(c), 'Основной телефон': c['primary_phone'], 'Email': ' · '.join(c['emails']) or None,
              'Сайты / соцсети': ' · '.join(c['sites']) or None, 'Фото и позиции': ' · '.join(c['source_positions']), 'Примечания': c['notes'],
              'Марки авто': ', '.join(c['vehicle_makes']) or None}
    for k, v in checks.items():
        if (row[k] or None) != v:
            bad += 1; print(row['ID'], k, '| xlsx:', repr(row[k])[:110], '| fmt:', repr(v)[:110])
print('mismatches', bad)
