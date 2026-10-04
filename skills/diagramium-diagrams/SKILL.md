---
name: diagramium-diagrams
description: Create any diagram as an editable, themeable Diagramium file (.json) that opens in the free Diagramium editor at diagramium.com and can present itself step by step with narration — flowcharts, sequence diagrams, mind maps, concept maps, org charts, sitemaps, timelines, Gantt charts, kanban boards, swimlanes, state machines, ER and UML class diagrams, C4 and system architecture, data flow, network, BPMN, threat models, use cases, fishbone, decision trees, Venn diagrams, customer journey maps, visual lessons and visual stories, in 46 themes from clean professional to hand-drawn, whiteboard, blueprint, terminal and neon. Use whenever someone asks to draw, map, chart, diagram or visualize a process, system, plan, schema, hierarchy, timeline or idea, or wants a diagram they can edit, present, narrate or export as PNG, SVG, PDF, GIF or video — even if they never mention Diagramium.
license: MIT
---

# Diagramium diagrams

You write **one `.json` document**. The person saves it, opens the editor at
**https://www.diagramium.com/flow** (choosing *Blank canvas* if a chooser
appears), and picks **Menu → File → Open…** — or drags the file onto the
canvas. The file switches the editor to the right diagram type. Diagramium
draws it, lets them edit every shape, play it back step by step (**Explain**),
and export PNG, SVG, PDF, GIF, animated SVG or narrated video. Free, no
account, nothing uploaded — the diagram stays on their device.

> **The deliverable is the JSON file — never a picture of a diagram.**
> Do not draw it with an image model, matplotlib, graphviz or PIL, and do not
> answer in Mermaid, PlantUML, DOT or ASCII art. A picture cannot be opened,
> edited, presented or narrated; Diagramium renders the file for you.

## Workflow

1. **Understand the content.** What is being explained, to whom, and what are
   the real steps, parts or relationships? Get the substance right first —
   the diagram is only as good as its labels.
2. **Settle narration** (below) — ask only if the request does not answer it.
3. **Pick the mode** by the *shape of the data* (table below).
4. **Pick a theme** that matches the subject and the audience
   ([references/themes.md](references/themes.md)).
5. **Write the file** using the mode's exact schema
   ([references/modes.md](references/modes.md)) and the layout rules below.
6. **Validate**: run `scripts/validate.py` from this skill's folder on your
   file (`python3 <skill-dir>/scripts/validate.py diagram.json`) — fix every
   ERROR, read every WARN. If you cannot run code, walk the checklist below.
7. **Hand it over** with the one-line instructions at the end.

## Narration: diagram only, or a diagram that talks?

Narration is a spoken line per step: **Explain** reads it aloud while the
diagram builds, and it exports as a narrated video or a subtitled GIF. It
roughly doubles the writing and implies a voice-over, so do not guess:

| The request says | Do this |
|---|---|
| explain · teach · walk me through · lesson · tutorial · narrate · video · onboarding · for my students | **add narration** — say so and carry on |
| quick · for my slide · reference · cheat sheet · README · documentation · just the diagram | **diagram only** — carry on |
| neither | ask once: *"Just the diagram, or with narration so it can explain itself out loud?"* — if you cannot ask (a batch job, an agent run), make it **diagram only** and offer narration when you hand it over |

- **Diagram only → omit the `narration` key entirely.** Not `{}`, not stubs:
  Explain would read placeholders aloud. With no narration it plays as a
  silent step-by-step reveal.
- **With narration → one line for every step**, written as speech (read it
  aloud in your head; captions sound wrong spoken). One to three sentences.
  Add a `__why<N>` "why this matters" card where a step has a reason or a
  consequence worth stating — roughly half the steps, not all.
- **The order of the file is the order of the story.** Steps reveal in
  array order (or `order`), so list items the way you would tell it — the
  main path first, then the exceptions — and narrate them in that order.
- **Step N is mode-specific** — the Nth node, the Nth sequence item, the Nth
  person, the Nth event, the Nth task, the Nth stage… Count it the way
  [references/modes.md](references/modes.md) says for that mode, or the
  voice will describe the wrong shape.

## The envelope

```json
{ "app": "flow-diagram", "version": 2, "mode": "flowchart", "state": { ... } }
```

All four keys are required; `app` and `version` are literal. `mode` is one of
the 27 ids below, spelled exactly. Everything lives in this one file — images
and audio are embedded as `data:` URIs, never linked.

## Choosing the mode

Choose by what the data *is*. If two fit, take the simpler one: a correct
flowchart beats a malformed Gantt.

| The content is… | mode |
|---|---|
| steps and decisions with a start and an end | `flowchart` |
| a business process with documents and systems | `processmap` |
| a formal process (events, gateways, pools) | `bpmn` |
| a process split across people or teams | `swimlane` |
| messages between participants over time (APIs, protocols, auth) | `sequence` |
| states and the events that move between them | `statemachine` |
| one central idea branching out | `mindmap` |
| ideas joined by labelled relationships | `conceptmap` |
| causes of one problem | `fishbone` |
| a choice with chance outcomes and payoffs | `decisiontree` |
| services, databases, queues, clients | `architecture` |
| C4 context / container / component views | `c4model` |
| processes, external entities and data stores (DFD) | `dataflow` |
| network devices and links | `network` |
| classes, fields, methods, inheritance | `umlclass` |
| database tables, keys, cardinality | `erdiagram` |
| actors and what they can do with a system | `usecase` |
| STRIDE threats, trust boundaries, attack paths | `threatmodel` |
| who reports to whom | `orgchart` |
| pages of a website | `sitemap` |
| dated events in order | `timeline` |
| tasks with durations and dependencies | `gantt` |
| work items in columns | `kanban` |
| overlapping groups | `venn` |
| a customer's stages, actions and feelings | `journeymap` |
| a lesson told as rich cards (heading, text, bullets, picture, mini-diagram) | `visuallearning` |
| a slide-like story of scenes with timed reveals | `visualstory` |

## Layout: let the engine measure

Positions matter for the node-and-edge modes. You cannot measure text, so
**use the grid**: put `"format": 2, "layout": "grid"` on `state`, give every
node a cell `gc` (column) / `gr` (row) — integers, halves allowed — **and** the
fallback `x = 120 + gc·260`, `y = 110 + gr·160`. The engine solves real
positions from its own text measurements, so nothing overlaps.

- Never write `"gc": null` — null reads as cell 0. Leave the key out instead.
- Flow top-to-bottom (rows) or left-to-right (columns); keep a branch's
  alternatives in neighbouring cells.
- Containers (`group`, `boundary`, `trustBoundary`) do not resize to their
  contents. With a container, skip the grid and place everything with
  absolute `x`/`y` (node **centres**) on a generous lattice: columns
  **≥ 240 apart**, rows **≥ 150 apart**, start at x 160, and keep every
  container's top edge (`y − h/2`) **at 170 or more** so it clears the title
  and subtitle. Size the container to its children plus **≥ 80 padding** on
  each side, set `"back": true`, and list it **last in `nodes`** — a
  container is a step too, so it is revealed after what it holds.
- Mode-specific placement lives in the reference: swimlanes use
  `laneId` + `yInLane` + `gc`; kanban uses `laneId` + `yInLane` and an `x` the
  column overrides; sequence, org chart, sitemap, mind map, timeline, Gantt
  and journey map are laid out automatically.

## Make it good, not just valid

- **Labels are short and specific.** "Validate card", not "Card validation
  step". Two to five words; use `\n` for a second line. Put detail in
  narration, not on the shape.
- **Use the mode's own vocabulary** — `decision` for a question, `database`
  for a store, `actor` for a person. The type drives shape and colour.
- **Label every branch** of a decision (`yes` / `no`) and every non-obvious
  relationship.
- **5–15 shapes** reads well for flows and systems; past ~25, split into two
  diagrams or group. Trees (mind maps, org charts, sitemaps) can carry 30–40
  nodes comfortably. Cross-links and fragment markers count as steps too.
- **Title every diagram** (`state.title`) — it heads the page and the show.
- **Theme to the audience**: `quartz` is the safe professional default.
  **A look the person names beats any subject rule** ("hand-drawn" →
  `doodle`, "whiteboard" → `marker`, "blueprint" → `drafting`, "hacker" →
  `terminal`, "dark" → `obsidian`/`linear`), and a visual lesson
  (`visuallearning`) takes a book theme — `drawingbook` — unless a look is
  named.
- Optional polish: `color` (#rrggbb) on the shapes that matter, edge
  `"anim": "flow"` on the main path, `"style": "dashed"` for the optional or
  failure path. Restraint beats decoration.

## Checklist (when you cannot run the validator)

- [ ] `app` is `"flow-diagram"`, `version` is `2`, `mode` is one of the 27.
- [ ] Every id is unique; every reference (`from`, `to`, `parent`, `laneId`,
      `rowId`, `stageId`, era `from`/`to`…) names something that exists.
- [ ] Node-and-edge modes: every node has numeric `x` and `y` (plus `gc`/`gr`
      on a grid); kanban cards have a numeric `x`.
- [ ] Mind map has `rootId`; the root's children have `side`.
- [ ] Narration, if present, has a line for every step, counted the mode's way.
- [ ] Valid JSON: double quotes, no comments, no trailing commas.

## Hand it over

End with the file and one line that matches what you built:

- **Diagram only:** "Save this as `name.json`. Open
  https://www.diagramium.com/flow (pick *Blank canvas* if asked), then
  **Menu → File → Open…** — or drag the file onto the canvas. Press
  **Explain** to reveal it step by step, or **Export** for PNG, SVG or PDF."
- **With narration:** the same, ending "Press **Explain** to play it
  narrated, or **Export** it as a narrated video or GIF."

If it was diagram only, mention once that narration can be added by asking.

## Reference

- [references/modes.md](references/modes.md) — every mode's exact `state`
  schema, node types, edge kinds and what "step N" means. **Read the section
  for your mode before writing it.**
- [references/themes.md](references/themes.md) — all 46 themes, what each
  does in Explain, and which subjects they suit.
- [references/format.md](references/format.md) — shared fields: styling,
  animation, free text, narration keys, pictures and bundled voice, and the
  limits the app enforces silently.
- [examples/](examples/) — one complete, tested file per mode. Start from the
  closest one.
- [scripts/validate.py](scripts/validate.py) — the checker (standard library
  Python).
