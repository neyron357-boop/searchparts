# База контактов поставщиков (визитки)

Сама база хранится у пользователя в Google Drive (папка «База контактов»), в репозитории её нет.
Файлы базы: `UAE_Contacts.xlsx` (для человека) и `UAE_Contacts_AI.json` (для агента; поля `handoff`,
`audit_log` описывают правила и историю правок). Обе версии обновляются из одного набора данных.

## Текущее состояние (после сверки 2026-11-12)

- 50 фото (`IMG_6231`–`IMG_6281`, файла `IMG_6254` в папке нет), по 4 позиции на фото = 200 позиций.
- 103 записи `CT-0001`…`CT-0103`: 63 автозапчасти, 40 прочие категории; 73 марки в индексе.
- Все 200 позиций независимо перечитаны и сверены (см. `sessions/2026-11-12-contacts-audit.md`).

## Схема JSON (кратко)

- `contacts[]`: `id`, `name`, `group_id` (филиалы одной сети), `categories`, `city`, `district`, `address`,
  `proximity_tier` 1–7 (1 — Al Qusais Ind. Area 4, 2 — Al Qusais/Damascus St, 3 — Sharjah Industrial/BMW Road,
  4 — прочий Dubai, 5 — Al Sajaa и прочий Sharjah, 6 — другие эмираты, 7 — район неизвестен),
  `vehicle_makes`, `market_coverage`, `vehicle_models`, `scope_notes`, `service_tags`, `part_condition`,
  `phones[]` (`label`, `printed_number`, `phone` в E.164, `whatsapp_marked`, `source` card_print|handwritten,
  `status` readable|needs_confirmation|invalid_format, `usage`), `primary_phone`, `whatsapp_url`, `emails`,
  `sites`, `map_links_from_card`, `map_search_url`, `qr_links`, `source_positions` (`6231TL`…),
  `review_flags`, `notes`, `verification`, `inventory_status`, `source_batch`, `audit`.
- `sources[]`: файл, Drive ID, SHA-256, поворот, и по позициям TL/TR/BL/BR: `contact_ids`, `observations`
  (card_face, brand_side, blank_back, map_side, same_face, additional_copy, possible_pair,
  different_company_same_person), счётчики и значения QR.
- `vehicle_make_index`, `vehicle_make_aliases`, `category_labels_ru`, `service_tag_labels_ru`, `proximity_tiers_ru`.

## Правила пополнения

- Новый ID — следующий свободный `CT-xxxx`; старые ID не переиспользовать; при слиянии — журнал перенаправлений.
- Сверять Drive ID и SHA-256 файлов (повторно скачанные файлы — те же байты).
- Дубли: название + номер + адрес. Филиалы с разными адресами — отдельные записи с общим `group_id`.
  Общий номер сам по себе не повод сливать.
- Телефоны — строкой в E.164 (+971…). Сомнительная цифра → `status: needs_confirmation`, не в `primary_phone`.
- WhatsApp — только по значку/пометке на визитке или QR `wa.me`. Значок перед группой номеров относится ко всей
  группе (пометить все, указать в `notes`).
- Марки — только по читаемой надписи или логотипу.
- Факсы хранятся в `notes`, не в `phones`.
- Каждая правка — запись в `audit_log` (дата, ID, поле, было, стало, основание) и лист «Журнал правок» в XLSX.

## Порядок обработки новой папки

Подробно — `tools/contacts/README.md`. Коротко: список папки → скачать → HEIC→JPEG с поворотом → 4 позиции на фото
→ чтение с лупой → сопоставление сторон → запись в JSON → XLSX → независимая слепая сверка → правки по фото.
