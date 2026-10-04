# Using the skill as a ChatGPT Custom GPT

ChatGPT does not read Agent Skills folders, but a Custom GPT can carry the
same instructions and reference files.

1. In ChatGPT: **Explore GPTs → Create → Configure**.
2. **Name**: Diagramium Diagrams. **Description**: Editable, themeable,
   self-narrating diagrams you open in the free Diagramium editor.
3. **Instructions**: paste the whole of [`gpt-instructions.txt`](gpt-instructions.txt)
   (it is under ChatGPT's 8,000-character limit).
4. **Knowledge** — upload these files from `skills/diagramium-diagrams/`:
   - `references/modes.md`
   - `references/themes.md`
   - `references/format.md`
   - `scripts/validate.py`
   - the examples you care most about from `examples/` (all 27 fit; at
     minimum flowchart, sequence, architecture, mindmap, erdiagram, gantt)
5. **Capabilities**: turn on **Code Interpreter & Data Analysis** (to write
   the file and run the validator). Image generation is only needed if you
   want step pictures.
6. **Conversation starters** (optional):
   - Draw how OAuth sign-in works as a sequence diagram
   - Turn this SQL schema into an ER diagram
   - A hand-drawn flowchart of our refund process, with narration
   - A mind map for planning a product launch

Save, then try one of the starters: the GPT should hand back a `.json` file
and the one-line instructions for opening it.
