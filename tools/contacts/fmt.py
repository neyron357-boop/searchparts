# Formatters reproducing the existing Excel text from JSON (round-trip tested on all 103 rows).
def all_numbers(c):
    out = []
    for p in c['phones']:
        num = p['phone'] if p.get('phone') else p['printed_number']
        s = (p['label'] + ' ' if p.get('label') else '') + num
        if p.get('whatsapp_marked'): s += ' WA'
        if p.get('status') in ('needs_confirmation', 'invalid_format'): s += ' проверить'
        out.append(s)
    return ' · '.join(out) or None
OBS_RU = {'card_face': 'Сторона визитки', 'brand_side': 'Марки / ассортимент', 'blank_back': 'Пустая сторона', 'same_face': 'Та же сторона',
          'map_side': 'Схема проезда', 'different_company_same_person': 'Разные компании, общий контакт', 'additional_copy': 'Повтор',
          'possible_pair': 'Связка для проверки'}
def photo_cell(pd):
    return ' / '.join(pd['contact_ids']) + ' · ' + ' · '.join(OBS_RU[o] for o in pd['observations'])
