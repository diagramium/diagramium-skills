#!/usr/bin/env python3
"""Check a Diagramium document before you hand it over.

    python3 validate.py diagram.json [more.json ...]

Exit code 0 = every file will open as intended. ERROR lines are things the
app will reject or silently drop; WARN lines are things that open but are
probably not what you meant (an unknown shape type falls back to a plain
box, an unknown theme renders as Classic, narration with gaps goes quiet).

Standard library only. The rules mirror the app's own loaders and
sanitizers (Diagramium file format, version 2).
"""
import json
import re
import sys

# --------------------------------------------------------------------------
# The 27 diagram types and their node vocabularies
# --------------------------------------------------------------------------
BASIC_SHAPES = set("""
rectangle roundRect squareBasic ellipse circleBasic semicircle donutBasic cylinderBasic cubeBasic triangle
rightTriangle diamondBasic parallelogramBasic trapezoidBasic pentagonBasic hexagonBasic octagonBasic cross
crossX lShape lightning cloudBasic folderBasic snipRect snipSameSide snipDiagonal roundOneCorner roundDiagonal
foldedCorner bevel frameBasic halfFrame plaque diagonalStripe heptagonBasic decagon dodecagon hexagonV
triangleDown pieBasic chordBasic arcBasic blockArc quarterCircle teardrop noSymbol crescent
chevron arrowBlock arrowLeftBlock arrowUpBlock arrowDownBlock doubleArrow doubleArrowV arrowQuad
arrowLeftRightUp arrowBent arrowBentUp arrowUTurn arrowStriped arrowNotched arrowCircular arrowCurvedRight
arrowCurvedUp arrowCalloutRight arrowCalloutUp
star star4 star6 star8 star12 explosion1 explosion2 sunShape ribbonUp ribbonDown scrollH scrollV wave doubleWave
callout calloutRect calloutRound calloutOval calloutCloud calloutLine
mathMinus mathDivide mathEqual mathNotEqual mathPlusMinus bracketLeft bracketRight braceLeft braceRight
smiley gearBasic personBasic flagBasic checkMark
""".split())
GRAPH_EXTRAS = set("""blob speech thought ribbon bannerShape badge shield heartShape blockArrow bracketShape
braceShape lineH lineV arrowLine arrowBoth divider sticky noteArea calloutNum image icon spotcard explainer note""".split())
FLOW_TYPES = set("""start end process decision io predefined document preparation manualInput manualOperation
connector offPage database delay display internalStorage card loopLimit or summingJunction note group
spotcard explainer""".split())

GRAPH_MODES = {
    "processmap": "start end process decision subprocess io document database delay note",
    "decisiontree": "decision chance option outcome note",
    "architecture": "client mobile webapp apigateway loadbalancer service worker ai auth database cache queue storage external cdn monitoring group",
    "dataflow": "entity dfProcess datastore note",
    "network": "internet cloud router switch firewall loadbalancer wifi vpn server database nas workstation mobile printer",
    "fishbone": "effect category cause subcause note",
    "usecase": "actor usecase boundary note",
    "threatmodel": "externalEntity actor dfProcess datastore cloud trustBoundary note",
    "c4model": "person softwareSystem container component externalSystem database boundary note",
    "conceptmap": "concept subtopic ellipse note",
    "umlclass": "umlClass note",
    "erdiagram": "erEntity entity note",
    "bpmn": ("bpmnStart bpmnMessage bpmnTimer bpmnInter bpmnBoundary bpmnEnd bpmnError bpmnTerminate task userTask "
             "serviceTask sendTask receiveTask subprocess bpmnGwX bpmnGwParallel bpmnGwInclusive bpmnGwEvent "
             "document database boundary note"),
    "visuallearning": "spotcard explainer rectangle ellipse decision database note",
}
GRAPH_MODES = {k: set(v.split()) for k, v in GRAPH_MODES.items()}
FORK_MODES = {
    "flowchart": FLOW_TYPES,
    "swimlane": FLOW_TYPES,
    "kanban": FLOW_TYPES,
    "statemachine": set("""simple composite note initial final choice junction forkjoin history deepHistory
entryPoint exitPoint terminate group spotcard explainer""".split()),
}
OTHER_MODES = {"sequence", "orgchart", "sitemap", "mindmap", "timeline", "gantt", "venn", "journeymap", "visualstory"}
ALL_MODES = set(GRAPH_MODES) | set(FORK_MODES) | OTHER_MODES

EDGE_KINDS = {
    "network": {"ethernet", "fiber", "wireless", "vpn", "serial"},
    "usecase": {"assoc", "include", "extend", "generalize", "dependency"},
    "umlclass": {"assoc", "inherit", "realize", "compose", "aggregate", "dependency"},
    "erdiagram": {"oneToMany", "oneToOne", "manyToMany", "oneToZeroMany", "zeroOneToMany"},
    "bpmn": {"sequence", "message", "association"},
}
CONTAINERS = {"architecture": {"group"}, "bpmn": {"boundary"}, "flowchart": {"group"},
              "statemachine": {"composite", "group"}}

THEMES = set("""quartz obsidian linear bento glassmorphism aurora-v2 editorial canvas marker forest executive
doodle handnote stickynote terminal metro orbit drafting neon notebook drawingbook sketchnote pencilsketch
classic ocean sunset mono midnight crayon bubblegum aurora gold slate grape coral handwriting glass blueprint
swiss clay papercut ink graffiti chalkboard deco storybook""".split())

SEQ_KINDS = {"participant", "actor", "database", "boundary", "control", "entity", "queue", "collection"}
SEQ_ITEMS = {"message", "note", "ref", "activate", "deactivate", "invariant", "divider",
             "fragStart", "fragElse", "fragEnd"}
FRAG_KINDS = {"loop", "opt", "alt", "par", "break", "critical", "seq", "strict", "neg", "assert", "ignore", "consider"}
HEX = re.compile(r"^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$")
IMG = re.compile(r"^data:image/(png|jpeg|jpg|webp|gif|svg\+xml);base64,")
AUDIO = re.compile(r"^data:audio/(mp4|mpeg|aac|wav|ogg|webm|x-m4a)[;,]")


class Report:
    def __init__(self, name):
        self.name, self.errors, self.warnings = name, [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def ids_of(items, what, r, required=("id",)):
    seen = set()
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            r.err(f"{what}[{i}] is not an object")
            continue
        for f in required:
            if it.get(f) in (None, ""):
                r.err(f"{what}[{i}] has no '{f}' — the app drops it")
        iid = it.get("id")
        if iid in seen:
            r.err(f"{what}: duplicate id {iid!r}")
        seen.add(iid)
    return seen


def check_colors(items, what, r, fields=("color", "textColor", "borderColor")):
    for it in items:
        if isinstance(it, dict):
            for f in fields:
                if f in it and it[f] is not None and not (isinstance(it[f], str) and HEX.match(it[f])):
                    r.warn(f"{what} {it.get('id')!r}: {f} {it[f]!r} is not #rgb/#rrggbb — dropped")


# --------------------------------------------------------------------------
# Per-mode structure; each returns the number of Present steps
# --------------------------------------------------------------------------
def check_node_edge(mode, st, r):
    nodes, edges = st.get("nodes"), st.get("edges", [])
    if not isinstance(nodes, list) or not nodes:
        r.err("state.nodes must be a non-empty list")
        return 0
    if not isinstance(edges, list):
        r.err("state.edges must be a list")
        edges = []
    grid = st.get("layout") == "grid"
    ids = ids_of(nodes, "nodes", r)
    allowed = GRAPH_MODES.get(mode) or FORK_MODES.get(mode)
    allowed = allowed | BASIC_SHAPES | (GRAPH_EXTRAS if mode in GRAPH_MODES else set())
    lane_ids = set()
    if mode in ("swimlane", "kanban"):
        lanes = st.get("lanes")
        if not isinstance(lanes, list) or not lanes:
            r.warn("state.lanes is empty — the app inserts default lanes")
            lanes = []
        lane_ids = ids_of(lanes, "lanes", r)
    for n in nodes:
        if not isinstance(n, dict):
            continue
        nid = n.get("id")
        t = n.get("type")
        if t and t not in allowed:
            r.warn(f"node {nid!r}: type {t!r} is not a {mode} shape — it opens as the default shape")
        for f in ("gc", "gr"):
            if f in n and not num(n[f]):
                r.err(f"node {nid!r}: {f} must be a number — never null (null reads as cell 0)")
        if mode == "kanban":
            if not num(n.get("x")):
                r.err(f"node {nid!r}: kanban cards need a numeric x (any value; the column decides)")
        elif mode == "swimlane":
            if not num(n.get("x")) and not num(n.get("gc")):
                r.err(f"node {nid!r}: swimlane nodes need numeric x or gc")
        else:
            if not (num(n.get("x")) and num(n.get("y"))):
                if grid and num(n.get("gc")) and num(n.get("gr")):
                    r.warn(f"node {nid!r}: add fallback x/y beside gc/gr (x = 120 + gc*260, y = 110 + gr*160)")
                else:
                    r.err(f"node {nid!r}: numeric x and y are required")
        if mode in ("swimlane", "kanban"):
            if n.get("laneId") not in lane_ids:
                r.warn(f"node {nid!r}: laneId {n.get('laneId')!r} is not a lane — it lands in the first lane")
            elif mode == "swimlane" and num(n.get("yInLane")):
                lane = next(l for l in st["lanes"] if isinstance(l, dict) and l.get("id") == n["laneId"])
                hgt = lane.get("height", 160) if num(lane.get("height", 160)) else 160
                if not 20 <= n["yInLane"] <= hgt - 20:
                    r.warn(f"node {nid!r}: yInLane {n['yInLane']} falls outside its {hgt}-high lane (use about {hgt // 2})")
        if "parentId" in n:
            pid = n["parentId"]
            box = next((m for m in nodes if isinstance(m, dict) and m.get("id") == pid), None)
            if not box or box.get("type") not in CONTAINERS.get(mode, set()):
                r.warn(f"node {nid!r}: parentId {pid!r} is not a container in {mode} — dropped")
    boxes = [n for n in nodes if isinstance(n, dict) and n.get("type") in ("group", "boundary", "trustBoundary", "composite")]
    if boxes and not st.get("order"):
        last = [n.get("id") for n in nodes[-len(boxes):] if isinstance(n, dict)]
        if any(b.get("id") not in last for b in boxes):
            r.warn("list containers (group/boundary) LAST in nodes — they are steps too, revealed after what they hold")
        if any(b.get("type") != "composite" and not b.get("back") for b in boxes):
            r.warn("give containers \"back\": true so arrows are drawn above them")
    check_colors(nodes, "node", r)
    for i, e in enumerate(edges):
        if not isinstance(e, dict):
            r.err(f"edges[{i}] is not an object")
            continue
        if e.get("from") not in ids or e.get("to") not in ids:
            r.err(f"edge {e.get('id')!r}: from/to must both name existing nodes — the edge is dropped")
        k = e.get("kind")
        if k is not None and mode in EDGE_KINDS and k not in EDGE_KINDS[mode]:
            r.warn(f"edge {e.get('id')!r}: kind {k!r} is not one of {sorted(EDGE_KINDS[mode])}")
        if "style" in e and e["style"] not in ("solid", "dashed", "dotted"):
            r.warn(f"edge {e.get('id')!r}: style must be solid, dashed or dotted")
        if "prob" in e and not (num(e["prob"]) and 0 <= e["prob"] <= 1):
            r.warn(f"edge {e.get('id')!r}: prob must be 0..1")
    ids_of(edges, "edges", r, required=("id",))
    order = st.get("order") or []
    for o in order:
        if not (isinstance(o, dict) and o.get("t") in ("n", "e")):
            r.err("order entries must look like {\"t\": \"n\", \"id\": \"...\"}")
    listed = {o.get("id") for o in order if isinstance(o, dict) and o.get("t") == "n"}
    attacks = sum(1 for e in edges if isinstance(e, dict) and e.get("attack")) if mode == "threatmodel" else 0
    return len(order) + len(ids - listed) + attacks


def check_sequence(st, r):
    actors, items = st.get("actors"), st.get("items")
    if not isinstance(actors, list) or not actors:
        r.err("state.actors must be a non-empty list")
        actors = []
    if not isinstance(items, list):
        r.err("state.items must be a list")
        return 0
    aids = ids_of(actors, "actors", r, required=("id", "name"))
    for a in actors:
        if isinstance(a, dict) and a.get("kind", "participant") not in SEQ_KINDS:
            r.warn(f"actor {a.get('id')!r}: kind must be one of {sorted(SEQ_KINDS)}")
    ids_of(items, "items", r, required=("id", "type"))
    depth = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        t, iid = it.get("type"), it.get("id")
        if t not in SEQ_ITEMS:
            r.err(f"item {iid!r}: type {t!r} is not one of {sorted(SEQ_ITEMS)}")
        if t == "message":
            gate = it.get("gate")
            if gate != "found" and it.get("from") not in aids:
                r.err(f"message {iid!r}: from {it.get('from')!r} is not an actor")
            if gate != "lost" and it.get("to") not in aids:
                r.err(f"message {iid!r}: to {it.get('to')!r} is not an actor")
            if it.get("style", "sync") not in ("sync", "async", "reply"):
                r.warn(f"message {iid!r}: style must be sync, async or reply")
        if t in ("note", "ref", "activate", "deactivate", "invariant") and it.get("actor") not in aids:
            r.err(f"{t} {iid!r}: actor {it.get('actor')!r} is not an actor")
        if t == "fragStart":
            depth += 1
            if it.get("kind") not in FRAG_KINDS:
                r.warn(f"fragment {iid!r}: kind must be one of {sorted(FRAG_KINDS)}")
        if t == "fragEnd":
            depth -= 1
            if depth < 0:
                r.err(f"fragEnd {iid!r} has no matching fragStart")
                depth = 0
    if depth > 0:
        r.warn(f"{depth} fragment(s) never closed — the app appends the missing fragEnd")
    return len(items)


def check_people(mode, st, r):
    people = st.get("people")
    if not isinstance(people, list) or not people:
        r.err("state.people must be a non-empty list")
        return 0
    pids = ids_of(people, "people", r, required=("id", "name"))
    seen = set()
    for p in people:
        if not isinstance(p, dict):
            continue
        par = p.get("parent")
        if par is not None and par not in pids:
            r.warn(f"{p.get('id')!r}: parent {par!r} does not exist — becomes a root")
        elif par is not None and par not in seen:
            r.warn(f"{p.get('id')!r}: listed before its parent — Present reveals in array order")
        if p.get("kind", "person") not in ("person", "vacant", "contractor", "department"):
            r.warn(f"{p.get('id')!r}: kind must be person, vacant, contractor or department")
        if mode == "sitemap" and ("dept" in p or "status" in p):
            r.warn(f"{p.get('id')!r}: dept/status are org-chart fields — sitemap drops them")
        seen.add(p.get("id"))
    check_colors(people, "person", r)
    return len(people)


def check_mindmap(st, r):
    nodes = st.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        r.err("state.nodes must be a non-empty list — an empty mind map is replaced by a blank one")
        return 0
    nids = ids_of(nodes, "nodes", r, required=("id", "text"))
    if st.get("rootId") not in nids:
        r.err("state.rootId must name a node — without it the file is read as a concept map")
    for n in nodes:
        if not isinstance(n, dict):
            continue
        if n.get("parent") is not None and n["parent"] not in nids:
            r.warn(f"node {n.get('id')!r}: parent {n['parent']!r} does not exist")
        if n.get("shape", "rounded") not in ("rounded", "ellipse", "plain", "cloud", "hexagon"):
            r.warn(f"node {n.get('id')!r}: shape must be rounded, ellipse, plain, cloud or hexagon")
        if st.get("rootId") is not None and n.get("parent") == st.get("rootId") and n.get("side") not in ("left", "right"):
            r.warn(f"node {n.get('id')!r}: set side to left or right on the root's children (default is right)")
    links = st.get("links") or []
    for l in links:
        if isinstance(l, dict) and (l.get("from") not in nids or l.get("to") not in nids or l.get("from") == l.get("to")):
            r.err(f"link {l.get('id')!r}: from/to must be two different existing nodes")
    if st.get("theme") and st["theme"] not in THEMES:
        r.warn("mind maps reset an unknown theme to classic")
    order = st.get("order")
    return len(order) if order else len(nodes) + len(links)


def check_timeline(st, r):
    ev = st.get("events")
    if not isinstance(ev, list) or not ev:
        r.err("state.events must be a non-empty list")
        return 0
    eids = ids_of(ev, "events", r)
    for e in ev:
        if isinstance(e, dict) and e.get("kind", "event") not in ("event", "milestone", "release", "deadline"):
            r.warn(f"event {e.get('id')!r}: kind must be event, milestone, release or deadline")
    for era in st.get("eras") or []:
        if era.get("from") not in eids or era.get("to") not in eids:
            r.err(f"era {era.get('id')!r}: from/to must be EVENT ids — the era is dropped")
    if st.get("track") and st["track"] not in ("line", "rail", "chevron", "arrows", "capsule"):
        r.warn("track must be line, rail, chevron, arrows or capsule")
    return len(ev)


def check_gantt(st, r):
    tasks = st.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        r.err("state.tasks must be a non-empty list")
        return 0
    tids = ids_of(tasks, "tasks", r)
    if st.get("startDate") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(st["startDate"])):
        r.err("startDate must be YYYY-MM-DD")
    for t in tasks:
        if not isinstance(t, dict):
            continue
        for f in ("start", "days"):
            if f in t and not (isinstance(t[f], int) and t[f] >= 0):
                r.err(f"task {t.get('id')!r}: {f} must be a whole number of days >= 0 (an offset, not a date)")
        if "done" in t and not (num(t["done"]) and 0 <= t["done"] <= 100):
            r.warn(f"task {t.get('id')!r}: done is a percentage 0..100")
    by = {t.get("id"): t for t in tasks if isinstance(t, dict)}
    for d in st.get("deps") or []:
        if d.get("from") not in tids or d.get("to") not in tids or d.get("from") == d.get("to"):
            r.err(f"dep {d}: from/to must be two different task ids")
            continue
        a, b = by[d["from"]], by[d["to"]]
        if all(isinstance(x.get(f), int) for x in (a, b) for f in ("start", "days")) and b["start"] < a["start"] + a["days"]:
            r.warn(f"task {b.get('id')!r} starts on day {b['start']} but depends on {a.get('id')!r}, "
                   f"which ends on day {a['start'] + a['days']} — dependencies do not move tasks")
    if st.get("ganttStyle") != "premium":
        r.warn("set \"ganttStyle\": \"premium\" for the modern Gantt renderer")
    return len(tasks)


def check_venn(st, r):
    sets, items = st.get("sets"), st.get("items") or []
    if not isinstance(sets, list) or not sets:
        r.err("state.sets must be a non-empty list")
        return 0
    ids_of(sets, "sets", r)
    if len(sets) > 6:
        r.warn("more than 6 sets is hard to read and the editor will not add a 7th")
    for s in sets:
        if isinstance(s, dict) and not (num(s.get("cx")) and num(s.get("cy"))):
            r.warn(f"set {s.get('id')!r}: without cx/cy the sets line up in a row instead of overlapping")
    ids_of(items, "items", r)
    for it in items:
        if isinstance(it, dict) and not (num(it.get("x")) and num(it.get("y"))):
            r.err(f"item {it.get('id')!r}: numeric x and y are required — it is dropped")
    check_colors(sets, "set", r)
    return len(sets) + len(items)


def check_journey(st, r):
    stages, rows, cells = st.get("stages") or [], st.get("rows") or [], st.get("cells") or []
    if not stages:
        r.err("state.stages must be a non-empty list")
    sids = ids_of(stages, "stages", r)
    rids = ids_of(rows, "rows", r)
    kinds = {x.get("id"): x.get("kind", "text") for x in rows if isinstance(x, dict)}
    for x in rows:
        if isinstance(x, dict) and x.get("kind", "text") not in ("text", "emotion", "rating"):
            r.warn(f"row {x.get('id')!r}: kind must be text, emotion or rating")
    ids_of(cells, "cells", r)
    for c in cells:
        if not isinstance(c, dict):
            continue
        if c.get("rowId") not in rids or c.get("stageId") not in sids:
            r.err(f"cell {c.get('id')!r}: rowId/stageId must name a row and a stage — dropped")
            continue
        k = kinds.get(c["rowId"])
        if k == "emotion" and not (isinstance(c.get("score"), int) and -2 <= c["score"] <= 2):
            r.warn(f"cell {c.get('id')!r}: emotion rows need score -2..2")
        if k == "rating" and not (num(c.get("rating")) and 0 <= c["rating"] <= 100):
            r.warn(f"cell {c.get('id')!r}: rating rows need rating 0..100")
    return len(stages)


def check_story(st, r):
    scenes = st.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        r.err("a visual story needs scenes[]")
        return 0
    sids = ids_of(scenes, "scenes", r)
    for sid in st.get("sceneOrder") or []:
        if sid not in sids:
            r.err(f"sceneOrder names unknown scene {sid!r}")
    steps = 0
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        objs = sc.get("objects") or []
        oids = ids_of(objs, f"scene {sc.get('id')!r} objects", r)
        for o in objs:
            if isinstance(o, dict) and o.get("type") not in ("text", "bullets", "shape", "callout", "image", "icon", "connector", "diagram"):
                r.err(f"object {o.get('id')!r}: type {o.get('type')!r} is not a story object type")
        for s in sc.get("steps") or []:
            steps += 1
            for a in s.get("actions") or []:
                if a.get("objectId") not in oids:
                    r.err(f"step {s.get('id')!r}: action points at missing object {a.get('objectId')!r}")
    return steps


# --------------------------------------------------------------------------
def context_targets(mode, st):
    if mode == "sequence":
        return {("actor", a.get("id")) for a in st.get("actors") or [] if isinstance(a, dict)}
    if mode == "swimlane":
        return ({("lane", l.get("id")) for l in st.get("lanes") or [] if isinstance(l, dict)}
                | {("phase", p.get("id")) for p in st.get("phases") or [] if isinstance(p, dict)})
    if mode == "kanban":
        return {("column", l.get("id")) for l in st.get("lanes") or [] if isinstance(l, dict)}
    return set()


def check_narration(nar, steps, r, mode=None, st=None):
    if not isinstance(nar, dict):
        r.err("narration must be an object")
        return
    ctx = nar.get("__context")
    if ctx is not None:
        allowed = context_targets(mode, st or {})
        if not allowed:
            r.warn(f"__context only plays in sequence, swimlane and kanban — ignored in {mode}")
        for it in (ctx.get("items") if isinstance(ctx, dict) else None) or []:
            t = it.get("target") or {} if isinstance(it, dict) else {}
            if allowed and (t.get("kind"), t.get("id")) not in allowed:
                r.err(f"__context item {it.get('id')!r}: target {t.get('kind')}:{t.get('id')} does not exist")
            if not (isinstance(it, dict) and it.get("id") and isinstance(it.get("text"), str) and it["text"].strip()):
                r.err("__context items need an id and non-empty text")
    numbered = [k for k in nar if re.fullmatch(r"[1-9]\d*", k)]
    for k in numbered:
        if not (isinstance(nar[k], str) and nar[k].strip()):
            r.err(f"narration[{k}] must be a non-empty string")
    if numbered:
        missing = [str(i) for i in range(1, steps + 1) if str(i) not in nar]
        if missing:
            r.warn(f"narration covers {len(numbered)} of {steps} steps — missing {', '.join(missing[:12])}"
                   + (" …" if len(missing) > 12 else "") + " (Present goes quiet there)")
        extra = [k for k in numbered if int(k) > steps]
        if extra:
            r.warn(f"narration has lines for steps {', '.join(extra)} but the diagram has {steps} — never spoken")
    for k, v in nar.items():
        if re.fullmatch(r"__(why|tech)\d+", k) and not (isinstance(v, str) and 0 < len(v) < 4000):
            r.err(f"{k} must be a string under 4000 characters")
        if re.fullmatch(r"__img\d+", k) and not (isinstance(v, str) and IMG.match(v) and len(v) < 400_000):
            r.err(f"{k} must be a data:image/ base64 URI under 400,000 characters — otherwise silently dropped")
        if k == "__titleimg" and not (isinstance(v, str) and IMG.match(v) and len(v) < 700_000):
            r.err("__titleimg must be a data:image/ base64 URI under 700,000 characters")
        if k == "__titleimglayout" and (v not in ("stack", "side", "cover") or "__titleimg" not in nar):
            r.err("__titleimglayout must be stack, side or cover, and needs __titleimg")
        m = re.fullmatch(r"__imgpos(\d+)", k)
        if m and f"__img{m.group(1)}" not in nar:
            r.warn(f"{k} without __img{m.group(1)} is dropped")
    ac = nar.get("__audioclips")
    if ac is not None:
        voices = ac.get("voices") if isinstance(ac, dict) else None
        if not isinstance(voices, dict) or not voices:
            r.err("__audioclips.voices must be a non-empty object")
            return
        if len(voices) > 8:
            r.err("at most 8 voices")
        total = 0
        for vk, v in voices.items():
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", vk):
                r.err(f"voice key {vk!r} must be letters, digits, _ or -, max 32")
            clips = (v or {}).get("clips") if isinstance(v, dict) else None
            if not isinstance(clips, dict) or not clips:
                r.err(f"voice {vk!r} has no clips")
                continue
            if len(clips) > 400:
                r.err(f"voice {vk!r}: at most 400 clips")
            for sk, url in clips.items():
                if not (re.fullmatch(r"[1-9]\d*|__intro|__index|__outro", sk) or sk.startswith("__context:")):
                    r.err(f"voice {vk!r}: clip key {sk!r} must be a step number")
                if not (isinstance(url, str) and AUDIO.match(url) and ";base64," in url):
                    r.err(f"voice {vk!r} clip {sk}: not an accepted data:audio/…;base64 URI")
                    continue
                if len(url) >= 1_500_000:
                    r.err(f"voice {vk!r} clip {sk}: over 1,500,000 characters — dropped")
                total += len(url)
        if total >= 24_000_000:
            r.err("audio bundle over 24,000,000 characters — the WHOLE bundle is dropped")


def validate(path):
    r = Report(path)
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:  # noqa: BLE001 — report any parse failure
        r.err(f"not valid JSON: {e}")
        return r
    if not isinstance(d, dict):
        r.err("the file must be a JSON object")
        return r
    if d.get("app") != "flow-diagram":
        r.err('"app" must be exactly "flow-diagram"')
    if d.get("version") != 2:
        r.err('"version" must be 2')
    mode, st = d.get("mode"), d.get("state")
    if mode not in ALL_MODES:
        r.err(f"mode {mode!r} is not one of the 27: {', '.join(sorted(ALL_MODES))}")
        return r
    if not isinstance(st, dict):
        r.err('"state" must be an object')
        return r
    if st.get("theme") and st["theme"] not in THEMES:
        r.warn(f"theme {st['theme']!r} is unknown — it renders as classic")
    if mode in GRAPH_MODES or mode in FORK_MODES:
        steps = check_node_edge(mode, st, r)
    elif mode == "sequence":
        steps = check_sequence(st, r)
    elif mode in ("orgchart", "sitemap"):
        steps = check_people(mode, st, r)
    else:
        steps = {"mindmap": check_mindmap, "timeline": check_timeline, "gantt": check_gantt,
                 "venn": check_venn, "journeymap": check_journey, "visualstory": check_story}[mode](st, r)
    if "narration" in st and mode != "visualstory":
        check_narration(st["narration"], steps, r, mode, st)
    r.steps = steps
    return r


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    bad = 0
    for p in argv:
        r = validate(p)
        status = "FAIL" if r.errors else "OK"
        print(f"{status}  {p}" + (f"  ({getattr(r, 'steps', 0)} steps)" if not r.errors else ""))
        for e in r.errors:
            print("   ERROR", e)
        for w in r.warnings:
            print("   WARN ", w)
        bad += bool(r.errors)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
