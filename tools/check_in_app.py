#!/usr/bin/env python3
"""Open every example in a running Diagramium and prove it loads.

For each file in skills/diagramium-diagrams/examples/ (or the paths given),
this opens it through the app's real File -> Open code (importFileText),
then reports: the mode the app chose, the Present step count, any field the
app's sanitizer dropped, and any page error. With --shots DIR it also saves a
PNG of each rendered diagram, so a human can look at the layouts.

    python3 tools/check_in_app.py --origin https://www.diagramium.com
    python3 tools/check_in_app.py --origin http://localhost:8010 --shots /tmp/shots

Needs Python Playwright (pip install playwright; playwright install chromium).
This is a maintainer check: the skill itself needs none of it.
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = HERE / "skills" / "diagramium-diagrams" / "examples"

PROBE = r"""
async (doc) => {
  const errs = [];
  const onErr = e => errs.push(String(e.message || e));
  window.addEventListener('error', onErr);
  const before = JSON.parse(JSON.stringify(doc.state || {}));
  let ok = false;
  try { ok = importFileText(JSON.stringify(doc), 'probe.json'); } catch (e) { errs.push('import threw: ' + e.message); }
  await new Promise(r => setTimeout(r, 600));
  window.removeEventListener('error', onErr);
  const after = activeDocState() || {};
  const lost = [];
  for (const k of Object.keys(before)) {
    if (!(k in after)) { lost.push('state.' + k); continue; }
    const b = before[k], a = after[k];
    if (Array.isArray(b) && Array.isArray(a)) {
      if (a.length !== b.length) lost.push(`state.${k}: ${b.length} -> ${a.length} items`);
      b.forEach((item, i) => {
        if (!item || typeof item !== 'object') return;
        const ai = a.find(x => x && x.id === item.id) || a[i];
        if (!ai) return;
        for (const f of Object.keys(item)) if (!(f in ai)) lost.push(`state.${k}[${item.id ?? i}].${f}`);
      });
    }
  }
  if (before.narration) {
    const na = Object.keys(after.narration || {});
    for (const k of Object.keys(before.narration)) if (k !== '__audioclips' && !na.includes(k)) lost.push('narration.' + k);
  }
  let steps = null; try { steps = presentTotalSteps(); } catch (e) {}
  return { ok, mode: appMode, theme: after.theme || null, steps, lost, errs };
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", default="https://www.diagramium.com")
    ap.add_argument("--shots", help="directory for one PNG per diagram")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()
    files = [pathlib.Path(f) for f in a.files] or sorted(EXAMPLES.glob("*.json"))
    from playwright.sync_api import sync_playwright
    shots = pathlib.Path(a.shots) if a.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    bad = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 1000})
        page.goto(a.origin.rstrip("/") + "/flow", wait_until="networkidle")
        page.wait_for_timeout(1500)
        for f in files:
            doc = json.loads(f.read_text(encoding="utf-8"))
            r = page.evaluate(PROBE, doc)
            # The grid solve stamps format 2 -> 3 on purpose; it is not a loss.
            fine = r["ok"] and not r["errs"] and not r["lost"] and r["mode"] == doc["mode"]
            bad += not fine
            print(("OK  " if fine else "FAIL"), f"{f.stem:<16} mode={r['mode']:<15} theme={r['theme']!s:<14} steps={r['steps']}",
                  ("" if fine else f"lost={r['lost']} errs={r['errs']}"))
            if shots:
                # The app's own still export (what File -> Export -> PNG
                # writes), so the picture is the diagram, not the editor.
                data = page.evaluate("""() => new Promise(res => {
                  try { renderPngBlob(b => { if (!b) return res(null);
                    const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(b); }); }
                  catch (e) { res(null); } })""")
                out = shots / (f.stem + ".png")
                if data:
                    import base64
                    out.write_bytes(base64.b64decode(data.split(",", 1)[1]))
                else:
                    (page.query_selector("#canvasWrap") or page).screenshot(path=str(out))
        b.close()
    print(f"\n{len(files) - bad}/{len(files)} examples open cleanly")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
