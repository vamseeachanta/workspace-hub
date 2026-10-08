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
3. **Save writes the JSON beside the HTML, never to Downloads.** This applies to every
   interactive HTML page across the repo ecosystem: decision boards, report comment
   copies and document review pages. The JSON is named after the page (`<page>.json`, or
   `<page> decisions.json`) and is written into the folder that holds the page, in every
   location the page is placed (for example the local output folder and the company
   share). The first Save asks once for that folder through the File System Access API
   (`showDirectoryPicker`); the page checks that the chosen folder contains the page
   itself and refuses any other folder; the folder handle is kept in IndexedDB and later
   Saves write straight to it. On opening, the page loads decisions already saved
   beside it. There is no Downloads fallback: a browser that cannot write to the folder
   gets a plain message and the entries stay in the tab. Save history (owner decision
   2026-10-08): a save overwrites the JSON within a round; a new round is a new page
   (`-rN`) and so a new JSON, and earlier rounds' files stay beside their pages. If a
   browser cannot save, the agent may recover the entries from the browser's local storage
   and write the JSON beside the page itself, recording that it did so. Owner instructions 2026-10-08: "we should save the json files in same location
   as the html"; "no to downloads.. write up to save it to the same html location(s) ...
   keep this consistent across repo ecosystem".
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
