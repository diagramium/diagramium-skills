# Contributing

Thanks for helping. The most useful contribution is a **diagram the skill
got wrong**: open an issue with what you asked for, the file you got, and
what Diagramium showed (or a screenshot).

## How the repo fits together

- `skills/diagramium-diagrams/` — the skill. Keep `SKILL.md` short; detail
  belongs in `references/`.
- `skills/diagramium-diagrams/examples/` — **generated** by
  `tools/make_examples.py`. Edit the generator, not the JSON, then run it.
- `skills/diagramium-diagrams/scripts/validate.py` — mirrors the rules the
  Diagramium app enforces when it opens a file. If the app changes a rule,
  change it here, in `references/`, and add or fix an example in the same PR.

## Before a pull request

```bash
python3 tools/make_examples.py
python3 skills/diagramium-diagrams/scripts/validate.py skills/diagramium-diagrams/examples/*.json
python3 tools/package.py
```

For a change to a schema or an example, also open the examples in the real
app (needs Python Playwright and Chromium):

```bash
python3 tools/check_in_app.py --origin https://www.diagramium.com
```

It opens every example through Diagramium's own File → Open code and fails
if any field is dropped or any page error occurs. `--shots DIR` saves the
rendered PNGs; `docs/gallery/` is made from those.

## Releasing

1. Bump `version` in `.claude-plugin/plugin.json`.
2. `python3 tools/package.py`
3. Tag `vX.Y.Z` and attach `dist/diagramium-diagrams.zip` to the GitHub
   release (Claude.ai users install from it).
