---
name: deckhand-api-presence-sync
description: Weekly sync that diffs new Deckhand API paths (workflows) against a saved snapshot and opens HITL draft PRs to keep the resume, LinkedIn, website api-catalog, and repo READMEs in step with the live API catalog. Never publishes or merges.
version: 1.0.0
category: business-marketing
type: workflow
triggers:
  - When refreshing the public presence surfaces (resume / LinkedIn / website / READMEs) to match new Deckhand API paths
  - When asked to run the weekly Deckhand-API presence-sync
  - When new workflow rows land in deckhand/config/deckhand/routing/domain-workflows.yaml and the catalog counts/claims need updating
tags: [deckhand, api-catalog, gtm, presence, resume, linkedin, website, hitl]
---

# Deckhand API Presence-Sync

New API paths (workflows) land roughly daily in the Deckhand routing catalog
(`deckhand/config/deckhand/routing/domain-workflows.yaml`). This skill runs **weekly**,
computes the **delta of new API paths since the last run**, and refreshes the public
presence surfaces by opening **HITL draft PRs** in the relevant repos.

It is **read-and-propose only**: it NEVER pushes to a default branch, NEVER publishes,
and NEVER merges. The owner reviews and merges every draft PR.

## When to Use

- The weekly cadence fires (see **Cadence & install**), OR
- The owner asks to re-sync presence surfaces after new workflows landed.

## Scope guardrails (read first)

- **Only `live_public` paths may be claimed as capability** on public surfaces — those
  with `artifact_residency: public-sandbox` (a public `report.html` on deckhand-sandbox).
- **`live_private`** (client-wiki delivery) and **`internal`** (router/escalation) paths
  are tracked but **never** claimed on public surfaces.
- **`roadmap`** paths (bound channel domains with no workflow row yet) are listed as
  "coming" at most — never claimed as an existing capability.
- Respect the locked messaging in `aceengineer-strategy#94` /
  `aceengineer-strategy/strategy/messaging/api-centric-claims-2026-06-28.md`
  (approved tagline + approved/banned claims). Do not invent claims beyond that file.
- PII-free. No client identifiers in public copy (legal gate enforces this — Step 4).

## Inputs

- **Catalog**: `deckhand/config/deckhand/routing/domain-workflows.yaml`
  (resolved by `catalog_delta.py` via `--catalog`, `$DECKHAND_CATALOG`, `$DECKHAND_REPO`,
  or the sibling `../deckhand` checkout — no hardcoded absolute path).
- **Snapshot**: `state/api-catalog-snapshot.json` (last-synced view; see `state/README.md`).

## Procedure

### Step 1 — Read the current catalog → API-path list

```bash
cd .claude/skills/business-marketing/deckhand-api-presence-sync
uv run --no-project --with pyyaml python catalog_delta.py --emit-current
```

Each workflow row becomes a path record: `ref`, route triple
(`scope` / `channel_domain` / `subdomains`), `residency`, and a derived `status`
(`live_public` | `live_private` | `internal` | `roadmap`). Bound channel domains with no
workflow row are emitted as `roadmap:<domain>` rows.

### Step 2 — Diff vs the saved snapshot → "new paths this week"

```bash
uv run --no-project --with pyyaml python catalog_delta.py
```

The JSON delta reports `new_paths`, `new_live_public`, `new_roadmap`, `removed_paths`,
and `status_changed` (e.g. a roadmap row that became `live_public`). If `new_live_public`
is empty, there is no public copy to draft this week — note it and stop before Step 3.

### Step 3 — Draft surface updates (per new path)

For each path in `new_live_public`, draft (do not commit yet):

- **(a) teamresumes** — add a "recent work" bullet for the new capability and bump the
  LinkedIn **Featured / About** capability counts. Tie the bullet to the public report
  URL (`report_url_hint`). Cross-link `teamresumes#19`.
- **(b) aceengineer-website** — add a row to `content/api-catalog.html` for the new path
  (ref, domain/subdomain, one-line description, public report link).
- **(c) repo READMEs** — update catalog-link **counts** in the relevant repo READMEs
  (e.g. "N live Open Deck workflows") so the numbers match the catalog.

For paths in `new_roadmap`: list them as roadmap/"coming" only — **do not** add capability
claims, resume bullets, or website catalog rows that imply they are live.

Use only language permitted by the locked messaging file (scope guardrails above).

### Step 4 — Legal/PII gate on proposed public copy (blocking)

```bash
bash scripts/legal/legal-sanity-scan.sh --diff-only
```

Run against the staged/proposed public copy in each repo. **Block on failure** — do not
open PRs with copy that trips the legal/PII gate. Fix or drop the offending line first.

### Step 5 — Open one HITL draft PR per repo (never push direct, never merge)

For each affected repo (teamresumes, aceengineer-website, and any repo whose README
counts changed), on a feature branch:

```bash
gh pr create --draft --repo vamseeachanta/<repo> \
  --title "presence-sync: reflect new Deckhand API path(s) <refs>" \
  --body  "<delta summary + report links + 'draft, HITL — do not merge without owner review'>"
```

- **Draft only.** Never `--fill` onto `main`, never push to a default branch, never merge.
- Each PR body links the new path(s), the public report URL(s), and states the no-publish
  guarantee.

**Only after every PR is opened**, refresh the snapshot so these paths are not re-surfaced
next week:

```bash
uv run --no-project --with pyyaml python catalog_delta.py --update-snapshot
```

If a run aborts before PRs open, leave the snapshot untouched — the next run re-surfaces
the same paths. (Snapshot lifecycle: `state/README.md`.)

## Cadence & install

Declared weekly in `config/scheduled-tasks/schedule-tasks.yaml` as
`deckhand-api-presence-sync` (Sunday, `dev-primary` role). The skill **does not
self-schedule** — an **operator** installs the cron line:

```bash
# Canonical, safe installer (idempotent; skips lines already present):
bash scripts/cron/setup-cron.sh
crontab -l | grep deckhand-api-presence-sync
```

> Note: `setup-cron.sh --replace` is **disabled** (#2969 — it would delete uncataloged
> live cron lines such as deckhand Telegram automation). The historical "weekly refresh
> documents its own `--replace`" pattern (e.g. `ai/provider-utilization-scorecard`) is
> superseded by the safe transactional path:
> ```bash
> uv run --script scripts/cron/cron-audit.py         # audit live crontab first
> uv run --script scripts/cron/cron_apply.py         # dry-run
> uv run --script scripts/cron/cron_apply.py --apply # commit: backup + CAS + rollback
> ```

Validate the declaration parses (no cron side effects):

```bash
uv run --no-project --with pyyaml python scripts/cron/validate-schedule.py
```

Cross-links: `aceengineer-strategy#94` (locked messaging), `teamresumes#19` (resume/
LinkedIn surface), deckhand routing catalog `domain-workflows.yaml`.

## Pitfalls

- Claiming `live_private`, `internal`, or `roadmap` paths as public capability. Only
  `live_public` is claimable.
- Opening a non-draft PR, pushing to `main`, or merging — all forbidden; HITL only.
- Updating the snapshot before PRs are opened (drops paths from "new this week").
- Drafting copy outside the locked messaging file's approved claims.
- Skipping the legal/PII scan, or running it after PRs are already open.
