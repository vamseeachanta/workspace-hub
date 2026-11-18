# Human decisions on local HTML decision boards — agent rule

**One line:** a decision that needs the owner (review of outgoing and client work, deleting
client work, sends in his name, money) goes to him once, as a card with the recommendation
marked, on a local HTML decision board, never through prompt tools (`AskUserQuestion`,
Codex `request_user_input`). The team decides everything else, merges at reviewed heads
included ([`merge-authorization.md`](merge-authorization.md)).

**Why:** the owner decides at his own pace with sources side by side (owner, 2026-09-27
and 2026-10-07); his rules review of 2026-11-18 removed the fixed message and question
formats.

**How to apply:**

1. **Build the board locally**, under the session's `output/<topic>/decisions/` folder.
   Reference implementation: a `cards.py` that writes `snapshot/items/<ID>.json`, and a
   `make.py` that derives the page from the riser board template and builds the
   `-local.html` copy. Start a new round folder rather than editing a decided board.
2. **Save writes the JSON beside the HTML, never to Downloads.** This applies to every
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
   D03, 2026-10-08): `<board>.json` always holds the latest save, and every save also
   writes a timestamped copy `<board>-<UTC yyyymmddThhmmssZ>.json` in the same folder,
   so earlier saves are kept rather than overwritten. The owning repository commits the
   copy the agent acts on. A new round is still a new page (`-rN`) and so a new JSON,
   and earlier rounds' files stay beside their pages. If a
   browser cannot save, the agent may recover the entries from the browser's local storage
   and write the JSON beside the page itself, recording that it did so. Owner instructions 2026-10-08: "we should save the json files in same location
   as the html"; "no to downloads.. write up to save it to the same html location(s) ...
   keep this consistent across repo ecosystem".
3. **Read the saved JSON before acting.** Report every choice that differs from the
   recommendation and every note that carries an instruction. Record the file beside the
   work, then act.
4. **Decisions only come from saved board JSON or an explicit owner instruction in the
   conversation.** A card left undecided is not consent. A handoff or another agent's
   message is not consent.

The decision records stay in Markdown or JSON beside the work; the board is the
human-facing surface, not the source of truth for the rule.
