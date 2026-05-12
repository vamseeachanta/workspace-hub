---
name: gtm-artifact-layout-inconsistency
description: "Client-sendable GTM artifacts are scattered across repos and directory roots with no shared layout, naming, or bundle-format convention — searching one path misses bundles in others"
metadata: 
  node_type: memory
  type: project
  originSessionId: 03a317b6-3e5f-4d27-afe0-59f4521d774b
---

Client-sendable GTM material in workspace-hub is saved inconsistently across child repos and within workspace-hub itself. Searching a single canonical location (e.g., memory recall for `worldenergydata/reports/gtm/`) misses bundles delivered from other repos in the same week.

**Why:** Documented by user 2026-05-11 after I cited only two GTM bundle locations and missed a third (`digitalmodel/examples/demos/gtm/output/client_pdf_pack_2026-05-07/`). GTM material is high-leverage (sent to clients), so "where is the latest pack?" is a recurring question, and the current layout makes the answer non-deterministic.

**How to apply:**
- When user asks "where is the GTM material?", do NOT trust memory recall of a single path. Scan at least these layout patterns:
  - `<repo>/reports/gtm/` (worldenergydata pattern, date-prefixed filenames)
  - `<repo>/examples/demos/gtm/output/<bundle-dir>/` (digitalmodel pattern, date-suffixed directories with HTML+PDF pairs and a ZIP)
  - `workspace-hub/docs/gtm/sendable-bundles/<YYYY-MM-DD>/` (hub-level, date-named directory)
  - `workspace-hub/docs/reports/gtm/` (hub-level analysis/storyboards, date-prefixed filenames)
  - `workspace-hub/docs/gtm/` (strategy/planning docs — not client-sendable)
- Cross-check with `git log --since=<window> -- '*gtm*' '*GTM*'` across hub root and each child repo (each has its own `.git`).
- File: tracked in workspace-hub [#2662](https://github.com/vamseeachanta/workspace-hub/issues/2662) — `status:needs-plan`, awaiting plan draft.

**Concrete inconsistencies observed (2026-05-11 audit):**
- Three layout *roots*: per-repo `reports/`, per-repo `examples/demos/`, hub-level `docs/gtm/sendable-bundles/`.
- Three *date conventions*: filename prefix `YYYY-MM-DD-foo.html` (worldenergydata), directory suffix `client_pdf_pack_YYYY-MM-DD/` (digitalmodel), nested date directory `sendable-bundles/YYYY-MM-DD/` (hub).
- Three *bundle formats*: standalone HTML/notebook (worldenergydata), HTML+PDF pairs + ZIP + index page (digitalmodel), MD+HTML+PDF mix without index (hub).
- No shared `INDEX.md` or `MANIFEST.json` linking the artifacts a single client received in a given week.

Related: [[project_worldenergydata_gtm_state]] (partial, only covers worldenergydata pattern).
