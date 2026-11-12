# Blind transcription of photographed business cards

You are doing an independent, blind transcription of photographed business cards (mostly auto-parts
suppliers and workshops in the UAE, plus some unrelated businesses). An earlier transcription exists and
yours will be diffed against it by a script to catch misread digits. So:

* Exactness of every digit and letter matters far more than speed.
* Stay blind: do NOT open anything under `drive_files/`, and no JSON/XLSX in the scratchpad other than
  the output file you write yourself. Do not read other batches' output.
* Never guess. An unreadable character is written as `?` and explained in `uncertain`.

## Input
Directory: $WORK/crops
Files: `IMG_XXXX_TL.jpg`, `_TR.jpg`, `_BL.jpg`, `_BR.jpg` — one upright crop per card position of photo
XXXX (each photo shows four cards in a 2x2 grid: top-left, top-right, bottom-left, bottom-right).
Each crop covers 56% of the frame, so edges of neighbouring cards may intrude at the inner sides —
transcribe only the card that belongs to that corner (the one mostly inside the crop).
A position may hold a card front, a card back (blank, a location map, a list of brands/services, an
Arabic-only side), a non-card item, or nothing.

## How to read
1. Read the crop image with the Read tool.
2. For phones, emails and websites read character by character. Whenever print is small, glossy,
   blurred, or two digits could be confused (3/8, 5/6, 0/8, 1/7, 0/6/9), zoom in:
   `python3 $WORK/scripts/zoom.py IMG_6231 x0 y0 x1 y1 [rotate_cw_deg]`
   Coordinates are fractions (0..1) of the upright FULL photo (x left→right, y top→bottom). The TL crop
   spans x 0–0.56, y 0–0.56; TR x 0.44–1, y 0–0.56; BL x 0–0.56, y 0.44–1; BR x 0.44–1, y 0.44–1.
   The script prints the path of a zoomed JPEG; Read it. Zooming on a strip of ~0.15–0.25 of the frame
   gives the best magnification. Use the optional rotation if a card lies sideways or upside down.
   Zoom freely — a zoom is cheap, a wrong digit is not.
3. After transcribing a phone number, re-read it once more from the image digit by digit before moving on.

## Output
Write ONE JSON file (UTF-8, valid JSON, a list with one object per crop, in photo/position order
TL, TR, BL, BR) to the path given in your task. Keys of each object:

* `photo` — e.g. "IMG_6231"; `pos` — "TL" | "TR" | "BL" | "BR"
* `content` — "contacts" (card side carrying any phone/email/address), "no_contacts" (card side with
  only logos / services / map / decoration), "blank" (empty card back), "no_card"
* `company` — company / trade name in Latin letters exactly as printed (null if none on this side)
* `people` — list of {"name", "title"} (title null if absent)
* `phones` — list of {"printed": number EXACTLY as printed incl. spaces/+/dashes,
  "kind": "mobile" | "landline" | "fax" | "tollfree" | "unknown",
  "label": printed label or the person it belongs to (null if none),
  "whatsapp": true only if a WhatsApp icon/word is attached to this number}
* `emails`, `websites`, `social` — lists of strings exactly as printed
* `address` — full address string as printed (null if none); `po_box` — string or null
* `activity` — tagline / goods / services as printed (English; if only Arabic, give a short English
  translation prefixed with "AR: ")
* `brands` — car makes or product brands named in text or shown as clearly identifiable logos
* `models_years` — any specific vehicle models / year ranges printed (list of strings, may be empty)
* `qr_codes` — integer, number of QR codes visible on this card side
* `other_text` — anything else useful (licence/TRN numbers, branch names, slogans), else null
* `legibility` — "clear" | "partly" | "poor"
* `uncertain` — list of strings, each naming the field and the doubtful character(s); empty if none

## Final reply
Reply briefly (do not paste the JSON): how many objects you wrote, which positions were blank / backs
without contacts / empty, and every character you remained unsure of. If a crop could not be opened, say so.
