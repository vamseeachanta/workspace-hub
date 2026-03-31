# Repo Hygiene Triage

> **Status:** TRIAGE COMPLETE
> **Date:** 2026-03-31
> **Scope:** workspace-hub root plus child repository control-plane folders
> **Goal:** identify the highest-value cleanup work to reduce AI friction across the workspace ecosystem

---

## Executive Summary

The highest-leverage cleanup is not a broad file purge. It is control-plane consolidation.

The live workspace currently has **25 child Git repositories**, but core docs still describe a **26+ repo** ecosystem with a root **`.agent-os/`** control plane that no longer exists in `workspace-hub`. Child repositories are also in mixed states: some retain `.agent-os`, some only have `.claude`, some only have `.codex`, and `.specify` does not appear to be active in the current ecosystem.

This creates three main forms of AI friction:

1. **Repo selection friction**: docs point agents toward repos that are not present and omit repos that are present.
2. **Dispatch/orchestration friction**: there is no clearly enforced canonical control-plane contract across child repos.
3. **Noise friction**: the workspace root includes stray top-level artifacts and cross-platform leftovers that make inventory scans less trustworthy.

The immediate recommendation is to standardize on a single documented contract:

- `AGENTS.md` as canonical workflow contract
- `.claude/`, `.codex/`, and `.gemini/` as provider adapters where needed
- `.agent-os/` treated as legacy unless a repo has a confirmed active dependency on it

That direction matches the current operating guidance in `docs/modules/ai/MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md`.

---

## Audit Scope

This triage reviewed:

- workspace root layout
- child repo presence via nested `.git/`
- control-plane folders at repo root:
  - `.agent-os`
  - `.claude`
  - `.codex`
  - `.specify`
  - plugin-like leftovers
- docs inventory in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- root and child artifacts likely to increase AI confusion

This document is intentionally a **map for cleanup**, not the cleanup itself.

---

## Current State Snapshot

### Actual child repo inventory

Detected child Git repos:

- `CAD-DEVELOPMENTS`
- `OGManufacturing`
- `aceengineer-admin`
- `aceengineer-strategy`
- `aceengineer-website`
- `achantas-data`
- `achantas-media`
- `acma-projects`
- `assethold`
- `assetutilities`
- `client_projects`
- `digitalmodel`
- `doris`
- `frontierdeepwater`
- `heavyequipemnt-rag`
- `hobbies`
- `investments`
- `rock-oil-field`
- `sabithaandkrishnaestates`
- `saipem`
- `sd-work`
- `seanation`
- `simpledigitalmarketing`
- `teamresumes`
- `worldenergydata`

### Control-plane folder distribution

Observed patterns:

- `.claude` is present in most active repos.
- `.codex` is present in many, but not all, repos.
- `.agent-os` is present in a subset of repos and absent in others.
- `.specify` was not found in the scanned repo roots.

Examples of inconsistency:

- `digitalmodel`: `.claude`, `.codex`, no `.agent-os`
- `achantas-media`: `.codex`, no `.claude`, no `.agent-os`
- `aceengineer-strategy`: `.claude`, no `.codex`, no `.agent-os`
- `OGManufacturing`: `.agent-os`, `.claude`, `.codex`
- `simpledigitalmarketing`: `.claude` only
- `pyproject-starter`: `.codex` exists but there is no nested `.git/`, so it is not an active child repo in the current inventory

### Root-level clutter indicators

The root contains multiple likely accidental or stale artifacts that degrade trust in quick scans:

- zero-byte or malformed top-level names such as `B[Resource`, `C[Triage]`, `E{User`, `P[Archive]`
- `paraview.80s-478634,ace-linux-2.btr`
- `echo`
- `exit: `

These are high-confusion artifacts because they resemble partial workflow outputs or interrupted shell writes.

### Cross-platform leftovers

Observed examples:

- `aceengineer-admin/.DS_Store`
- `acma-projects/Thumbs.db`
- `aceengineer-admin/verify_claude_setup.bat`
- `acma-projects/sync_git.bat`
- `acma-projects/sync_git.ps1`
- `teamresumes/claude-flow.cmd`

These are not necessarily wrong individually, but they should be intentional, documented, and gitignored appropriately.

---

## Docs vs Actual Inventory

### High-confidence mismatches

`docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` is materially stale.

Repos referenced in the doc but not present as child Git repos:

- `energy`
- `ai-native-traditional-eng`
- `pyproject-starter`

Repos present as child Git repos but not reflected in the overview:

- `CAD-DEVELOPMENTS`
- `aceengineer-strategy`
- `heavyequipemnt-rag`
- `simpledigitalmarketing`

### Control-plane mismatch in docs

Multiple docs still describe the old model:

- root `.agent-os/` in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- root `.agent-os/` in `docs/README.md`
- `26+` repo language in:
  - `README.md`
  - `docs/README.md`
  - `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
  - `.claude/README.md`

This is now misleading because:

- root `workspace-hub` does not currently contain `.agent-os/`
- the live child repo inventory is 25, not 26+
- current provider behavior appears to center on `AGENTS.md`, `.claude`, `.codex`, and `.gemini`

### Internal strategy mismatch

There is a newer and more coherent direction already documented in `docs/modules/ai/MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md`:

- treat `AGENTS.md` as canonical
- treat provider folders as adapters
- avoid building or preserving multiple overlapping control planes

That strategy should become the primary documented workspace model.

---

## Prioritized Cleanup Recommendations

## Fix Now

### 1. Reconcile the official workspace inventory

**Why now:** Repo selection errors are one of the fastest ways to waste agent cycles.

Recommended actions:

- update `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` to match the actual 25 child repos
- update `README.md` and `docs/README.md` to remove stale `26+` language
- remove or explicitly mark legacy references to root `.agent-os/`

Expected value:

- less hallucinated repo routing
- lower chance of dispatching work to non-existent repos
- more reliable onboarding for both humans and agents

### 2. Define the canonical control-plane contract for child repos

**Why now:** the ecosystem is visibly mid-migration and lacks a crisp “source of truth”.

Recommended decision to document:

- `AGENTS.md` is canonical
- `.claude/` is the primary Claude adapter
- `.codex/` is the Codex adapter where needed
- `.gemini/` is the Gemini adapter where needed
- `.agent-os/` is legacy unless specifically required and documented per repo
- `.specify/` is not part of the active default contract

Expected value:

- reduced orchestration ambiguity
- easier repo bootstrap and audit automation
- fewer partial migrations

### 3. Remove or quarantine root-level accidental artifacts

**Why now:** these files pollute every inventory scan and make the root look unreliable.

Targets:

- malformed bracketed files
- stray zero-byte files
- `.btr` residue
- shell-like leftovers such as `echo` and `exit: `

Expected value:

- cleaner root scans
- fewer false positives during agent exploration
- easier distinction between intentional and accidental state

### 4. Create a single hygiene rule for OS-specific artifacts

**Why now:** cross-platform debris is already present across repos.

Recommended action:

- define a workspace-wide policy for `.DS_Store`, `Thumbs.db`, `desktop.ini`, `*.bat`, `*.cmd`, `*.ps1`
- separate “allowed platform tooling” from “accidental checked-in noise”

Expected value:

- lower clutter
- fewer ambiguous files during repo triage

## Fix Later

### 5. Normalize provider adapter presence by repo class

Not every repo needs every provider folder. The problem is undocumented variance.

Recommended later action:

- define repo classes such as:
  - full-control repos
  - minimal-doc repos
  - archive/reference repos
- specify which adapters are expected for each class

This avoids forcing `.codex` or `.gemini` into repos that do not benefit from them.

### 6. Audit `.mcp.json` usage and consolidate where possible

Several repos contain `.mcp.json`, but the workspace also has a root `.mcp.json`.

Recommended later action:

- determine whether child `.mcp.json` files are actively required
- collapse duplicates if the root config can safely cover them
- document exceptions explicitly

### 7. Reduce archive/state/report sprawl in the root repo

The root contains many state-bearing or archival directories:

- `_archive`
- `reports`
- `state`
- `logs`
- `queue`
- `notes`
- `coordination`
- `.planning`
- `.worktrees`
- `.sync-reports`
- `.swarm`
- `.hive-mind`
- `.SLASH_COMMAND_ECOSYSTEM`

This may be valid operationally, but without clear lifecycle rules it becomes hard to tell what is active, historical, ephemeral, or disposable.

Recommended later action:

- classify these into:
  - operational state
  - generated reports
  - archival history
  - transient scratch
- move transient outputs behind a smaller number of obvious containers

## Leave Alone

### 8. Keep provider-specific adapters where they reflect real behavioral differences

Do not force fake parity across providers just for symmetry.

Current guidance already supports thin adapters instead of one giant neutral control plane. That is the right default until there is evidence that parity work will pay off.

### 9. Keep intentional Windows helper scripts when they support real user workflows

Files like `sync_git.ps1` or `claude-flow.cmd` should not be deleted just because they are Windows-specific. They should only be cleaned up if they are unowned, unused, or undocumented.

### 10. Keep historical analysis docs if they remain explicitly marked as archive/reference

There are many old references to `.agent-os`, SPARC, and Claude Flow in archived or historical docs. Those do not all need immediate deletion. They do need clearer labeling so agents do not treat them as current policy.

---

## Suggested GitHub Issue Actions

## Create

### Create: “Canonical control-plane contract for workspace ecosystem”

Scope:

- define canonical control-plane layers
- mark `.agent-os` as legacy or approved-exception only
- define whether `.specify` is retired, deferred, or unsupported
- document required files for new repos

Why create:

- this is the highest-leverage missing policy

### Create: “Refresh workspace inventory and repository overview docs”

Scope:

- update repo count and repo list
- correct root control-plane references
- align overview with current operating model

Why create:

- fastest win for reducing AI routing mistakes

### Create: “Root workspace artifact cleanup and guardrails”

Scope:

- remove accidental root files
- add guardrails to prevent malformed shell/workflow residue from landing at repo root
- strengthen ignores if appropriate

Why create:

- root clutter currently degrades every exploration pass

### Create: “Cross-platform artifact policy and ignore baseline”

Scope:

- decide which Windows/macOS files are allowed
- update ignore patterns
- document allowed exceptions

Why create:

- prevents recurring hygiene drift

## Merge

### Merge duplicate or overlapping issues about provider-neutral control planes into the canonical control-plane issue

Reason:

- the current strategy is to keep one canonical workflow contract and thin provider adapters
- separate parity or abstraction issues will likely duplicate effort and keep the ecosystem half-migrated

### Merge old “standardize `.agent-os` everywhere” work into either:

- the canonical control-plane issue, if parts are still relevant
- or a legacy-deprecation issue, if the main value is removal rather than standardization

Reason:

- the evidence suggests `.agent-os` is no longer the universal future state

## Close

### Close issues that assume `.specify` is an active required control-plane dependency

Reason:

- current repo inventory shows no active `.specify` roots in the scanned ecosystem
- keeping these issues open encourages work against a non-canonical path

### Close issues whose success condition is “provider command parity everywhere”

Reason:

- this conflicts with the newer operating model that explicitly avoids heavy parity work

## Defer

### Defer broad archive/state/reports consolidation until the canonical control-plane decision is made

Reason:

- otherwise cleanup work may simply move clutter from one unclear area to another

### Defer per-repo adapter normalization until repos are classified

Reason:

- not every repo should necessarily carry the same adapter surface

---

## Proposed Execution Order

1. Refresh the workspace inventory docs.
2. Decide and publish the canonical control-plane contract.
3. Clean the root accidental artifacts.
4. Add cross-platform ignore/policy guardrails.
5. Audit per-repo exceptions and normalize only where needed.
6. Tackle larger archive/state/report consolidation after the policy layer is stable.

---

## Bottom Line

The biggest ecosystem hygiene problem is **not** archive volume or plugin leftovers by themselves. It is that the workspace currently presents **multiple overlapping control-plane stories**:

- older `.agent-os` / SPARC / Claude Flow framing in major docs
- newer `AGENTS.md` + provider-adapter framing in recent AI operating guidance
- inconsistent child repo implementation of both models

The highest-value cleanup work is therefore:

1. make the official story true
2. freeze the canonical contract
3. remove obvious root noise

Once those are done, the rest of the cleanup becomes straightforward and much lower risk.
