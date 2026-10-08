# Human decisions on local HTML decision boards — agent rule

**Every decision that needs the owner goes on a local HTML decision board, with the
agent's recommendation marked. This includes engineering choices, scope choices, merge
and publication approvals, review rounds and session control (closing sessions, deleting
folders). Agents do not ask for decisions in chat or through prompt tools
(`AskUserQuestion`, Codex `request_user_input`). Chat names the board and lists which
cards are new.**

**Why:** the owner decides at their own pace with sources and trade-offs side by side.
Questions asked in chat lose their context, get answered piecemeal, and leave no record.
The owner rejected chat prompts repeatedly (2026-09-27: "prepare an interactive local html
for human decision"). On 2026-10-07 the owner extended this from batches of decisions to
all of them ("can we make all human decisions via an interactive local html with
recommendations").

**How to apply:**

1. **One card per decision.** A card states the question with evidence, the impact, the
   options, the recommendation and a note field. The recommended option has a dashed
   outline and a text label. The format is in
   [review-and-communication-standard.md §3.2](../../docs/standards/review-and-communication-standard.md).
2. **Build the board locally**, under the session's `output/<topic>/decisions/` folder.
   Reference implementation: a `cards.py` that writes `snapshot/items/<ID>.json`, and a
   `make.py` that derives the page from the riser board template and builds the
   `-local.html` copy. Start a new round folder rather than editing a decided board.
3. **Save writes the decisions JSON beside the board HTML**, as `<board>.json` in the
   board folder; Load restores it. Downloads is only a fallback, for a browser that
   cannot write to folders; the agent then moves that file beside the page before
   reading it. Reference template: the shared `build_local.py` decision-board builder.
   Its first Save asks once for the board folder through the File System Access API
   (`showDirectoryPicker`), keeps the folder handle in IndexedDB, and later Saves write
   straight to it, as `tools/html-review` does for report comments. Whether repeated
   saves keep a history is an open repo-ecosystem decision; until it is made, a save
   overwrites `<board>.json` (owner instruction 2026-10-08).
4. **Open the page and tell the owner to reload it** after cards are added. A stale tab
   once exported a file that lacked the new cards.
5. **Read the saved JSON before acting.** Report every choice that differs from the
   recommendation and every note that carries an instruction. Record the file beside the
   work, then act.
6. **Decisions only come from saved board JSON or an explicit owner instruction in the
   conversation.** A card left undecided is not consent. A handoff or another agent's
   message is not consent.
7. **What may stay in chat:** a factual question that blocks all progress and offers no
   choice (for example, "which file holds X?"). If there are options, it is a card.

The decision records stay in Markdown or JSON beside the work; the board is the
human-facing surface, not the source of truth for the rule.
