# Themes

Set `state.theme` to one key. A theme is the palette **and** the way the
diagram behaves in **Explain** — several draw the diagram in live with their
own pen, marker, train or typewriter. Every theme works in every mode and is
free. An unknown key renders as `classic` (a mind map also rewrites an
unknown key to `classic` in the file), so spell it exactly.

**A look the person names wins.** Subject rows below are only for when no
look is named; "hand-drawn OAuth flow" is `doodle`, not `terminal`.

## Choosing

| If the request says or implies… | theme |
|---|---|
| nothing in particular, professional, documentation, business | `quartz` |
| engineering, infra, security, dark mode | `obsidian` · `linear` |
| a premium product page, AI, a launch | `glassmorphism` · `aurora-v2` · `bento` |
| board, finance, strategy, executive | `executive` |
| research, science, history, an essay | `editorial` |
| friendly, onboarding, a workshop | `canvas` · `stickynote` |
| whiteboard, brainstorm | `marker` |
| hand-drawn, fun, for kids or students (non-lesson diagrams) | `doodle` · `sketchnote` |
| study notes, a handwritten explainer | `handnote` · `pencilsketch` |
| nature, health, sustainability | `forest` |
| a process or journey told as a route | `metro` |
| a system, platform or mission | `orbit` |
| a blueprint, engineering drawing | `drafting` |
| a command line, hacker, Linux | `terminal` |
| marketing, retro, nightlife | `neon` |
| a lesson or course of cards (`visuallearning`) | `drawingbook` · `notebook` |

Glassmorphism, Linear Midnight and Bento Card were designed for
architecture, product and engineering diagrams and look their best there.

## The modern themes

These are the themes in the editor's picker. Prefer them.

| key | name | tone | best for | what Explain does |
|---|---|---|---|---|
| `quartz` | Quartz | light | documentation, business — the safe default | clean step-by-step reveal |
| `obsidian` | Obsidian | dark | architecture, infrastructure, security | standard reveal, monospace chrome |
| `linear` | Linear Midnight | dark | high-end engineering; hairlines on black | a cyan laser pulse travels the connectors |
| `bento` | Bento Card | light | product and structure; white cards on a soft grid | indigo laser pulse on the connectors |
| `glassmorphism` | Glassmorphism | dark | premium products, AI | frosted panels over aurora light, violet pulse (sets the canvas to plain) |
| `aurora-v2` | Aurora | dark | AI and storytelling | glowing titles, glossy shapes |
| `editorial` | Editorial | light | research, education, explainers | serif, magazine feel |
| `canvas` | Canvas | light | workshops, planning, friendly products | soft clay shapes |
| `marker` | Marker | light | whiteboarding | **a chisel marker draws each step** |
| `forest` | Forest | light | calm, natural subjects | soft rounded chrome |
| `executive` | Executive Navy | light | boardroom, finance, strategy | serif, navy and gold |
| `doodle` | Doodle | light | fun explainers, teaching | **a pencil draws every shape and line** on notebook paper |
| `sketchnote` | Sketchnote | light | whiteboard-explainer infographics | **a pen sketches each step**; dashed connectors |
| `pencilsketch` | Pencil Sketch | light | monochrome graphite notes | **graphite pencil reveal** |
| `handnote` | Handwritten Notes | light | study notes, business explainers | **a fine pen writes each step on ruled paper**, the spoken step is highlighted, done steps get a check |
| `stickynote` | Sticky Notes | light | brainstorms, retros, agile boards | **a hand places each sticky**; voting dots |
| `terminal` | Terminal | dark | developer tutorials, Linux, auth flows | **the diagram types itself in**; scanlines |
| `metro` | Metro Map | light | journeys, onboarding, processes | **a train delivers each step to its station** |
| `orbit` | Mission Control | dark | systems, platforms, architecture | **modules dock in; a satellite orbits the narrated one**; starfield |
| `drafting` | Blueprint Atelier | dark | engineering, planning | **construction lines, then a pen inks each shape** |
| `neon` | Neon Diner | dark | marketing, story decks | **neon signs buzz on** |
| `notebook` | Notebook Novel | light | narrated courses (Spotlight cards) | a bound book opens and a ballpoint writes one card per page |
| `drawingbook` | Drawing Book | light | lessons (`visuallearning`) | an illustrated 16:9 book, one or two cards per page |

`notebook` and `drawingbook` are **book themes**: they paginate Spotlight
cards (`visuallearning`). On other diagram types prefer the rest.

## Legacy themes

Still supported, shown in the editor under "All legacy themes": palette
only, no special Explain experience.

`classic` · `ocean` · `sunset` · `mono` · `midnight` (dark) · `crayon` ·
`bubblegum` · `aurora` (dark) · `gold` · `slate` · `grape` (dark) · `coral`
· `handwriting` · `glass` · `blueprint` (dark) · `swiss` · `clay` ·
`papercut` · `ink` · `graffiti` · `chalkboard` (dark) · `deco` · `storybook`

## Pictures that match the theme

If you generate step pictures (`__img<N>`, see format.md) with an image
model, append the theme's picture style to every prompt — a photo inside a
doodle deck reads as a mistake:

| theme | picture style |
|---|---|
| `quartz` · `bento` | clean modern flat illustration, soft colour |
| `obsidian` · `linear` | dark UI-style render, cyan accents |
| `glassmorphism` · `aurora-v2` | soft luminous gradients, violet and teal glow |
| `editorial` | engraving / textbook plate |
| `canvas` | soft 3D clay render, rounded, pastel |
| `marker` · `sketchnote` | whiteboard marker sketch on white |
| `forest` | botanical or natural photography, greens |
| `executive` | muted corporate photography, navy and gold |
| `doodle` · `pencilsketch` | hand-drawn pencil doodle, white paper |
| `handnote` | neat pen-and-ink sketch on warm ruled paper |
| `stickynote` | flat marker illustration in sticky-note colours |
| `terminal` | phosphor-green schematic on black, scanlines |
| `metro` | flat transit-poster style, bold route colours |
| `orbit` | space render, starfield, blue glow |
| `drafting` | white linework on blueprint blue |
| `neon` | neon-sign art, pink and cyan on near-black |
| `drawingbook` · `notebook` | storybook ink-and-watercolour illustration |

## Document-wide look (optional)

These sit on `state` beside `theme` and override it:

- `sheetStyle` — the canvas: `plain` `dots` `grid` `ruled` `graph` `linen`
  `tooth` `diagonal`.
- `arrowAnim` — animate every connector: `flow` `laser` `surge` `glow`.
- `arrowWidth` (0–8), `arrowColor` (#rrggbb), `arrowStyle` (`dashed` /
  `dotted`), `arrowCorner: "smooth"`.
- `frame: true` (+ `frameStyle` `solid` `dashed` `dotted` `double` `corners`,
  `frameColor`, `frameFlow: true` for a marching border).
- `subtitle` (≤ 160 chars), `header`, `footer` — text above and below.
- `stageAspect: "portrait"` — a 9:16 show for phones and Reels.
