# state/ — presence-sync snapshot

`api-catalog-snapshot.json` is the **last-synced view** of the Deckhand API catalog
(`deckhand/config/deckhand/routing/domain-workflows.yaml`), normalized into API-path
records by `../catalog_delta.py`.

## What it is for

Each weekly run diffs the *current* catalog against this snapshot to find the
**new API paths since last run**. The skill drafts public-presence updates only for
**new `live_public` paths** (those with a public report on deckhand-sandbox). Roadmap
and client-private paths are tracked here but are never claimed as public capability.

## Lifecycle

1. The skill reads the live catalog and computes the delta vs this file (read-only).
2. It opens **HITL draft PRs** in the affected repos (resume / website / READMEs).
3. **Only after** the draft PRs are opened does it refresh this snapshot:
   `uv run --no-project --with pyyaml python catalog_delta.py --update-snapshot`.

This ordering guarantees a path is never dropped from "new this week" until its
draft PRs exist — if a run aborts before PRs open, the next run re-surfaces it.

## Seed

This file was seeded from the catalog as of the skill's creation so the **first real
run shows a clean (empty) delta**. Do not hand-edit; regenerate via `catalog_delta.py`.

## Fields (per path record)

- `ref` — workflow key (or `roadmap:<domain>` for bound-but-uncovered domains)
- `kind` — `workflow` | `roadmap`
- `scope`, `channel_domain`, `subdomains` — route triple
- `residency` — `public-sandbox` | `client-wiki` | `none`
- `status` — `live_public` | `live_private` | `internal` | `roadmap`
- `claimable_public` — true only for `live_public`
- `report_url_hint` — public report URL stub (live_public only)
