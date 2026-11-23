# Machine Repo Placement: Repo/Data Boundary

Use when deciding which tier-1 repositories belong on each workstation.

## Core rule

Separate **repo clone placement** from **large data residency**.

- Repo clone: local working tree used for code, tests, plans, docs, and agent execution.
- Data residency: raw/large datasets, knowledge corpora, generated heavy outputs, and mounted storage roots.

A workstation can host a tier-1 repo clone without hosting the repo's full raw data corpus.

## Recommended decision sequence

For each machine, decide interactively in this order:

1. Which tier-1 repo clones should exist locally?
2. Where is the local repo root? Prefer a local disk, not another machine's working tree.
3. Which large data roots are canonical elsewhere?
4. Should those data roots be mounted read-only, mounted read/write controlled, staged as subsets, or omitted initially?
5. What workload class justifies each repo/data decision?

Do not batch assumptions across machines when the user asked for interactive decisions. Finish one machine decision surface, then move to the next.

## Safety defaults

- Do not run development, tests, agent execution, commits, or package installs against another machine's live working tree.
- Use separate local clones per machine and reconcile through GitHub.
- Cross-machine access is acceptable for read-only inspection or controlled data mounts, not as a shared `.git` working directory.
- Prefer sample fixtures or bounded staged subsets for tests and smoke runs.
- Mount huge canonical data stores read-only/read-mostly unless a clear write workflow and conflict policy exists.

## Example pattern

For `worldenergydata` on a secondary Linux worker:

- local clone: `/mnt/local-analysis/worldenergydata`
- large raw data: canonical on the primary knowledge/data host, e.g. `/mnt/ace/worldenergydata`
- secondary access: mount canonical data as read-only/read-mostly or stage bounded subsets only when needed

This lets the worker run code/tests/agents locally without duplicating terabytes of raw data or touching another machine's live checkout.
