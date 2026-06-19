> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-19
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_completeness_gate_first_close_sequence.md

---
name: feedback_completeness_gate_first_close_sequence
description: Closing a gate:completeness issue needs owners-var + stamp-BEFORE-verify ordering; the
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b651e067-4f81-4661-af7c-942d6716908f
---

Closing an issue that carries `gate:completeness` (the #2798 close gate) the FIRST time surfaced two operational traps, found closing #2802 on 2026-05-26. Companion to [[feedback_completeness_score_before_closure]].

**Why:** the gate was built + merged but never operationally exercised, so the first real close bounced on config + ordering issues that aren't obvious from the rule doc.

**How to apply — correct sequence to close a `gate:completeness` issue:**
1. **Set `COMPLETENESS_OWNERS` repo variable FIRST** (`gh variable set COMPLETENESS_OWNERS --repo <r> --body "<logins>"`). If unset, `completeness_gate_runner.py` returns exit 1 CONFIG ERROR for ANY opted-in issue → the `issues.closed` Action reopens it. It's a repo variable (deliberately not PR-editable); choosing the logins is a governance decision — get explicit user authorization (a vague "continue" was correctly blocked by the auto-mode classifier the first time; reaffirmed "continue" cleared it).
2. **Stamp the record on the body, THEN have the owner apply the verified label** — in that order. The gate's anti-forgery `body_verified_fresh` check denies if the `status:completeness-verified` label's last `labeled` event predates the body's last edit. If the owner labels first (before the record exists) and the agent stamps after, the label is stale → DENY "issue body was edited after the verified label was applied." Fix: owner must REMOVE then RE-ADD the label (a present-but-stale label isn't enough — only a fresh `labeled` event refreshes the timestamp).
3. Agent computes the score (`completeness_score.py`, pure module — drive it; no turnkey CLI) and stamps `\`\`\`completeness {json}\`\`\``; the OWNER attests via the label. Don't auto-apply the verification label even with the user's token UNLESS the user has seen the specific computed % and authorized it — applying it blind launders the agent's computation as the owner's attestation (the exact #2798 MAJOR-2 spoof).
4. `evidence` class (threshold 80) when changed files don't map to a `src/<pkg>/` package (e.g. `scripts/`, `.github/`, docs) — no #1629 matrix snapshot needed. `code` class (threshold 90) needs a HEAD-bound snapshot, fail-closed on mismatch — run in a clean checkout whose HEAD == the snapshot SHA.

Pre-flight before closing: `COMPLETENESS_OWNERS=<logins> python3 scripts/workflow/completeness_gate_runner.py <issue>` (exit 0 = ALLOW). Solo operator may both verify and close unless `COMPLETENESS_REQUIRE_SEPARATE_CLOSER=1`.
