#!/usr/bin/env python3
"""Build dist/diagramium-diagrams.zip — the file Claude.ai's "Upload skill"
takes. The zip holds the skill folder itself (SKILL.md at
diagramium-diagrams/SKILL.md). Run from the repo root."""
import pathlib, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "diagramium-diagrams"
OUT = ROOT / "dist" / "diagramium-diagrams.zip"
OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(SKILL.rglob("*")):
        if f.is_file() and f.name != ".DS_Store" and "__pycache__" not in f.parts:
            z.write(f, f.relative_to(SKILL.parent))
print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")
