# Plan for #3532: Reserve cross-provider memory budget for operational feedback

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3532
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3532-claude.md` | `scripts/review/results/2026-07-14-plan-3532-codex.md` | `scripts/review/results/2026-07-14-plan-3532-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/memory/curate_readback_slice.py` reads only git-tracked memory, filters Claude-only slugs, preserves source order, and caps Codex/Gemini at 7,000 characters. `_collect_entries()` currently returns unclassified strings, so project rows consume the cap before feedback and institutional knowledge.
- `scripts/memory/tests/test_curate_readback_slice.py` already covers caps, entry-boundary truncation, machine invariance, determinism, filtering, and Codex/Gemini parity; class-allocation RED tests will extend this suite.
- `scripts/memory/bridge-hermes-claude.sh` already invokes the curator for Codex and Gemini with temp-file-then-move safety. Its generator path will remain canonical and will not be reimplemented.
- `config/agents/codex/MEMORY.runtime.md` and `config/agents/gemini/MEMORY.runtime.md` are managed outputs; each current file contains 36 project entries and zero feedback entries.

### Standards

| Standard | Status | Source |
|---|---|---|
| Cross-agent context parity | applicable; compact, curated, git-tracked memory required | `.claude/skills/coordination/agent-memory-bridge/SKILL.md` |
| Managed runtime artifacts | applicable; generator-only edits | managed headers in `config/agents/{codex,gemini}/MEMORY.runtime.md` |
| TDD and user approval | mandatory | `AGENTS.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` |

### LLM Wiki pages consulted

- No relevant wiki pages apply; this is agent-memory infrastructure.

### Documents consulted

- [Issue #3532](https://github.com/vamseeachanta/workspace-hub/issues/3532) defines class-aware allocation and hard-cap requirements.
- [Issue #3527](https://github.com/vamseeachanta/workspace-hub/issues/3527) supplies the incident that exposed missing cross-provider retrieval.
- `.claude/memory/claude-auto-memory.md` places project entries before key lessons; the strict-up-to-date and generated-state lessons occur later in the tracked index.
- `.claude/memory/topics/feedback_strict_uptodate_ruleset_no_admin_bypass.md` already describes latest-base/ruleset behavior.
- `.claude/memory/topics/feedback_verify_generated_state_against_origin_not_working_copy.md` already describes canonical generated-state verification.
- `analysis/provider-session-ecosystem-audit.json` records session-read asymmetry across Claude, Codex, and other providers; adding more source memory without retrieval allocation will not close the read-back gap.
- Drive-file index results from #3527 contain no relevant off-repo memory-system document; repo-tracked sources are authoritative.

### Gaps identified

- Candidate entries carry no allocation class.
- No deterministic budget reservation protects operational feedback or `.claude/memory/KNOWLEDGE.md` bullets from project-list pressure.
- Tests do not exercise mixed-class cap pressure or guarantee retention of representative merge/generated-state lessons.
- Managed Codex/Gemini runtime outputs omit operational feedback under the current nominal 7,000-character cap; they measure 7,077 UTF-8 bytes, exposing the unit mismatch this plan will close.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-14):

- [#3532](https://github.com/vamseeachanta/workspace-hub/issues/3532) — OPEN, `status:needs-plan`, `lane:claude`.
- [#3527](https://github.com/vamseeachanta/workspace-hub/issues/3527) — OPEN; scheduler repair remains separately scoped.

**Reproduction proof** (fresh `origin/main` `03cc01e0ca4793b7208d449b7310d6a47bd3fe9a`, 2026-07-14):

```text
config/agents/codex/MEMORY.runtime.md entries=36 project_entries=36 feedback_entries=0
config/agents/gemini/MEMORY.runtime.md entries=36 project_entries=36 feedback_entries=0
strict-up-to-date lesson present: false
generated-state-against-origin lesson present: false

.claude/memory/claude-auto-memory.md:67  feedback_strict_uptodate_ruleset_no_admin_bypass
.claude/memory/claude-auto-memory.md:86  feedback_verify_generated_state_against_origin_not_working_copy
```

Failure mode observed matches issue claim: **YES**. The issue body was corrected from an earlier 25-entry observation to the fresh 36-entry result.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-14-issue-3532-cross-provider-memory-budget.md` |
| Human-readable plan | `docs/plans/2026-07-14-issue-3532-cross-provider-memory-budget.html` |
| Curator | `scripts/memory/curate_readback_slice.py` |
| Priority manifest | `config/agents/memory-readback-priorities.yaml` |
| TDD suite | `scripts/memory/tests/test_curate_readback_slice.py` |
| Codex output | `config/agents/codex/MEMORY.runtime.md` |
| Gemini output | `config/agents/gemini/MEMORY.runtime.md` |

---

## Deliverable

The canonical curator will deterministically reserve a 7,000 UTF-8 byte runtime-memory budget across institutional knowledge, operational feedback, and active context so Codex/Gemini receive critical working lessons without losing current project context.

---

## Pseudocode

```text
classify each candidate entry:
    unindented .claude/memory/KNOWLEDGE.md bullet without a terminal *stale: ...* marker -> institutional
    indented/nested or explicitly stale .claude/memory/KNOWLEDGE.md bullet -> not a standalone entry
    auto-memory slug beginning feedback_ -> operational
    every other allowed auto-memory row -> context

measure the cap and every entry in UTF-8 bytes
load and validate the repo-tracked ordered priority-slug manifest
reserve the UTF-8 byte length of the maximum-count omitted marker using total candidate count
allocate usable budget after header and marker:
    institutional reservation = 15 percent
    operational reservation = 50 percent
    context reservation = usable - floor(institutional) - floor(operational)

for each class in institutional, operational, context order:
    preserve that class's source order
    for operational, select required priority slugs first in manifest order
    fail closed if required slugs are missing, duplicated, filtered, or exceed reservation
    pack remaining whole entries within the class reservation

combine every unused reservation and integer remainder into a spill budget
reconsider omitted whole entries in original global source order
sort selected entries by original source position before emission
emit managed header, selected whole entries, and exact omitted count
never exceed the UTF-8 byte cap; never read HOME; keep equal-cap Codex/Gemini byte-identical
```

The class ratios will be named constants with comments so policy is reviewable. A new repo-tracked priority manifest will initially require the two incident-relevant slugs, `feedback_strict_uptodate_ruleset_no_admin_bypass` and `feedback_verify_generated_state_against_origin_not_working_copy`, for every target. This is a general, reviewable promotion surface rather than title matching or code-level special casing. `reference_` and unknown auto-memory slugs will default to `context`, preserving the existing default-include polarity without allowing reference pressure to displace feedback. Reserving the maximum possible marker length will terminate in one packing pass and will keep the emitted omitted count exact, at the cost of only the deterministic difference between maximum-count and actual-count marker length. Caps at or above the smallest production default (2,000 bytes) will enforce manifest priorities fail-closed. Smaller custom caps will remain an explicitly degraded diagnostic mode that may clamp the header and will not promise priority or exact-marker retention.

---

## Implementation Tasks

### Task 1: Add RED mixed-class allocation contracts

**File:** modify `scripts/memory/tests/test_curate_readback_slice.py`.

- [ ] Build a pressure fixture whose project rows alone exceed the cap while institutional, feedback, reference, and unknown rows are also present.
- [ ] Require at least one institutional bullet, operational feedback, and context row to survive.
- [ ] Require the strict-up-to-date and generated-state representative lesson rows to survive at the production Codex/Gemini cap.
- [ ] Run the retention assertion against the actual tracked `.claude/memory/` corpus at production caps, not only a synthetic fixture.
- [ ] Require both manifest-priority rows to survive at the production Hermes cap; missing, duplicate, filtered, or over-budget required slugs will fail closed rather than silently degrade.
- [ ] Require stable final source ordering even when an earlier large entry is selected during spill after a later small entry, deterministic spill behavior, exact omitted count, whole-entry output, UTF-8 byte cap, and Codex/Gemini parity.
- [ ] Add an integer-rounding fixture whose usable budget is not divisible by 100 and require context to receive the deterministic remainder before spill.
- [ ] Add omitted-count digit-boundary cases proving the maximum-count reserve always bounds the exact emitted marker, and define production-cap behavior separately from the degraded cap-below-2,000 fallback.
- [ ] Add production 2,000-byte Hermes coverage proving institutional, feedback, and context retention plus exact marker/whole-entry behavior.
- [ ] Add institutional eligibility tests proving nested bullets do not detach from their parent and terminal markers matching `r"\*stale:\s*[^*]+\*\s*$"` do not consume protected budget; unrelated prose containing “stale” remains eligible.
- [ ] Add a negative/default test proving an unknown slug remains included as context rather than being silently dropped.
- [ ] Run the focused suite and capture RED failures under the current source-order allocator.

### Task 2: Implement deterministic class-aware packing

**Files:** create `config/agents/memory-readback-priorities.yaml`; modify `scripts/memory/curate_readback_slice.py`.

- [ ] Introduce a small immutable entry record carrying text, UTF-8 byte length, source position, slug/source, and class.
- [ ] Preserve the current Claude-only slug filter and machine-invariant source boundary.
- [ ] Tighten `.claude/memory/KNOWLEDGE.md` collection to column-zero bullets and exclude only a terminal `r"\*stale:\s*[^*]+\*\s*$"` marker; do not use broad title substring heuristics.
- [ ] Parse the manifest with strict schema validation and expose an injectable priority list/path for isolated unit fixtures.
- [ ] Implement 15/50/remainder reservations, entry-boundary packing, deterministic original-order spill selection, and final source-position emission.
- [ ] Replace the fixed 64-byte reserve with a single-pass reserve equal to the UTF-8 byte length of the marker for all candidates omitted; emit the exact actual omitted count without repacking.
- [ ] Assign every entry a globally unique collection ordinal (auto-memory rows first in file order, then eligible `.claude/memory/KNOWLEDGE.md` rows in file order) and use it for final emission.
- [ ] Enforce manifest priority guarantees and strict validation only for caps at or above 2,000 bytes; preserve existing explicit clamp semantics for smaller diagnostic caps.
- [ ] Apply the same class-aware policy to Hermes and enforce useful three-class coverage at its production 2,000-byte cap.
- [ ] Keep the current managed header, degenerate tiny-cap clamp, CLI, target caps, Claude-only filter, and equal-cap Codex/Gemini byte parity.
- [ ] Run the focused tests and require GREEN before regenerating managed outputs.

### Task 3: Regenerate and verify managed provider runtimes

**Files:** regenerate `config/agents/codex/MEMORY.runtime.md` and `config/agents/gemini/MEMORY.runtime.md` using the curator command used by bridge section 7b.

- [ ] Generate each repo-tracked target to a temporary file, validate non-empty output/UTF-8 byte cap/managed header, then replace its runtime artifact. Generate the Hermes slice to a temporary verification path without replacing the operator's local memory sink.
- [ ] Prove both critical lessons, at least one institutional row, and at least one active project row are present.
- [ ] Prove Codex and Gemini outputs are byte-identical at the equal 7,000-byte cap and prove a 2,000-byte Hermes generation retains all three classes.
- [ ] Run a second generation and require a byte-identical diff.
- [ ] Verify only the curator, priority manifest, tests, two managed runtimes, plan/review artifacts, and plan index change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/memory/tests/test_curate_readback_slice.py` | Add RED allocation, retention, spill, and parity contracts |
| Modify | `scripts/memory/curate_readback_slice.py` | Implement deterministic class-aware budget allocation |
| Create | `config/agents/memory-readback-priorities.yaml` | Declare ordered must-retain operational slugs outside code |
| Regenerate | `config/agents/codex/MEMORY.runtime.md` | Publish balanced Codex read-back context |
| Regenerate | `config/agents/gemini/MEMORY.runtime.md` | Publish balanced Gemini read-back context |
| Update | `docs/plans/README.md` | Index this plan |

The managed runtime files will never be hand-edited.

---

## TDD Test List

| Test name | What it will verify | Expected RED | Expected GREEN |
|---|---|---|---|
| `test_class_reservations_survive_project_pressure` | all three classes retain entries under 15/50/remainder allocation | projects consume entire cap | institutional/operational/context survive |
| `test_live_merge_lessons_survive_production_cap` | representative critical feedback reaches providers | both lessons absent | both lessons present |
| `test_tracked_corpus_retains_manifest_priorities` | production source/caps satisfy the actual contract | current runtimes omit priorities | direct curate of tracked corpus retains both |
| `test_priority_manifest_fails_closed` | missing/duplicate/filtered/over-budget priorities cannot silently vanish | no manifest contract | precise validation error and no output replacement |
| `test_spill_reuses_post_reserve_budget_deterministically` | all capacity remaining after the pessimistic marker reserve is reusable | source-order-only selection | remaining class capacity fills in original order; marker-reserve slack is explicitly permitted |
| `test_spill_selection_emits_in_original_order` | earlier skipped/later packed entries never invert | selection order would invert | final source-position order is stable |
| `test_reservation_rounding_remainder_is_deterministic` | non-divisible budget has no ambiguous bytes | rounding unspecified | context receives exact remainder |
| `test_exact_marker_across_digit_boundaries` | pessimistic maximum-count reserve bounds exact marker | fixed 64-byte reserve | exact count and byte cap at 9/10/99/100 |
| `test_unknown_slug_defaults_to_context` | default-include polarity remains | unclassified behavior | unknown row retained when capacity permits |
| `test_class_order_is_stable` | per-class source order is deterministic | no class contract | repeatable ordered output |
| `test_hermes_production_cap_retains_all_classes` | shared 2,000-byte target remains useful | no allocation contract | knowledge/feedback/context and marker survive |
| `test_institutional_entries_are_top_level_and_current` | nested or explicit stale bullets cannot consume reservation | current `strip()` detaches/includes them | only current column-zero bullets qualify |
| `test_small_custom_cap_is_explicitly_degraded` | sub-2,000 diagnostic caps retain legacy clamp without false priority promise | precedence ambiguous | bounded degraded output; no priority assertion |
| `test_supported_cap_fails_closed_on_priority_error` | production/default caps never silently omit manifest rows | priorities could vanish | precise nonzero failure before output replacement |
| existing cap/oversize/tiny-cap tests | hard limits and whole entries remain | current baseline GREEN | remain GREEN |
| existing Gemini parity tests | equal-cap provider outputs remain identical | current baseline GREEN | remain GREEN |

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/memory/tests/test_curate_readback_slice.py -q` passes.
- [ ] Each repo-tracked runtime output is non-empty, managed, and at most 7,000 UTF-8 bytes.
- [ ] Both runtime outputs contain the strict-up-to-date and generated-state-against-origin lessons.
- [ ] The priority manifest is schema-valid, contains no duplicate/filtered/missing slug, and fits the 2,000-byte Hermes operational reservation.
- [ ] Both outputs contain institutional knowledge, operational feedback, and active project context.
- [ ] Institutional output contains no detached nested bullet or entry matching terminal `r"\*stale:\s*[^*]+\*\s*$"`.
- [ ] Codex and Gemini outputs are byte-identical at equal cap.
- [ ] A 2,000-byte Hermes generation retains institutional knowledge, operational feedback, and active context without mutating the local operator sink during verification.
- [ ] Two consecutive generations from the same tracked source are byte-identical.
- [ ] Claude-only slugs remain excluded and unknown slugs remain default-included.
- [ ] No HOME/per-machine file influences curation.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes.
- [ ] Adversarial code/artifact reviews have no unresolved MAJOR findings.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR r1 addressed; final unavailable | Independent r1 caught allocation/test/Hermes/institutional defects; bounded final retries exhausted turn caps. |
| Codex | MINOR (round 3) — addressed | After two MAJOR rounds were corrected, round 3 confirmed feasibility/termination and narrowed stale-marker acceptance plus permitted pessimistic-marker slack. |
| Gemini | UNAVAILABLE | CLI exit 41: noninteractive authentication unavailable. |

**Overall result:** PASS (provider coverage degraded) — Codex no-MAJOR after three adversarial rounds; Claude/Gemini availability remains documented. Implementation remains blocked pending user approval.

Revisions made after round 1:

- Changed 15/45/40 character allocation to 15/50/remainder UTF-8 byte allocation, limited the operational class to structured `feedback_` slugs, and added a fail-closed repo-tracked must-retain manifest.
- Replaced potentially oscillating fixed-point marker accounting with a one-pass maximum-count reserve; added deterministic rounding, global-ordinal emission, digit-boundary tests, and explicit supported/degraded cap precedence.
- Added explicit production-cap Hermes contracts because the shared curator serves Hermes too.
- Added live-corpus retention proof for both required lessons and top-level/current institutional eligibility before approval.

---

## Risks and Open Questions

- **Policy rigidity:** fixed ratios may underfill a sparse class. Deterministic global spill will reclaim unused reservation without weakening minimum class opportunity. A live-corpus pre-approval simulation must prove all manifest priorities fit the smallest 2,000-byte target's operational reservation.
- **Entry-size pressure:** a required lesson that cannot fit the smallest supported operational reservation will fail generation before output replacement. Non-required oversized entries will be omitted at boundaries with an exact count; no mid-entry truncation will be introduced.
- **False classification:** only structured source/slug rules will classify entries; title substring matching will remain forbidden.
- **Context freshness:** reserving operational space reduces the number of project rows. The context class receives the deterministic remainder (approximately 35%) plus spill, and tests will require active context to remain present.
- **Managed-file churn:** regeneration will use identical tracked inputs and a second-run equality check.

---

## Complexity: T2

This changes a deterministic selector shared by Hermes/Codex/Gemini and two repo-managed provider runtimes with focused unit tests. It has no external service or live scheduler mutation.
