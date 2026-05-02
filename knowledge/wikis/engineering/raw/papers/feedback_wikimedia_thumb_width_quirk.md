> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_wikimedia_thumb_width_quirk.md

---
name: Wikimedia thumb URL — query API, never hand-construct
description: Wikimedia Commons thumbnail URLs only resolve at widths the cache has actually generated for that file; hand-constructing 800px-/1024px- URLs returns 400. Always query the imageinfo API for the canonical thumburl and verify with curl in the main session.
type: feedback
originSessionId: 548f0fc8-ec3a-4bb0-8291-cc056d20468b
---
**Rule:** When sourcing Wikimedia Commons thumbnail URLs for hot-linking, query the `imageinfo` API for the `thumburl` — never hand-construct the URL by inserting a width segment.

**Why:** On 2026-04-27, a research subagent constructed Switzerland Matterhorn and Landwasser Viaduct thumb URLs by hand using `/800px-<filename>.jpg` and reported them as "verified 200." Main-session re-verify showed both returned `400 Bad Request`. The hash prefixes (`6/6e`, `5/57`) were correct — the 800px width simply isn't a cached size for those specific files; the canonical bucket was 960px. Wikimedia generates thumb sizes per-file based on source dimensions; you can't predict which widths exist.

A separate issue: Wikimedia returns 403 to Python's default urllib User-Agent. Use curl with an explicit UA, or set the User-Agent header in Python.

**How to apply:**

1. For each filename, query: `curl -s -A "<UA>" "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&iiurlwidth=<desired>&format=json&titles=<urlencoded-File:filename>"`
2. Use the returned `thumburl` exactly. Wikimedia auto-bumps your requested width to the nearest cached size (e.g., 1024 → 1280 for one file, 800 → 960 for another).
3. Re-verify the URL in the **main session** with curl + real User-Agent before embedding. Subagent verification has been wrong twice.

**Codified in:** `.claude/skills/travel/visual-review-board/SKILL.md` (workspace-hub, committed 2026-04-27 at SHA `0722fa994`).

**Related:** `feedback_attestation_enables_contradiction_detection.md` (broader pattern: don't trust subagent claims for load-bearing facts).
