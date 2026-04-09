# Terminal 6 — Session Governance Phase 3: Restore Lost Session Infrastructure

## Issue Metadata

| Field | Value |
|-------|-------|
| Issue | #2057 |
| Title | Session governance Phase 3: restore lost session infrastructure |
| Labels | `enhancement`, `priority:medium`, `cat:ai-orchestration`, `agent:claude` |
| State | OPEN |
| Parent | #1839 |
| Date | 2026-04-09 |
| Phase | Planning dossier — no production code written |

---

## 1. Current-State Findings

### Overview

Issue #2057 lists four deliverables. Deep repo inspection reveals **two are already implemented**, one is partially done, and one is genuinely missing. The issue body is partially stale.

### Deliverable Status Matrix

| # | Deliverable | Issue Claims | Actual Status | Remaining Work |
|---|-------------|-------------|---------------|----------------|
| 1 | session-start-routine skill | "Lost during GSD migration" | **MISSING** — no skill file exists | Full creation needed |
| 2 | session-corpus-audit skill | "Never built" | **DONE** — 363-line skill (v1.0.0) | Smoke test only |
| 3 | comprehensive-learning → skills tree | "Invisible to discovery" | **DONE** — skill exists + `/learn-extended` registered | Smoke test + verify routing |
| 4 | cross-review-policy skill | "Policy exists but not actionable skill" | **PARTIAL** — related skill exists (`multi-provider-adversarial-review`) | Thin wrapper skill or alias |

### Files/Modules Already Present

#### Session Governance Core (Phase 1 + 2)
- `docs/governance/SESSION-GOVERNANCE.md` — 105 lines, Phase 1-4 roadmap with Phase 3 section at line 87
- `scripts/workflow/governance-checkpoints.yaml` — 7 checkpoints (3 hard-stops, 4 auto-gates)
- `scripts/workflow/session_governor.py` — 300+ lines, full verification utility with `--check-limits`
- `docs/governance/TRUST-ARCHITECTURE.md` — 300 lines, canonical governance reference (WRK-381)

#### Session-Corpus-Audit (Deliverable #2 — COMPLETE)
- `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md` — **363 lines, v1.0.0** (author: Hermes Agent)
  - 7 analysis phases (A–G): file frequency, command patterns, tool distribution, temporal patterns, skill gap detection, dead skill audit, correction hotspot analysis
  - Data sources: `logs/orchestrator/claude/session_*.jsonl`, `logs/orchestrator/hermes/session_*.jsonl`, `logs/orchestrator/codex/`
  - Outputs: `phase-a-baseline.md`, `phase-b-skill-gaps.md`, CSV/JSON intermediates
  - 14 documented pitfalls
  - **Verdict**: Production-ready. Issue says "never built" — this is stale.

#### Comprehensive-Learning (Deliverable #3 — COMPLETE)
- `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` — **159 lines, v2.5.0** (updated 2026-03-09, WRK-299)
  - `references/pipeline-detail.md` — 909 lines of phase-by-phase implementation detail
  - 10-phase pipeline: insights → reflect → knowledge → improve → corrections → WRK feedback → action candidates → report review → skill coverage → cross-machine compile
  - Cross-machine routing (dev-primary aggregates, secondaries commit local state)
  - Iron Law: "No learning pipeline phase shall run standalone during an active work session"
- `scripts/cron/comprehensive-learning-nightly.sh` — 163 lines, nightly 22:00 UTC cron script
- `/learn-extended` is listed as a registered skill in the skills ecosystem
- **Verdict**: Skill exists, cron runs it, and `/learn-extended` appears registered. Issue's claim of "invisible to skill discovery" appears resolved.

#### Cross-Review-Policy Infrastructure (Deliverable #4 — PARTIAL)
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 60 lines, three-agent adversarial review policy (#1515, effective 2026-03-31)
- `.claude/hooks/cross-review-gate.sh` — 81 lines, PreToolUse hook that gates PR creation
- `scripts/ai/review_routing_gate.py` — 345 lines, routing recommendation engine
- `.claude/skills/software-development/multi-provider-adversarial-review/SKILL.md` — 15,437 bytes (v1.1.0), covers HOW to dispatch reviews
- **Gap**: No dedicated `cross-review-policy` skill that wraps the ROUTING DECISION (which agent reviews which agent's work). The `multi-provider-adversarial-review` skill covers execution mechanics but not the policy routing matrix itself.

#### Session Hooks & Signals Infrastructure
- `.claude/hooks/emit-session-quality-signals.sh` — Stop event, emits `session_tool_summary` to JSONL
- `.claude/hooks/session-logger.sh` — pre/post hook pairs for tool invocation capture
- `.claude/hooks/session-review.sh` — Stop event, raw signal capture for 3AM analysis
- `.claude/hooks/gsd-session-state.sh` — GSD workflow state tracking
- `.claude/state/session-signals/` — 397 JSONL files (daily from 2026-02-20 through 2026-04-09)

#### Session-Start-Routine References (Deliverable #1 — MISSING)
- **Broken links in 4 skill files** reference `../session-start-routine/SKILL.md`:
  - `.claude/skills/_internal/meta/repo-cleanup/SKILL.md:51`
  - `.claude/skills/_internal/meta/module-based-refactor/SKILL.md:141`
  - `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md:42`
  - `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md:177`
- `.claude/skills/_internal/meta/session-start-routine/` — **directory does not exist**
- SessionStart hooks exist in `settings.json` (lines 162-191) but they are thin shell scripts, not a comprehensive skill
- Related prior work: commit `ad2e442f8` — `feat(WRK-691): session drift detection + session-start Step 0 auto-load`

### Tests Already Present

- `tests/work-queue/test_session_governor.py` — 297 lines, 25 tests (14 Phase 1 + 11 Phase 2), covers checkpoint config loading, gate verification, and runtime limit checking
- `tests/work-queue/test_stage_lifecycle.py` — stage lifecycle enforcement tests
- `tests/unit/test_session_signal_coverage_audit.py` — agent cross-review detection, session signal coverage
- `tests/unit/test_build_session_gate_analysis.py` — gate analysis tests
- `tests/unit/test_verify_gate_evidence.py` — gate evidence verification
- `tests/cron/test_skills_curation.py` — skill curation dry-run validation
- **No smoke tests** for skill file loading/structure validation exist for the Phase 3 deliverables

### Latest Relevant Commits

| Hash | Date | Message |
|------|------|---------|
| `e69473081` | 2026-04-09 | `feat(governance): session hard-stop checkpoint model and verifier (#1839)` |
| `ad2e442f8` | earlier | `feat(WRK-691): session drift detection + session-start Step 0 auto-load` |
| `13600c9b0` | earlier | `chore(WRK-1102): archive — comprehensive-learning modular chain repair complete` |
| `2f1e3914d` | earlier | `fix(WRK-1102): Fix 1/2/3/4/6/7 — comprehensive-learning modular chain repairs` |
| `a9da698e0` | earlier | `feat(learning): integrate Hermes into ecosystem learning pipeline (#1719)` |

---

## 2. Remaining Implementation Delta

### Deliverable #1: session-start-routine (FULL BUILD NEEDED)

**What's missing**: A complete skill file at `.claude/skills/workspace-hub/session-start-routine/SKILL.md` (or `.claude/skills/_internal/meta/session-start-routine/SKILL.md` to match existing broken links).

**Required behaviors**:
1. Pre-flight context loading — read CLAUDE.md, MEMORY.md, recent session signals
2. Check prior session state — look at `.claude/state/session-signals/` for the last session's quality signals
3. Validate environment — verify Python/uv, git status, network mounts
4. Check for in-flight work — scan for parallel sessions (other terminals with active Claude Code)
5. Load GSD state — check `.planning/` for active phases, pending work
6. Surface relevant memory — consult `.claude/memory/` for feedback and project context

**File paths that should change**:
- CREATE: `.claude/skills/workspace-hub/session-start-routine/SKILL.md`
- FIX: `.claude/skills/_internal/meta/repo-cleanup/SKILL.md` (broken link at line 51)
- FIX: `.claude/skills/_internal/meta/module-based-refactor/SKILL.md` (broken link at line 141)
- FIX: `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md` (broken link at line 42)
- FIX: `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md` (broken link at line 177)
- CREATE: `tests/skills/test_session_start_routine_smoke.py` (smoke test)

### Deliverable #2: session-corpus-audit (SMOKE TEST ONLY)

**What's missing**: The skill specification exists and is production-ready. Only a smoke test verifying structure is needed.

**File paths that should change**:
- CREATE: `tests/skills/test_session_corpus_audit_smoke.py`

### Deliverable #3: comprehensive-learning registration (VERIFY + SMOKE TEST)

**What's missing**: The skill exists and `/learn-extended` appears registered. Need to verify the routing chain works end-to-end, then add a smoke test.

**File paths that should change**:
- CREATE: `tests/skills/test_comprehensive_learning_smoke.py`
- POTENTIALLY UPDATE: Skill discovery configuration (if `/learn-extended` doesn't properly route to comprehensive-learning)

### Deliverable #4: cross-review-policy skill (THIN WRAPPER NEEDED)

**What's missing**: A dedicated skill that presents the routing matrix as an actionable checklist. The `multi-provider-adversarial-review` skill covers mechanics but not routing policy decisions.

**Required behaviors**:
1. Present the provider roles table (Claude=orchestrator, Codex=worker+reviewer, Gemini=reviewer)
2. Surface routing decision criteria (two-provider vs three-provider)
3. Reference the enforcement chain (policy doc → routing gate script → hook)
4. Provide actionable steps: "before creating a PR, run this check"

**File paths that should change**:
- CREATE: `.claude/skills/workspace-hub/cross-review-policy/SKILL.md`
- CREATE: `tests/skills/test_cross_review_policy_smoke.py`

---

## 3. TDD-First Execution Plan

### Phase A: Write Failing Tests (RED)

**Step A1**: Create skill smoke test framework (if not already established)

```python
# tests/skills/test_skill_smoke.py — shared utility
import yaml, pathlib

def load_skill(skill_path: str) -> dict:
    """Load a skill file and return parsed frontmatter + content."""
    path = pathlib.Path(skill_path)
    assert path.exists(), f"Skill file missing: {skill_path}"
    text = path.read_text()
    assert text.startswith("---"), "Skill must have YAML frontmatter"
    parts = text.split("---", 2)
    meta = yaml.safe_load(parts[1])
    body = parts[2] if len(parts) > 2 else ""
    return {"meta": meta, "body": body, "path": path}

REQUIRED_FRONTMATTER = {"name", "description", "version"}
```

**Step A2**: Create `tests/skills/test_session_start_routine_smoke.py`

```python
# Tests that WILL FAIL until deliverable #1 is built
def test_skill_file_exists():
    assert Path(".claude/skills/workspace-hub/session-start-routine/SKILL.md").exists()

def test_frontmatter_has_required_fields():
    skill = load_skill(".claude/skills/workspace-hub/session-start-routine/SKILL.md")
    for field in REQUIRED_FRONTMATTER:
        assert field in skill["meta"]

def test_body_has_checklist_sections():
    skill = load_skill(".claude/skills/workspace-hub/session-start-routine/SKILL.md")
    for section in ["Pre-flight", "Context", "Environment", "In-flight"]:
        assert section.lower() in skill["body"].lower()
```

**Step A3**: Create `tests/skills/test_session_corpus_audit_smoke.py`

```python
# Should PASS immediately — skill already exists
def test_skill_file_exists():
    assert Path(".claude/skills/workspace-hub/session-corpus-audit/SKILL.md").exists()

def test_frontmatter_has_required_fields():
    skill = load_skill(".claude/skills/workspace-hub/session-corpus-audit/SKILL.md")
    for field in REQUIRED_FRONTMATTER:
        assert field in skill["meta"]

def test_body_has_analysis_phases():
    skill = load_skill(".claude/skills/workspace-hub/session-corpus-audit/SKILL.md")
    assert "Phase A" in skill["body"]
```

**Step A4**: Create `tests/skills/test_comprehensive_learning_smoke.py`

```python
# Should PASS immediately — skill already exists
def test_skill_file_exists():
    assert Path(".claude/skills/workspace-hub/comprehensive-learning/SKILL.md").exists()

def test_cron_script_exists():
    assert Path("scripts/cron/comprehensive-learning-nightly.sh").exists()

def test_frontmatter_has_required_fields():
    skill = load_skill(".claude/skills/workspace-hub/comprehensive-learning/SKILL.md")
    for field in REQUIRED_FRONTMATTER:
        assert field in skill["meta"]
```

**Step A5**: Create `tests/skills/test_cross_review_policy_smoke.py`

```python
# Tests that WILL FAIL until deliverable #4 is built
def test_skill_file_exists():
    assert Path(".claude/skills/workspace-hub/cross-review-policy/SKILL.md").exists()

def test_frontmatter_has_required_fields():
    skill = load_skill(".claude/skills/workspace-hub/cross-review-policy/SKILL.md")
    for field in REQUIRED_FRONTMATTER:
        assert field in skill["meta"]

def test_references_policy_doc():
    skill = load_skill(".claude/skills/workspace-hub/cross-review-policy/SKILL.md")
    assert "AI_REVIEW_ROUTING_POLICY" in skill["body"]
```

### Phase B: Implementation (GREEN)

**Step B1**: Create `session-start-routine` skill

Create `.claude/skills/workspace-hub/session-start-routine/SKILL.md` with:
- YAML frontmatter: name, description, version (1.0.0), category, type, capabilities, tags
- Sections: "When to Use", "Pre-flight Checklist" (6 checks from issue), "Output Format"
- Reference: `docs/governance/SESSION-GOVERNANCE.md`, `.claude/state/session-signals/`
- Match existing skill conventions from `session-corpus-audit` and `comprehensive-learning`
- Update or symlink to fix the 4 broken references in `_internal/meta/` skills

**Step B2**: Create `cross-review-policy` skill

Create `.claude/skills/workspace-hub/cross-review-policy/SKILL.md` with:
- Frontmatter: name, description, version (1.0.0), category
- Content: routing matrix extracted from `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Actionable checklist: which agent reviews what, when three-provider is required
- References: policy doc, `scripts/ai/review_routing_gate.py`, `.claude/hooks/cross-review-gate.sh`
- Cross-link to `multi-provider-adversarial-review` for execution mechanics

**Step B3**: Fix broken links in 4 referencing skill files

Update the `session-start-routine` link paths in:
- `.claude/skills/_internal/meta/repo-cleanup/SKILL.md`
- `.claude/skills/_internal/meta/module-based-refactor/SKILL.md`
- `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md`
- `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md`

### Phase C: Verification (REFACTOR)

Run all smoke tests and verify governance doc reflects Phase 3 completion.

### Verification Commands

```bash
# 1. Run all smoke tests
uv run pytest tests/skills/test_session_start_routine_smoke.py tests/skills/test_session_corpus_audit_smoke.py tests/skills/test_comprehensive_learning_smoke.py tests/skills/test_cross_review_policy_smoke.py -v

# 2. Verify skill files exist and have frontmatter
for skill in session-start-routine session-corpus-audit comprehensive-learning cross-review-policy; do
  echo "--- $skill ---"
  head -15 .claude/skills/workspace-hub/$skill/SKILL.md 2>/dev/null || echo "MISSING: $skill"
done

# 3. Verify no broken links remain
grep -rn "session-start-routine" .claude/skills/ | grep -v "workspace-hub/session-start-routine"

# 4. Verify session governor tests still pass
uv run pytest tests/work-queue/test_session_governor.py -v

# 5. Verify learn-extended routes to comprehensive-learning
grep -r "comprehensive-learning" .claude/skills/workspace-hub/

# 6. Verify cross-review enforcement chain
ls -la .claude/hooks/cross-review-gate.sh scripts/ai/review_routing_gate.py docs/standards/AI_REVIEW_ROUTING_POLICY.md
```

---

## 4. Risk/Blocker Analysis

### Plan-Gate Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| Issue #2057 lacks `status:plan-approved` label | **BLOCKING** — AGENTS.md requires user approval before implementation | Add `status:plan-review` label, then user approves to `status:plan-approved` |
| Issue body is stale (claims items 2+3 are unbuilt) | Low | Update issue body to reflect actual state; convert to delta report |

### Data/Source Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Exists, 60 lines | None — source for cross-review-policy skill |
| `.claude/state/session-signals/` | Active, 397 files | None — source for session-start-routine to check |
| Skill frontmatter convention | Established (see session-corpus-audit, comprehensive-learning) | None — clear pattern to follow |
| `scripts/ai/review_routing_gate.py` | 345 lines, functional | None — cross-review-policy skill references this |
| SessionStart hooks in `settings.json` | Configured (lines 162-191) | session-start-routine skill should complement, not duplicate these hooks |

### Merge/Contention Concerns

| Concern | Likelihood | Mitigation |
|---------|------------|------------|
| Terminal 7 (Phase 2 runtime hooks) touches `scripts/workflow/session_governor.py` | Medium | No conflict — Phase 3 creates NEW skill files, doesn't modify governor |
| Other terminals modifying `.claude/skills/` | Low | Phase 3 creates files in new subdirectories, not modifying existing |
| 4 broken link fixes touch `_internal/meta/` skills | Low | Simple path updates, unlikely to conflict with other work |
| SESSION-GOVERNANCE.md update to mark Phase 3 done | Low | Single-line status update at line 87 |

---

## 5. Ready-to-Execute Implementation Prompt

```
## Implementation Task: GitHub Issue #2057

You are implementing Session Governance Phase 3 for the workspace-hub repository.
Issue: #2057 — "Session governance Phase 3: restore lost session infrastructure"
Parent: #1839

### Context

Phase 1 (checkpoint model) and Phase 2 (runtime enforcement) are already implemented.
Phase 3 restores lost session skills. Two of four deliverables are already complete:

- session-corpus-audit: DONE at .claude/skills/workspace-hub/session-corpus-audit/SKILL.md (v1.0.0)
- comprehensive-learning: DONE at .claude/skills/workspace-hub/comprehensive-learning/SKILL.md (v2.5.0)

### Remaining Work

1. CREATE `.claude/skills/workspace-hub/session-start-routine/SKILL.md`
   - Pre-flight checks at session start
   - Load context (CLAUDE.md, MEMORY.md, session signals)
   - Check prior state (last session quality signals from .claude/state/session-signals/)
   - Validate environment (Python/uv, git, network mounts)
   - Check for in-flight work from other terminals
   - Load GSD state (.planning/ active phases)
   - Follow frontmatter convention from session-corpus-audit skill

2. CREATE `.claude/skills/workspace-hub/cross-review-policy/SKILL.md`
   - Wrap docs/standards/AI_REVIEW_ROUTING_POLICY.md as actionable skill
   - Present routing matrix: Claude=orchestrator, Codex=worker+reviewer, Gemini=reviewer
   - Surface when 2-provider vs 3-provider review applies
   - Reference enforcement chain: policy doc → scripts/ai/review_routing_gate.py → .claude/hooks/cross-review-gate.sh
   - Cross-link to multi-provider-adversarial-review skill for execution mechanics

3. FIX broken session-start-routine links in 4 files:
   - .claude/skills/_internal/meta/repo-cleanup/SKILL.md:51
   - .claude/skills/_internal/meta/module-based-refactor/SKILL.md:141
   - .claude/skills/_internal/meta/hidden-folder-audit/SKILL.md:42
   - .claude/skills/operations/devtools/ai-tool-assessment/SKILL.md:177

4. CREATE smoke tests (TDD-first — write tests BEFORE implementation):
   - tests/skills/test_session_start_routine_smoke.py
   - tests/skills/test_session_corpus_audit_smoke.py
   - tests/skills/test_comprehensive_learning_smoke.py
   - tests/skills/test_cross_review_policy_smoke.py
   Each test verifies: file exists, frontmatter has name/description/version, body has required sections.

5. UPDATE docs/governance/SESSION-GOVERNANCE.md line 87-91 to reflect Phase 3 completion status.

### Acceptance Criteria

- [ ] All 4 skill directories exist under .claude/skills/workspace-hub/
- [ ] All 4 smoke tests pass: `uv run pytest tests/skills/test_*_smoke.py -v`
- [ ] No broken links: `grep -rn "session-start-routine" .claude/skills/ | grep -v workspace-hub/session-start-routine` returns only valid references
- [ ] session-start-routine includes checklist for: context load, prior state, env validation, in-flight check
- [ ] cross-review-policy references AI_REVIEW_ROUTING_POLICY.md and routing gate script
- [ ] SESSION-GOVERNANCE.md Phase 3 section updated
- [ ] Existing tests still pass: `uv run pytest tests/work-queue/test_session_governor.py -v`

### Cross-Review Requirements

Per AI_REVIEW_ROUTING_POLICY.md, this is a medium-priority enhancement:
- Plan review: Claude + at least one of Codex/Gemini
- Implementation review: Claude + Codex + Gemini (three-agent default)
- Review evidence must be recorded before PR creation (cross-review-gate.sh enforces this)

### Constraints

- Do NOT modify session_governor.py — Phase 2 deliverable, separate concern
- Do NOT modify governance-checkpoints.yaml — Phase 1 deliverable
- Do NOT modify existing skill content in session-corpus-audit or comprehensive-learning
- Only create/modify files listed in this prompt
- Use `uv run` for all Python commands
```

---

## 6. Final Recommendation

### Assessment: ALREADY MOSTLY DONE

Two of four deliverables are fully implemented (session-corpus-audit, comprehensive-learning). The remaining work is:

1. **session-start-routine skill** — new skill file creation (~100-150 lines) + fix 4 broken links
2. **cross-review-policy skill** — thin wrapper skill (~60-80 lines) referencing existing policy doc and enforcement infrastructure
3. **Smoke tests** — 4 test files (~20-30 lines each)

**Estimated scope**: Small — approximately 6-8 files to create/modify, no complex logic, pattern-following work.

**Issue body update recommended**: The issue should be updated to reflect that deliverables #2 and #3 are already complete, converting the scope to a delta.

---

**RECOMMENDATION: READY AFTER LABEL UPDATE**

Add `status:plan-review` label to #2057, then user approves to `status:plan-approved` to unblock implementation. The issue body should be updated to note that session-corpus-audit (v1.0.0) and comprehensive-learning (v2.5.0) are already built — the remaining scope is session-start-routine creation, cross-review-policy wrapper, broken link fixes, and smoke tests.
