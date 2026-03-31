# Claude Prompt Pack: Repo Hygiene / Taxonomy / Consistency

> **Date:** 2026-03-31
> **Purpose:** reusable Claude prompts to execute the repo-hygiene feature and child issues
> **Primary Feature:** `#1530`
> **Child Issues:** `#1531` through `#1536`

---

## How To Use

Use these prompts when dispatching Claude to work on the workspace-hub repo hygiene program.

Important operating assumptions for all prompts:

- do not perform a broad cleanup pass without evidence
- investigate first, then implement only what is justified
- prefer small, reviewable changes tied to one issue at a time
- document exceptions explicitly instead of letting them remain implicit
- use `digitalmodel`, `worldenergydata`, `assethold`, and `assetutilities` as the starter convergence set
- long-term goal: all repos follow the same core structure and user/agent experience over time

---

## Shared Preamble

Use this preamble ahead of any issue-specific prompt:

```text
Work in /mnt/local-analysis/workspace-hub.

You are working on workspace ecosystem consistency for both humans and AI agents.

Operating rules:
- Investigate before changing anything.
- Do not perform a broad cleanup sweep.
- Keep changes scoped to the issue at hand.
- Prefer explicit documentation of standards, taxonomy, and exceptions.
- Treat AGENTS.md as part of the current control-plane reality and verify assumptions from the live repo state.
- Use digitalmodel, worldenergydata, assethold, and assetutilities as the starter convergence set unless the issue clearly requires a wider scan.
- Over time all repos should converge toward the same core structure and experience, with deviations documented as exceptions.

Expected output:
- findings
- decision or recommendation
- concrete changes made
- open questions / follow-ups
```

---

## Prompt: Feature #1530

```text
Work issue #1530 in /mnt/local-analysis/workspace-hub.

Goal: drive a structured repo-hygiene and taxonomy program for workspace-hub that produces a consistent filesystem and control-plane experience for both humans and AI agents.

Start from:
- docs/reports/repo-hygiene-triage-2026-03-31.md
- issue #1530
- related issues #1531 through #1536

Your job in this session:
- assess which child issue is the next highest-leverage step
- validate whether the current issue hierarchy still looks correct
- make only the scoped progress justified by the chosen child issue
- update docs or issue references if needed to keep the program coherent

Constraints:
- do not do broad cleanup
- do not remove non-obvious files without evidence
- keep the rollout anchored on digitalmodel, worldenergydata, assethold, and assetutilities first

Deliver:
- brief current-state assessment
- chosen next child issue and why
- scoped implementation or doc updates
- follow-up recommendations
```

---

## Prompt: Issue #1531

```text
Work issue #1531 in /mnt/local-analysis/workspace-hub.

Goal: reconcile workspace inventory docs with the actual repo inventory and current control-plane reality.

Investigate:
- docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md
- README.md
- docs/README.md
- .claude/README.md
- any other current-facing docs that claim 26+ repos or describe root .agent-os as active

Tasks:
- determine the actual current child repo inventory from the live filesystem
- identify all mismatches between docs and reality
- correct current-facing docs so they agree on repo count, repo list, and root control-plane structure
- preserve historical docs where needed, but clearly mark them as historical if they are no longer current policy

Constraints:
- fix current-facing documentation first
- do not rewrite archival material unless needed to prevent confusion

Deliver:
- exact mismatches found
- docs updated
- any remaining follow-up items that belong in another issue
```

---

## Prompt: Issue #1532

```text
Work issue #1532 in /mnt/local-analysis/workspace-hub.

Goal: define the canonical control-plane contract across the workspace ecosystem.

Starter repos:
- digitalmodel
- worldenergydata
- assethold
- assetutilities

Investigate:
- AGENTS.md
- root .claude, .codex, .gemini, .mcp.json
- control-plane folders in the starter repos
- any active docs describing provider adapters, .agent-os, .specify, or MCP expectations

Tasks:
- determine what should be canonical versus legacy
- define the expected role of AGENTS.md, .claude, .codex, .gemini, .mcp.json, and .agent-os
- identify which current repo variations are intentional and which are migration drift
- write or update the standard so a human or AI agent can reliably know what to read first in any repo

Constraints:
- do not force fake parity across providers
- do not remove legacy paths unless the evidence is strong and the issue scope supports it
- document exceptions explicitly

Deliver:
- recommended canonical contract
- documented starter-repo convergence plan
- clear list of legacy or exception states
```

---

## Prompt: Issue #1533

```text
Work issue #1533 in /mnt/local-analysis/workspace-hub.

Goal: define a workspace file-structure taxonomy that gives humans and AI agents the same predictable navigation model.

Starter repos:
- digitalmodel
- worldenergydata
- assethold
- assetutilities

Investigate:
- root workspace-hub top-level folders
- operational directories such as reports, state, logs, queue, notes, coordination, .planning, _archive
- starter repo top-level structures
- prior structure-related work if still relevant

Tasks:
- classify top-level workspace folders by purpose
- define naming expectations for active, generated, archival, and transient directories
- describe what should live at workspace root versus under docs/, reports/, state/, or repo-local paths
- define a starter taxonomy that can be applied to the four convergence repos first and then rolled out across the rest of the ecosystem

Constraints:
- avoid broad moves without a migration rationale
- prefer taxonomy clarity over premature reorganization

Deliver:
- taxonomy standard
- recommended migration map
- explicit notes on what can stay as an exception
```

---

## Prompt: Issue #1534

```text
Work issue #1534 in /mnt/local-analysis/workspace-hub.

Goal: investigate root-level accidental artifacts and define a safe cleanup or quarantine plan.

Investigate:
- suspicious root files and malformed names
- shell residue or zero-byte artifacts
- non-obvious leftover files such as .btr or partial workflow outputs

Tasks:
- classify each suspicious root artifact as keep, move, archive, quarantine, or delete
- gather evidence before recommending removal
- propose safeguards to prevent the same kind of artifact from landing in the root again

Constraints:
- do not delete non-obvious files without evidence
- prefer a documented cleanup plan if certainty is incomplete

Deliver:
- artifact classification table
- recommended cleanup actions
- proposed guardrails
```

---

## Prompt: Issue #1535

```text
Work issue #1535 in /mnt/local-analysis/workspace-hub.

Goal: define a cross-platform artifact policy and ignore baseline for workspace repos.

Starter repos:
- digitalmodel
- worldenergydata
- assethold
- assetutilities

Also inspect any obvious examples in other repos if they help clarify the policy.

Investigate:
- .DS_Store
- Thumbs.db
- desktop.ini
- *.bat
- *.cmd
- *.ps1
- existing gitignore coverage
- whether platform-specific scripts are intentional and documented

Tasks:
- separate accidental OS residue from intentional platform tooling
- propose ignore rules and policy language
- define how exceptions should be documented
- recommend how the starter repos should adopt the standard first

Constraints:
- do not remove legitimate Windows tooling just because it is Windows-specific
- optimize for explicit policy, not blanket deletion

Deliver:
- policy
- ignore baseline
- exception-handling guidance
```

---

## Prompt: Issue #1536

```text
Work issue #1536 in /mnt/local-analysis/workspace-hub.

Goal: consolidate overlapping hygiene and control-plane issues so this program stays focused and non-duplicative.

Investigate:
- issue #1514
- issue #1515
- older issues about .agent-os, config drift, filesystem naming, repo cleanup, or provider adapters
- any open issue that materially overlaps #1530 through #1535

Tasks:
- map overlaps
- decide which issues should stay separate, merge conceptually, close, or defer
- update issue comments or parent issue notes if needed to clarify boundaries

Constraints:
- do not collapse distinct work streams that have materially different outcomes
- optimize for clear tracker hygiene, not for forcing everything into one issue

Deliver:
- overlap matrix
- explicit disposition recommendations
- any tracker updates you made
```

---

## Prompt: Starter-Repos Convergence Pass

Use this when you want Claude to work across the four starter repos specifically.

```text
Work in /mnt/local-analysis/workspace-hub.

Focus on starter-repo convergence for:
- digitalmodel
- worldenergydata
- assethold
- assetutilities

Goal:
Use these four repos as the first standardization set for workspace consistency across:
- control-plane structure
- navigation model
- taxonomy expectations
- documentation cues for both humans and AI agents

Tasks:
- compare the four repos against the current proposed standard
- identify convergence gaps
- propose the smallest high-value changes that improve consistency without overfitting
- document which patterns should become ecosystem defaults
- note which gaps should be rolled out to all repos later

Constraints:
- do not assume every repo must carry every provider adapter
- only standardize what clearly improves navigation and orchestration
- document exceptions explicitly

Deliver:
- convergence comparison
- recommended standard
- specific next changes for the four repos
- rollout notes for the broader ecosystem
```

---

## Suggested Order

Recommended execution order for Claude:

1. `#1531` inventory/docs reconciliation
2. `#1532` canonical control-plane contract
3. `#1533` file-structure taxonomy
4. `#1534` root accidental artifact plan
5. `#1535` cross-platform artifact policy
6. `#1536` issue consolidation

That order keeps the visible “truth layer” and canonical standards ahead of cleanup and tracker consolidation.
