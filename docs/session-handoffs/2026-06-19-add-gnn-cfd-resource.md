# Session handoff — Add GNN surrogate paper to CFD resources

**Date:** 2026-06-19
**Session scope:** Single-task — add a LinkedIn-sourced research reference to the CFD domain resource catalog.
**Repo:** `workspace-hub` (branch: `main`)
**External actions:** none (no commits pushed, no issues created, no email/web mutations).

## What was requested

> "add this to CFD: <LinkedIn post by Gabriel Weymouth about a graph neural network>"

URL: `https://www.linkedin.com/posts/gabriel-weymouth-3a312489_how-fast-do-you-think-a-graph-neural-network-share-7473156153926098947-3-DR/`

## What the post is

A Graph Neural Network (GNN) **surrogate model** that predicts pressure and friction
stresses on ship hulls **~1M–100M× faster than RANS CFD**, with physical insight/constraints
embedded so it generalizes to hulls outside the training distribution (OOD).
Authors: **Sankalp Jena, Andrea Coraddu, Artur Lidtke**; presented at the Symposium on
Naval Hydrodynamics. The precursor foil-application research is published online; the full
ship-hull paper was not yet published at post time (2026-06).

## Change made (footprint = 2 files)

The CFD resources page is **auto-generated**, so the durable edit is to the source catalog:

1. **`data/document-index/online-resource-registry.yaml`** (+22/−4)
   - New entry `id: gnn_ship_hull_stress_surrogate_jena_2026`, inserted after the last
     `domain: cfd` entry (SU2 docs). Fields: `type: paper`, `domain: cfd`,
     `download_status: reference_only` (a research pointer, not a download target),
     `relevance_score: 5`, LinkedIn URL, full notes capturing the claim + authors + provenance.
   - Summary counts corrected to stay consistent: `by_type.paper` 31→32,
     `by_domain.cfd` 12→13, `by_download_status.reference_only` 9→10, and `total_entries`
     set to the **verifiable true count 250** (the header was already drifted by one before
     this edit — it read 248 while 249 entries actually existed).

2. **`docs/resources/cfd-resources.md`** — regenerated via
   `uv run --no-project python scripts/data/generate-domain-resource-views.py`.
   New entry renders at the top of the CFD "Online Resources" table (score 5, 📄 reference_only).
   "Undownloaded Resources" correctly stays at 12 (reference_only is not a download gap).

## Verification

- YAML parses cleanly; `yaml.safe_load` reports 250 entries, 13 with `domain: cfd`, new entry present.
- Regenerated CFD view shows the entry and `Online Resources | 13`.

## Important note on blast radius

`generate-domain-resource-views.py` regenerates **all 16 domain views** in one run, not just CFD.
That run rewrote 13 other `docs/resources/*-resources.md` files because they were **stale**
relative to the current registry (committed views dated 2026-04-02; registry has since drifted).
Those 13 side-effect regenerations were **reverted to HEAD** to keep this session's footprint
scoped to CFD. They remain stale — a full `generate-domain-resource-views.py` regen is overdue
and should be done as its own deliberate change, not smuggled in under a CFD edit.

## Pre-existing residue (NOT from this session — left untouched)

The working tree on `main` carries ~200 unrelated dirty/untracked files from background
automation (cron): `.claude/memory/topics/*` mirrors, `config/ai-tools/provider-*.json`,
`docs/reports/provider-*`, solver/queue dashboards, etc. These were **not** created or
modified by this session and were deliberately left alone (per multi-agent commit
serialization + do-not-sweep rules).

## State at exit

- **Committed on `main`** (user approved "merge to main") via a **pathspec-scoped** commit
  covering only the three intended files (registry yaml + cfd view + this handoff). The ~200
  background-cron dirty/untracked files were deliberately excluded — not staged, not swept.
- Commit command used:
  ```bash
  git commit -m "data(resources): add GNN ship-hull surrogate (Jena et al.) to CFD catalog" -- \
    data/document-index/online-resource-registry.yaml docs/resources/cfd-resources.md \
    docs/session-handoffs/2026-06-19-add-gnn-cfd-resource.md
  ```
- **Push status:** see the session chat summary. Pushing `main` triggers the repo's pre-push
  gates (full pytest, check-all sibling layout); agent `--no-verify` on the default branch is
  auto-denied, so if the gate blocks, the push is handed to the user to run manually.

## Follow-ups

- A full `generate-domain-resource-views.py` regen is overdue (13 other domain views are stale
  since 2026-04-02). Do it as its own deliberate change.
- Optionally swap the LinkedIn URL for the DOI/arXiv link once the full ship-hull paper publishes.
