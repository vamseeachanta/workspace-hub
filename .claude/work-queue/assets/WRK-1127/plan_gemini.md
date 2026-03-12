# Gemini Cross-Review — WRK-1127 Feature-First Planning

**Reviewer:** Gemini
**Date:** 2026-03-11
**Stage:** 6 — Cross-Review
**Artifact reviewed:** `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md`

---

## Review Scope

Architecture fit with the existing work-queue system, INDEX.md "By Feature" section
design, `feature-close-check.sh` gate correctness, and `whats-next.sh` category
filter gap.

---

## 1. Architecture Fit with the Existing Work-Queue System

### 1.1 Layering model

The existing work-queue system is flat: every WRK item is a peer, differentiated
only by `status`, `priority`, and `category`. The Feature WRK layer adds a
hierarchical parent-child relationship on top of this flat model.

The plan's approach is **additive, not invasive**: it introduces new frontmatter
fields (`type`, `children`, `parent`, `blocked_by`) and a new status value
(`coordinating`) without modifying the core stage lifecycle scripts or changing
existing WRK item behaviour. This is the correct architectural choice for a
backward-compatible extension.

**Alignment with existing patterns:**

| Existing pattern | Feature layer follows it? |
|-----------------|--------------------------|
| Frontmatter YAML fields | Yes — additive fields only |
| `status:` vocabulary extended via plan change | Yes — `coordinating` added |
| Scripts read frontmatter via `grep`/`sed` | Yes — `feature-status.sh`, `feature-close-check.sh` use the same pattern |
| Stage YAML files as metadata descriptors | Yes — `stage-09-routing.yaml` extended, not replaced |
| `generate-index.py` as the index source of truth | Yes — By Feature section added there |

### 1.2 New status value: `coordinating`

Adding `coordinating` to the status vocabulary is the most significant semantic
change. The plan correctly identifies that `generate-index.py` must include
`coordinating` in its active-status filters (two occurrences, lines 600 and 665)
to prevent coordinating Feature WRKs from disappearing from the index.

**Issue (MINOR-1): `coordinating` status handling in `close-item.sh` and
`archive` scripts is not addressed.**
When a Feature WRK's children are all archived and `feature-close-check.sh`
returns 0, what script transitions the Feature WRK from `coordinating` to
`archived`? The plan documents that Stage 19/20 run on the Feature WRK itself as
normal, but `close-item.sh` may have a status guard that only allows transitioning
from `working` or `blocked`, not from `coordinating`. Child-c should verify this
before Stage 7 sign-off.

### 1.3 Machine-partitioned IDs and child WRK creation

`new-feature.sh` calls `next-id.sh` to allocate child WRK IDs. `next-id.sh` reads
`config/work-queue/machine-ranges.yaml` and allocates within the machine's range.
This means child WRKs are always allocated on the machine where `new-feature.sh`
runs (typically the machine where Stage 7 completes). This is consistent with the
existing allocation policy and requires no change.

### 1.4 `work-queue-workflow/SKILL.md` vs. `stage-07-user-review-plan-final.yaml`

Task 12 updates the SKILL.md to document the Stage 7 exit action (run
`new-feature.sh`). The corresponding stage YAML file
(`stage-07-user-review-plan-final.yaml`) is not updated. SKILL.md is
documentation; stage YAML files are operational contracts used by agents to
understand what is required at each stage. For a robust architecture, the
`exit_artifacts` list in `stage-07-user-review-plan-final.yaml` should include
`feature-decomposition.yaml` for Feature WRK items.

**Issue (MINOR-2): Stage 7 YAML `exit_artifacts` not updated for Feature WRKs.**
This is a documentation gap, not a functional failure. Acceptable as MINOR.

---

## 2. INDEX.md "By Feature" Section Design

### 2.1 Proposed format

The plan specifies:

```
| WRK-NNN | title | coordinating | 1/3 (33%) |
```

This format is clean and answers the primary question ("how far along is this
feature?"). The implementation calls `generate-index.py` which already has access
to the `children:` list and can compute completion % by checking each child's
`status` field.

### 2.2 Completion % computation in generate-index.py

The plan does not specify how `generate-index.py` computes completion % for the
By Feature section. There are two approaches:

**Option A:** Import/inline the logic from `feature-status.sh` (re-derive in
Python by reading child WRK files).

**Option B:** Call `feature-status.sh` as a subprocess from Python.

Option A is preferred (follows the "scripts over LLM judgment" and
"deterministic" patterns from `patterns.md`). The Python implementation should
iterate the `children:` list, look up each child's `status` in the WRK files
already loaded in memory by `generate-index.py`, and compute done/total.

**Issue (MINOR-3): The By Feature completion % computation method is not specified
in the plan.** Child-b should use Option A (in-memory Python count) rather than
subprocess-calling `feature-status.sh`, to avoid N subprocesses launched during
index generation.

### 2.3 Orphaned children (children whose parent is archived)

If a Feature WRK is archived, it moves from `pending/working/blocked` to
`archive/`. The `generate-index.py` By Feature section should either:
(a) Skip archived Feature WRKs (consistent with By Category which only shows
active items), or
(b) Show all Feature WRKs including archived ones for historical tracking.

The plan does not specify which. Option (a) is consistent with the existing index
design and should be made explicit.

**Issue (MINOR-4): By Feature section visibility scope (active-only vs. all-time)
not specified.** Recommend active-only (status in `pending`, `working`, `blocked`,
`coordinating`) for consistency.

### 2.4 INDEX.md section ordering

The plan places "By Feature" after "By Category". Given that By Category is the
primary navigation aid, placing By Feature after it is correct — users find the
overall queue first, then drill into feature groupings.

---

## 3. feature-close-check.sh Gate Correctness

### 3.1 Gate logic analysis

```bash
STATUS=$(find .claude/work-queue -name "${CHILD}.md" 2>/dev/null \
  -exec grep '^status:' {} \; | head -1 | awk '{print $2}')
if [[ "$STATUS" != "archived" ]]; then
  echo "BLOCK: ${CHILD} is ${STATUS:-unknown} (not archived)"
  FAIL=1
fi
```

This logic is correct for the primary case. Key properties:

- Searches all work-queue subdirectories (pending, working, blocked, archive) for
  the child WRK file.
- Uses `head -1` to take the first `status:` line found (frontmatter position).
- Blocks if status is anything other than `archived`, including `unknown` (missing
  file case).

**Issue (MINOR-5): A child WRK that has been `status: done` but not yet moved to
`archive/` will cause the feature close check to BLOCK.**
The plan's feature lifecycle states that Feature WRK closes when all children
reach `status: archived`. The current script does not accept `done` as a passing
state. This is intentional and correct — children must complete the full Stage 20
archive step before the parent can close. However, this means the Feature WRK
cannot close until ALL children complete Stage 20, not just Stage 19. The plan
should make this explicit ("children must reach `archived`, not just `done`").

**Issue (MINOR-6): No handling for a child WRK file that no longer exists (fully
purged).** If a child's `.md` file is deleted (not archived, just deleted), `find`
returns nothing, `STATUS` is empty, and the check blocks with "BLOCK: WRK-X is
unknown". This is safe-fail behaviour — blocking is correct when a child's state
cannot be verified. No change needed; just noting the behaviour.

### 3.2 Integration with Stage 19 lifecycle

As noted in the Claude review (MINOR-2 there), `feature-close-check.sh` is
documented in SKILL.md but not wired into `stage-19-close.yaml`'s
`blocking_condition`. The SKILL.md approach is documentation-only. For the gate to
be enforced by agents following the stage contract, it needs to be in the YAML.

**Issue (MAJOR-1):** Without `feature-close-check.sh` in `stage-19-close.yaml`'s
`blocking_condition`, an agent following the stage lifecycle could close a Feature
WRK while children are still executing. This is a process integrity gap that SKILL.md
documentation alone cannot reliably prevent. This should be resolved before Stage 7.

Proposed fix: Add to `stage-19-close.yaml`:

```yaml
blocking_condition: >
  For type:feature items: feature-close-check.sh WRK-NNN must exit 0.
  For regular items: status not 'working' or 'done'.
```

Or add a pre-condition note as a separate `feature_blocking_condition:` key
(parallel to the proposed `feature_routing:` key in stage-09-routing.yaml).

---

## 4. whats-next.sh Category Filter Gap

### 4.1 Current filter behaviour

`whats-next.sh` defaults to `FILTER_CATEGORY="harness"`. The filter is applied
per-item at line 106:

```bash
[[ -n "$FILTER_CATEGORY" && "$category" != *"$FILTER_CATEGORY"* ]] && return
```

Items where `category != harness` are silently skipped. The proposed "Features in
progress" section calls `feature-status.sh` for items with `status: coordinating`.

### 4.2 Gap analysis

The plan's triage YAML (`triage.yaml`) records this risk as:

> "whats-next.sh category filter hiding non-harness features — acceptable;
> WRK-1127 is harness"

This acceptance is correct for WRK-1127 but creates a systemic gap: any Feature
WRK in a category other than `harness` (e.g. `engineering`, `data`, `platform`)
will not appear in the default `whats-next.sh` output, even though `coordinating`
status indicates active work.

**Issue (MINOR-7):** The "Features in progress" section should either:

(a) Bypass the category filter for coordinating Feature WRKs specifically (since
Feature WRKs are always high-visibility orchestration items regardless of category),
or

(b) Be documented as category-filtered with a note in the output: "Run
`whats-next.sh --all` to see features in all categories."

The plan currently does neither. The implementation task (Task 13) should explicitly
choose one option.

### 4.3 Proposed resolution

Option (a) is architecturally cleaner and aligns with the intent: Feature WRKs are
epic-level work that should always be visible. Implementing this requires a small
change in the item scanning loop:

```bash
# In the per-item processing function:
local type; type=$(get_field "$f" "type")
# Bypass category filter for coordinating feature WRKs
if [[ "$type" == "feature" && "$status" == "coordinating" ]]; then
  : # always include
elif [[ -n "$FILTER_CATEGORY" && "$category" != *"$FILTER_CATEGORY"* ]]; then
  return
fi
```

This adds ~4 lines to the existing filter logic and is fully backward-compatible.

---

## 5. Summary of Findings

| ID | Severity | Finding |
|----|----------|---------|
| MINOR-1 | MINOR | `coordinating` → `archived` transition in close-item.sh not verified |
| MINOR-2 | MINOR | Stage 7 YAML exit_artifacts not updated for Feature WRK items |
| MINOR-3 | MINOR | By Feature completion % computation method unspecified |
| MINOR-4 | MINOR | By Feature section scope (active-only vs. all-time) unspecified |
| MINOR-5 | MINOR | Plan does not explicitly state children must reach `archived` (not `done`) |
| MINOR-6 | MINOR | Deleted child WRK (not archived) causes safe-fail block — document behaviour |
| MAJOR-1 | MAJOR | feature-close-check.sh not wired into stage-19-close.yaml blocking_condition |
| MINOR-7 | MINOR | whats-next.sh "Features in progress" section subject to category filter gap |

**One MAJOR finding** (MAJOR-1): The feature close gate relies on SKILL.md
documentation rather than a machine-enforced stage contract. This creates a
process integrity risk that should be resolved before Stage 7 approval.

---

## Verdict: MINOR

The architecture is sound and the overall design fits the existing work-queue system
well. MAJOR-1 is the single critical gap: the feature close gate must be enforced
in `stage-19-close.yaml`, not only in SKILL.md documentation. This can be resolved
with a one-line addition to `stage-19-close.yaml` in child-c scope, and does not
require a full re-design. Recommend proceeding to Stage 7 with MAJOR-1 resolved
(or explicitly scoped to child-c as a mandatory AC).
