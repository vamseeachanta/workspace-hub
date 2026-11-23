# Fresh session entry prompt — 2026-05-17 close-out → next session

Paste the section between the `===` markers below into a fresh Claude Code session opener. The prompt is self-contained for cold-start: it points to canonical context, names the open work paths, lists hard constraints, and asks the user to pick a direction before doing anything.

===

Continuing the multi-day session arc on `vamseeachanta/llm-wiki` + `vamseeachanta/workspace-hub`. Three independent work paths are open with explicit user approval already in place; pick one before doing anything.

## Cold-start context — read first

Latest exit handoff (read fully — it's the canonical state-at-exit record):
- `workspace-hub/docs/session-handoffs/2026-05-17-sub-issue-approvals-phase-b-redact-exit.md` — covers Wave 2 sub-issue approvals + Phase B redaction + Hermes-canonical-memory architectural path + stash-drop incident continuation section

Prior handoffs in the same arc (read for full context):
- `2026-05-16-issue-40-wave1-92-plan-paths-a-b-exit.md` (paths A + B parallel — reservoir-engineering Wave 1 founding + PE Phase 5 plan)
- `2026-05-16-phase-5-execution-complete-exit.md` (Phase 5 epic execution)
- `2026-05-16-phase-5-hygiene-wave2-final-exit.md` (Phase 5 hygiene + Wave 2 + memory updates + addendum on sub-issues filed)

Operational incident report (read if attempting stash recovery work):
- `workspace-hub/docs/incidents/2026-05-17-stash-drop-sweep-incident.md` — 65 stash SHAs dropped + recovery procedure (~14-day gc window) + triage confirming zero meaningful data loss

Active memories worth re-reading at session start (auto-memory `~/.claude/projects/.../memory/`):
- `feedback_never_offer_to_self_label_plan_approved` — user-approval gate is load-bearing
- `feedback_parallel_subagent_shared_target_manifest_deferral` — 2-batch + solo trailing dispatch pattern (validated 4 PE epics; updated 2026-05-16)
- `feedback_retry_loop_sweep_contamination` — sweep-contamination class (commit + stash variants; updated 2026-05-17 with stash-drop incident learning)
- `feedback_closes_trailer_fires_once` — comma-joined fires once; line-separated fires all (verified 2026-05-16)
- `feedback_memory_aspire_to_hermes_level` — user's bar for memory tooling = Hermes; all AI provider work should flow through Hermes canonical memory (in GitHub)
- `feedback_offrepo_intel_routing` — client/employer materials stay off-repo for published repositories
- `feedback_autosync_silent_pusher` — workspace-hub push race is reproducible; retry-once recovers cleanly

## Workspace state at session start

| Repo | HEAD | Notes |
|---|---|---|
| llm-wiki main | `f30e0e86` | Wave 2 corpus manifest with Phase B redacted; clean state |
| workspace-hub main | `2c1d23c15` (or auto-sync-advanced descendant) | Incident doc + handoff addendum landed; pull first to catch any auto-sync drift |

Sibling clone `/mnt/local-analysis/llm-wiki` may have continued #78 RAG-benchmark workstream activity — confirm non-collision before any llm-wiki work.

## Three open work paths

### Path 1 — llm-wiki #40 Wave 2 follow-ups → Wave 3 (sequential)

All 3 sub-issues `status:plan-approved` 2026-05-17. Recommended order:

1. **[llm-wiki#98](https://github.com/vamseeachanta/llm-wiki/issues/98)** — Kansas Geological Survey reuse-permission email — ~15 min draft + send (async response time TBD; file-and-forget after send)
2. **[llm-wiki#96](https://github.com/vamseeachanta/llm-wiki/issues/96)** — license-verification for 10 `defer` rows in Wave 2 manifest — ~30-60 min per-row WebFetch on publisher / repo licence-statement pages
3. **[llm-wiki#97](https://github.com/vamseeachanta/llm-wiki/issues/97)** — arXiv expansion to close mixed-quality gap to ≥50 — ~45-60 min targeted physics.geo-ph + stat.ML searches
4. **Then llm-wiki Wave 3** — concept-page authoring (gamma-ray-log-interpretation + dip-azimuth + formation-tops) — ~60-90 min via subagent. **Do NOT start until #96 + #97 land** so the `ingest`-tier source pool is finalized

Total estimated budget: ~2.5-3.5 hours across 2-3 fresh sessions. Each step is independent.

### Path 2 — Hermes-canonical-memory architecture (parallel/independent)

All 4 issues `status:plan-approved` 2026-05-17. Markers at `workspace-hub/.planning/plan-approved/{2733,2734,2735,2736}.md`.

User-stated architectural directives (apply to ALL 4 sub-issues):
- **Historical-memory consolidation is in scope** — not just future writes; existing per-provider history (Claude auto-memory `~/.claude/projects/<project>/memory/`, Codex `~/.codex/`, Gemini session memory) migrates INTO Hermes with provenance preservation
- **Canonical memory goes WITH the repo ecosystem (in GitHub)** — git-tracked, cross-machine sync via pull/push, public-vs-private layering via repo visibility, conflict resolution = git merge, format = git-friendly (markdown/yaml/json)

Recommended order:

1. **[workspace-hub#2734](https://github.com/vamseeachanta/workspace-hub/issues/2734)** — audit current Hermes memory capabilities + identify gaps (8 axes including the git-trackability axis added by user clarification) — produces inputs for #2735 + #2736
2. **[workspace-hub#2735](https://github.com/vamseeachanta/workspace-hub/issues/2735)** — design write/read API for non-Hermes providers — depends on #2734 audit
3. **[workspace-hub#2736](https://github.com/vamseeachanta/workspace-hub/issues/2736)** — design migration plan from per-provider stores — parallelizable with #2735 (different surface: interface vs migration)

Per CLAUDE.md planning workflow: even with `status:plan-approved` set, each sub-issue still needs its own Resource Intel + adversarial review pass before implementation begins.

Total estimated budget: audit ~1-2 hours; design issues TBD scope; full architecture rollout multi-session.

### Path 3 — Optional: stash recovery / peace-of-mind triage

The 2026-05-17 stash-drop incident left 65 stash SHAs in git object store with ~14-day recovery window. Triage during the incident showed ZERO meaningful data loss (all 3 high-suspicion stashes confirmed operational debris; underlying files / branches all exist in active state). This path is genuinely optional.

If you want full peace of mind, the incident doc at `docs/incidents/2026-05-17-stash-drop-sweep-incident.md` lists all 65 SHAs. Run `git stash show -p <sha>` on any candidate for read-only inspection.

## Hard constraints carrying forward (all paths)

- **No self-approval of any kind** per `feedback_never_offer_to_self_label_plan_approved`. All `status:plan-approved` was set via explicit user action 2026-05-17; do NOT extend that scope to sub-issues or follow-ups discovered during implementation without fresh user approval
- **Plan-approved marker file discipline**: only write `.planning/plan-approved/<NN>.md` after explicit user "yes approve" — never auto-write on label flip
- **llm-wiki CLAUDE.md agent-context firewall**: no workspace-hub private memory bleed, no `/mnt/ace` references in wiki content, no `feedback_*` slugs in wiki concept/standards pages, no recruiter / hermes refs in wiki content
- **Validate via `python3 scripts/validate_*.py` direct invocation** — NOT pytest (pytest hangs on workspace-hub .venv FUSE per `feedback_local_venv_pytest_import_hang`)
- **Vendor-IP discipline**: cite-by-name + chemistry/hardware-class only, no SKUs, no dosage with units, no performance curves. New deny-list test `validate_production_chemistry_deny_list.py` enforces this — run it before any wiki commit touches concept / standards pages
- **Paywalled standards**: structural intent paraphrased only, no verbatim >30 words
- **No citations of `wikis/*/wiki/sources/`** per workspace-hub#2482 deny-list
- **Calc-citation contract**: doc-only metadata posture committed across Phase 5 + reservoir-engineering Waves 1-2 — apply same posture uniformly to Wave 3 concept pages
- **Two-batch dispatch pattern** for sub-issue counts > 2: Batch 1 parallel (2 subagents with manifest-deferral for shared targets), Batch 2 solo. Validated 4 PE epics in a row
- **Pathspec form on commits**: `git commit -m "..." -- <files>` per `feedback_retry_loop_sweep_contamination` — order matters: `--` after `-m`
- **NEVER `while git stash list | drop`** — per `feedback_retry_loop_sweep_contamination` stash variant. Drop a specific `stash@{N}` after grep-verifying description matches your own session
- **Off-repo data-layer governance**: client/employer materials at `/mnt/ace/*/` stay off-repo. Inventory references in `docs/research/` corpus manifests must redact client / project / vessel / document-ID identifiers. The Wave 2 corpus manifest's Phase B redaction (`docs/research/reservoir-engineering-corpus.md`) is the established precedent.
- **Auto-sync race expectation**: workspace-hub `git push` reliably races with auto-sync 2-4x per session on handoff/docs commits. Standard recovery: `[remote rejected]` → retry → "Everything up-to-date" confirms (origin already at your SHA). Per `feedback_autosync_silent_pusher`
- **Closes-trailer form**: use line-separated `Closes vamseeachanta/<repo>#X\nCloses vamseeachanta/<repo>#Y` (fires all refs on direct push) — NOT comma-joined `Closes #X, #Y` (fires once only). Per `feedback_closes_trailer_fires_once`

## First-step recommendation

Ask user: "Path 1 (llm-wiki Wave 2/3 — concrete continuation), Path 2 (Hermes-canonical-memory — architectural new work), or Path 3 (optional stash recovery)?"

Then:
- **If Path 1**: start with #98 (KGS email draft+send — lowest effort, async response). Read `feedback_offrepo_intel_routing` + `feedback_llm_wiki_concept_pages_need_public_references` first
- **If Path 2**: start with #2734 audit. Read the auto-memory `feedback_memory_aspire_to_hermes_level` for full architectural framing; the umbrella issue #2733 has 9 open questions for user-side enrichment that should be addressed before audit begins
- **If Path 3**: read `docs/incidents/2026-05-17-stash-drop-sweep-incident.md` for SHA list + triage priority. Use `git stash show -p <sha>` (read-only) on candidates

Don't auto-pick. Don't self-approve any future plan. Do not start implementation work without re-reading the relevant prior-session handoff + relevant memories first.

===

## How to use this prompt

1. **Read this file in full** (this is the wrapper; the prompt itself is between the `===` markers above)
2. **Copy the section between the `===` markers** (everything from "Continuing the multi-day session arc..." through "...without re-reading the relevant prior-session handoff + relevant memories first.")
3. **Paste as the first user message in a fresh Claude Code session** in this workspace (cwd: `/mnt/local-analysis/workspace-hub`)
4. **Claude will**: load CLAUDE.md + memory base automatically, read the named handoff docs, ask which path you want, then proceed once you pick

The prompt is self-contained for cold-start — no prior conversation context needed beyond what's named in the prompt itself.

## Why this is a separate doc (not just chat output)

Session-entry prompts persist as discoverable artifacts in `docs/session-handoffs/` with the `-entry.md` suffix (existing convention: `2026-05-16-soul-ecosystem-followup-entry.md`, `2026-05-17-soul-rules-approval-and-followups-entry.md`, etc. — see existing files in the directory). Future-me cold-starting can find them via:

```bash
ls docs/session-handoffs/2026-05-17-*entry*.md
```

Filing the entry prompt as a doc also means edits/refinements can land via normal commit workflow rather than re-pasting.
