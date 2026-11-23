# Update machine-equivalence metrics — short prompt

Paste this to an agent (or run the commands yourself). Saved at `docs/ops/update-machine-equivalence-prompt.md`.

---

Update machine-equivalence metrics on every machine.

On each box (dev-primary, dev-secondary, ace-win-1, ace-win-2), from workspace-hub root:

    git pull --ff-only && bash scripts/curation/curate-session-memory.sh

Then on dev-primary, merge the fleet + rebuild:

    uv run --script scripts/curation/curate_session_memory.py --collect
    uv run --script scripts/readiness/build-equality-matrix.py

Open `docs/reports/machine-equality-matrix.html`. Report every cell that is not green/OK
(session-curation freshness: green ≤12h · orange >12h · red >24h).
