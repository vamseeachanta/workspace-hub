> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-14
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_offrepo_intel_routing.md

---
name: Off-repo intel routing for published repos
description: Side-channel notes (vendor marketing, intel sightings, future-attention parking) for a published repo go to /mnt/ace/<repo-name>/docs/, not the in-repo docs/
type: feedback
originSessionId: 16551784-4b91-4e6e-a344-efbed44673ec
---
For repos that are *published artifacts* (licensed corpus, public GitHub repo
with curated `docs/`), side-channel working material — vendor-marketing
captures, "is this useful?" sightings, future-attention parking, intel logs,
unciteable-but-suggestive references — routes to `/mnt/ace/<repo-name>/docs/`,
not the in-repo `<repo>/docs/`.

**Examples:**
- `vamseeachanta/llm-wiki` (CC-BY-4.0 corpus + curated governance/reports
  in `docs/`) → side-channel intel goes to `/mnt/ace/llm-wiki/docs/`.
- Pattern generalizes to other published repos: `/mnt/ace/<repo-name>/docs/`.

**Why:** Published repos have license boundaries and a curated public surface
even in `docs/` (governance, reports, schemas — part of the artifact, not a
scratchpad). Vendor-marketing captures and "future notes" can't carry the
license guarantee, will pollute the public history, and dilute the curated
docs/ surface. `/mnt/ace` is the household staging area for non-public
working material — same disk family as datasets, build outputs, archives.
The user stated this convention explicitly on 2026-05-07 after I put a
GeoSlipPro LinkedIn intel note into `llm-wiki/docs/external-intel.md`; the
correct destination was `/mnt/ace/llm-wiki/docs/external-intel.md`.

**How to apply:**

1. Before writing an `external-intel.md`, watchlist, vendor-sighting log, or
   "future notes" file inside a published repo's `docs/`, redirect the path
   to `/mnt/ace/<repo-name>/docs/<file>`. Run `mkdir -p` first since the
   side-channel directory may not exist yet.
2. Promotion path is one-way: a side-channel entry can later be rewritten
   as a properly-cited wiki page in the published repo when a non-vendor
   primary source is found. The reverse (taking published content
   off-repo) is rare and should be questioned.
3. Does **not** apply to internal/non-published repos (e.g., the kaggle
   competition repo `kaggle-rogii-2026`, which is private working scope).
   In-repo `docs/external-intel.md` is fine there because the whole repo is
   working material.
4. Heuristic for "is this repo published?": does it have a clear
   `LICENSE`/`LICENSE-CONTENT` pair, an explicit corpus directory like
   `wikis/`, an obvious public-audience README, or governance docs scoped
   to external contributors? If yes → route side-channel notes to
   `/mnt/ace/<repo-name>/docs/`.
