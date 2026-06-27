# Plan for #3252: Auto-graduate high-confidence correction candidates to draft skills (owner-review-gated)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3252
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-27-plan-3252-r1.md | scripts/review/results/2026-06-27-plan-3252-r2.md

---

## Resource Intelligence Summary

This issue (#3252, child of epic [#3248](https://github.com/vamseeachanta/workspace-hub/issues/3248)) closes **gap #1**: "No auto-graduation of correction candidates → canonical skills." Today `correction-promotions.yaml` candidates carry `status: identified` and a human must hand-promote each. The ask is a **GUARDED** auto-graduation: high-confidence + repeated correction patterns become **DRAFT** skills/memory entries, **parked behind a HUMAN owner-review gate, never auto-merged into the canonical tree.** The epic mandate is explicit: *integrate, do not rebuild.*

### How correction candidates are produced today (the live pipeline)
- Found: `.claude/hooks/capture-corrections.sh:80-198` — the PostToolUse capture hook. When the same file is re-edited within 600s (`capture-corrections.sh:93`, `IS_CORRECTION=true`), it appends a `type: "correction"` JSONL record (`capture-corrections.sh:188`) to `.claude/state/corrections/session_YYYYMMDD.jsonl` carrying `basename`, `file_extension`, `chain_id`, `correction_gap_seconds`, and old/new previews (truncated to 100 chars — leak-bounded). **This is the raw signal substrate.**
- Found: `scripts/analysis/session-analysis.sh:21,168-240` — the 3AM cron analysis. `CANDIDATES_DIR=.claude/state/candidates` (L21); Step 5 "Route candidates" appends to `skill-candidates.md` (L213), `script-candidates.md`, `hook-candidates.md`, `agent-candidates.md`, `mcp-candidates.md`. These `.md` files are the routed candidate surfaces (currently near-empty stubs — `skill-candidates.md` header `*Updated by session-analysis.sh — do not edit manually*`).
- Found: `scripts/learning/comprehensive-learning.sh` — the nightly Session-Learning-Pipeline orchestrator (10-phase, header comment L1-4). `MACHINE` is defined at **L26** (`MACHINE=$(hostname | tr …)`) and the **Single-Machine Guard** runs at **L28-29** (`if [[ "$MACHINE" != "dev-primary" && "$MACHINE" != "ace-linux-1" ]]` → echo "commit state files and push", populate `STATE_PATHS`, then early-`exit`). **CRITICAL SCOPING FACT (corrected from r1):** that L28 guard early-exits **comprehensive-learning.sh itself only**; it does NOT gate the nightly wrapper that calls it (see next bullet). So the candidate substrate is a single-box (dev-primary) generative pipeline *by virtue of cron registration*, not because any guard protects the wrapper.
- Found: `scripts/cron/comprehensive-learning-nightly.sh` — the dev-primary nightly aggregator (rsyncs sessions FROM contributor boxes, L30-34). It calls `scripts/learning/comprehensive-learning.sh` at **L158** and `scripts/cron/commit-learning-artifacts.sh` at **L162**. **It has NO internal machine guard and never even defines `MACHINE`** (`grep -n 'MACHINE\|hostname\|dev-primary' comprehensive-learning-nightly.sh` → only rsync host strings, no guard). It is dev-primary-only purely by cron registration. **Consequence for design:** because `correction-promotions.yaml` is git-committed (present on every box), a graduation step wired here would produce drafts if the nightly were ever run elsewhere — so graduation MUST carry its own explicit machine guard (see Design Decision + Implementation Step 3).
- Found: `.claude/state/candidates/correction-promotions.yaml` — the issue's named input. Schema (verified): top-level `promotions:` list, each item `{rank, theme, correction_count, files[], action, target_skill, rationale, status: identified}`. The promotion-target field is named **`target_skill`** (NOT `target`). **Generated 2026-03-25 by a one-time "WRK-1405 Phase 3 analysis" (`generated_at: 2026-03-25T17:45:00Z`); `grep -rln correction-promotions scripts/` finds NO regenerator** — it is a frozen snapshot. Its 5 live rows (`correction_count` 313/169/96/93/31) point `target_skill` at: rank 1 (313) → `superpowers/writing-skills` (a **plugin-namespaced** target — see classification note below), ranks 2/4 → a **rule** (`.claude/rules/coding-style.md`), rank 5 → a **rule** (`.claude/rules/python-runtime.md`), rank 3 → **auto memory** (`auto memory (system prompt)`). **Verified live values:** L10/14 `SKILL.md authoring` → `superpowers/writing-skills`; L22/26 → `.claude/rules/coding-style.md`; L33/37 → `auto memory (system prompt)`; L44/48 → `.claude/rules/coding-style.md`; L55/59 → `.claude/rules/python-runtime.md`.
- **Classification of the rank-1 live row (corrected from r1, addresses round-2 major-1):** `superpowers/writing-skills` is a **`<plugin>/<skill>` plugin-namespaced** target. It does **NOT** appear as a name in `.claude/skills-index.yaml` — that index is *"Auto-generated from `.claude/skills/`"* (header L2) and every entry is a **bare slug** `name:` (e.g. `agent-usage-optimizer`, L17) plus a `.claude/skills/.../SKILL.md` `path:` (verified: `grep -n 'writing-skills\|superpowers' .claude/skills-index.yaml` → only prose at L601/761/781, **no skill named `writing-skills`**). So `read_skill_index_names()` can never contain `superpowers/writing-skills`. A NAIVE `classify_target` (bare `in existing_skill_names`, else `new_skill`) would therefore mis-route the **highest-count, first-to-graduate** row into the `new_skill` branch and emit a spurious `SKILL.md.draft` for what is actually a *checklist-addition to an existing plugin skill*. **Fix (Design + Step 2):** `classify_target` treats any `<plugin>/<skill>` string (contains `/`, not under `.claude/rules/`) as an **existing-skill addition**, and reserves `new_skill` **only** for a *bare slug absent from the index*. Under that rule, **none of the 5 live rows is a new skill** (rank 1 → existing_skill via the namespace rule; ranks 2/4/5 → rule; rank 3 → memory), so the `new_skill` / `SKILL.md.draft` code path is genuinely **not exercised by current real data** and is covered by SYNTHETIC-data tests (see Test Plan + Risks). This consistency — code never routes a live row into `new_skill` — is now load-bearing and test-pinned with the REAL loader output, not a hand-fed set.
- Found: `.claude/docs/self-learning-workflow.md` — the canonical loop: session-signals → session-analysis (3AM, routes candidates) → claude-reflect (5AM RAGS over correction events) → weekly skills-curation. Graduation slots in as the **promote** step that the loop currently leaves to a human.

### Where a draft skill would land — and the auto-promotion hazard
- Found: `scripts/skills/generate_skills_index.py:55-61` (`committed_skill_md()`) — rebuilds `.claude/skills-index.yaml` (the CURATED catalog consumed by humans AND by `audit_skill_currency.py`). Inclusion rule: it runs `git ls-tree -r --name-only HEAD .claude/skills` and keeps only paths where `ln.endswith("/SKILL.md")` (L61). **HAZARD:** any committed `SKILL.md` *under `.claude/skills/`* is auto-added to the canonical index at the next curate run — and from there `scripts/propagate-ecosystem.sh` propagates it to every provider/repo. A naive "write the draft to `.claude/skills/...`" design would therefore **silently bypass the owner gate.** The quarantine location AND the `.draft` suffix are load-bearing (see Design Decision 1): a path ending in `SKILL.md.draft` does NOT match the `endswith("/SKILL.md")` filter even if it leaked into the skills tree.
- Found: `scripts/curation/curate-session-memory.sh:32-37` regenerates the index every 6h on every box (`generate_skills_index.py`), so a draft committed under `.claude/skills/` would be picked up within hours, fleet-wide. This is the exact failure to design against.

### How committed learning state is gitignore-excepted (the staging precondition — addresses round-2 major-2)
- Found: `.gitignore:165,169,176-205` — `.claude/state/` is itself un-ignored (L165 `!.claude/state/`), then **everything under it is re-ignored** by L169 `.claude/state/*`, and individual subpaths are re-included by an **explicit whitelist** (L176 `!.claude/state/candidates/`, L177 `!.claude/state/corrections/`, … through L205 `!.claude/state/correction-trend-meta.json`). **There is NO `!.claude/state/graduation/` entry.** Consequence: the staging loop `git add "$dir" 2>/dev/null && ((staged++)) || true` (`commit-learning-artifacts.sh:134-137`) **swallows** the "ignored by .gitignore" error, so a graduation dir added ONLY to `STATE_DIRS` would be **silently never staged/committed** — drafts stay dev-primary-local, cross-box owner review fails, and the commit-time redactor pass over them is moot (it runs over the filesystem but nothing is committed). **Therefore a `.gitignore` edit (`!.claude/state/graduation/`) is a hard PRECONDITION** for Steps 6/7 and Rollout step 3 to mean anything (see Implementation Step 5 + acceptance test).

### How committed learning state is PII-redacted before commit (the defense-in-depth substrate)
- Found: `scripts/cron/commit-learning-artifacts.sh:94-99` — **before** any staging, the script runs `scripts/legal/redact-client-pii.py` over an **EXPLICIT, hardcoded list of state dirs**: the `uv run python "$PII_REDACTOR" --map "$PII_MAP" --root "$WORKSPACE_HUB" \` invocation is on **L94** and its directory arguments span **L95-99** (verified) — `corrections patterns reflect-history` (L95), `cc-insights candidates trends` (L96), `session-signals skill-eval-results` (L97), `config/agents/claude/memory-snapshots config/agents/codex/state-snapshots` (L98), `config/agents/gemini/state-snapshots` (L99, terminated by `2>&1 || log …`). L100 is `else`, L101 the missing-map WARNING. This codename-redacts client identifiers from every committed learning-state dir as defense-in-depth (#3097), with the #3099 legal scan as the hard backstop.
- Found: `scripts/cron/commit-learning-artifacts.sh:108-117` — a **separate** `STATE_DIRS=( … )` array is the *staging* list; `.claude/state/candidates/` is at **L113**; the array closes at **L117**. The actual git-add loop is **L134-137**. **These are two distinct lists** (redactor args L95-99 vs. staging array L108-117), and r1 correctly flagged that they must BOTH be extended: a state dir added only to STATE_DIRS gets committed **without** the codename redaction every neighbor receives. Graduation drafts render `correction_count` / old/new previews (exactly the client-identifier-bearing content the redactor scrubs), so `.claude/state/graduation` MUST be added to BOTH lists (see Implementation Steps 6 + 7).

### Reuse targets (pattern substrate — do NOT rebuild)
- Found: `scripts/operations/venue_absence_detector.py:197-209` — the **detector pattern to mirror**: a PURE `evaluate(...)` core (no IO/clock/subprocess, fully unit-testable, fails closed on malformed input) + a thin `run_cli(args, notify_fn=_default_notify)` that gathers inputs, calls the core, and routes each alert through an **injectable `notify_fn`** so tests assert call counts without shelling out. (Note: `venue_absence_detector.run_cli` returns **1** on alert at L218 — graduation deliberately does NOT copy that; see Rule 4.)
- Found: `scripts/curation/detect_skill_drift.py` (#3250, live — wired at `curate-session-memory.sh:52`) — the **spam-suppression + machine-label + bounded-publish + rc-safety precedent**: a stable `signature` compared against a persisted `.claude/state/skill-drift-<machine>.json`, alert only on a transition into/within a changed state, `_default_notify` (L222) shells `bash scripts/notify.sh …`, machine label borrowed via `audit_skill_currency.machine_label()` (resolved at call time, L265), `publish_drift` (L235) wraps `equivalence_state.py publish` in a `PUBLISH_TIMEOUT_S = 90` (L46) `subprocess` timeout (fail-soft), and **`run_cli` returns `0` on ANY successful run — clean OR drift — at L288** (docstring L257-264 spells out the "exit code is NOT the signal" contract). **Graduation reuses the last-seen/signature idiom, the injectable-notify shape, the rc-0-on-success contract, AND the machine-label/guard idiom; it does NOT publish (see Rule 5).**
- Found: `scripts/readiness/audit_skill_currency.py:53,57` — `machine_label()` (L53) maps the real host (`ace-linux-1`) → `dev-primary` (L57). Graduation borrows this exact helper for both its machine guard and any label rendering, so the guard set `{dev-primary, ace-linux-1}` passes on the real box and no-ops on `ace-win-1`.
- Found: `scripts/notify.sh` — `bash scripts/notify.sh <source> <job> <status> [details]`; appends one JSONL event to `logs/notifications/YYYY-MM-DD.jsonl`; always exits 0; `status ∈ {pass,fail}`. The graduation alert channel.
- Found: `scripts/learnings/extract-learnings.sh:21-23,181-218` — the **bounded-emission precedent**: `MAX_ISSUES_PER_SESSION=3`, an `AUTO_ISSUE_THRESHOLD` confidence floor, "log the recommendation but stop at the cap." Graduation copies this posture: `GRADUATION_MIN_COUNT` floor + `MAX_GRADUATIONS_PER_RUN` cap.
- Found: `scripts/cron/comprehensive-learning-nightly.sh:158,162` — Step 3e runs `scripts/learning/comprehensive-learning.sh` (L158), Step 10 runs `commit-learning-artifacts.sh` (L162). The graduation step wires in **between** them (after candidates are fresh, before the artifact commit/redact).
- Found: `.claude/hooks/check-state-file-size-precommit.sh` + `check-state-file-size-prepush.sh` — state-file size guards. Drafts must be small scaffolds + a per-run cap so graduation never trips these.

### Standards
Not applicable — harness/self-improvement tooling; no engineering standard involved.

### LLM Wiki pages consulted
None — workspace-hub-internal artifact; `.claude/rules/wiki-sibling-routing.md` "Do not apply when … workspace-hub-internal artifact."

### Documents consulted
- Epic [#3248](https://github.com/vamseeachanta/workspace-hub/issues/3248) body — gap #1 (this child) + "integrate, do not rebuild"; lists `claude-reflect`, `capture-corrections.sh`, `comprehensive-learning-nightly.sh` as the existing machinery to hook into.
- Sibling plans `docs/plans/2026-06-26-3250-skill-drift-detector-alert.md` (pure-core + injectable-notify + last-seen dedup + rc-0 contract), `docs/plans/2026-06-26-3251-resync-skills-no-freeze-at-link.md` (the ~11-touchpoint cost of a new matrix dimension), `docs/plans/2026-06-26-3255-memory-staleness-alert.md` (the audit→state-JSON→matrix substrate). **These three ADD matrix cells because they grade per-machine STATE; #3252 is a single-box generative pipeline and deliberately does NOT — see Decision below.**
- `config/agents/claude/SOUL.runtime.md` Must-Fire: "Never self-label `status:plan-approved`"; "Plan future-tense only." Both honored.

### Gaps identified
- No code path turns a high-confidence `correction-promotions.yaml` candidate into a draft artifact — promotion is 100% manual.
- No quarantine surface that holds a draft skill/memory proposal WITHOUT it leaking into `.claude/skills-index.yaml` / propagate.
- No `.gitignore` exception for a graduation dir, so a STATE_DIRS-only staging change would silently no-op (round-2 major-2).
- No graduation ledger / dedup, so any future automation would re-graduate the same standing candidate every night.
- No alert when new candidates graduate to "awaiting owner review."
- No machine guard on the nightly wrapper, so a graduation step naively wired there would fire on any box that runs the wrapper (the git-committed candidate file is present everywhere).

### Evidence (embedded verification)
- `#3252` — OPEN — "Self-improvement: auto-graduate high-confidence correction candidates to skills — epic #3248"; labels `cat:skills-improvement`, `domain:ai-orchestration` (verified 2026-06-27 `gh issue view`).
- EXISTS: `.claude/state/candidates/correction-promotions.yaml` (frozen 2026-03-25 snapshot, 5 rows, field `target_skill`; rank-1 `target_skill: "superpowers/writing-skills"` at L14), `.claude/hooks/capture-corrections.sh`, `scripts/analysis/session-analysis.sh`, `scripts/learning/comprehensive-learning.sh`, `scripts/curation/detect_skill_drift.py`, `scripts/readiness/audit_skill_currency.py`, `scripts/operations/venue_absence_detector.py`, `scripts/notify.sh`, `scripts/skills/generate_skills_index.py`, `scripts/cron/comprehensive-learning-nightly.sh`, `scripts/cron/commit-learning-artifacts.sh`, `scripts/legal/redact-client-pii.py`.
- MISSING (this plan creates): `scripts/curation/graduate_corrections.py`, `tests/curation/test_graduate_corrections.py`, the `.claude/state/graduation/` quarantine tree, the `.gitignore` exception.
- Gap proof: `grep -rln "graduate\|graduation" scripts/curation/ scripts/learning/` → empty → no graduation code exists.
- Plugin-namespace proof (major-1): `grep -n 'writing-skills\|superpowers' .claude/skills-index.yaml` → only prose at L601/761/781; NO `name: writing-skills` entry → `read_skill_index_names()` never contains `superpowers/writing-skills` → it MUST be classified by the `/`-namespace rule, not by index membership.
- Hazard proof: `generate_skills_index.py:55-61` keys ONLY on `git ls-tree -r HEAD .claude/skills` filtered by `endswith("/SKILL.md")` → a draft under `.claude/state/graduation/` (and any `SKILL.md.draft`) is structurally invisible to it.
- Gitignore proof (major-2): `.gitignore:169` `.claude/state/*` ignores all; whitelist L176-205 re-includes named dirs but has NO `graduation` entry → without an added `!.claude/state/graduation/` the `git add` at L134-137 silently no-ops for graduation.
- Scoping proof: `grep -n 'MACHINE\|hostname\|dev-primary' scripts/cron/comprehensive-learning-nightly.sh` → no machine guard (only rsync hostnames); `MACHINE` defined only in `comprehensive-learning.sh:26`, guarded L28-29.
- Redactor proof: `commit-learning-artifacts.sh:94` runs `redact-client-pii.py`, dir args L95-99 (candidates at L96); STATE_DIRS staging L108-117 (candidates L113); git-add loop L134-137.

<!-- Source count: issue + epic #3248 + 13 cited source files = ≥3 satisfied. -->

---

## Decision: NO new matrix dimension — hook into the existing nightly + candidate machinery (single-box, explicitly guarded)

**addsMatrixDimension = false.** Unlike siblings #3250/#3251/#3255 (which add a matrix cell because they grade per-machine STATE — drift facts, link health, memory freshness — that legitimately varies box-to-box and must be reconciled to parity), **#3252 is a single-box GENERATIVE pipeline**, and three independent facts make a matrix dimension wrong here:

1. **Nothing cross-machine to grade.** The matrix grades *equivalence across boxes*. Graduation is dev-primary-only — but, per the corrected scoping analysis above, **that is true by (a) cron registration of the nightly wrapper on dev-primary AND (b) an EXPLICIT machine guard this plan adds inside `graduate_corrections.run_cli`** (no-op + rc 0 on any host other than `dev-primary`/`ace-linux-1`, mirroring `comprehensive-learning.sh:26-29` and `audit_skill_currency.machine_label()`). It is NOT scoped by the inner `comprehensive-learning.sh:28` guard, which only early-exits that inner script and does not gate the nightly wrapper. There is no per-box parity question — a "graduation cell" on `ace-win-1` would be permanently MISSING-EVIDENCE by construction (the explicit guard no-ops there), which is noise, not signal.
2. **A new dimension costs ~11 touchpoints + a reconcile OK-skip entry** (per the #3251 enumeration: (1) a `verdict_<dim>()` fn, (2) `verdict_for` dispatch at `build-equality-matrix.py:411`, (3) `BASE_DISPLAY_DIMS`, (4) `DISPLAY_DIMS`, (5) `GROUPS` at L475, (6) `ROLLUP_SEVERITY` at L491, (7) `OK_VERDICTS` at L516, (8) `remediate()` at L521, (9) CSS, (10) legend, (11) the SKILL.md/reconcile sync). **Every new green/OK verdict string must ALSO be added to `reconcile-ecosystem.sh:204`'s OK-skip `case`** or healthy cells fire spurious reconcile actions. Paying that cost for a single-box queue gauge is unjustified.
3. **The right signal shape is an ALERT + a reviewable queue file, not a verdict.** "N drafts are parked awaiting owner review" is a notification/worklist, surfaced via `scripts/notify.sh` (like `detect_skill_drift`) and a human-readable `queue.yaml` — exactly the substrate epic #3248 says already exists.

**Therefore:** graduation hooks into the **dev-primary nightly orchestrator** (`comprehensive-learning-nightly.sh`, between L158 and L162) and the **candidate/learning-artifact substrate** — adding **zero** matrix verdict strings, so `reconcile-ecosystem.sh`'s OK-skip list (`build-equality-matrix.py:516` `OK_VERDICTS`, `reconcile-ecosystem.sh:204`) is **UNTOUCHED**. It is explicitly NOT wired into the every-6h all-box `curate-session-memory.{sh,ps1}` wrappers (those carry per-machine matrix audits; graduation is neither per-machine nor a matrix audit — see Rule 2 below).

---

## Recommended approach

A new pure-core + thin-CLI module `scripts/curation/graduate_corrections.py` that, on dev-primary nightly:

0. **Machine-guards first.** `run_cli` borrows the machine label via `audit_skill_currency.machine_label()` (same idiom as `detect_skill_drift`) and, on any host other than `dev-primary`/`ace-linux-1`, prints a one-line notice and **returns rc 0 without producing drafts** — mirroring `comprehensive-learning.sh:26-29`. This is load-bearing because the nightly wrapper has no guard of its own and the candidate file is git-committed everywhere.
1. **Reads** `.claude/state/candidates/correction-promotions.yaml` (the candidate source named by the issue).
2. **Selects** candidates that are **high-confidence AND repeated** — `correction_count >= GRADUATION_MIN_COUNT` (named module constant) AND `status == "identified"` AND **not already in the graduation ledger** — capped at `MAX_GRADUATIONS_PER_RUN` (highest-count-first), mirroring `extract-learnings.sh`'s bounded emission.
3. **Classifies each candidate's `target_skill`** (the verified field name) into one of: rule edit (`target_skill` starts with `.claude/rules/`), memory edit (`target_skill == "auto memory (system prompt)"`), existing-skill addition (`target_skill` is a bare slug present in the committed skills index **OR** a `<plugin>/<skill>` plugin-namespaced string such as `superpowers/writing-skills`), or **new skill** (a *bare slug absent from the index*). **Only the new-skill class emits a `SKILL.md.draft` scaffold** — and, per the verified live data, no current real row reaches that branch (rank 1 is a plugin-namespace existing-skill add, not a new skill).
4. **Renders** each selected candidate into a **DRAFT graduation proposal** under the **quarantine tree** `.claude/state/graduation/drafts/<slug>/proposal.md` — owner-facing: theme, `correction_count`, `target_skill`, `target_kind`, `action`, `rationale`, a bounded sample of correction evidence (basenames + truncated previews only), and the recommended human apply command (`/write-a-skill` for a NEW skill, or a manual targeted edit for an existing skill/rule/memory).
5. **Parks** them in `.claude/state/graduation/queue.yaml` with `status: draft-parked`, `owner_review: pending`, `created_at`, `source_rank`, `source_theme`, `target_skill`, `target_kind` — and records a dedup ledger entry in `.claude/state/graduation/graduated.json`.
6. **Alerts** via `scripts/notify.sh cron skill-graduation pass <N new drafts parked>` **only when NEW drafts appear** (spam-suppressed by a last-seen signature, mirroring `detect_skill_drift`), so an unchanged standing backlog never re-alerts.
7. **Stops.** The owner reviews `queue.yaml`, and **a human** moves an approved draft into `.claude/skills/` (via `/write-a-skill`) or hand-edits the target rule/memory. The script **never** writes into `.claude/skills/`, **never** git-commits to canonical, **never** applies a `status:` label, **never** runs `propagate-ecosystem.sh`.

### Why this design
- **Quarantine is the gate.** Drafts live under `.claude/state/graduation/` — structurally invisible to `generate_skills_index.py` (`git ls-tree .claude/skills` filtered to `endswith("/SKILL.md")`, L55-61) and `propagate-ecosystem.sh`. The new-skill scaffold is named `SKILL.md.draft` (not `SKILL.md`) as belt-and-suspenders so even an accidental copy into the skills tree won't match the index glob.
- **The graduation dir is gitignore-excepted so staging actually works.** `.gitignore` adds `!.claude/state/graduation/` alongside the L176-205 whitelist; without it, `.claude/state/*` (L169) would silently ignore the dir and the `git add` at `commit-learning-artifacts.sh:134-137` would no-op (round-2 major-2). This is a precondition for owner cross-box review and the commit-time redactor pass to mean anything.
- **Owner-review gate is a real HUMAN step**, not a self-applied label (Hard Rule 1). The script's terminal state is `draft-parked / owner_review: pending`. Promotion to canonical is a separate human action.
- **The classifier never mis-routes a plugin-namespaced existing-skill add into the new-skill path.** A `<plugin>/<skill>` target (rank-1 live row) is an EXISTING-skill checklist addition; `new_skill` is reserved for a bare slug absent from the index. This prevents the day-one spurious `SKILL.md.draft` round-2 major-1 flagged.
- **Drafts inherit the neighbor's PII redaction.** `.claude/state/graduation` is added to BOTH the `redact-client-pii.py` argument list (`commit-learning-artifacts.sh:94-99`) AND the `STATE_DIRS` staging array (L108-117), so parked drafts are codename-redacted before commit exactly like `corrections`/`candidates`/`patterns` — preserving the defense-in-depth the epic mandates rather than re-deriving a weaker bespoke scrub.
- **Reuses proven substrate** (`detect_skill_drift` dedup/notify/machine-guard, `extract-learnings` caps, the nightly orchestrator), per the epic's integrate-don't-rebuild mandate.

### Rejected alternatives
1. **Write drafts directly under `.claude/skills/<cat>/<skill>/SKILL.md` (even with a `draft: true` frontmatter flag).** REJECTED — `generate_skills_index.py:55-61` keys on path + `endswith("/SKILL.md")`, NOT on a `draft` flag, so a committed draft is auto-indexed and then auto-propagated fleet-wide within 6h, bypassing the owner gate entirely. The frontmatter flag is not load-bearing; the *location* + `.draft` suffix are.
2. **A naive `classify_target` (bare `in existing_skill_names` else `new_skill`, no plugin-namespace handling).** REJECTED — it mis-routes the rank-1 live row `superpowers/writing-skills` (not in the bare-slug index) into `new_skill` and emits a spurious `SKILL.md.draft` for a checklist-addition to an existing plugin skill on the very FIRST live run. The corrected classifier treats any non-rules `<plugin>/<skill>` string as an existing-skill add.
3. **Add a `graduation_backlog` matrix dimension.** REJECTED — single-box pipeline, nothing cross-machine to grade; permanently MISSING-EVIDENCE on every non-dev-primary box; ~11 touchpoints + a reconcile OK-skip entry for a queue gauge. (See Decision above.)
4. **Auto-open a GitHub issue per graduation (extend `extract-learnings.sh`).** REJECTED for this issue — issue spam + the must-fire "comment/label on issues" gates pull in workflow the owner-review queue handles more cheaply; a `queue.yaml` + one `notify.sh` event is lower-friction. (A `--emit-issue` opt-in is a clean follow-on, not the default.)
5. **Regenerate `correction-promotions.yaml` from raw `.claude/state/corrections/*.jsonl` inside this module.** REJECTED — that is the producer concern of gap #5 / sibling [#3254](https://github.com/vamseeachanta/workspace-hub/issues/3254) ("recurring drift → candidates"). Graduation has a single responsibility: *graduate an existing candidate list*. It reads the file; it does not produce it. (Documented as a dependency/risk — the file is currently a frozen 2026-03-25 snapshot.)
6. **Wire into the every-6h `curate-session-memory.{sh,ps1}` wrappers.** REJECTED — those carry per-machine matrix audits run on ALL boxes 4×/day; graduation is dev-primary-only and nightly. Wiring it there would run it on boxes that lack the candidate substrate and graduate 4×/day. The dev-primary nightly is the correct carrier.
7. **Rely on the nightly wrapper / inner `comprehensive-learning.sh:28` guard for single-box scoping instead of an explicit guard.** REJECTED — the inner guard early-exits only `comprehensive-learning.sh`; the wrapper (`comprehensive-learning-nightly.sh`) has no guard and the candidate file is git-committed everywhere, so graduation would fire if the wrapper ran off dev-primary. An explicit in-module guard is required.
8. **Add `.claude/state/graduation` to `STATE_DIRS` only, trusting the array's "already excepted in .gitignore" comment.** REJECTED — that comment is true for the dirs already whitelisted at L176-205, but `graduation` is NOT among them; `.claude/state/*` (L169) ignores it, and the `git add … 2>/dev/null || true` swallows the error, so staging silently no-ops. The `.gitignore` exception is a required separate step.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-27-3252-auto-graduate-correction-candidates.md |
| Graduation engine (new) | scripts/curation/graduate_corrections.py |
| Engine tests (new) | tests/curation/test_graduate_corrections.py |
| Quarantine tree (new, runtime) | .claude/state/graduation/{drafts/,queue.yaml,graduated.json,last-seen.json} |
| Gitignore exception (modify) | .gitignore (add `!.claude/state/graduation/`) |
| Nightly wiring (modify) | scripts/cron/comprehensive-learning-nightly.sh |
| Artifact-commit redactor + staging (modify) | scripts/cron/commit-learning-artifacts.sh |
| Plan review — round 1 | scripts/review/results/2026-06-27-plan-3252-r1.md |
| Plan review — round 2 | scripts/review/results/2026-06-27-plan-3252-r2.md |
| Plans index (update) | docs/plans/README.md |

---

## Implementation Steps (TDD-first — tests before code)

> Order is strict: each code file is preceded by its failing tests. No implementation lands before a red test exists for it.

1. **Write `tests/curation/test_graduate_corrections.py` FIRST (red).** Cover the pure core (`select_candidates`, `slug_for`, `classify_target`, `graduation_signature`, `evaluate`), the machine guard, the quarantine/no-self-promotion guarantees, the plugin-namespace classification using the REAL `read_skill_index_names()` output (major-1), the new-skill (`SKILL.md.draft`) branch via SYNTHETIC bare-slug data (live data never triggers it), the gitignore exception (major-2), and the redaction wiring. Load the module via `importlib.util.spec_from_file_location` (kebab/underscore idiom from `tests/readiness/test_skill_currency.py`). All tests fail (module absent) — confirm red.
2. **Implement the PURE core of `scripts/curation/graduate_corrections.py`** until the core tests pass:
   - `GRADUATION_MIN_COUNT = 50` and `MAX_GRADUATIONS_PER_RUN = 3` — named module constants with a rationale comment tying them to `extract-learnings.sh`'s bounded-emission posture and flagging that sibling [#3256](https://github.com/vamseeachanta/workspace-hub/issues/3256) will make the threshold *adaptive* (keep it a single constant so #3256 has one place to change).
   - `select_candidates(promotions, *, min_count, already_graduated, cap)` → PURE: filter `status == "identified"` AND `correction_count >= min_count` AND `slug not in already_graduated`; sort by `correction_count` desc; take `cap`. No IO.
   - `slug_for(theme)` → PURE, deterministic slug (stable across runs → dedup key).
   - `classify_target(target_skill, existing_skill_names)` → PURE: returns `"rule" | "memory" | "existing_skill" | "new_skill"`. Branch order: `startswith(".claude/rules/")` → `rule`; `== "auto memory (system prompt)"` → `memory`; `in existing_skill_names` (bare slug in index) → `existing_skill`; **`"/" in target_skill`** (a `<plugin>/<skill>` namespaced target, e.g. `superpowers/writing-skills`) → `existing_skill`; else (a bare slug absent from the index) → `new_skill`. `target_is_new_skill = classify_target(...) == "new_skill"`. **The `/`-namespace branch is the major-1 fix: it keeps the rank-1 live row out of the new-skill path.**
   - `graduation_signature(parked_slugs)` → PURE: sorted set of parked slugs (spam-suppression key; mirrors `detect_skill_drift.drift_signature`).
   - `evaluate(promotions, already_graduated, queue, last_seen, *, now_iso, existing_skill_names, min_count, cap)` → PURE: returns `{new_drafts:[...], queue_additions:[...], ledger_additions:[...], alerts:[...], new_state:{signature,updated_at}}`. Each addition carries `target_skill` + `target_kind` (from `classify_target`). `alerts` non-empty **only** when the signature changed (new slugs parked); `status="pass"` (graduation is informational, never a failure). No IO, no clock (now injected).
3. **Implement the thin CLI + machine guard + renderers** until CLI tests pass:
   - **Machine guard (first thing in `run_cli`):** resolve the machine label via `audit_skill_currency.machine_label()` (maps `ace-linux-1` → `dev-primary`, verified at `audit_skill_currency.py:53,57`); if it is not in `{dev-primary, ace-linux-1}`, print one notice line and `return 0` WITHOUT reading the candidate file or writing any draft — mirrors `comprehensive-learning.sh:26-29`. Guarded by `test_machine_guard_noop_off_dev_primary`.
   - `read_skill_index_names()`: parse `.claude/skills-index.yaml` and return the set of bare `name:` slugs (e.g. `agent-usage-optimizer`). It will NOT contain `superpowers/writing-skills` — that row is classified by the `/`-namespace branch, not by membership.
   - `run_cli(args, notify_fn=_default_notify)`: (after the guard) read `correction-promotions.yaml` + `graduated.json` + `last-seen.json` + the committed skills-index names; call `evaluate`; **render** each `new_draft` to `.claude/state/graduation/drafts/<slug>/proposal.md` (+ `SKILL.md.draft` only when `target_kind == "new_skill"`); append to `queue.yaml` + `graduated.json`; write `last-seen.json`; fire `notify_fn` per alert. **Returns rc 0 on success regardless of draft count** (Rule 4); reserves non-zero for an unhandled hard error only.
   - `_default_notify(alert)`: `subprocess.run(["bash", notify_sh, "cron", "skill-graduation", alert["status"], alert["detail"]], check=False)` (mirrors `venue_absence_detector._default_notify` / `detect_skill_drift._default_notify` L222).
   - Renderers read `addition["target_skill"]` EXPLICITLY (verified field name — never a bare `target` key) and refuse to write any path outside `.claude/state/graduation/` (assert-guarded); they never name a file exactly `SKILL.md`.
   - All paths derived from `Path(__file__).resolve().parents[...]` — no hardcoded absolutes (`check-no-abs-paths.sh`). Evidence rendered as basenames + truncated previews only — no client identifiers, no absolute file paths from the correction records (belt; the commit-time redactor is the defense-in-depth backstop — Step 7).
4. **Wire the nightly (modify `comprehensive-learning-nightly.sh`)** — add a best-effort step **after** Step 3e (`comprehensive-learning.sh` run, L158) and **before** Step 10 (`commit-learning-artifacts.sh`, L162): `bash scripts/curation/... graduate_corrections.py || echo "WARNING: correction graduation failed — see above"`. Best-effort (`|| echo`) so a graduation failure never aborts the nightly. The in-module machine guard (Step 3) keeps it inert if the wrapper ever runs off dev-primary.
5. **Add the `.gitignore` exception (PRECONDITION for Steps 6/7 — modify `.gitignore`)** — add a single line `!.claude/state/graduation/` alongside the existing `.claude/state/` whitelist block (L176-205, e.g. immediately after L205 `!.claude/state/correction-trend-meta.json`). Without it, L169 `.claude/state/*` ignores the dir and the `git add` at `commit-learning-artifacts.sh:134-137` silently no-ops. Guarded by `test_graduation_dir_not_gitignored` (asserts `git check-ignore .claude/state/graduation/queue.yaml` is a NON-match / exit 1).
6. **Wire artifact-commit STAGING (modify `commit-learning-artifacts.sh:108-117`)** — add `.claude/state/graduation/` to the `STATE_DIRS` array (alongside `.claude/state/candidates/` at L113) so parked drafts are committed and visible to the owner across boxes. Committed-parked ≠ promoted. (Effective only because of Step 5.)
7. **Wire artifact-commit REDACTION (modify `commit-learning-artifacts.sh:94-99`)** — add `.claude/state/graduation` to the `redact-client-pii.py` argument list (the explicit dir args at L95-99, e.g. on the same line as `candidates` at L96) so rendered draft evidence receives the SAME codename redaction every neighbor state dir gets BEFORE staging/commit. **This is a separate edit from Step 6** (the redactor arg list at L94-99 ≠ the STATE_DIRS staging array at L108-117); both are required.
8. **Update `docs/plans/README.md`** index.
9. **Run the full guard battery** (Acceptance Criteria) — size-hooks, abs-path, legal scan, redaction proof, index-isolation proof, gitignore-exception proof.

---

## Test Plan

`tests/curation/test_graduate_corrections.py` (py:tmp-dir sandbox; never touches the real `.claude/state/graduation/`):

| Test | Verifies | Input | Expected |
|---|---|---|---|
| test_select_high_confidence_repeated | floor + repeated filter | rows counts 313/169/96/93/31, min=50 | selects 313/169/96/93, drops 31 |
| test_select_respects_status_identified | already-promoted rows skipped | one row `status: promoted` | excluded |
| test_select_dedup_against_ledger | already-graduated slug skipped | slug in `already_graduated` | excluded |
| test_select_caps_per_run | bounded emission | 6 eligible rows, cap=3 | 3 highest-count returned |
| test_slug_for_stable_deterministic | dedup key stability | same theme twice | identical slug |
| test_classify_target_rule_and_memory | rule/memory classification on LIVE field values | `.claude/rules/coding-style.md`, `auto memory (system prompt)` | `rule`, `memory` |
| **test_classify_target_plugin_namespace_is_existing_skill** | **major-1 fix**: the LIVE rank-1 value classifies as `existing_skill` via the `/`-namespace rule using the ACTUAL `read_skill_index_names()` output | `existing_skill_names = read_skill_index_names()` over the real index (asserted NOT to contain `superpowers/writing-skills`), `target_skill = "superpowers/writing-skills"` | `existing_skill` (NOT `new_skill`); test first asserts the loader output lacks `writing-skills`, so the pass is via the namespace branch, not a hand-fed set |
| test_classify_target_bare_slug_in_index_is_existing | bare in-index slug | `agent-usage-optimizer` in index set | `existing_skill` |
| **test_classify_target_new_skill_synthetic** | **data-untested branch**: a *bare slug* matching no rule/memory/index entry and containing no `/` classifies as `new_skill` | synthetic row `target_skill: "some-brand-new-skill"`, empty index | `new_skill` |
| test_no_live_row_classifies_new_skill | consistency guard (major-1) | the 5 real `correction-promotions.yaml` rows + real index | every live row's `target_kind` ∈ {existing_skill, rule, memory}; none is `new_skill` |
| test_signature_unchanged_no_alert | spam suppression | queue unchanged vs last_seen | `alerts == []` |
| test_signature_changed_alerts_once | new parked draft alerts | new slug added | exactly 1 `pass` alert |
| test_evaluate_is_pure_no_io | core does no IO/clock | monkeypatch open/subprocess to raise; now injected | no raise; deterministic |
| **test_machine_guard_noop_off_dev_primary** | **Rule-6 scoping**: guard no-ops on a non-dev-primary host | machine label = `ace-win-1` | rc 0, zero drafts, zero notify, candidate file never read |
| **test_render_never_writes_under_skills_tree** | **CORE GATE**: renderer refuses any path outside `.claude/state/graduation/`; never names a file `SKILL.md` | run renderer in tmp repo | draft at `state/graduation/drafts/<slug>/proposal.md`; NO file under `.claude/skills/`; new-skill scaffold named `SKILL.md.draft` |
| **test_render_emits_skill_draft_only_for_new_skill** | new-skill scaffold gated on `target_kind` (synthetic bare slug) | one `new_skill` row (bare slug) + one `rule` row | `SKILL.md.draft` exists for the new-skill slug only |
| **test_generate_index_ignores_quarantine_drafts** | **CORE GATE**: a parked draft is invisible to the canonical catalog | render a draft, then run `generate_skills_index.py` over a tmp tree | draft slug absent from emitted `skills-index.yaml` |
| **test_graduation_dir_not_gitignored** | **major-2 fix**: the `.gitignore` exception is present | `git check-ignore .claude/state/graduation/queue.yaml` in the repo | NON-match (exit 1) — path is committable |
| **test_graduation_dir_in_redactor_arg_list** | **redaction wiring**: `.claude/state/graduation` is an explicit arg to `redact-client-pii.py` | grep the redactor invocation block (L94-99) | `.claude/state/graduation` present in the redactor arg list (not only STATE_DIRS) |
| **test_graduation_dir_in_state_dirs_array** | **staging wiring**: `.claude/state/graduation/` is in `STATE_DIRS` | grep the STATE_DIRS block (L108-117) | present alongside `.claude/state/candidates/` |
| **test_redaction_runs_over_rendered_draft_evidence** | **redaction (behavioral)**: a codename in rendered draft evidence is scrubbed by `redact-client-pii.py` | render a proposal containing a known client name under a tmp root, run `redact-client-pii.py --map <test-map> --root <tmp> .claude/state/graduation` | client name replaced by its codename in the draft |
| test_no_status_label_no_git_no_propagate | owner-gate integrity | run CLI in tmp repo | no `gh`, no `git commit`, no `propagate-ecosystem` invoked (monkeypatched subprocess records zero such calls); queue status == `draft-parked`/`owner_review: pending` |
| test_cli_returns_zero_on_drafts | Rule 4 exit-code safety | eligible candidates present | rc == 0 (not non-zero) |
| test_cli_returns_zero_on_empty | rc-safe when nothing to do | no eligible candidates | rc == 0, 0 notify calls |
| test_cli_injected_notify_fires_per_new_draft | injectable notify | 2 new drafts | `notify_fn` called once (one summary `pass` event) with `job=skill-graduation` |
| test_queue_and_ledger_written | persistence | new drafts | `queue.yaml` + `graduated.json` updated; rerun graduates nothing (dedup) |
| test_idempotent_second_run | no re-graduation | run twice same input | second run: 0 new drafts, 0 alerts, rc 0 |
| test_missing_promotions_file_failsoft | absent input | no `correction-promotions.yaml` | rc 0, 0 drafts, 0 alerts (fail-soft) |
| test_evidence_no_abs_paths_no_client_ids | leak safety (belt) | correction records with abs paths | rendered proposal contains basenames/previews only, no `/mnt/...` |
| test_draft_size_bounded | size-hook safety | a fat candidate | each proposal under the state-file size cap; ≤ `MAX_GRADUATIONS_PER_RUN` drafts/run |

**Acceptance Criteria**
- [ ] `uv run --no-project --with pyyaml pytest tests/curation/test_graduate_corrections.py -v` green.
- [ ] `evaluate`/`select_candidates`/`slug_for`/`classify_target`/`graduation_signature` are PURE (proven by `test_evaluate_is_pure_no_io`).
- [ ] `classify_target` routes the LIVE rank-1 row `superpowers/writing-skills` to `existing_skill` via the `/`-namespace rule against the REAL `read_skill_index_names()` output (which lacks `writing-skills`); NO live row classifies as `new_skill` (`test_classify_target_plugin_namespace_is_existing_skill` + `test_no_live_row_classifies_new_skill`).
- [ ] The machine guard no-ops (rc 0, zero drafts) off dev-primary (`test_machine_guard_noop_off_dev_primary`).
- [ ] No draft is ever written under `.claude/skills/`; a parked draft is invisible to `generate_skills_index.py` (`test_render_never_writes_under_skills_tree` + `test_generate_index_ignores_quarantine_drafts`); the `SKILL.md.draft` branch is exercised by SYNTHETIC bare-slug data only (`test_render_emits_skill_draft_only_for_new_skill`).
- [ ] `.gitignore` un-ignores the graduation dir — `git check-ignore .claude/state/graduation/queue.yaml` is a non-match (`test_graduation_dir_not_gitignored`).
- [ ] `.claude/state/graduation` is in BOTH the `redact-client-pii.py` arg list (`commit-learning-artifacts.sh:94-99`) AND the `STATE_DIRS` staging array (L108-117); rendered draft evidence is codename-redacted before commit (`test_graduation_dir_in_redactor_arg_list` + `test_graduation_dir_in_state_dirs_array` + `test_redaction_runs_over_rendered_draft_evidence`).
- [ ] The script applies NO `status:` label, runs NO `gh`, NO `git commit` to canonical, NO `propagate-ecosystem.sh` (`test_no_status_label_no_git_no_propagate`). Terminal state is `draft-parked / owner_review: pending`.
- [ ] CLI returns rc 0 on success regardless of draft count (`test_cli_returns_zero_on_*`); the nightly wrapper guards it `|| echo WARNING`.
- [ ] Re-running on unchanged candidates graduates nothing and fires zero `notify.sh` events (`test_idempotent_second_run`).
- [ ] `notify.sh` event uses `source=cron`, `job=skill-graduation`, `status=pass`.
- [ ] `bash scripts/enforcement/check-no-abs-paths.sh` + `scripts/legal/legal-sanity-scan.sh` clean on changed files; rendered evidence carries basenames/previews only.
- [ ] Drafts pass `check-state-file-size-precommit.sh` / `-prepush.sh` (bounded size + per-run cap).
- [ ] `comprehensive-learning-nightly.sh` invokes graduation best-effort between L158 (Step 3e) and L162 (Step 10).
- [ ] NO new matrix verdict string added → `reconcile-ecosystem.sh:204` OK-skip list and `build-equality-matrix.py:516` `OK_VERDICTS` are byte-unchanged (regression: `tests/readiness/` still green).
- [ ] Review artifacts posted to `scripts/review/results/2026-06-27-plan-3252-r1.md` + `-r2.md` (T2 → ≥2 providers).

---

## Pseudocode

```
# scripts/curation/graduate_corrections.py
GRADUATION_MIN_COUNT   = 50    # high-confidence floor; #3256 will make this ADAPTIVE — single source
MAX_GRADUATIONS_PER_RUN = 3    # bounded emission (mirrors extract-learnings MAX_ISSUES_PER_SESSION)
GRAD_DIR  = STATE / "graduation"          # QUARANTINE — outside .claude/skills/, invisible to the index
DRAFTS    = GRAD_DIR / "drafts"
QUEUE     = GRAD_DIR / "queue.yaml"
LEDGER    = GRAD_DIR / "graduated.json"
LASTSEEN  = GRAD_DIR / "last-seen.json"
DEV_HOSTS = {"dev-primary", "ace-linux-1"}

def slug_for(theme) -> str:                       # PURE, deterministic dedup key
    return re.sub(r"[^a-z0-9]+", "-", theme.lower()).strip("-")

def classify_target(target_skill, existing_skill_names) -> str:   # PURE
    if target_skill.startswith(".claude/rules/"):           return "rule"
    if target_skill == "auto memory (system prompt)":       return "memory"
    if target_skill in existing_skill_names:                return "existing_skill"  # bare slug IN index
    if "/" in target_skill:                                 return "existing_skill"  # <plugin>/<skill> namespace add
    return "new_skill"          # ONLY a bare slug ABSENT from the index — only path that drafts SKILL.md
    # major-1: superpowers/writing-skills hits the "/" branch -> existing_skill, NOT new_skill.

def select_candidates(promotions, *, min_count, already_graduated, cap) -> list:   # PURE
    eligible = [p for p in promotions
                if p.get("status") == "identified"
                and isinstance(p.get("correction_count"), int)
                and p["correction_count"] >= min_count
                and slug_for(p["theme"]) not in already_graduated]
    return sorted(eligible, key=lambda p: -p["correction_count"])[:cap]

def graduation_signature(parked_slugs) -> str:    # PURE; mirrors detect_skill_drift.drift_signature
    return "CLEAN" if not parked_slugs else "|".join(sorted(parked_slugs))

def evaluate(promotions, already_graduated, queue, last_seen, *, now_iso,
             existing_skill_names, min_count=GRADUATION_MIN_COUNT,
             cap=MAX_GRADUATIONS_PER_RUN) -> dict:                                  # PURE
    picked = select_candidates(promotions, min_count=min_count,
                               already_graduated=already_graduated, cap=cap)
    additions = [{slug: slug_for(p["theme"]), theme: p["theme"],
                  correction_count: p["correction_count"],
                  target_skill: p["target_skill"],                # EXPLICIT field name (not "target")
                  target_kind: classify_target(p["target_skill"], existing_skill_names),
                  action: p.get("action"), rationale: p.get("rationale"),
                  status: "draft-parked", owner_review: "pending", created_at: now_iso}
                 for p in picked]
    parked = sorted(set(existing_queue_slugs(queue)) | {a["slug"] for a in additions})
    sig = graduation_signature(parked)
    changed = sig != (last_seen or {}).get("signature")
    alerts = ([{status:"pass",
                detail:f"{len(additions)} correction candidate(s) graduated to DRAFT — owner review: {QUEUE}"}]
              if (additions and changed) else [])
    return {new_drafts:additions, queue_additions:additions,
            ledger_additions:[a["slug"] for a in additions], alerts:alerts,
            new_state:{signature:sig, updated_at:now_iso}}

def render_draft(addition):                        # writes ONLY under DRAFTS; never names a file "SKILL.md"
    d = DRAFTS / addition["slug"]; d.mkdir(parents=True, exist_ok=True)
    assert is_relative_to(d, GRAD_DIR)             # belt-and-suspenders: refuse to escape quarantine
    write(d/"proposal.md", owner_facing_md(addition))   # theme, count, target_skill, target_kind, evidence, apply-cmd
    if addition["target_kind"] == "new_skill":     # data-untested today (no live row) — synthetic test covers it
        write(d/"SKILL.md.draft", skill_scaffold(addition))  # .draft suffix -> never matches index glob

def run_cli(args, notify_fn=_default_notify) -> int:
    machine = audit_skill_currency.machine_label()              # maps ace-linux-1 -> dev-primary (L53,57)
    if machine not in DEV_HOSTS:                                # mirrors comprehensive-learning.sh:26-29
        print(f"graduate_corrections: dev-primary only (machine={machine}); no-op.")
        return 0                                                # Rule 4 + Rule 6: guarded, rc 0
    existing = read_skill_index_names()                         # bare slugs from .claude/skills-index.yaml (committed)
    promotions = read_yaml(STATE/"candidates"/"correction-promotions.yaml").get("promotions", [])  # absent -> []
    res = evaluate(promotions, read_json(LEDGER) or set(), read_yaml(QUEUE) or {},
                   read_json(LASTSEEN), now_iso=_now(), existing_skill_names=existing)
    for a in res["queue_additions"]: render_draft(a)
    append_queue(QUEUE, res["queue_additions"]); extend_ledger(LEDGER, res["ledger_additions"])
    write_json(LASTSEEN, res["new_state"])
    for al in res["alerts"]: notify_fn({**al})
    return 0                                        # Rule 4: success rc is ALWAYS 0 (signal via state+notify)
```

---

## Risks & Hard-Rule Compliance

**Rule 1 — never self-apply `status:plan-approved` / `status:completeness-verified`; owner gate is HUMAN.**
COMPLIANT. The script's terminal artifact is a `draft-parked / owner_review: pending` entry in `.claude/state/graduation/queue.yaml`. It applies NO GitHub label, makes NO `gh` call, and performs NO commit into the canonical skills tree. Promotion from draft → canonical is a separate, explicit HUMAN action (owner runs `/write-a-skill` or hand-edits the target rule/memory). Guarded by `test_no_status_label_no_git_no_propagate`. There is no label surface in this code at all.

**Rule 2 — any session/curation audit must be wired into BOTH `curate-session-memory.sh` AND `.ps1`, reusing `machine_label()`/audit→state-JSON→collect→verdict substrate.**
COMPLIANT BY NON-APPLICABILITY (justified). This design adds **no session/curation audit and no matrix cell**, so the `.sh`/`.ps1` wrapper rule does not trigger. Graduation is a dev-primary-only nightly generative step; it wires into `comprehensive-learning-nightly.sh` (between L158 and L162), NOT the every-6h all-box curate wrappers (where `detect_skill_drift` lives at `curate-session-memory.sh:52`). Wiring it into the wrappers would run it on boxes lacking the candidate substrate and 4×/day — wrong cadence and wrong host. It DOES reuse `machine_label()` (`audit_skill_currency.py:53,57`) for its guard, and reuses the established defense-in-depth redactor (`redact-client-pii.py` via `commit-learning-artifacts.sh:94-99`) — that is the "integrate, do not rebuild" obligation r1 flagged, addressed in Implementation Step 7; it is a leak-prevention wiring, not a Rule-2 audit-wrapper obligation.

**Rule 3 — a new matrix dimension touches ~11 places + every OK verdict must enter `reconcile-ecosystem.sh`'s OK-skip list.**
COMPLIANT BY AVOIDANCE. No new dimension, no new verdict string. `build-equality-matrix.py` `OK_VERDICTS` (L516), `ROLLUP_SEVERITY` (L491), `verdict_for` (L411), `GROUPS` (L475), `remediate()` (L521), and `reconcile-ecosystem.sh:204`'s OK-skip `case` are all **byte-unchanged**. The ~11-touchpoint cost (verdict fn, dispatch, `BASE_DISPLAY_DIMS`, `DISPLAY_DIMS`, `GROUPS`, `ROLLUP_SEVERITY`, `OK_VERDICTS`, `remediate()`, CSS, legend, SKILL.md/reconcile sync) is deliberately not incurred — see Decision. Regression-guarded by the existing `tests/readiness/` suite staying green.

**Rule 4 — do NOT overload exit codes; audits signal via state JSON, not exit status (non-zero aborts the Windows cron under `$ErrorActionPreference='Stop'`).**
COMPLIANT. `run_cli` returns rc **0 on success regardless of draft count** (and rc 0 on the off-host machine-guard no-op); new-draft state is signaled via `queue.yaml`/`graduated.json`/`last-seen.json` + a `notify.sh` `pass` event, never via a non-zero rc. This mirrors `detect_skill_drift.run_cli`'s `return 0` (L288) — and deliberately diverges from `venue_absence_detector.run_cli` (returns 1 on alert, L218). Non-zero is reserved for an unhandled hard error only. The nightly wiring additionally guards the call `|| echo "WARNING: ..."`. Graduation is NOT on the Windows `.ps1` cron, so the `ErrorActionPreference=Stop` hazard does not arise. Guarded by `test_cli_returns_zero_on_drafts` + `test_cli_returns_zero_on_empty`.

**Rule 5 — any cross-machine state-ref git push HANGS (operator issue) — bound with a timeout.**
COMPLIANT BY AVOIDANCE. Graduation is dev-primary-only and publishes **nothing** to a state-ref — drafts/queue/ledger are local files committed by the existing `commit-learning-artifacts.sh` (normal `git add`/commit/push the nightly already performs, not a state-ref plumbing push). There is no `equivalence_state.py publish` call, so the hang cannot occur. (Note: the round-2 major-2 gitignore fix is what makes that normal commit actually stage the graduation dir; it introduces no state-ref push and therefore no Rule-5 hang.) (If cross-machine draft visibility were ever wanted via state-refs, it would reuse `detect_skill_drift.publish_drift`'s `PUBLISH_TIMEOUT_S = 90` bounded fail-soft pattern — out of scope.)

**Rule 6 — first assess whether a new matrix dimension is warranted; these 4 children are automation pipelines that may hook existing machinery.**
ADDRESSED — decision is **NO new dimension** (see Decision section): nothing cross-machine to grade (single-box pipeline → permanent MISSING-EVIDENCE elsewhere), the signal shape is an alert+worklist not a verdict, and the dimension cost (~11 touchpoints + OK-skip) is unjustified for a queue gauge. CRITICAL CORRECTION from r1: the single-box premise rests on (a) cron registration of the nightly wrapper on dev-primary AND (b) an **explicit in-module machine guard** using `audit_skill_currency.machine_label()` (real host `ace-linux-1` → `dev-primary`, L57; guard set `{dev-primary, ace-linux-1}` passes on the real box, no-ops on `ace-win-1`), NOT on the inner `comprehensive-learning.sh:28` guard (which only early-exits that inner script and does NOT gate the nightly wrapper — the wrapper defines no `MACHINE` and the candidate file is git-committed everywhere). Graduation hooks the dev-primary nightly + candidate/learning-artifact substrate. Guarded by `test_machine_guard_noop_off_dev_primary`.

### Additional risks
- **Risk — the skills-index auto-promotion hazard (the headline trap).** A draft committed under `.claude/skills/` would be auto-indexed by `generate_skills_index.py` (6h cron) and propagated fleet-wide, silently bypassing the owner gate. **Mitigation:** quarantine under `.claude/state/graduation/` (invisible to the `git ls-tree .claude/skills` + `endswith("/SKILL.md")` filter, L55-61) + name new-skill scaffolds `SKILL.md.draft` (never matches the index glob) + an assert that the renderer cannot write outside the quarantine. Double-locked by `test_render_never_writes_under_skills_tree` + `test_generate_index_ignores_quarantine_drafts`.
- **Risk — plugin-namespaced existing-skill add mis-routed to the new-skill path (round-2 major-1).** A naive classifier sends the rank-1 live row `superpowers/writing-skills` (not in the bare-slug index) to `new_skill` and emits a spurious `SKILL.md.draft` on the FIRST live run. **Mitigation:** `classify_target` treats any non-rules `<plugin>/<skill>` string as an existing-skill add; `new_skill` is reserved for a bare slug absent from the index. Pinned by `test_classify_target_plugin_namespace_is_existing_skill` (uses the REAL loader output) + `test_no_live_row_classifies_new_skill`.
- **Risk — STATE_DIRS staging silently no-ops because the graduation dir is gitignored (round-2 major-2).** `.claude/state/*` (L169) ignores everything not on the L176-205 whitelist, and `git add … 2>/dev/null || true` swallows the "ignored" error, so parked drafts would never be committed and cross-box owner review + the redactor pass would be moot. **Mitigation:** an explicit `.gitignore` edit `!.claude/state/graduation/` (Implementation Step 5, a precondition for Steps 6/7) + `test_graduation_dir_not_gitignored` asserting `git check-ignore` is a non-match.
- **Risk — parked drafts committed WITHOUT codename redaction (r1 leak gap).** Drafts render `correction_count`/old-new previews — the same client-identifier-bearing content the codename redactor scrubs from every sibling state dir. **Mitigation:** add `.claude/state/graduation` to BOTH the `redact-client-pii.py` arg list (`commit-learning-artifacts.sh:94-99`, Step 7) AND the `STATE_DIRS` staging array (L108-117, Step 6), so drafts inherit the same defense-in-depth redaction before commit. The renderer's basename/preview discipline is a belt; the commit-time redactor is the load-bearing scrub. Guarded by `test_graduation_dir_in_redactor_arg_list` + `test_redaction_runs_over_rendered_draft_evidence`.
- **Risk — the new-skill (`SKILL.md.draft`) path is data-untested today.** With the corrected classifier, NONE of the 5 live `correction-promotions.yaml` rows targets a brand-new skill (rank 1 → existing skill via the namespace rule, ranks 2/4/5 → rules, rank 3 → auto-memory), so the `target_kind == "new_skill"` branch never fires against current real data. **Mitigation:** SYNTHETIC bare-slug tests (`test_classify_target_new_skill_synthetic`, `test_render_emits_skill_draft_only_for_new_skill`) exercise it; flagged here so a future `correction-promotions.yaml` refresh that introduces a bare-slug new-skill target is known-covered.
- **Risk — stale candidate source.** `correction-promotions.yaml` is a frozen 2026-03-25 snapshot with no live regenerator; against it graduation will produce drafts ONCE (ranks 1-4 ≥ 50) then idempotently stop. **Mitigation/flag:** producing fresh candidates is gap #5 / sibling [#3254](https://github.com/vamseeachanta/workspace-hub/issues/3254)'s responsibility and the `session-analysis.sh` routing; graduation deliberately stays single-responsibility (graduate, don't produce). Documented as a dependency, not solved here.
- **Risk — state-file size growth.** Drafts under `.claude/state/` are size-guarded by the precommit/prepush hooks. **Mitigation:** small scaffolds + `MAX_GRADUATIONS_PER_RUN=3` cap + bounded evidence; `test_draft_size_bounded`.
- **Risk — re-alert noise on standing backlog.** **Mitigation:** last-seen signature dedup (mirrors `detect_skill_drift`); `test_idempotent_second_run` + `test_signature_unchanged_no_alert`.
- **Open question (owner):** should an approved draft auto-open a tracking GitHub issue on owner sign-off (a `--emit-issue` opt-in extending `extract-learnings.sh`), or stay a pure file-queue? Default ships as file-queue; flag for the user.
- **Open question (owner):** is `GRADUATION_MIN_COUNT=50` the right high-confidence floor, or should it gate on a multi-session/multi-file "repeated" predicate too? Kept a single named constant so sibling #3256 (adaptive threshold) has one change site.

---

## Rollout
1. Land behind no flag but **inert by data**: until a producer refreshes `correction-promotions.yaml`, graduation processes the existing 5-row snapshot once then idempotently no-ops — zero blast radius. (The first run will park up to 3 drafts: ranks 1-4 are eligible at min=50; with the corrected classifier rank 1 → existing-skill add, ranks 2/4 → rule, none → new_skill.)
2. **Dev-primary nightly only — by cron registration of the wrapper AND the explicit in-module machine guard** (`audit_skill_currency.machine_label()`, mirroring `comprehensive-learning.sh:26-29`). NOT relied on the inner `comprehensive-learning.sh:28` early-exit, which does not gate the wrapper. Any other box that runs the wrapper hits the guard and no-ops at rc 0.
3. First live run (dev-primary): inspect `.claude/state/graduation/queue.yaml` + the rendered `proposal.md` drafts; confirm NO file appeared under `.claude/skills/`, NO `SKILL.md.draft` was emitted (no live row is `new_skill`), `generate_skills_index.py` output is unchanged (the index-isolation acceptance gate), `git check-ignore .claude/state/graduation/queue.yaml` is a non-match (the dir is committable), AND the commit-time `redact-client-pii.py` pass covered `.claude/state/graduation` (grep the commit log / redactor invocation block L94-99).
4. Owner reviews the parked drafts; promote approved ones via `/write-a-skill` (new skills) or targeted hand-edits (existing rules/memory + the plugin-skill checklist add for rank 1). Mark promoted entries in `queue.yaml` so the ledger dedup never re-graduates them.
5. Monitor `logs/notifications/*.jsonl` for `job=skill-graduation` events; confirm one event per genuinely-new batch (no re-alert on standing backlog).
6. Follow-ons (separate issues): live candidate producer (#3254 / `session-analysis` routing), adaptive threshold (#3256), optional `--emit-issue` owner-signoff bridge.

## Complexity: T2
One new pure-core+CLI module (with an explicit machine guard + plugin-namespace-aware classifier) + one new test file, plus four surgical wiring edits (nightly orchestrator at L158-162; `.gitignore` exception; artifact-commit STAGING array L108-117; artifact-commit REDACTOR arg list L94-99) and a new quarantine state tree. Multi-file and harness-touching, reusing the proven `detect_skill_drift` dedup/notify/machine-guard/rc-0 + `extract-learnings` bounded-emission patterns; NOT cross-provider-systemic and adds NO matrix dimension. TDD mandatory; T2 → ≥2-provider adversarial review (rounds r1 + r2).
