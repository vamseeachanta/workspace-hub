# Agent Performance Audit
*WRK-226 | Run: 2026-02-20 | Sessions analysed: 8 (5 JSONL hook logs + 3 transcript sources)*

## TL;DR

The primary noise source is `CLAUDE.md`, which at 6728 bytes exceeds its own stated 4KB budget by 68%, and the full auto-loaded context stack (CLAUDE.md + rules/*.md + MEMORY.md) reaches 23,351 bytes — 142% of the 16KB system budget. The most actionable patterns are: (a) the Windows Compatibility section is loaded for every session on a Linux-only machine, (b) cross-provider adapters CODEX.md and GEMINI.md are missing security, testing, and legal rules that CLAUDE.md carries, and (c) MEMORY.md records WRK items as "done" when they are still pending in the queue. Top recommendation: trim CLAUDE.md by relocating the Resource Index, Windows Compatibility, SPARC Modes, and Plan Mode Convention to `.claude/docs/` — estimated savings of ~2100 bytes (32% reduction).

---

## Session Log Analysis

### Sessions analysed

| Session file | Date | Lines | Duration | Primary project |
|---|---|---|---|---|
| session_20260220.jsonl | 2026-02-20 | 4,772 | ~641 min | worldenergydata (69%), workspace-hub (30%) |
| session_20260219.jsonl | 2026-02-19 | 3,785 | ~1090 min | workspace-hub (77%), worldenergydata (20%) |
| session_20260218.jsonl | 2026-02-18 | 4,858 | ~1030 min | workspace-hub (50%), digitalmodel (31%) |
| session_20260217.jsonl | 2026-02-17 | 3,473 | ~502 min | workspace-hub (95%) |
| session_20260216.jsonl | 2026-02-16 | 7,399 | ~1308 min | workspace-hub (77%), worldenergydata (17%) |
| transcript: workspace-hub | 2026-02-10 | 421 msgs | — | workspace-hub |
| transcript: workspace-hub/digitalmodel | 2026-02-04 | 749 msgs | — | digitalmodel |
| session-logs/session_20260201 | 2026-02-01 | 876 hooks | — | digitalmodel |

Date range: 2026-02-01 to 2026-02-20. All JSONL files are hook event logs (`pre`/`post` per tool call); conversation text is available only in the transcript files.

### Context load patterns

Claude Code auto-loads the following at every session start (confirmed by readiness-report.md and CLAUDE.md policy):

1. `/mnt/local-analysis/workspace-hub/CLAUDE.md` — 6728 bytes, 140 lines (system prompt injected unconditionally)
2. `/mnt/local-analysis/workspace-hub/.claude/rules/*.md` — six rule files totalling 12,182 bytes, 403 lines
3. `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 4279 bytes, 58 lines
4. **On-demand** (session-start skill reads these): `.claude/state/readiness-report.md`, `.claude/state/session-snapshot.md`
5. **Not auto-loaded**: `.claude/memory/KNOWLEDGE.md` (5452 bytes) — requires explicit read or `@`-import

Total auto-loaded context: **23,189 bytes** (~5,800 tokens estimated at 4 chars/token).

The readiness hook independently reports: *"Total context 23351 bytes (142% of 16KB budget)"*.

### Loaded-but-never-referenced (noise candidates)

Evidence from hook log tool distribution and transcript content analysis:

| Section / File | Evidence of Use | Noise Assessment |
|---|---|---|
| CLAUDE.md: Windows Compatibility (404b) | No Windows tool calls observed; server is Linux (`uname -a: Linux ace-linux-1`) | Loaded every session, never triggered |
| CLAUDE.md: SPARC Modes (82b) | 0 SPARC mentions across 3 transcript sessions; `sparc` agents exist but no `/sparc-*` invocations seen | Likely never invoked in recent sessions |
| CLAUDE.md: Resource Index (1095b) | Content is a compressed duplicate of `.claude/RESOURCE_INDEX.md`; not cited in transcripts | Redundant with auto-generated full index |
| CLAUDE.md: Plan Mode Convention (836b) | Cross-review procedure also in `work-queue/process.md` and MEMORY.md gate rules | Partial overlap with 2 other files |
| rules/patterns.md (2837b) | No SOLID/Factory/Repository pattern questions observed in sessions; design-pattern examples redirected to `.claude/docs/` | Loaded but examples stripped to external docs |
| KNOWLEDGE.md (5452b) | Not auto-loaded; requires explicit read. Overlaps with MEMORY.md on git/shell patterns | Only loaded when explicitly requested |

---

## Noise Catalogue

### (a) Stale facts

**File: MEMORY.md — AI Orchestration section, line 58**
- Content: `"Skills: .claude/skills/ canonical; .codex/skills+.gemini/skills → symlinks; WRK-198/200-202 done"`
- Evidence: WRK-198 is in `pending/` (not archived), WRK-202 is not in archive. WRK-200 and WRK-201 are archived. The "done" claim is partially false.

**File: MEMORY.md — Work Queue section, line 33**
- Content: `"200+ items, ~95 archived"`
- Evidence: This is a spot estimate, likely stale by several months given active archiving pace. No automated sync of this count.

**File: MEMORY.md — AI Orchestration section, line 54**
- Content: `"preferred over Opus 4.5"` — references Opus 4.5 as the comparison baseline.
- Evidence: model-registry.yaml v2.1 has no Opus 4.5 entry. The current hierarchy is Opus 4.6 vs Sonnet 4.6. Opus 4.5 is an obsolete reference point.

**File: CODEX.md — Default thread cap section, line 73**
- Content: `"workspace-hub constraint: MAX_TEAMMATES=3 (Claude Code, git-tracked in .claude/settings.json)"`
- Evidence: `.claude/settings.json` currently has `"MAX_TEAMMATES": "5"` (updated per recent commit `48aca5b`). CODEX.md has not been updated to reflect the new limit.

**File: scripts/development/ai-workflow/auto-fix-loop.sh:178 and primary-claude.sh:180**
- Content: hardcoded `claude-sonnet-4-20250514` (stale dated model ID)
- Evidence: model-registry.yaml maps this to `claude-sonnet-4-5-20250929` as replacement.

**File: scripts/improve/lib/classify.sh:14**
- Content: fallback `model="${model:-claude-sonnet-4-5-20250929}"` — a stale short-format ID.
- Status: The primary path reads from registry correctly; the fallback is stale.

**File: scripts/development/ai-workflow/review-openai.sh:182**
- Content: hardcoded `gpt-4o` (stale — registry has `gpt-4.1` as primary).

**File: scripts/development/ai-workflow/test-runner.sh:309**
- Content: hardcoded `gemini-2.0-flash` (stale — registry has `gemini-2.5-flash`).

**File: scripts/automation/agent_orchestrator.sh:129**
- Content: hardcoded `claude-sonnet-4.5` (dot notation, likely a typo variant of stale ID).

### (b) Redundant rules

**Git workflow — 3-way duplication:**
- `CLAUDE.md §Git Operations` (584b): submodule handling, no-rebase, stash, Windows path, LF endings
- `MEMORY.md §Git & Shell Essentials`: submodule commit order, pre-commit bypass, lib/ gitignore, sed symlink issue
- `KNOWLEDGE.md §Git Multi-Repo Sync Patterns` + `§Git Credential & Auth`: submodule detached HEAD, pull --no-rebase, stash conflicts

All three files carry overlapping "never rebase", "submodule commit inside first", and "stash before pull" content.

**Work Queue approval gates — 2-way duplication:**
- `CLAUDE.md §Work Items & Approval Gates` (532b): plan → approval → implement sequence, never auto-execute
- `MEMORY.md §Work Queue Gate Rules`: same sequence, plus Route-specific detail (plan_reviewed/plan_approved flags, execution brief, 3 reviewers)

The CLAUDE.md section is a shorter summary of what MEMORY.md already covers fully.

**Shell portability — 2-way duplication:**
- `MEMORY.md`: `awk` capture groups are gawk-only; `sed -i` destroys symlinks
- `KNOWLEDGE.md §Shell Script Portability`: same two facts, worded slightly differently

**Orchestrator pattern — 2-way duplication:**
- `CLAUDE.md §Golden Rule` + `§Delegation Pattern` (860b + 602b = 1462b): full orchestrator ASCII diagram, delegation triggers
- `.claude/docs/orchestrator-pattern.md`: dedicated doc with full detail (loaded on demand)

The CLAUDE.md summary is appropriate but partially redundant with the dedicated doc Claude is instructed to consult.

### (c) Over-verbose sections

**CLAUDE.md §Resource Index** (1095b, ~14% of CLAUDE.md):
- The inline resource index is a static mini-map that duplicates `.claude/RESOURCE_INDEX.md` (13,907b, auto-generated).
- Sessions don't need both. The inline version is already out of date vs the auto-generated one (e.g., missing `agents/swarm/` subdir reality check).
- Lines used: 0 observed citations in transcripts. Total lines: 13.

**CLAUDE.md §Plan Mode Convention** (836b):
- Cross-review procedure (Codex = hard gate, 3 reviewers, Gemini syntax) is already fully documented in `work-queue/process.md` and partially in `MEMORY.md §Work Queue Gate Rules`.
- Sessions accessing this section can be served by the process.md reference alone.

**rules/patterns.md** (2837b, 104 lines):
- Every concrete example has been stripped to `.claude/docs/design-patterns-examples.md` ("See .../design-patterns-examples.md for examples" appears 4 times).
- What remains is the list of pattern names and brief descriptions. Only the "Research Before Building" and "Fail Fast" entries have non-trivial actionable content not in a referenced doc.
- Estimated lines actually needed: ~20 of 104.

**rules/testing.md** (2057b, 64 lines):
- The "Test Types" and "Test Maintenance" sections (performance budgets, parallelism hints) are generic software engineering guidance unlikely to be referenced in a workspace that runs specific pytest commands.
- Core TDD mandate is captured in CLAUDE.md Core Rules item 3.

### (d) Contradictory instructions

**MAX_TEAMMATES:**
- `CODEX.md` line 73: `"workspace-hub constraint: MAX_TEAMMATES=3"`
- `.claude/settings.json`: `"MAX_TEAMMATES": "5"`
- Verdict: settings.json is ground truth; CODEX.md is 2 versions behind (commit `48aca5b` raised it from 3 to 5).

**Cross-review Codex gate:**
- `CLAUDE.md §Plan Mode Convention`: "If Codex fails or is unavailable, the review is BLOCKED until resolved. Do not proceed without Codex approval."
- `MEMORY.md §Work Queue Gate Rules` / `process.md`: "Route A: inline plan + user confirm sufficient; no cross-review required"
- Verdict: CLAUDE.md absolutizes the Codex gate without Route-A exception. MEMORY.md and process.md correctly scope it. Reading CLAUDE.md alone creates a false "always blocked" interpretation.

**Gemini CLI syntax:**
- `CLAUDE.md §Plan Mode Convention`: `gemini --prompt` (non-interactive flag)
- `MEMORY.md`: `echo content | gemini -p "prompt" -y` (pipe syntax with `-p` and `-y`)
- Verdict: `-p` is the correct short flag; `--prompt` may or may not be valid depending on CLI version. Instructions are inconsistent.

**`specs/modules/` vs `specs/wrk/WRK-NNN/`:**
- `CLAUDE.md §Plan Mode Convention`: "Save plans to: specs/modules/<module>/"
- `work-queue/process.md §Plan §Route C`: "Separate spec in specs/wrk/WRK-<id>/ linked via spec_ref"
- Verdict: Two different target directories for plan specs, neither deprecating the other. Most recent Route C specs are in `specs/wrk/` but CLAUDE.md still points to `specs/modules/`.

### (e) Missing cross-provider rules

| Rule category | Present in | Missing from |
|---|---|---|
| Security (secrets, injection, XSS, CSRF, auth) | `rules/security.md` (Claude only) | CODEX.md, GEMINI.md |
| Legal compliance (deny list, client ID prevention) | `rules/legal-compliance.md` (Claude only) | CODEX.md, GEMINI.md |
| Testing (TDD mandatory, 80% coverage) | `rules/testing.md` (Claude only) | CODEX.md, GEMINI.md |
| Coding style (max 400 lines, snake_case, no wildcards) | `rules/coding-style.md` (Claude only) | CODEX.md, GEMINI.md |
| Git workflow (branch naming, commit format) | `rules/git-workflow.md` (Claude only) | CODEX.md, GEMINI.md |

CODEX.md and GEMINI.md carry only: Required Gates (WRK mapping, approval, cross-review), Plan/Spec Locality, Provider Strengths, and Skills reference. When Codex executes code (its primary use case — "Focused code tasks, single-file changes, algorithms, testing, refactoring"), it has no access to the security hardening, TDD mandate, or legal compliance rules.

### (f) Loaded but never referenced

| Section / File | Sessions loaded in | Times cited | Note |
|---|---|---|---|
| CLAUDE.md §Windows Compatibility | All 5 sessions (auto-loaded) | 0 | Machine is Linux; MINGW/CRLF rules irrelevant |
| CLAUDE.md §SPARC Modes | All 5 sessions (auto-loaded) | 0 in transcripts | No sparc invocations seen in 2026-02 sessions |
| CLAUDE.md §Resource Index | All 5 sessions (auto-loaded) | 0 direct citations | Duplicates .claude/RESOURCE_INDEX.md |
| rules/patterns.md §God Objects | All 5 sessions (auto-loaded) | 0 | Examples moved to external doc |
| KNOWLEDGE.md (entire file) | Not auto-loaded | N/A (on-demand only) | Overlap with MEMORY.md; no session-start hook loads it |

---

## Noise Ranking by Source File

| File | Noise patterns | Estimated token waste | Priority |
|---|---|---|---|
| `CLAUDE.md` | (b) redundant git/approval rules, (c) verbose Resource Index + Plan Mode, (d) cross-review contradiction, (d) specs path mismatch, (f) Windows + SPARC never referenced | ~530 tokens (2100b wasted vs 4KB budget) | HIGH |
| `MEMORY.md` | (a) stale WRK status, (a) stale Opus 4.5 reference, (a) stale queue count, (b) redundant git/shell rules duplicate KNOWLEDGE.md | ~120 tokens (480b) | MEDIUM |
| `CODEX.md` | (a) MAX_TEAMMATES=3 contradicts settings.json value of 5, (e) no security/testing/legal rules | ~90 tokens (360b of stale + missing content) | HIGH |
| `rules/patterns.md` | (c) 84 lines of examples stripped to external doc; skeleton file with repeated "See design-patterns-examples.md" | ~530 tokens (2100b for ~20b of actual value) | MEDIUM |
| `rules/testing.md` | (c) Test Types + Test Maintenance sections generic boilerplate | ~150 tokens (600b of low-use content) | LOW |
| `scripts/development/ai-workflow/*.sh` | (a) 3 files with stale hardcoded model IDs | ~20 tokens (documentation waste) | LOW (runtime impact) |
| `GEMINI.md` | (e) no security/testing/legal rules; very thin adapter (40 lines) | Structural gap not token waste | MEDIUM |
| `KNOWLEDGE.md` | (b) duplicates MEMORY.md on shell/git patterns; not auto-loaded but confusing when explicitly read | ~150 tokens when loaded | LOW |

---

## Model Currency Check

| Check | Status | Detail |
|---|---|---|
| `config/agents/model-registry.yaml` age | CURRENT | `last_updated: 2026-02-18` (2 days ago, within 14-day threshold) |
| `model-registry.yaml` version | v2.1.0 | Sonnet 4.6 as default, Opus 4.6 for Route C plan phase |
| Hardcoded stale IDs in `.sh` files | FAIL | 5 scripts with stale IDs: `auto-fix-loop.sh`, `primary-claude.sh` (claude-sonnet-4-20250514), `review-openai.sh` (gpt-4o), `test-runner.sh` (gemini-2.0-flash), `agent_orchestrator.sh` (claude-sonnet-4.5) |
| Hardcoded stale IDs in `.py` files | 1 file | `scripts/data/og-standards/rag.py` — needs inspection |
| `workflow-guards.sh` model map | OK | Lines 160-164: inline model name→ID map is manually maintained but matches registry |
| `scripts/maintenance/update-model-ids.sh` | EXISTS, NOT SCHEDULED | Script exists and is functional; no cron entry found in `crontab.example` or any `.cron` file for this script |
| CODEX.md MAX_TEAMMATES | STALE | Claims 3; settings.json has 5 (updated by commit 48aca5b) |
| MEMORY.md Opus 4.5 reference | STALE | "preferred over Opus 4.5" — Opus 4.5 not in model-registry.yaml |

---

## Proposed Fixes (for user review — not applied yet)

### Fix 1: Trim CLAUDE.md — remove/relocate 4 sections (~2100 bytes)

**File:** `/mnt/local-analysis/workspace-hub/CLAUDE.md`

**Section: Windows Compatibility**
- Action: Remove entirely from CLAUDE.md
- Rationale: Machine is `Linux ace-linux-1`. If Windows support is re-introduced, restore. Until then, 404 bytes of MINGW/CRLF/symlink rules load for every session on a Linux host with zero benefit.
- Cross-reference: KNOWLEDGE.md §Environment Conventions already has Windows paths; git-workflow.md can carry the "LF line endings" note.

**Section: Resource Index (inline)**
- Action: Replace 13-line inline block with a single pointer: `See .claude/RESOURCE_INDEX.md (auto-generated).`
- Rationale: `.claude/RESOURCE_INDEX.md` at 13,907 bytes (auto-generated at session end) is the canonical, always-current index. The 1095-byte inline copy is static and drifts. Saves ~950 bytes.

**Section: SPARC Modes**
- Action: Collapse to one line: `/sparc-*: architect, coder, reviewer, tester, planner — see .claude/agent-library/sparc/`
- Rationale: 82 bytes becomes ~80 bytes (no savings, but removes the invitation to use SPARC without any context that it hasn't been used in 2026-02 sessions at all). Alternatively: move to Command Conventions.

**Section: Plan Mode Convention (cross-review sub-block)**
- Action: Replace the 5-line cross-review procedure block (Codex = hard gate, Gemini CLI syntax) with: `Cross-review: see work-queue/process.md. Codex is required for Route B/C.`
- Rationale: The detailed procedure (including Gemini CLI syntax that contradicts MEMORY.md) is duplicated in `process.md`. Saves ~400 bytes and eliminates the Gemini syntax contradiction.

Estimated total savings: ~2100 bytes (brings CLAUDE.md from 6728b to ~4600b, still slightly over 4KB but much closer).

---

### Fix 2: Correct CODEX.md stale facts

**File:** `/mnt/local-analysis/workspace-hub/.codex/CODEX.md`

**Section: Default thread cap, line 73**
- Action: Change `MAX_TEAMMATES=3` to `MAX_TEAMMATES=5`
- Rationale: settings.json ground truth is 5 since commit 48aca5b. CODEX.md is factually wrong.

**Section: Required Gates (add security/legal note)**
- Action: Add: `4. All code must pass legal-sanity-scan.sh before PR. Secrets must use environment variables, never hardcoded.`
- Rationale: Codex is the primary code-writing provider. Security and legal rules not present in its adapter.

---

### Fix 3: Consolidate MEMORY.md stale WRK references

**File:** `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md`

**Section: AI Orchestration, line 58**
- Action: Change `"WRK-198/200-202 done"` to `"WRK-200/201 done; WRK-198 pending; WRK-202 pending"`
- Rationale: WRK-198 is in `pending/`; WRK-202 not found in archive. Recording done items as done and pending items as pending prevents false-confidence routing decisions.

**Section: AI Orchestration, line 54**
- Action: Remove `"preferred over Opus 4.5"` — replace with `"preferred over Opus 4.6 for iterative work"`
- Rationale: Opus 4.5 doesn't exist in the model registry. The contrast should be Opus 4.6 vs Sonnet 4.6.

**Section: Work Queue, line 33**
- Action: Remove the static count `"200+ items, ~95 archived"` — replace with: `"See .claude/work-queue/INDEX.md for current counts (auto-generated)"`
- Rationale: Static counts drift immediately. The auto-generated index is the live truth.

---

## Preflight Hook Design

Based on findings, the preflight hook (to run before every session response and at `/session-start`) should perform these checks:

**Check 1: CLAUDE.md size gate**
- What it detects: `wc -c CLAUDE.md` exceeds 4096 bytes (4KB budget from CLAUDE.md line 3)
- Warning: `[R5-CLAUDE] CLAUDE.md is Xb (Y% of 4KB limit). Top trim candidate: <section>`
- Evidence: Already fires on every session (readiness-report.md R5 warning, confirmed)
- Improvement: Surface which section is largest (currently omits section breakdown)

**Check 2: Total context budget**
- What it detects: Sum of CLAUDE.md + rules/*.md + MEMORY.md exceeds 16KB
- Warning: `[R5-CONTEXT] Total context Xb (Y% of 16KB budget)`
- Evidence: Already fires; refinement needed to show per-file breakdown to identify biggest contributors quickly

**Check 3: CODEX.md MAX_TEAMMATES sync**
- What it detects: `grep MAX_TEAMMATES .claude/settings.json` value vs `grep MAX_TEAMMATES .codex/CODEX.md`
- Warning: `[R-CODEX] CODEX.md MAX_TEAMMATES value does not match settings.json`
- Evidence: Currently undetected drift (3 vs 5)

**Check 4: Model ID currency**
- What it detects: Presence of known-stale model strings (`claude-sonnet-4-20250514`, `gpt-4o`, `gemini-2.0-flash`) in `scripts/` directory
- Warning: `[R-MODEL] X stale model IDs found in scripts/ — run scripts/maintenance/update-model-ids.sh`
- Evidence: 5 scripts currently contain stale IDs; `update-model-ids.sh` exists but is not scheduled

**Check 5: WRK item status drift**
- What it detects: Items named as "done" in MEMORY.md that are still in `pending/` or not in `archive/`
- Warning: `[R-WRK] MEMORY.md references WRK-NNN as done but item is not archived`
- Evidence: WRK-198 claimed done in MEMORY.md, found in `pending/`

**Check 6: Cross-provider rule coverage**
- What it detects: Rules present in `rules/*.md` but absent from both CODEX.md and GEMINI.md (specifically: security, legal-compliance, testing)
- Warning: `[R-XPROV] Security/legal/testing rules not propagated to CODEX.md or GEMINI.md`
- Evidence: All five rule files are Claude-only; Codex executes code without any security rules

**Check 7: model-registry.yaml age**
- What it detects: `last_updated` field in `config/agents/model-registry.yaml` is older than 14 days
- Warning: `[R-REGISTRY] model-registry.yaml last updated Nd ago — review for new model releases`
- Evidence: Currently 2 days old (CURRENT); check would have caught the Feb-18 update within the window

---

*Steps 4 (file edits) and 5 (preflight hook implementation) are pending user review.*
