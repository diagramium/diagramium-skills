# Format — shared fields, narration, pictures and voice

The per-mode schemas are in `modes.md`. This file covers what every mode
shares, and the limits the app enforces **silently** — over a limit, a field
is simply dropped on load with no error, so check before you hand over.

**Contents**: [Envelope](#envelope) · [Document fields](#document-fields) ·
[Free text](#free-text) · [Icons](#icons) · [Narration](#narration) ·
[Pictures](#pictures) · [Bundled voice](#bundled-voice) ·
[Limits](#limits-at-a-glance)

## Envelope

```json
{ "app": "flow-diagram", "version": 2, "mode": "<one of the 27>", "state": { } }
```

- `app` and `version` are literal. A misspelt `mode` is guessed from the
  name and the data, and the person is told it was guessed — spell it
  exactly instead.
- Valid JSON only: double quotes, no comments, no trailing commas. Write
  real characters (é, —, 💡) rather than escapes where you can.
- Ids: any unique strings. Short, readable ids (`login`, `db`, `e3`) make the
  file easy to edit by hand.

## Document fields

On `state`, in every mode:

| field | meaning |
|---|---|
| `title` | heads the page and the show — always set it |
| `subtitle` | a second line (≤ 160 chars) |
| `header`, `footer` | small text above / below the diagram |
| `theme` | see themes.md |
| `sheetStyle` | `plain` `dots` `grid` `ruled` `graph` `linen` `tooth` `diagonal` |
| `frame`, `frameStyle`, `frameColor`, `frameFlow` | a page border (`frameFlow: true` marches) |
| `arrowAnim` | animate every connector: `flow` `laser` `surge` `glow` |
| `arrowWidth`, `arrowColor`, `arrowStyle`, `arrowCorner` | document-wide connector look |
| `stageAspect` | `"portrait"` = a 9:16 show |
| `narration` | the spoken script (below) |

Leave out anything you do not need — every field has a sensible default.

## Free text

Node-and-edge modes, org charts, timelines and journey maps accept loose
labels that are not part of the structure:

```json
"texts": [ { "id": "t1", "text": "Draft — for review", "x": 900, "y": 60, "fontSize": 13, "italic": true } ]
```

`x`/`y` are required numbers. Use sparingly — a legend, a caveat, a source.

## Icons

Architecture, network and other technical shapes already carry icons. To
put your own on a node, embed it (never link it) as stroked paths on a
24 × 24 grid:

```json
"iconDef": { "p": ["M12 2 2 7l10 5 10-5-10-5Z", "M2 17l10 5 10-5"] }, "iconTint": "#4f46e5"
```

Each string is an SVG path `d`. No `<` or `>` characters.

## Narration

Add it only if the person wants narration (SKILL.md). Everything below —
including `__intro`, `__outro` and `__context` — lives **inside**
`state.narration`, and works in every mode except `visualstory` (whose
narration lives in each step). Keys:

| key | value |
|---|---|
| `"1"`, `"2"`, … | the spoken line for step N — counted the mode's way (modes.md) |
| `__why<N>` | the "why this matters" card for step N (< 4 000 chars) |
| `__tech<N>` | an optional technical aside for step N (< 4 000 chars) |
| `__intro` | `{ "enabled": true, "source": "custom", "text": "…" }` — spoken before step 1 |
| `__outro` | same shape — spoken after the last step |
| `__context` | sequence / swimlane / kanban only: introduces each participant, lane or column before step 1 (below) |
| `__img<N>`, `__imgpos<N>`, `__titleimg`, `__titleimglayout` | pictures (below) |
| `__audioclips` | a bundled recorded voice (below) |

```json
"narration": {
  "__intro": { "enabled": true, "source": "custom", "text": "Here is how a password reset works, end to end." },
  "1": "It starts when someone asks to reset their password.",
  "2": "We email them a one-time link.",
  "__why2": "Sending a link, not a new password, means nothing secret ever travels by email."
}
```

Writing it well:

- **Speech, not captions.** "We email them a one-time link." — not
  "Email link sent." Read each line aloud in your head.
- **One to three sentences per step**, and say something the shape does not:
  the reason, the consequence, the surprise.
- **Every step gets a line.** A gap goes silent mid-show and reads as broken.
- `__why` on about half the steps — where there is a genuine reason.
- Explain uses the device's own voice; nothing is sent anywhere.

`__context` (participant / lane / column introductions):

```json
"__context": { "enabled": true, "items": [
  { "id": "ctx-api", "target": { "kind": "actor", "id": "api" }, "source": "custom",
    "text": "The auth API checks credentials and issues sessions." } ] }
```

`target.kind` ∈ `actor` (sequence) · `lane` · `phase` (swimlane) · `column`
(kanban, where a column is a lane id); `target.id` must exist. These play
before step 1 and do **not** shift the step numbers. A bundled voice keys
their clips `__context:<item id>`.

## Pictures

Only when asked — they are the slow, failure-prone part.

| key | rule |
|---|---|
| `__img<N>` | the picture for step N: a `data:image/(png\|jpeg\|webp\|gif\|svg+xml);base64,…` string **under 400 000 characters** |
| `__imgpos<N>` | where it sits: absent = the step panel; `tl` `tr` `bl` `br` = that corner; `"0.8,0.15"` = fractions of the free space |
| `__titleimg` | the cover picture, **under 700 000 characters** |
| `__titleimglayout` | `stack` · `side` · `cover` (needs `__titleimg`) |

A URL or file path is always rejected — documents must work offline. The
cap counts characters of the data URI (base64 adds a third), so encode,
measure and re-encode:

```python
import base64, io
from PIL import Image

def fit(image_bytes, cap=400_000, long_edge=640, q=80):
    """A data URI guaranteed under `cap` characters."""
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if max(im.size) > long_edge:
        r = long_edge / max(im.size)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    while True:
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        if len(url) < cap * 0.975 or q <= 35:
            return url
        q -= 5

# step pictures: fit(b)                       16:10, e.g. 640 x 400
# the cover:     fit(b, 700_000, 1024, 88)
```

Use JPEG for illustrations and photos — PNG runs 10–20× larger. Match the
picture style to the theme (themes.md).

## Bundled voice

A document can carry recorded narration — one clip per step — that plays
instead of the device voice, offline, and survives File → Save.

```json
"__audioclips": {
  "id": "password-reset-tour",
  "voices": {
    "professional": {
      "label": "Nova (Studio)", "engine": "kokoro",
      "clips": { "1": "data:audio/mp4;base64,AAAAHGZ0eXBNNEEg…", "2": "data:audio/mp4;base64,…" }
    }
  }
}
```

- Clip keys are the narration step numbers (also `__intro`, `__outro`).
  A step without a clip falls back to the device voice.
- Clips are `data:audio/(mp4|mpeg|aac|wav|ogg|webm|x-m4a);base64,…` — m4a
  (AAC) is best. Voice keys: letters, digits, `_`, `-`, ≤ 32
  (`professional` opens by default). `label` is what the picker shows.
- Render at speech bitrate, e.g. `ffmpeg -i step1.wav -ac 1 -b:a 48k step1.m4a`
  (≈ 6 KB per second). One voice for a ten-step tour is about 1–2 MB of JSON.
- The narration **text** is still required — it drives subtitles and the
  fallback voice.

## Limits at a glance

| what | limit | over it |
|---|---|---|
| `__img<N>` | < 400 000 chars | picture dropped |
| `__titleimg` | < 700 000 chars | cover dropped |
| `__why<N>`, `__tech<N>` | < 4 000 chars | card dropped |
| voices | ≤ 8 | extra voices dropped |
| clips per voice | ≤ 400 | — |
| one clip | < 1 500 000 chars | clip dropped |
| whole audio bundle | < 24 000 000 chars | **whole bundle dropped** |
| Spotlight card `blocks` | ≤ 14 | extra blocks dropped |
| `subtitle` | ≤ 160 chars | truncated |

Run `scripts/validate.py` — it checks all of these.
