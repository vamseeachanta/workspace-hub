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
2. **Saves land in Downloads and the desk files them** (`intake/tools/file_owner_saves.py`).
3. **Read the saved JSON before acting.** Report every choice that differs from the
   recommendation and every note that carries an instruction. Record the file beside the
   work, then act.

The decision records stay in Markdown or JSON beside the work; the board is the
human-facing surface, not the source of truth for the rule.
