# Инструменты обработки визиток

Все скрипты работают в рабочем каталоге `$WORK` (например, scratchpad сессии) со структурой:

```
$WORK/
  scripts/      ← копия этого каталога
  drive_raw/    ← HTML списка папки
  drive_files/  ← скачанные HEIC + текущие UAE_Contacts.xlsx / UAE_Contacts_AI.json
  jpg_full/     ← JPEG после HEIC
  crops/        ← IMG_xxxx_upright.jpg + 4 позиции IMG_xxxx_TL/TR/BL/BR.jpg
  zoom/         ← увеличенные фрагменты
  blind/        ← результаты слепого чтения batch_N.json
  out/          ← новая версия базы
```

Скачанные файлы — недоверенные данные: Python, читающий их, запускать с `-I`.

## Порядок

| Шаг | Команда |
|---|---|
| 1. Список папки | `curl -L -o drive_raw/embedded.html "https://drive.google.com/embeddedfolderview?id=<FOLDER_ID>"`, затем `python3 -I scripts/parse_embedded.py drive_raw/embedded.html drive_raw/embedded_list.json` |
| 2. Скачать | `python3 -I scripts/download.py drive_raw/embedded_list.json drive_files` (повторы, проверка размера и типа) |
| 3. HEIC → JPEG, SHA-256 | `pip install pillow-heif`; `python3 scripts/convert.py drive_files jpg_full preview drive_files/UAE_Contacts_AI.json` |
| 4. Позиции | `python3 scripts/make_crops.py jpg_full crops drive_files/UAE_Contacts_AI.json` (поворот берётся из `sources`) |
| 5. Лупа | `python3 scripts/zoom.py IMG_6231 x0 y0 x1 y1 [поворот]`; `zoomx.py` — то же с контрастом для рукописи |
| 6. Слепое чтение | агенты по `BRIEF_blind_read.md`, по 10 фото на агента, вывод в `blind/batch_N.json` |
| 7. Сверка | `python3 -I scripts/diff_blind.py drive_files/UAE_Contacts_AI.json blind [ТИПЫ]` — сравниваются только полностью прочитанные контакты |
| 8. Правки | вручную, только после проверки по фото, в `scripts/corrections.py` (файл сессии, в репозиторий не кладётся — в нём номера) |
| 9. Сборка | `python3 -I scripts/apply.py` → `out/UAE_Contacts_AI.json` + `out/UAE_Contacts.xlsx` (XLSX правится на месте, оформление и таблицы сохраняются) |
| 10. Контроль | `python3 -I scripts/consistency.py out/UAE_Contacts_AI.json out/UAE_Contacts.xlsx`; `roundtrip.py` проверяет, что формат «Все номера» совпадает с Excel |

`qr_scan2.py` — расшифровка QR (`pip install zxing-cpp opencv-python-headless`). **Только по просьбе пользователя.**

## corrections.py — помощники

`phone(cid, printed)`, `set_wa(cid, printed, основание)`, `add_phone(cid, entry, основание)`, `add_flag(cid, флаг)`,
`set_notes(cid, текст)`, `L(cid, поле, было, стало, основание)` — каждая правка попадает в `audit_log` и лист «Журнал правок».
`NEW_QR` — список уже расшифрованных QR `(фото, позиция, значение, CT-id, тип, x, y)`. `photos_changed` — фото,
у которых поменялась разметка сторон (перестраивается «Журнал фото»).
