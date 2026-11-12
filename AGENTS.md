# Инструкция для ИИ-агентов (AGENTS.md)

> **English summary for any AI agent:** this repository is the shared, cumulative knowledge base of an auto-parts
> sourcing assistant working with suppliers in the UAE. Read the files listed in "Start" before doing anything,
> follow `knowledge/rules.md`, never commit personal data (the repo is PUBLIC), and at the end of every task update
> the knowledge files and merge them into `main` (see "Finish"). Work and answer in Russian unless asked otherwise.

Этот файл читают все агенты: Claude Code (через `CLAUDE.md`), OpenAI Codex, Cursor, Gemini CLI (через `GEMINI.md`),
GitHub Copilot (через `.github/copilot-instructions.md`) и любые другие. Для чат-агентов без доступа к репозиторию
(ChatGPT, Gemini, Claude в браузере и т. п.) есть готовый текст для вставки — [`knowledge/agent-prompt.md`](knowledge/agent-prompt.md).

## Кто пользователь и что за задачи

Пользователь подбирает автозапчасти и работает с базой поставщиков в ОАЭ (точка отсчёта — Dubai, Al Qusais
Industrial Area 4). Присылает VIN, фото техпаспорта, фото деталей, названия запчастей, прайсы, ссылки на Google Drive.
Отвечать по-русски; тексты для поставщиков — по-английски одним блоком.

## Start — прочитать перед работой

1. [`knowledge/rules.md`](knowledge/rules.md) — постоянные правила пользователя (обязательны).
2. [`knowledge/lessons.md`](knowledge/lessons.md) — уроки и типовые ошибки.
3. [`knowledge/contacts-base.md`](knowledge/contacts-base.md) — если задача касается базы поставщиков/визиток.
4. Последние записи в [`knowledge/sessions/`](knowledge/sessions/) — что делали раньше и что осталось открытым.
5. [`tools/contacts/README.md`](tools/contacts/README.md) — если нужно обрабатывать фото визиток.

## Жёсткие ограничения

- **Репозиторий публичный.** Не коммитить: телефоны, имена, email людей с визиток, фото визиток и деталей
  с персональными данными, файлы базы `UAE_Contacts*`, ссылки на личные папки Google Drive, VIN и номера
  автомобилей клиентов. Перед коммитом — поиск по `+971`, `05x xxx xxxx`, `@gmail`, `wa.me/` (см. «Finish»).
- База контактов живёт у пользователя в Google Drive. В репозиторий — только методика, правила, уроки,
  инструменты и обезличенные итоги (количества, ID записей без контактов).
- Писать поставщикам, звонить, отправлять запросы — только по прямой просьбе пользователя.
- Наличие детали у поставщика считать подтверждённым только при наличии подтверждающих данных.
- Расшифровку QR-кодов не запускать без просьбы (пользователь просил пропускать).

## Работа с базой поставщиков

- Существующие ID `CT-xxxx` не менять и не переиспользовать; новые — следующий свободный номер.
- Любая правка — в `audit_log` (JSON) и на листе «Журнал правок» (XLSX), с основанием (фото/позиция).
- Обе версии базы (`UAE_Contacts.xlsx` и `UAE_Contacts_AI.json`) обновлять из одного набора данных
  скриптами `tools/contacts/` — оформление Excel сохраняется.
- Результат отдавать пользователю файлом; загрузка в Drive — если у агента есть доступ и пользователь просит.

## Finish — сразу после каждой работы (обязательно)

1. Обновить знания:
   - `knowledge/lessons.md` — новые уроки, ошибки, приёмы (коротко, по делу);
   - `knowledge/sessions/ГГГГ-ММ-ДД-тема.md` — что сделано, итоги в цифрах, что осталось открытым;
   - `knowledge/rules.md` — если пользователь дал новое постоянное правило;
   - `tools/` — если появился или улучшился переиспользуемый скрипт (без данных сессии).
2. Проверить, что нет персональных данных:
   `grep -rnE "\+?971 ?5[0-9]|05[0-9] ?[0-9]{3} ?[0-9]{4}|@gmail|@outlook|@yahoo|wa\.me/[0-9+]" . --exclude-dir=.git`
3. Закоммитить и **перенести в `main`** (пользователь разрешил и требует это после каждой работы):
   ```bash
   git add -A && git commit -m "knowledge: <кратко>"
   git checkout main && git pull --ff-only origin main
   git merge --ff-only <рабочая-ветка>   # если не fast-forward: git merge --no-ff <рабочая-ветка>
   git push origin main
   ```
   Если агенту доступна только своя ветка — запушить её и сказать пользователю, что нужен перенос в `main`.
4. В ответе пользователю одной строкой сообщить, что знания обновлены и перенесены в `main`.

## Если агент не может работать с репозиторием

Вернуть пользователю в конце ответа блок «Для репозитория» — готовые фрагменты для `lessons.md` и записи сессии,
без персональных данных. Пользователь или другой агент перенесёт их в `main`.
