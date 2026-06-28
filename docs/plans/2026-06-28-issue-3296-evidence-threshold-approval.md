# Plan for #3296: Evidence-threshold approval evolution (graduate routine approvals off user-gate)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3296
> **Client:** N/A     <!-- governance/policy; touches no wiki content -->
> **Project:** (none)
> **Lane:** lane:claude   <!-- governance authoring + a small advisory pilot module; no heavy compute -->
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3296-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

Issue class: **Documentation / Governance** (universal minimum + governance bundle). Consulted: issue body, parent epic, the agents.md rule being implemented, the two cited enforcement substrates (#2798 completeness gate, #1839 enforced-gates), the live plan-approval hook, and the review-artifact substrate that the rigor metrics must read from.

### Existing repo code
- Found: `.claude/hooks/plan-approval-gate.sh` — the load-bearing PreToolUse hook. `has_approval()` (line 34) accepts a write only when a non-self-approved marker exists under `.planning/plan-approved/`; `is_self_approved()` (line 54) rejects markers that say "Worker session/auto-approved/self-approved" or are <120s old and never committed. `is_safe_path()` (line 75) already exempts `docs/governance/*` and `docs/plans/*` (line 80), so this plan's deliverables write without a marker. **This is the exact mechanism #3296 proposes to evolve** — any auto-approval scheme must interoperate with, not bypass, this gate.
- Found: `scripts/workflow/completeness_score.py` — the closest existing "evidence-based gate" pattern, and the **direct template** for this plan's evaluator on three points:
  1. **Class is auto-derived from changed files, NOT caller-selectable** — `classify(changed_files, path_package_map)` (line 83) returns `code` if any changed file maps to a package else `evidence`, with the explicit "dodge code scoring via the ops path" anti-gaming note (lines 1-7, 84-88). The #3296 evaluator MUST mirror this: `issue_class` is **derived, never caller-supplied** (owner decision D5).
  2. **Fail-closed validation BEFORE arithmetic, not just before comparison** — `score_code` coerces and validates coverage with `cov = float(changed_code_coverage)` then `if not (0.0 <= cov <= 1.0): raise CompletenessError` (lines 113-114) **before** any downstream arithmetic uses `cov`, and the comment notes "NaN compares False on both sides -> rejected". The #3296 evaluator reuses the exact finite-range guard **and follows the same ordering discipline: validate every raw metric is a finite number in its declared raw domain INSIDE `normalize_metrics` BEFORE performing any arithmetic (`1.0 - raw`, `(raw - best)/span`)** — so a missing/None/non-numeric raw metric can never reach an arithmetic op and raise a `TypeError`. It still **deliberately diverges on the failure action** (see below).
  3. `THRESHOLDS = {"code": 90, "evidence": 80}` (line 30) — a small, named threshold table, the shape the policy doc's metric thresholds follow.
- **Deliberate divergence from `completeness_score.py` on malformed-input handling (owner decision D5).** `completeness_score.py` *raises* `CompletenessError` on an out-of-range/NaN metric (line 114-115) because it is a scoring module whose only correct response to bad input is to halt the score. The #3296 evaluator instead **fails closed to `INELIGIBLE` (stays manual)** on a missing, non-finite, or out-of-domain metric. Rationale: the evaluator's safe state is "keep the human-in-loop gate," so a malformed metric must yield the conservative *verdict*, not a raised exception that a shadow-mode advisory caller could swallow and mis-default. **This divergence is only honored if the validation actually runs first:** the check therefore sits **inside `normalize_metrics`, before any arithmetic**, and short-circuits to INELIGIBLE for BOTH higher-is-better and lower-is-better metrics — otherwise a lower-is-better raw metric would raise a `TypeError` in `1.0 - raw` / `(raw - best)/span` *before* the conservative verdict could be produced, re-introducing the exact raise-on-malformed direction this divergence is meant to eliminate (Round-2 finding). This is the single intentional deviation from the template and is called out in the policy doc.
- Found: `.github/workflows/completeness-gate.yml` — the opt-in rollout precedent. Fires only when `state_reason == 'completed'` **AND** `contains(labels, 'gate:completeness')` (lines 23-25). The evidence-threshold pilot reuses this **opt-in label + server-side authority** shape. **This plan does not author or modify that workflow** (the pilot ships only the pure evaluator + policy + tests; any server-side enforcement is a later, separately-approved graduation phase).
- Gap: No `scripts/governance/` directory exists (`ls scripts/governance/` → "No such file or directory"). No existing eligibility evaluator, evidence ledger, or rigor-metrics aggregator anywhere in the repo.

### Standards
Not applicable — this is a workspace-hub governance/policy issue, not an engineering-calculation issue. No entry in `standards-transfer-ledger.yaml` is implicated.

### LLM Wiki pages consulted
No relevant wiki pages — the work is workspace-hub-internal governance and touches no `llm-wiki`/`llm-wiki-<client>` content. Per `.claude/rules/wiki-sibling-routing.md` "Do not apply when … the content is a workspace-hub-internal artifact (rule, skill, doc, hook script)," `Client: N/A` is correct.

### Documents consulted
- `.claude/memory/agents.md:57` — the **"Autonomous gate evolution"** rule this issue implements: *"hard gates remain in force until metrics prove agent rigor is consistently safe; over time, shift routine plan/review/execution/verification cycles from user-managed approval to evidence-threshold approval so the owner focuses on ideas, GTM throughput, and customer/prospect artifacts."* This plan converts that one-line intent into a concrete metric+threshold+eligibility policy.
- Parent epic [#3290](https://github.com/vamseeachanta/workspace-hub/issues/3290) — Theme D "Owner orchestration overhead." Epic acceptance includes: *"A written, owner-approved policy for evidence-threshold approval graduation exists."* This issue is the sole Theme-D child. **Epic sequencing (owner decision D6):** sibling #3283 (golden-harness / volatile-field spec) is deferred to Wave 2 and is **not** a dependency of this plan; the #3296 evidence ledger is governance-internal and does **not** define the envelope-determinism fields owned by #3282/#3283 (see Open Questions / Scope boundaries).
- `config/agents/claude/SOUL.runtime.md` Must-Fire rule **"Never self-label `status:plan-approved`. The user-in-loop approval gate is load-bearing. Never offer to self-apply; never pre-authorize via handoff prompt."** — the binding constraint the policy must not violate. The pilot must therefore start in **shadow mode** (compute + record an eligibility verdict; human still applies the label). **Owner decision D5:** the policy doc must name *"amend the SOUL never-self-approve must-fire rule"* as an explicit **hard precondition** of any future auto-apply phase — i.e., auto-apply cannot ship until that must-fire rule is itself amended by the owner. Shadow mode never touches it.
- `docs/governance/2026-06-17-cost-ceiling-policy.md` — format model for a workspace-hub decision record (Context / Decisions table / Enforcement status / Related). The policy doc will follow this shape.
- `scripts/review/results/` — the rigor-metric data substrate. Files are named `YYYY-MM-DD-plan-<issue>-<provider>.md` (live example: `2026-06-27-plan-3282-{claude,codex,gemini}.md` plus a `-disagreement.md`). The "adversarial-review APPROVE rate" metric reads verdicts from these artifacts; this confirms the data exists and is parseable.

### Gaps identified
- No definition anywhere of *which* metrics prove "agent rigor is consistently safe," nor their thresholds, rolling-window size, or minimum sample before graduation.
- No enumerated eligible/ineligible issue-class taxonomy (the policy must list both explicitly and fail-closed on unknown classes).
- No deterministic classifier mapping changed files + labels → issue class (the evaluator needs one so the class is never caller-supplied).
- No evidence ledger / audit-trail format making each (shadow) auto-approval reconstructable.
- No kill-switch design returning the pilot class to fully manual.
- No advisory eligibility evaluator module (would be built from scratch under a new `scripts/governance/`).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3296` — OPEN — "seamless(governance): evidence-threshold approval evolution (graduate routine approvals off user-gate)"; labels include `status:needs-plan`, `lane:claude`, `cat:ai-orchestration`.
- `#3290` — OPEN — parent epic "EPIC: Seamless ecosystem development …"; Theme D names this child.
- `#1839` — OPEN — "Workflow hard-stops and session governance — Hermes-orchestrated lifecycle with enforced gates" (the enforced-gates epic; substrate).
- `#2798` — CLOSED — "feat(governance): test-based completeness score (0–100%) as pre-closure hard-stop gate + HTML artifact" (substrate; landed).

**File existence** (`ls -la` 2026-06-28):
- EXISTS: `.claude/hooks/plan-approval-gate.sh` (5054 bytes)
- EXISTS: `scripts/workflow/completeness_score.py` (7758 bytes)
- EXISTS: `.github/workflows/completeness-gate.yml` (2792 bytes)
- EXISTS: `scripts/review/results/2026-06-27-plan-3282-claude.md` (+ codex/gemini/disagreement)
- MISSING (new — this plan creates): `docs/governance/2026-06-28-evidence-threshold-approval-policy.md`
- MISSING (new — this plan creates): `scripts/governance/evidence_threshold_eligibility.py`
- MISSING (new dir — `ls scripts/governance/` → "No such file or directory")

**Line excerpts (verified against the real files this revision):**
```
agents.md:57: - **Autonomous gate evolution**: hard gates remain in force until metrics prove
              agent rigor is consistently safe; over time, shift routine plan/review/execution/
              verification cycles from user-managed approval to evidence-threshold approval …
completeness_score.py:30:  THRESHOLDS = {"code": 90, "evidence": 80}
completeness_score.py:83:  def classify(changed_files, path_package_map) -> str:  # auto-derived, NOT selectable
completeness_score.py:114: if not (0.0 <= cov <= 1.0):  # NaN compares False on both sides -> rejected
completeness-gate.yml:23-25: if: >- github.event.issue.state_reason == 'completed' &&
              contains(github.event.issue.labels.*.name, 'gate:completeness')
plan-approval-gate.sh:80: */.planning/*|*/docs/plans/*|*/docs/governance/*|… return 0 ;;
```

**Gap proofs:**
- `ls scripts/governance/` → "No such file or directory" → confirms no eligibility evaluator/classifier exists.
- `ls scripts/workflow/ | grep -i 'ledger\|audit\|metric'` → empty → confirms no rigor-metric aggregator or audit ledger exists.

**Reproduction proofs:** N/A — this is a governance/policy issue with no runtime/behavioral claim. There is no failing test, broken import, or incorrect numeric output to reproduce. Per `issue-planning-mode` Step 1.5 skip-allowance ("documentation-only, governance-only"), the skip is intentional. Substrate existence was instead verified empirically above (file `ls`, line excerpts re-checked this revision, `gh issue view` states).

<!-- Distinct sources consulted: issue body (1) + epic #3290 (2) + agents.md (3) + SOUL.runtime.md (4) + completeness_score.py (5) + completeness-gate.yml (6) + plan-approval-gate.sh (7) + scripts/review/results/ (8) + cost-ceiling-policy.md (9). Count: 9 (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3296-evidence-threshold-approval.md |
| Policy doc (main deliverable) | docs/governance/2026-06-28-evidence-threshold-approval-policy.md |
| Ledger schema + dir | docs/governance/evidence-threshold/README.md (+ `ledger/.gitkeep`) |
| Pilot eligibility evaluator | scripts/governance/evidence_threshold_eligibility.py |
| Tests | tests/governance/test_evidence_threshold_eligibility.py |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3296-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3296-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3296-gemini.md |
| Plans index row | docs/plans/README.md |

---

## Deliverable

An owner-approved governance policy doc (`docs/governance/2026-06-28-evidence-threshold-approval-policy.md`) that defines the rigor metrics + thresholds, the explicit eligible/ineligible issue-class taxonomy (load-bearing gates stay manual), a **deterministic classifier** (changed files + labels → class, never caller-supplied), and an evidence-ledger/audit-trail format — backed by a small, fail-closed, **shadow-mode-only** advisory eligibility evaluator (`scripts/governance/evidence_threshold_eligibility.py`) with a kill-switch and TDD coverage, that recommends but never applies `status:plan-approved`. The graduation phase to true auto-apply will name **amending the SOUL never-self-approve must-fire rule** as a hard precondition (D5).

---

## Pseudocode

Pure, no-I/O evaluator (mirrors `completeness_score.py`'s fail-closed + non-selectable-class pattern). Inputs (`changed_files`, `labels`, raw `metrics_window`) are gathered by a thin CLI wrapper from authoritative sources — git for changed files, `gh` for issue labels — never passed in pre-classified by the agent. Shadow mode prints the verdict only.

```
# Load-bearing classes are NEVER eligible, regardless of metrics.
INELIGIBLE_CLASSES = {
    "ci-workflow", "schema-contract", "security-legal", "outward-facing",
    "engineering-calc", "harness-enforcement", "gate-self-modification"
}
ELIGIBLE_CLASSES = {
    "docs-typo-index",        # T1 single-file docs / index / README typo
    "test-only-additive",     # pure additive test changes, no src
    "low-risk-config",        # non-CI, non-schema config edits
}

# --- D5: class is DERIVED, never caller-supplied (mirrors completeness_score.classify) ---
function classify(changed_files, labels):
    # Deterministic, ordered, fail-closed: the FIRST load-bearing signal wins, so a
    # cross-cutting change can never down-classify itself into an eligible bucket.
    for f in changed_files or []:
        if f matches CI/workflow paths (.github/workflows/, .github/actions/):   return "ci-workflow"
        if f matches schema/contract paths (schema/, *.schema.json, registry):   return "schema-contract"
        if f matches security/legal paths (.legal-*, scripts/legal/, secrets):   return "security-legal"
        if f matches gate/hook self-mod (.claude/hooks/, plan-approval-gate):     return "gate-self-modification"
        if f matches harness/enforcement (scripts/enforcement/, SOUL, agents.md): return "harness-enforcement"
        if f maps to a source package (engineering calc):                         return "engineering-calc"
        if f matches outward-facing (reports shared w/ clients, public sites):    return "outward-facing"
    # label-derived signals (authoritative issue state, read via gh — not agent-asserted):
    if any(l in labels for l in ELIGIBLE-blocking labels e.g. "gate:*", "client:*"): return that load-bearing class
    # only-docs / only-tests / only-low-risk-config remain:
    if all changed_files are single-file docs/index/README:  return "docs-typo-index"
    if all changed_files under tests/ (additive):            return "test-only-additive"
    if all changed_files are non-CI/non-schema config:       return "low-risk-config"
    return "unknown"                                          # -> fail-closed to manual below

# --- D5 + R2: VALIDATE every raw metric BEFORE any arithmetic, THEN normalize to higher-is-better [0,1] ---
# Each metric_spec declares its raw domain [raw_lo, raw_hi]:
#   higher_is_better / rate_lower_better -> raw domain [0.0, 1.0]
#   count_lower_better                   -> raw domain [spec.best, spec.best + spec.span]
# normalize_metrics returns (normalized_dict, bad_metric_name). bad_metric_name is None on
# success, else the FIRST raw metric that is missing/None/non-numeric/non-finite/out-of-domain.
# The caller maps a non-None bad_metric_name to INELIGIBLE (fail-closed) — it never raises.
function normalize_metrics(raw_metrics, metric_specs):
    normalized = {}
    for name, spec in metric_specs.items():
        raw = raw_metrics.get(name)
        # R2 FIX: validate raw is a finite real number in its DECLARED raw domain BEFORE any
        # arithmetic (1.0 - raw, (raw - best)/span). Covers a MISSING key (raw is None),
        # None, bool, non-numeric, NaN/Inf, and out-of-domain — for BOTH higher-is-better
        # and lower-is-better metrics. Short-circuit to the caller; do NOT raise, do NOT
        # let a TypeError escape from the arithmetic below.
        if raw is None \
           or isinstance(raw, bool) \
           or not isinstance(raw, (int, float)) \
           or not isfinite(raw) \
           or not (spec.raw_lo <= raw <= spec.raw_hi):
            return (None, name)                  # caller -> INELIGIBLE, fail-closed to manual
        if spec.direction == "higher_is_better":    v = raw                                       # raw domain [0,1]
        elif spec.direction == "rate_lower_better": v = 1.0 - raw                                  # e.g. revert_rate, raw [0,1]
        elif spec.direction == "count_lower_better": v = max(0.0, min(1.0, 1.0 - (raw - spec.best)/spec.span))  # plan_revision_rounds
        normalized[name] = v
    return (normalized, None)                     # all raw metrics valid + in-domain

function evaluate_eligibility(changed_files, labels, raw_metrics, config):
    if config.kill_switch_on:                              # kill-switch = always manual
        return INELIGIBLE("kill-switch engaged")
    issue_class = classify(changed_files, labels)          # D5: derived, never caller-supplied
    if issue_class in INELIGIBLE_CLASSES:
        return INELIGIBLE("load-bearing class '%s' — stays manual" % issue_class)
    if issue_class not in ELIGIBLE_CLASSES:                # fail-closed on unknown / "unknown"
        return INELIGIBLE("class '%s' not in eligible set — fail-closed to manual" % issue_class)
    if raw_metrics.sample_size < config.min_sample:        # not enough evidence yet
        return INELIGIBLE("insufficient sample (n=%d < %d)" % (raw_metrics.sample_size, config.min_sample))

    # R2: validation now runs INSIDE normalize_metrics, BEFORE any arithmetic. A missing/None/
    # non-finite/out-of-domain raw metric returns (None, name) here -> INELIGIBLE, never a raise.
    normalized, bad_metric = normalize_metrics(raw_metrics, config.metric_specs)
    if bad_metric is not None:
        return INELIGIBLE("metric '%s' missing/non-finite/out-of-domain — fail-closed to manual" % bad_metric)

    for metric, threshold in config.thresholds.items():
        value = normalized.get(metric)
        # Defense-in-depth: the normalized value must still be a finite float in [0,1].
        # Raw-domain validation above already removed the TypeError path; this guard catches
        # any spec-arithmetic edge and remains fail-closed (INELIGIBLE), never raises.
        if value is None or not isfinite(value) or not (0.0 <= value <= 1.0):
            return INELIGIBLE("metric '%s' normalized out-of-range (%r) — fail-closed to manual" % (metric, value))
        if value < threshold:
            return INELIGIBLE("metric %s=%.3f < %.3f" % (metric, value, threshold))

    return ELIGIBLE_SHADOW(reason="all metrics pass; SHADOW MODE — human still applies label",
                           issue_class=issue_class,
                           audit=build_ledger_record(issue_class, normalized, raw_metrics, config))

function build_ledger_record(...):
    return {reviewed_commit_sha, plan_path, review_artifact_paths,
            issue_class, raw_metric_snapshot, normalized_metric_snapshot, thresholds,
            window_bounds, sample_size, decision, decided_at_utc, mode:"shadow"}
```

Rigor metrics (computed over a trailing window of eligible-class issues; full definitions + normalization direction + **declared raw domain** in the policy doc). Each metric spec declares a `[raw_lo, raw_hi]` domain that is validated **before any normalization arithmetic**; each is then normalized to a **higher-is-better [0,1]** score before the threshold loop:
1. **adversarial_review_approve_rate** (`higher_is_better`, raw domain [0,1]) — fraction of plans where all required providers returned APPROVE (no MAJOR) on first pass, read from `scripts/review/results/`.
2. **post_merge_revert_rate** (`rate_lower_better` → normalized `1 - rate`, raw domain [0,1]) — fraction of merged eligible-class issues reopened/reverted/bug-followed within N days. Externally grounded (depends on real reopens the agent cannot fake).
3. **completeness_gate_pass_rate** (`higher_is_better`, raw domain [0,1]) — fraction of opted-in closes passing #2798 at/above threshold on first computation.
4. **reproduction_compliance_rate** (`higher_is_better`, raw domain [0,1]) — fraction of plans with a valid Step-1.5 reproduction citation or a justified `N/A`.
5. **plan_revision_rounds** (`count_lower_better` → normalized to [0,1], raw domain [`best`, `best`+`span`]) — mean MAJOR-driven re-draft rounds before approval.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/governance/2026-06-28-evidence-threshold-approval-policy.md | main deliverable: metrics + normalization directions, thresholds, eligible/ineligible taxonomy, deterministic classifier spec, ledger format, pilot scope, kill-switch, graduation phases (with SOUL-amendment precondition) |
| Create | docs/governance/evidence-threshold/README.md | evidence-ledger schema + audit-trail reconstruction guide (governance-internal; NOT the #3282/#3283 envelope-determinism schema) |
| Create | docs/governance/evidence-threshold/ledger/.gitkeep | ledger directory placeholder (append-only JSON records land here) |
| Create | scripts/governance/evidence_threshold_eligibility.py | pure, fail-closed, shadow-mode advisory evaluator + deterministic `classify()` + `normalize_metrics()` that validates each raw metric's finite-in-declared-raw-domain status BEFORE any arithmetic and signals INELIGIBLE (returns `(None, name)`, never raises) for missing/None/non-finite/out-of-domain metrics |
| Create | tests/governance/test_evidence_threshold_eligibility.py | TDD suite (written first) |
| Update | docs/plans/README.md | add this plan's index row |

> Note: this plan deliberately does **not** modify `.claude/hooks/plan-approval-gate.sh`, `.github/workflows/completeness-gate.yml`, `agents.md`, `SOUL.runtime.md`, or any `status:*` label flow. The pilot is shadow-mode only; touching the load-bearing gate (and amending the SOUL never-self-approve rule, which is the *precondition* for auto-apply) is explicitly out of scope until a later, separately-approved graduation phase.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_classify_ci_workflow_changed_file | CI path → load-bearing class, never caller-chosen | changed_files=[".github/workflows/x.yml"] | classify(...) == "ci-workflow" |
| test_classify_gate_self_mod_changed_file | editing the gate itself → load-bearing | changed_files=[".claude/hooks/plan-approval-gate.sh"] | classify(...) == "gate-self-modification" |
| test_classify_docs_typo_single_file | only a docs file → eligible class | changed_files=["docs/foo.md"], labels=[] | classify(...) == "docs-typo-index" |
| test_classify_mixed_change_picks_load_bearing | a docs+CI change cannot down-classify to docs | changed_files=["docs/foo.md", ".github/workflows/x.yml"] | classify(...) == "ci-workflow" (load-bearing wins) |
| test_classify_unknown_when_no_rule_matches | unmatched change → "unknown" | changed_files=["weird/path.bin"] | classify(...) == "unknown" |
| test_issue_class_is_not_a_parameter | no caller-supplied class path exists | inspect `evaluate_eligibility` signature | has no `issue_class` param; derives via classify() |
| test_load_bearing_class_blocked_even_with_perfect_metrics | derived ineligible class never graduates | CI changed file, all metrics 1.0, sample≥min | INELIGIBLE("load-bearing class 'ci-workflow'") |
| test_unknown_class_fails_closed | unrecognized class → manual | changed_files=["weird/path.bin"] | INELIGIBLE("not in eligible set — fail-closed") |
| test_kill_switch_forces_manual | kill-switch overrides everything | eligible docs change, perfect metrics, kill_switch_on=True | INELIGIBLE("kill-switch engaged") |
| test_insufficient_sample_blocks | below min sample → manual | eligible class, sample_size=3, min_sample=20 | INELIGIBLE("insufficient sample") |
| test_lower_is_better_metric_normalized_before_loop | revert_rate normalized 1-rate before compare | revert_rate raw=0.02 (→0.98), threshold=0.95 | ELIGIBLE_SHADOW (passes after normalization) |
| test_lower_is_better_metric_unnormalized_would_fail | proves normalization is load-bearing | revert_rate raw=0.02 compared RAW against 0.95 would block | normalized path → ELIGIBLE_SHADOW (raw path would wrongly INELIGIBLE) |
| test_metric_below_threshold_blocks | one failing normalized metric blocks | eligible class, approve_rate=0.7, threshold=0.9 | INELIGIBLE("metric … < …") |
| test_eligible_shadow_when_all_pass | happy path → shadow-eligible | eligible class, all normalized metrics ≥ thresholds, sample≥min | ELIGIBLE_SHADOW + audit record |
| test_ledger_record_has_required_fields | audit reconstructability | a shadow-eligible decision | record contains reviewed_commit_sha, plan_path, review_artifact_paths, issue_class, raw_metric_snapshot, normalized_metric_snapshot, decided_at_utc, mode="shadow" |
| test_shadow_mode_never_returns_auto_apply | never self-approves | any eligible input | verdict.mode == "shadow"; no "auto_apply" verdict path exists |
| test_nan_metric_yields_ineligible | malformed (NaN) higher-is-better raw metric fails closed to manual (NOT a raised exception) | raw approve_rate=NaN | INELIGIBLE("missing/non-finite/out-of-domain — fail-closed"); does NOT raise |
| test_out_of_range_metric_yields_ineligible | out-of-raw-domain (>1 or <0) higher-is-better raw metric fails closed | raw approve_rate = 1.4 / -0.1 | INELIGIBLE("missing/non-finite/out-of-domain — fail-closed"); does NOT raise |
| test_missing_lower_is_better_metric_yields_ineligible | a MISSING (absent-key/None) lower-is-better raw metric fails closed BEFORE `1.0 - raw` runs — no TypeError | raw_metrics omits `post_merge_revert_rate` (so `raw is None`) | INELIGIBLE("'post_merge_revert_rate' missing/non-finite/out-of-domain — fail-closed"); does NOT raise (proves validation precedes the `1.0 - raw` arithmetic) |
| test_nonfinite_lower_is_better_metric_yields_ineligible | a NaN/Inf/non-numeric lower-is-better raw metric fails closed BEFORE `1.0 - raw` runs | raw `post_merge_revert_rate`=NaN (and a variant = "x") | INELIGIBLE("'post_merge_revert_rate' missing/non-finite/out-of-domain — fail-closed"); does NOT raise / no TypeError |
| test_missing_count_lower_better_metric_yields_ineligible | a MISSING count-lower-better raw metric fails closed BEFORE `(raw - best)/span` runs | raw_metrics omits `plan_revision_rounds` | INELIGIBLE("'plan_revision_rounds' missing/non-finite/out-of-domain — fail-closed"); does NOT raise (no TypeError on subtraction) |
| test_normalize_metrics_returns_bad_name_not_raise | `normalize_metrics` signals via return value, never raises | metric_specs with one missing/non-finite raw metric | returns `(None, "<bad-metric-name>")`; raises nothing |

> **Inverted test note (D5, honest scope change):** the prior draft's `test_negative_or_nan_metric_rejected` asserted the evaluator *raises ValueError* on a malformed metric. That is now **explicitly inverted** to `test_nan_metric_yields_ineligible` / `test_out_of_range_metric_yields_ineligible`, which assert the evaluator returns **INELIGIBLE** (fail-closed to manual) and does **not** raise — per owner decision D5 ("NaN → INELIGIBLE"). The raise-based behavior is the wrong fail direction for a shadow-mode advisory gate.
>
> **Round-2 fail-direction completeness note:** the NaN/out-of-range tests above exercised only a **higher-is-better** metric, where the malformed value never hit an arithmetic op. They did **not** prove the lower-is-better path: `normalize_metrics` ran `1.0 - raw` and `(raw - best)/span` on the *raw* value, so a missing/None/non-numeric lower-is-better metric raised a `TypeError` **before** any fail-closed guard — re-introducing the raise-on-malformed direction R1-3 eliminated. `test_missing_lower_is_better_metric_yields_ineligible`, `test_nonfinite_lower_is_better_metric_yields_ineligible`, and `test_missing_count_lower_better_metric_yields_ineligible` now assert the **lower-is-better and count-lower-better** paths also fail closed to INELIGIBLE with **no TypeError**, because validation moved INSIDE `normalize_metrics` ahead of all arithmetic (`test_normalize_metrics_returns_bad_name_not_raise` pins the return-not-raise contract). Fail-closed posture now holds symmetrically for every metric direction.

---

## Acceptance Criteria

- [ ] Policy doc exists with: (a) the 5 named rigor metrics + each metric's **normalization direction** + numeric thresholds + rolling-window size + minimum sample; (b) an explicit **eligible** class list and an explicit **ineligible/load-bearing** class list, with a fail-closed default for unknown classes; (c) the **deterministic classifier** spec (changed files + labels → class, ordered so load-bearing signals win, never caller-supplied); (d) an evidence-ledger format making each (shadow) decision reconstructable; (e) a documented kill-switch returning the pilot class to fully manual; (f) the graduation phases (shadow → owner-authorized auto-apply) that name **amending the SOUL never-self-approve must-fire rule as a HARD PRECONDITION** of the auto-apply phase, with the rule preserved unchanged through the shadow phase.
- [ ] `scripts/governance/evidence_threshold_eligibility.py` is pure/unit-testable, **derives** `issue_class` via `classify()` (no caller-supplied class parameter — verified by `test_issue_class_is_not_a_parameter`), **validates every raw metric is a finite number in its declared raw domain INSIDE `normalize_metrics` BEFORE any normalization arithmetic** (`1.0 - raw`, `(raw - best)/span`) so a missing/None/non-finite/out-of-domain metric of **any direction** (higher-is-better AND lower-is-better AND count-lower-better) **fails closed to INELIGIBLE and never raises a `TypeError`** — verified by `test_missing_lower_is_better_metric_yields_ineligible`, `test_nonfinite_lower_is_better_metric_yields_ineligible`, `test_missing_count_lower_better_metric_yields_ineligible`, and `test_normalize_metrics_returns_bad_name_not_raise`, **normalizes all valid metrics to higher-is-better in [0,1] before the threshold loop**, and **never** returns an auto-apply verdict (shadow-only — verified by `test_shadow_mode_never_returns_auto_apply`).
- [ ] All new tests pass: `uv run pytest tests/governance/test_evidence_threshold_eligibility.py -v`
- [ ] No regression: targeted run of `tests/governance/` passes; no change to `tests/` for the plan-approval hook.
- [ ] Load-bearing gates (CI/workflow, schema/contract, security/legal, outward-facing, engineering-calc, harness/enforcement, gate-self-modification) are enumerated and confirmed to stay manual, and the classifier maps their changed-file/label signatures to those classes.
- [ ] Pilot is scoped to ONE eligible class (proposed: `docs-typo-index`) with an audit trail and a documented rollback (kill-switch + label removal).
- [ ] Review artifacts posted to `scripts/review/results/2026-06-28-plan-3296-*.md`.
- [ ] **Owner approval** of the policy doc (the policy itself requires owner sign-off; the agent never self-approves).

---

## Adversarial Review Summary

<!-- Round-1 = inline Claude + owner cross-cutting decisions (D5/D6). Round-2 = dispatched re-review (MAJOR, now addressed). Round-3 = this re-review (PENDING). Keep future-tense; do not post to GitHub until Round-3 populated. -->

| Round | Reviewer(s) | Verdict | Finding count |
|---|---|---|---|
| Round 1 | Claude (inline) + owner cross-cutting decisions D5/D6 | **MAJOR** | 4 MAJOR, 2 MINOR |
| Round 2 | Claude + one of Codex/Gemini (T2) | **MAJOR (now addressed)** | 1 MAJOR |
| Round 3 | Claude + one of Codex/Gemini (T2) — this re-review | **PENDING** | — |

**Round-1 findings (all resolved in this revision):**

| # | Severity | Finding | Resolution in this revision |
|---|---|---|---|
| R1-1 | MAJOR | `evaluate_eligibility` took `issue_class` as a **caller-supplied parameter** — a gaming vector (the agent could declare a load-bearing change "docs-typo-index"). Contradicts the `completeness_score.classify()` non-selectable-class precedent (D5). | Added a deterministic `classify(changed_files, labels)` (mirrors `completeness_score.py:83`), load-bearing-signal-first ordering; removed the `issue_class` param. New tests `test_classify_*`, `test_issue_class_is_not_a_parameter`, `test_classify_mixed_change_picks_load_bearing`. |
| R1-2 | MAJOR | The threshold loop compared every metric `value < threshold` assuming higher-is-better, but `post_merge_revert_rate` and `plan_revision_rounds` are **lower-is-better** — those metrics would be evaluated backwards (D5). | Added `normalize_metrics(...)` that converts every metric to higher-is-better [0,1] **before** the loop; tagged each metric's direction in the policy + pseudocode. New tests `test_lower_is_better_metric_normalized_before_loop`, `test_lower_is_better_metric_unnormalized_would_fail`. |
| R1-3 | MAJOR | Malformed/NaN metric handling **raised `ValueError`** — wrong fail direction for a shadow advisory gate; a swallowed exception could mis-default toward graduation (D5). | Validation now runs **before** comparison and **fails closed to INELIGIBLE (does not raise)**. Inverted the named test `test_negative_or_nan_metric_rejected` → `test_nan_metric_yields_ineligible` + `test_out_of_range_metric_yields_ineligible`. Documented the deliberate divergence from `completeness_score.py` (which raises). |
| R1-4 | MAJOR | The graduation-to-auto-apply phase did not name **amending the SOUL never-self-approve must-fire rule** as a precondition — leaving a path to auto-apply without first relaxing the binding rule (D5). | Policy doc AC (e)/(f) now requires the graduation section to name amending the SOUL never-self-approve must-fire rule as a **hard precondition** of auto-apply; shadow phase preserves it unchanged. |
| R1-5 | MINOR | Evidence-ledger schema risked conflation with the #3282/#3295 envelope/registry schema and the #3283 determinism fields. | Scope note added: the #3296 ledger is **governance-internal audit** only; it does NOT define envelope-determinism fields (`input_hash`/`result_hash`/`provenance.code_version`) owned by #3282/#3283, which are deferred (D6). |
| R1-6 | MINOR | Pilot inertness (sample may never reach `min_sample`) under-surfaced for the owner. | Reinforced in Risks: low eligible-class volume → pilot rarely fires = fail-safe-to-manual, stated so the owner is not surprised. |

**Round-2 findings (addressed in this revision):**

| # | Severity | Finding | Resolution in this revision |
|---|---|---|---|
| R2-1 | MAJOR | The fail-closed guard sat **inside the threshold loop**, but `normalize_metrics` ran FIRST and did raw arithmetic (`1.0 - raw`, `(raw - best)/span`) on an **unvalidated** value. A missing/None/non-numeric **lower-is-better** (or count-lower-better) metric therefore raised a `TypeError` BEFORE the None/`isfinite` guard ever ran — so malformed input still RAISED, the exact direction R1-3 was meant to eliminate. The R1-3 tests only covered NaN on a **higher-is-better** metric (which never hits arithmetic), masking the gap. | Moved validation **EARLIER**: `normalize_metrics` now validates each raw metric is a finite number in its **declared raw domain `[raw_lo, raw_hi]`** BEFORE any arithmetic, and returns `(None, bad_metric_name)` to signal INELIGIBLE (fail-closed) instead of raising. `evaluate_eligibility` maps a non-None `bad_metric_name` to INELIGIBLE. Added per-direction raw-domain declarations to the 5 metric specs. New tests `test_missing_lower_is_better_metric_yields_ineligible`, `test_nonfinite_lower_is_better_metric_yields_ineligible`, `test_missing_count_lower_better_metric_yields_ineligible`, `test_normalize_metrics_returns_bad_name_not_raise`. Updated Resource-Intel divergence note (validation-before-arithmetic), Files-to-Change evaluator row, and the evaluator Acceptance Criterion to require fail-closed-no-raise for **all** metric directions. |

**Overall result:** Round-1 MAJOR → revised; Round-2 MAJOR → revised (this revision); Round-3 PENDING.

Revisions made based on review:
- (R2-1) Relocated metric validation from inside the threshold loop into `normalize_metrics`, ahead of all normalization arithmetic; switched it from a potential raise to a `(None, name)` fail-closed signal; added declared raw domains per metric; added 4 new lower-is-better / count-lower-better / return-contract tests; updated the divergence note, Files-to-Change, and Acceptance Criteria.

Revisions made based on Round-1 review:
- Removed caller-supplied `issue_class`; added deterministic `classify()` + classifier AC + 5 new classifier/derivation tests (R1-1).
- Added metric normalization step before the threshold loop with per-metric direction tags (R1-2).
- Switched malformed-metric handling from raise → fail-closed INELIGIBLE; inverted the affected test (R1-3).
- Added SOUL-amendment-as-hard-precondition to the policy-doc graduation AC (R1-4).
- Added ledger-scope boundary vs #3282/#3283/#3295 and pilot-inertness disclosure (R1-5, R1-6).

---

## Risks and Open Questions

- **Risk (load-bearing):** This issue evolves the exact gate named by the must-fire rule *"Never self-label `status:plan-approved`."* Mitigation: the pilot is **shadow mode only** — the evaluator recommends and records, the human still applies the label. True auto-apply is a separate, future, owner-authorized phase whose **hard precondition is amending that must-fire rule** (D5); it is not in this plan's scope. The plan must not modify `plan-approval-gate.sh` or the SOUL must-fire rule.
- **Risk (metric gaming):** thresholds computed from agent-produced artifacts (review verdicts, completeness scores) can be inflated by the same agents. Mitigation: (a) class is **derived, never caller-supplied** (R1-1), closing the "declare a load-bearing change eligible" vector; (b) follow `completeness_score.py`'s fail-closed posture — malformed inputs → INELIGIBLE; (c) at least one externally-grounded metric (`post_merge_revert_rate`, which depends on real reopens/reverts the agent cannot fake).
- **Risk (fail-direction inversion, R2-1):** a fail-closed guard placed AFTER normalization arithmetic is bypassable — a missing/None/non-numeric lower-is-better metric raises a `TypeError` in `1.0 - raw` / `(raw - best)/span` before the guard runs, and a caller (e.g., a shadow-mode advisory wrapper) that swallows the exception could mis-default toward graduation. Mitigation: validation lives **inside `normalize_metrics`, before any arithmetic**, validates the **declared raw domain** for every metric direction, and returns a `(None, name)` fail-closed signal rather than raising; the post-normalization guard remains only as defense-in-depth. Regression-pinned by the lower-is-better / count-lower-better / return-contract tests so this ordering cannot silently regress.
- **Risk (small sample):** the eligible-class issue volume may be too low to reach `min_sample` for a long time, making the pilot inert. This is acceptable (fail-safe-to-manual) but is surfaced so the owner isn't surprised the pilot rarely fires.
- **Scope boundary (settled, D6):** the #3296 evidence ledger is **governance-internal audit** and does NOT define the envelope-determinism fields (`input_hash`, `result_hash`, `provenance.code_version`) owned by #3282/#3283, nor the deckhand routing / `result:` registry descriptor owned by #3282/#3295. #3283 is deferred to Wave 2 and is not a dependency here.
- **Open:** Exact numeric thresholds (e.g., approve_rate ≥ 0.90? normalized revert ≥ 0.95? min_sample = 20?) and trailing-window length (count-based vs days-based) — the policy doc proposes defaults; owner decides these at approval. (This is a genuine owner-input item, not resolved by D1–D6.)
- **Open:** Should the first pilot class be `docs-typo-index` or `test-only-additive`? **Recommend `docs-typo-index`** (lowest blast radius; already a safe-path in the hook). Owner confirms at approval.
- **Open:** Where should the rolling-metric aggregator live and run (cron? on-demand)? The pilot ships only the pure evaluator + classifier; the aggregator/CLI wrapper is deferred to a follow-on so the pilot stays small and reversible.

---

## Complexity: T2

**T2** — a governance policy doc plus a small, fail-closed advisory module (evaluator + deterministic classifier + metric normalization) with TDD across ~5 new files; no heavy compute, no engineering calc, but more than a single-file trivial change. Governance T2 → 2-provider adversarial review (Claude + one of Codex/Gemini), per the gate-depth scale in `SOUL.runtime.md`.
