# Hermes Kanban — ecosystem source-of-truth

This directory is the cross-machine, git-tracked source-of-truth for every
Hermes kanban board across the repo ecosystem. The Hermes runtime (`~/.hermes/kanban.db`)
is per-machine local; this directory replays into it deterministically.

## Layout

```
.claude/memory/kanban/
├── SCHEMA.yaml          contract for board YAML (read this first)
├── README.md            this file
├── manifest.yaml        top-level index of all boards (slug → file)
├── boards/              one YAML per board (tier-0 + tier-1 + tier-2)
│   ├── ecosystem.yaml                       tier-0 master
│   ├── repo-digitalmodel.yaml               tier-1 repo board
│   ├── repo-digitalmodel-solver.yaml        tier-2 domain board
│   └── ...
├── gaps/                detected-gap cards awaiting GH-issue promotion
│   └── <repo>.yaml
└── scripts/
    └── load.py          idempotent loader: YAML → `hermes kanban` CLI
```

## Three-tier model

| Tier | Slug pattern             | Example                          | Purpose                                  |
|------|--------------------------|----------------------------------|------------------------------------------|
| 0    | `ecosystem`              | `ecosystem`                      | Cross-repo strategic themes              |
| 1    | `repo-<reponame>`        | `repo-digitalmodel`              | Per-repo board (one per active repo)     |
| 2    | `repo-<reponame>-<dom>`  | `repo-digitalmodel-solver`       | Domain sub-board inside a big repo       |

Each tier is an **isolated Hermes board** — its own dispatcher loop, its own task
ID space, its own queue. Tasks on `repo-digitalmodel-solver` cannot collide with
tasks on `repo-workspace-hub`.

## Safety: all imports land in `triage`

The loader passes `--triage` to every `hermes kanban create` call, so imported
tasks land in the **triage** column and workers **cannot auto-claim** them.
Promotion is explicit:

- `hermes kanban specify <task-id>`     — let aux LLM flesh out spec, promote to `todo`
- `hermes kanban decompose <task-id>`   — fan out into child tasks
- `hermes kanban edit <task-id>`        — manual promotion

This guards against the bulk-import dispatch hazard from
[[feedback_multi_agent_commit_serialization]] / runaway worker fan-out.

## GH issues are canonical

Per [[feedback_no_reserved_wrk_ids]], mirrored cards carry the GitHub issue ref
as their `idempotency_key`:

```
gh:vamseeachanta/digitalmodel#2289
```

Detected gaps that don't yet have GH issues use `gap:<board-slug>:<n>` and live
**in YAML only** until promoted to real GH issues — they are skipped by the loader.

## Running the loader

```bash
# preview, no mutations
uv run python .claude/memory/kanban/scripts/load.py --dry-run

# load a single small board first
uv run python .claude/memory/kanban/scripts/load.py --board aceengineer-website

# full load (idempotent; safe to re-run)
uv run python .claude/memory/kanban/scripts/load.py
```

Re-runnable: `--idempotency-key` makes existing tasks return their existing id
instead of duplicating. Adding new cards to a YAML and re-running appends only
the new ones.

## Cross-machine model

Per [[feedback_cross_machine_execution]], the Hermes kanban.db lives per-machine.
This directory is the shared spec. Workflow:

1. Edit YAML on any machine (or via subagent batch).
2. `git commit && git push`.
3. On every machine where you want the board state present: `git pull`, then
   `uv run python .claude/memory/kanban/scripts/load.py`.
4. Promotion / claim / dispatch decisions are **per-machine** and not synced
   back to YAML — YAML captures intent, not runtime state.

## Why not store cards in workspace-hub git directly as Hermes state?

Because the runtime state (claim_lock, worker_pid, run history, heartbeats) is
intrinsically machine-local and very chatty. Pushing it to git would create
merge conflicts every minute. The split is:

- **YAML in repo**  = stable intent (which boards exist, which cards belong on
  them, idempotency keys for upsert)
- **kanban.db local** = volatile runtime (status transitions, claims, runs)

This mirrors the [[feedback_html_default_artifact]] / data-format rule: agent-facing
structured state is YAML; runtime queues are SQLite.

## Augmented "gap" cards

Subagents that scanned each repo also surfaced un-issued work — TODOs in code,
stale PRs without tracking issues, README gaps, etc. These land in `gaps/<repo>.yaml`
**not** in `boards/`. Review and either:

- Promote: open a GH issue, move card into the relevant board YAML with the new
  `gh:` idempotency key.
- Reject: delete the entry.

Loader **never** touches `gaps/` — it's a holding pen.
