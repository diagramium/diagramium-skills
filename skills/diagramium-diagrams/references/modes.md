# Modes — the exact `state` for each of the 27 diagram types

Every mode loads through a **whitelist**: unknown per-item fields are
dropped silently, and an unknown node `type` quietly becomes the mode's
default shape. Use exactly the fields below. Each section ends with the
matching tested file in `examples/`.

**Contents**
- [Node-and-edge modes — shared rules](#node-and-edge-modes--shared-rules)
- [flowchart](#flowchart) · [processmap](#processmap) · [bpmn](#bpmn) ·
  [swimlane](#swimlane) · [kanban](#kanban) · [statemachine](#statemachine)
- [architecture](#architecture) · [c4model](#c4model) · [dataflow](#dataflow) ·
  [network](#network) · [threatmodel](#threatmodel) · [umlclass](#umlclass) ·
  [erdiagram](#erdiagram) · [usecase](#usecase)
- [conceptmap](#conceptmap) · [fishbone](#fishbone) · [decisiontree](#decisiontree) ·
  [visuallearning](#visuallearning)
- [sequence](#sequence) · [mindmap](#mindmap) · [orgchart](#orgchart) ·
  [sitemap](#sitemap) · [timeline](#timeline) · [gantt](#gantt) ·
  [venn](#venn) · [journeymap](#journeymap) · [visualstory](#visualstory)

---

## Node-and-edge modes — shared rules

Applies to every mode from `flowchart` through `visuallearning` below.

```json
"state": {
  "format": 2, "layout": "grid",
  "title": "…", "theme": "quartz",
  "nodes": [ { "id": "n1", "type": "process", "text": "Label", "gc": 0, "gr": 0, "x": 120, "y": 110 } ],
  "edges": [ { "id": "e1", "from": "n1", "to": "n2", "label": "yes" } ],
  "order": []
}
```

**Node fields** (all optional except `id`, `type`, `text`, position):

| field | meaning |
|---|---|
| `id` | unique string |
| `type` | the mode's shape (tables below), any of the [100 basic shapes](#basic-shapes), or `note` |
| `text` | the label; `\n` for a new line |
| `x`, `y` | **centre** of the shape, document units — required numbers |
| `gc`, `gr` | grid column / row (with `format: 2, layout: "grid"`); never `null` |
| `w`, `h` | size — leave out and the engine sizes the shape to its text |
| `color` | fill, `#rrggbb` |
| `textColor`, `borderColor` | `#rrggbb` |
| `borderStyle` | `solid` · `dashed` · `dotted` |
| `borderWidth`, `cornerRadius` (0–60), `fontSize`, `opacity` (0–1) | numbers |
| `fontFamily` | `sans` `serif` `mono` `rounded` `condensed` `geometric` `humanist` `editorial` `didone` `slab` `typewriter` `industrial` `handwriting` `handnote` `script` |
| `bold`, `italic`, `underline` | booleans |
| `align` | `left` · `center` · `right` |
| `fill` | `gradient` · `glass` (a fill *style*; the colour is `color`) |
| `shadow`, `glow`, `sketch` | booleans |
| `anim` | entrance in Explain: `fade` `draw` `grow` `slide` `pulse` `sketch` |
| `animFx` | looping motion: `pulse` `float` `bounce` `wiggle` `spin` `blink` `glow` |
| `borderFlow` | `true` = marching-dash outline |
| `back` | `true` = drawn beneath the connectors (containers, backdrops) |
| `parentId` | the container this node sits in (only where the mode has one) |
| `iconDef`, `iconTint` | an embedded icon (see format.md) |

**Edge fields**: `id`, `from`, `to` (both must exist or the edge is
dropped), `label`, `style` (`solid` · `dashed` · `dotted`), `color`,
`width` (0–8), `labelSize`, `labelAt` (`0.25` or `0.75` to move the label
off centre), `anim` (`flow` · `laser` · `surge` · `glow`), plus the
mode's own `kind` where listed.

**Step N** = `order[N-1]`. `order` is a list of `{"t": "n", "id": …}`;
nodes you do not list are appended **in `nodes` array order**. So with no
`order`, step N is simply the Nth node. Edges are not steps — each appears
once both its ends are visible. (Threat-model attack edges are the one
exception: each is an extra step at the end.) Write `nodes` in the order
the story should be told.

**Layout**: use the grid (see SKILL.md). Fallback `x = 120 + gc·260`,
`y = 110 + gr·160`. For diagrams with a container, use absolute `x`/`y`
instead (columns ≥ 240 apart, rows ≥ 150 apart, container top ≥ 170,
≥ 80 padding) and list the container last in `nodes`.

---

## flowchart

| type | shape |
|---|---|
| `process` (default) | step |
| `start`, `end` | terminators |
| `decision` | diamond — a yes/no question |
| `io` | data in / out |
| `document`, `database`, `delay`, `display`, `predefined`, `preparation`, `manualInput`, `manualOperation`, `internalStorage`, `card`, `loopLimit`, `connector`, `offPage`, `or`, `summingJunction` | standard flowchart symbols |
| `group` | a frame; children set `parentId` |
| `note` | annotation |

Edges: `style` is `solid` or `dashed` only; no `kind`. → `examples/flowchart.json`

## processmap

Types: `process` (default, "Task / activity"), `start`, `end`, `decision`
(gateway), `subprocess`, `io`, `document`, `database` (data store),
`delay`, `note`. Directed elbow connectors. → `examples/processmap.json`

## bpmn

Types — events: `bpmnStart`, `bpmnMessage`, `bpmnTimer`, `bpmnInter`,
`bpmnBoundary`, `bpmnEnd`, `bpmnError`, `bpmnTerminate`; activities: `task`
(default), `userTask`, `serviceTask`, `sendTask`, `receiveTask`,
`subprocess`; gateways: `bpmnGwX` (exclusive), `bpmnGwParallel`,
`bpmnGwInclusive`, `bpmnGwEvent`; data: `document`, `database`; `boundary`
= pool / lane (**a container** — children set `parentId`); `note`.

Edge `kind`: `sequence` (default) · `message` · `association`.

Pools do not resize: give the `boundary` explicit `w`/`h`, `"back": true`,
absolute positions for everything, and list it last in `order`.
→ `examples/bpmn.json`

## swimlane

Same node types as flowchart, plus:

```json
"lanes":  [ { "id": "L1", "name": "Employee", "height": 160, "color": "#…" } ],
"phases": [ { "id": "P1", "label": "Submit", "width": 260 } ],
"nodes":  [ { "id": "a", "type": "start", "text": "Submit receipt",
              "laneId": "L1", "yInLane": 80, "gc": 0, "x": 120 } ]
```

- Lanes stack top to bottom; `height` ≥ 80 (default 160).
- Phases are column headers left to right (`width` ≥ 90). No node field
  links a node to a phase — line columns up with `gc`.
- A node is placed by `laneId` (unknown → first lane), `yInLane` = the
  node's centre below the lane's top (half the lane height centres it; keep
  it ≤ lane height − 40), and `gc` for the column (fallback `x`). `y` is
  always recomputed.
- Give each step its own column (`gc` 0, 1, 2 …) and one phase per column
  if you use phases. A decision's outcomes go in the lanes that own them —
  the next column, in each owner's lane. List the main path first, the
  exception branch after it.
- `parentId` and `gr` are not used here.
→ `examples/swimlane.json`

## kanban

Same node types as flowchart (cards are usually `process`).

```json
"lanes": [ { "id": "todo", "name": "To do", "height": 260 } ],
"nodes": [ { "id": "k1", "type": "process", "text": "Sign-in page",
             "laneId": "todo", "yInLane": 50, "x": 0 } ]
```

- `lanes` are the **columns**, left to right; `height` is reused as the
  column **width** (≥ 180).
- Every card **needs a numeric `x`** (any value — the column re-centres it)
  or it is dropped. `yInLane` stacks cards: 50, 130, 210, …
- No grid, no phases, usually no edges.
→ `examples/kanban.json`

## statemachine

| type | meaning |
|---|---|
| `simple` (default) | a state |
| `initial`, `final` | start dot, end bullseye (use `"text": ""`) |
| `composite` | a state containing states (container; children set `parentId`) |
| `choice`, `junction`, `forkjoin`, `history`, `deepHistory`, `entryPoint`, `exitPoint`, `terminate` | UML pseudo-states |
| `group`, `note` | frame, annotation |

Extra node fields: `entry`, `exit`, `doAct` (strings shown in the state),
`orient` (`h` / `v` for `forkjoin`). Label transitions with the event
(`"label": "payment ok"`). → `examples/statemachine.json`

## architecture

Types: `client`, `mobile`, `webapp`, `apigateway`, `loadbalancer`, `service`
(default), `worker`, `ai`, `auth`, `database`, `cache`, `queue`, `storage`,
`external`, `cdn`, `monitoring`, and `group` (a boundary such as a VPC or
cluster — **a container**; children set `parentId`, give it `w`/`h` and
`"back": true`). Use `"anim": "flow"` or `"laser"` on edges to show traffic.
→ `examples/architecture.json`

## c4model

Types: `person`, `softwareSystem`, `container` (default), `component`,
`externalSystem`, `database`, `boundary` (visual only — not a container),
`note`. Extra node field `tech` (≤ 60 chars) shows as `[Container: tech]`.
Label every relationship with what flows ("JSON / HTTPS").
→ `examples/c4model.json`

## dataflow

Types: `entity` (external entity), `dfProcess` (default; numbered
automatically), `datastore`, `note`. Label every flow with the data that
moves. A flow between two non-process nodes is shown red as invalid — data
must pass through a process. → `examples/dataflow.json`

## network

Types: `internet`, `cloud`, `router`, `switch`, `firewall`, `loadbalancer`,
`wifi`, `vpn`, `server` (default), `database`, `nas`, `workstation`,
`mobile`, `printer`. Undirected links. Edge `kind`: `ethernet` (default) ·
`fiber` · `wireless` · `vpn` · `serial`. → `examples/network.json`

## threatmodel

Types: `externalEntity`, `actor`, `dfProcess` (default), `datastore`,
`cloud`, `trustBoundary` (visual only — give it `w`/`h`, `"back": true`),
`note`.

Threats ride on nodes **and** edges:

```json
"threats": [ { "id": "t1", "stride": "S", "sev": "high", "title": "Credential stuffing",
               "desc": "…", "mitigation": "Rate limits", "controls": "…" } ]
```

`stride` ∈ `S T R I D E`; `sev` ∈ `low medium high critical`. An edge with
`"attack": true` is drawn as an attack path and becomes an extra step at the
end of the show. → `examples/threatmodel.json`

## umlclass

One type: `umlClass` (plus `note`). **All members go in `text`**; a line
that is exactly `--` starts the next compartment:

```json
{ "type": "umlClass", "text": "Order\n--\n+ id: UUID\n+ total: Money\n--\n+ pay(): void" }
```

Put «interface» or «abstract» in the name line when relevant. Members are
plain text, one per line (`+ name: Type`, `- secret`, `# protected`). Edge `kind`:
`assoc` (default) · `inherit` · `realize` · `compose` · `aggregate` ·
`dependency`. For `inherit`/`realize` draw **from the child to the parent**;
`compose`/`aggregate` put the diamond at the **from** end (the whole).
→ `examples/umlclass.json`

## erdiagram

Types: `erEntity` (table, default), `entity` (weak entity), `note`. Columns
go in `text` after a `--` line; rows starting `PK`, `FK` or `UK` are styled
as keys:

```json
{ "type": "erEntity", "text": "orders\n--\nPK id\nFK customer_id\ncreated_at" }
```

Write one column per line, optionally with its type (`FK customer_id uuid`).
A column that is both key and reference is `PK FK user_id`; a composite key
is simply two `PK` lines. Mark a nullable column in words (`FK assignee_id
(nullable)`) — there is no separate flag.

Edge `kind` puts crow's-foot marks on both ends. Read the name **from →
to**: the first half is the mark at the `from` table, the second at the `to`
table.

| kind | at `from` | at `to` | typical use |
|---|---|---|---|
| `oneToMany` (default) | exactly one | many | customer → orders |
| `oneToOne` | one | one | user → profile |
| `manyToMany` | many | many | students ↔ courses (better: a join table) |
| `oneToZeroMany` | one | zero or many | order → optional notes |
| `zeroOneToMany` | zero or one | many | an optional FK, e.g. assignee → tasks |

Draw the relationship from the parent (referenced) table to the child (the
one holding the FK). Tip for the person: the ER editor can also import SQL
or DBML directly (**Import SQL / DBML** in its panel).
→ `examples/erdiagram.json`

## usecase

Types: `actor`, `usecase` (default), `boundary` (the system box — visual,
give it `w`/`h` and `"back": true`), `note`. Edge `kind`: `assoc` (default)
· `include` · `extend` · `generalize` · `dependency`. Actors sit outside the
boundary, use cases inside. → `examples/usecase.json`

## conceptmap

Types: `concept` (default), `subtopic`, `ellipse` (an example / instance),
`note`. **Label every link** with a verb phrase so each reads as a sentence
("Plants → *make* → Glucose"); unlabelled links are flagged. Document field
`focusQuestion` (≤ 240 chars) heads the map. → `examples/conceptmap.json`

## fishbone

Types: `effect` (the problem, at the head — right), `category` (a bone),
`cause`, `subcause`, `note`. There is no special spine renderer: the fish is
made by placement. Put the effect at the far right, categories above and
below on rows 0 and 2, causes beside their category; edges run cause →
category → effect. Classic categories: People, Process, Machines,
Materials, Measurement, Environment. → `examples/fishbone.json`

## decisiontree

Types: `decision` (square — a choice you make), `chance` (circle — luck),
`option` (default), `outcome` (a leaf), `note`. Node field `value` = the
payoff (a number) on outcomes; edge field `prob` (0–1) on a chance node's
branches. Expected values roll up automatically and the best branch is
highlighted. Probabilities out of one chance node should sum to 1.
→ `examples/decisiontree.json`

## visuallearning

A lesson made of rich cards, shown as a book or a carousel. Types:
`spotcard` (default), `explainer` (a full-frame scene), `rectangle`,
`ellipse`, `decision`, `database`, `note`. Empty lessons default to the
`drawingbook` theme.

```json
{ "id": "s1", "type": "spotcard", "text": "Card heading",
  "blocks": [
    { "k": "text", "text": "A paragraph." },
    { "k": "bullets", "text": "One\nTwo\nThree", "marker": "num", "anim": "pop" },
    { "k": "diagram", "text": "Browser -> Server\nServer -> Browser" },
    { "k": "img", "d": "data:image/jpeg;base64,…" }
  ] }
```

- `blocks` (≤ 14): `k` ∈ `heading` `text` `bullets` `diagram` `img`.
  `bullets` take one item per line, `marker` ∈ `dot` `dash` `check` `arrow`
  `num`, `anim` ∈ `appear` `float` `pop` `slide`. A `diagram` block is a tiny
  arrow diagram, one `A -> B` per line. Text blocks also take `bold`,
  `italic`, `color`, `align`.
- `explainer`: `text` (headline), `layout` ∈ `hero` `visual` `focus-diagram`
  `comparison` `scenario` `payoff`, `blocks`, optional `narration` string.
- One card per idea, 3–8 cards per lesson; a card holds a heading, a short
  paragraph (≤ 40 words) and up to ~5 bullets. Card order is `nodes` order.
- Place cards in a row on the grid (`gc` 0, 1, 2 … , `gr` 0). Edges between
  cards are optional — they draw the thread from one idea to the next in
  diagram view; book and carousel views paginate the cards in order
  regardless. Do not set `w`/`h`; cards size themselves. → `examples/visuallearning.json`

---

## sequence

Laid out automatically — no coordinates.

```json
"state": {
  "title": "…", "theme": "quartz",
  "actors": [ { "id": "user", "kind": "actor", "name": "User" } ],
  "items":  [ { "id": "m1", "type": "message", "from": "user", "to": "api", "text": "POST /login", "style": "sync" } ]
}
```

- **Actors** (left to right in array order) need `id` and `name`. `kind` ∈
  `participant` (default) `actor` `database` `boundary` `control` `entity`
  `queue` `collection`. Optional `color`, `icon` (an emoji).
- **Items** (top to bottom) need `id` and `type`:

| type | fields |
|---|---|
| `message` | `from`, `to` (actor ids), `text`, `style` ∈ `sync` (solid arrow) · `async` · `reply` (dashed return); optional `create`, `destroy`, `color`, `animLine` (`flow` `laser` `surge` `glow`); `gate: "found"` needs only `to`, `gate: "lost"` only `from` |
| `note` | `actor`, `pos` ∈ `over` `left` `right`, `text`; `actor2` spans two actors (with `over`) |
| `activate`, `deactivate` | `actor` |
| `fragStart` | `kind` ∈ `loop` `opt` `alt` `par` `break` `critical` `seq` `strict` `neg` `assert` `ignore` `consider`, `label` (the guard) |
| `fragElse` | `label` — the next branch of an `alt`/`par` |
| `fragEnd` | closes the innermost fragment |
| `ref` | `actor`, optional `actor2`, `text` |
| `divider` | `text` |

- Document options: `showNumbers` (number the messages), `showActivations`.
- `text` (messages, notes) and actor `name` accept `\n` for a second line.
- **Step N = `items[N-1]` — every item counts**, including notes,
  activations and every `fragStart` / `fragElse` / `fragEnd`. Number the
  narration against the items array, not the messages. Actors are not steps.
- Narrating the structural items: a `fragStart` line states the condition
  ("Now the outcome depends on whether the password matches."), a `fragElse`
  line introduces the alternative ("If it doesn't…"), and a `fragEnd` line
  sums up or moves on ("Either way, the app now knows."). A narrated diagram
  with few fragments reads best — use them where the branch matters.
→ `examples/sequence.json`

## mindmap

A **tree**, laid out automatically.

```json
"state": {
  "title": "…", "theme": "canvas", "rootId": "r",
  "nodes": [
    { "id": "r", "text": "Central idea", "shape": "ellipse" },
    { "id": "a", "text": "Branch", "parent": "r", "side": "left", "color": "#6d7cff" },
    { "id": "a1", "text": "Leaf", "parent": "a" }
  ],
  "links": [ { "id": "l1", "from": "a1", "to": "b1", "label": "relates to", "style": "dashed" } ]
}
```

- **`rootId` is required** — without it the file is read as a concept map.
- Nodes need `id` and `text`; `parent` = the parent's id (null for the root).
  Set `side` (`left` / `right`) on each **direct child of the root** —
  unset means right. `shape` ∈ `rounded` (default) `ellipse` `plain` `cloud`
  `hexagon`. Optional `color` (#rrggbb) per node.
- `links` are optional cross-links between branches (`style` `solid` /
  `dashed`).
- No `x`/`y` — the tree is laid out for you.
- **Step N = `order[N-1]`**, where `order` is
  `[{"t": "n", "id": "r"}, {"t": "n", "id": "a"}, …, {"t": "e", "id": "l1"}]`
  (`n` = node, `e` = cross-link). With no `order`: all nodes in array order,
  then all links. Simplest: omit `order` and list nodes depth-first (root,
  branch, its leaves, next branch…) so the show grows branch by branch.
→ `examples/mindmap.json`

## orgchart

Laid out automatically as a tree.

```json
"people": [
  { "id": "ceo", "name": "Ana Ruiz", "title": "Chief Executive" },
  { "id": "cto", "name": "Chen Wei", "title": "CTO", "parent": "ceo", "dept": "Engineering" }
]
```

- Needs `id` and `name`; `title` is the job line; `parent` = manager's id
  (omit for the top). `kind` ∈ `person` (default) `vacant` (open role)
  `contractor` `department` (a team box). Optional `dottedParent` (a
  secondary manager), `dept`, `status` (`online` `away` `busy` `offline`),
  `color`, `icon` (emoji), `photo` (`data:image/…`).
- **Step N = `people[N-1]`** — list managers before their reports.
→ `examples/orgchart.json`

## sitemap

Same shape as orgchart (`people`), read as pages: `name` = page title,
`title` = a note such as the URL, `kind` ∈ `person` (a page) `department`
(a section) `vacant` (planned) `contractor` (external link). No `dept` or
`status`. Step N = `people[N-1]`. → `examples/sitemap.json`

## timeline

Laid out automatically; **array order is chronological order** (dates are
labels, not sort keys).

```json
"state": {
  "title": "…", "theme": "editorial", "track": "chevron", "showGaps": true,
  "events": [ { "id": "e1", "date": "2025-01", "title": "Idea", "desc": "…", "kind": "event", "emoji": "💡" } ],
  "eras":   [ { "id": "p1", "label": "Build", "from": "e1", "to": "e2" } ]
}
```

- Event fields: `id`, `date` (free text; `YYYY-MM`, `YYYY-MM-DD`, `Q3 2025`
  or a year let `showGaps` print the time between events), `title`, `desc`,
  `kind` ∈ `event` `milestone` `release` `deadline`, `emoji`, `color`,
  `side` ∈ `auto` `up` `down`.
- `eras` shade a span; `from` / `to` are **event ids**.
- `track` ∈ `line` `rail` `chevron` `arrows` `capsule`; `layout` ∈
  `straight` `fold` (`fold` wraps long timelines into rows).
- **Step N = `events[N-1]`**. → `examples/timeline.json`

## gantt

```json
"state": {
  "title": "…", "theme": "quartz", "ganttStyle": "premium",
  "startDate": "2026-01-05", "showCritical": true,
  "tasks": [ { "id": "t1", "name": "Design", "start": 0, "days": 5, "done": 100 } ],
  "deps":  [ { "from": "t1", "to": "t2" } ]
}
```

- Always set `"ganttStyle": "premium"` (the modern renderer).
- `startDate` is `YYYY-MM-DD`. A task's `start` is a **whole number of
  calendar days after `startDate`** and `days` its duration in calendar days
  (weekends included — `showWeekends` only shades them). `days: 0` is a
  milestone diamond. `done` = percent complete. Compute dates before writing:
  a "6-week plan" is 42 calendar days; land milestones on weekdays.
- `deps` are finish-to-start arrows; they do not move tasks, so make the
  numbers agree (a dependant starts at or after its predecessor ends).
- `showCritical` highlights the critical path. Optional: `showToday`,
  `showWeekends`, `ganttAxisScale` (`auto` `day` `week` `month`),
  `ganttDensity` (`compact` `comfortable` `spacious`).
- **Step N = `tasks[N-1]`**, one row each. → `examples/gantt.json`

## venn

```json
"sets":  [ { "id": "s1", "label": "Design", "cx": 380, "cy": 340, "r": 150 } ],
"items": [ { "id": "i1", "text": "Prototyping", "x": 470, "y": 340 } ]
```

- Sets need `cx`/`cy` to overlap (without them they sit in a row). Standard
  placements, `r: 150`: **2 sets** (380,340) and (560,340); **3 sets**
  (470,248), (550,386), (390,386). Up to 6 sets.
- Items need numeric `x` **and** `y`; an item's region is decided purely by
  where it sits. Put shared items in the overlap.
- **Step N**: sets first (in order), then items. → `examples/venn.json`

## journeymap

A grid: stages are columns, rows are lanes of information.

```json
"stages": [ { "id": "st1", "name": "Sign up" } ],
"rows":   [ { "id": "r1", "name": "Doing", "kind": "text" },
            { "id": "r2", "name": "Feeling", "kind": "emotion" },
            { "id": "r3", "name": "Satisfaction", "kind": "rating" } ],
"cells":  [ { "id": "c1", "rowId": "r1", "stageId": "st1", "text": "Creates an account" },
            { "id": "c2", "rowId": "r2", "stageId": "st1", "score": 1 },
            { "id": "c3", "rowId": "r3", "stageId": "st1", "rating": 80 } ]
```

- `stageWidth` (140–320, default 200) widens every column for longer text;
  keep a cell to about 60 characters.
- `kind`: `text` rows take `text`; `emotion` rows take `score` −2 … 2
  (frustrated → delighted, drawn as a curve); `rating` rows take `rating`
  0–100 (a bar).
- Every cell names a real `rowId` and `stageId`. Fill every row for every
  stage.
- **Step N = `stages[N-1]`** — a whole column at a time.
→ `examples/journeymap.json`

## visualstory

A story of slide-like scenes; objects appear by step. The `state` is a
story document:

```json
"state": {
  "type": "visual-story", "schemaVersion": 1, "title": "…", "theme": "quartz",
  "sceneOrder": ["s1"],
  "scenes": [ {
    "id": "s1", "title": "Intro", "aspectRatio": "16:9",
    "objects": [
      { "id": "o1", "type": "text", "x": 120, "y": 90, "width": 1040, "height": 90, "text": "Headline" },
      { "id": "o2", "type": "shape", "shape": "rounded", "x": 160, "y": 300, "width": 360, "height": 160,
        "text": "Box", "initialVisibility": false }
    ],
    "steps": [
      { "id": "st1", "title": "Reveal", "narration": { "text": "Spoken line." },
        "actions": [ { "id": "a1", "objectId": "o2", "type": "appear" } ] }
    ] } ]
}
```

- A 16:9 scene is 1280 × 720; `x`/`y` are the object's **top-left**.
- Object `type` ∈ `text` `bullets` (`items: [...]`) `shape` (`shape` = any
  basic shape name) `callout` `image` `icon` `connector` (`fromObjectId`,
  `toObjectId`) `diagram`. `style`: `fill`, `stroke`, `textColor`,
  `fontSize`, `fontFamily`, `radius`, `textAlign`.
- Objects a step reveals must start hidden: `"initialVisibility": false`.
- Action `type`: `appear` `disappear` `highlight` `dim` `move` `zoom`
  `focus` `draw-connector` `reveal-text` `pulse`.
- **Narration lives in each step** (`narration.text`, optional `why`), not in
  a `narration` map. → `examples/visualstory.json`

---

## Basic shapes

Every node-and-edge mode (and Visual Story's `shape`) also accepts these 100
general shapes as a `type`:

- **Basic**: rectangle roundRect squareBasic ellipse circleBasic semicircle
  donutBasic cylinderBasic cubeBasic triangle rightTriangle diamondBasic
  parallelogramBasic trapezoidBasic pentagonBasic hexagonBasic octagonBasic
  cross crossX lShape lightning cloudBasic folderBasic snipRect snipSameSide
  snipDiagonal roundOneCorner roundDiagonal foldedCorner bevel frameBasic
  halfFrame plaque diagonalStripe heptagonBasic decagon dodecagon hexagonV
  triangleDown pieBasic chordBasic arcBasic blockArc quarterCircle teardrop
  noSymbol crescent
- **Block arrows**: chevron arrowBlock arrowLeftBlock arrowUpBlock
  arrowDownBlock doubleArrow doubleArrowV arrowQuad arrowLeftRightUp arrowBent
  arrowBentUp arrowUTurn arrowStriped arrowNotched arrowCircular
  arrowCurvedRight arrowCurvedUp arrowCalloutRight arrowCalloutUp
- **Stars & banners**: star star4 star6 star8 star12 explosion1 explosion2
  sunShape ribbonUp ribbonDown scrollH scrollV wave doubleWave
- **Callouts**: callout calloutRect calloutRound calloutOval calloutCloud
  calloutLine
- **Math & brackets**: mathMinus mathDivide mathEqual mathNotEqual
  mathPlusMinus bracketLeft bracketRight braceLeft braceRight
- **Symbols**: smiley gearBasic personBasic flagBasic checkMark

The graph modes (architecture through visuallearning) additionally accept
blob speech thought ribbon bannerShape badge shield heartShape blockArrow
bracketShape braceShape lineH lineV arrowLine arrowBoth divider sticky
noteArea calloutNum. Prefer the mode's own vocabulary; reach for these only
when no domain shape fits.
