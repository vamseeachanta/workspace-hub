---
title: "Skill Eval - Test/Evaluate All Skills"
description: "Add a /skill-eval command that validates all 230+ SKILL.md files for structural correctness, content quality, cross-reference integrity, and registry consistency"
version: "1.0"
module: skill-eval
session:
  id: "2026-01-29-skill-eval"
  agent: "claude-opus-4.5"
review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 0
      feedback: ""
  ready_for_next_step: false
status: "draft"
progress: 0
created: "2026-01-29"
updated: "2026-01-29"
target_completion: ""
priority: "medium"
tags: [skills, evaluation, quality, verification]
links:
  spec: ""
  branch: "feature/skill-eval"
---

# Skill Eval - Test/Evaluate All Skills

> **Module**: skill-eval | **Status**: draft | **Created**: 2026-01-29

## Summary

Add a `/skill-eval` command that validates all 230+ SKILL.md files in `.claude/skills/` for structural correctness, content quality, cross-reference integrity, and registry consistency. Outputs a categorized report with actionable fix suggestions.

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini before implementation.

### Review Status

| Gate | Status |
|------|--------|
| Iterations (>= 3) | 0/3 |
| OpenAI Codex | pending |
| Google Gemini | pending |
| **Ready** | false |

### Review Log

| Iter | Date | Reviewer | Status | Feedback Summary |
|------|------|----------|--------|------------------|
| 1 | | Codex | Pending | |
| 1 | | Gemini | Pending | |
| 2 | | Codex | Pending | |
| 2 | | Gemini | Pending | |
| 3 | | Codex | Pending | |
| 3 | | Gemini | Pending | |

### Approval Checklist

- [ ] Iteration 1 complete (both reviewers)
- [ ] Iteration 2 complete (both reviewers)
- [ ] Iteration 3 complete (both reviewers)
- [ ] **APPROVED**: Ready for implementation

---

## Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `.claude/skills/development/skill-eval/scripts/eval-skills.py` | Python evaluation engine (~350 lines) |
| 2 | `.claude/skills/development/skill-eval/SKILL.md` | Skill definition (v2 template) |
| 3 | `.claude/commands/verify/skill-eval.md` | Slash command entry point |
| 4 | `.claude/skill-registry.yaml` | Add registry entry |

---

## Phases

### Phase 1: Core Evaluation Script

Create `eval-skills.py` -- self-contained Python script using PEP 723 inline metadata for `uv run --script`. Single dependency: `pyyaml`.

**Script structure (~350 lines):**
- Constants & config (required fields, sections, thresholds)
- Dataclasses: `Issue`, `SkillResult`, `EvalReport`
- Frontmatter parser (YAML `---` + legacy blockquote fallback)
- Check functions (one per check, returns `list[Issue]`)
- Report generators (human-readable + JSON)
- `main()` with argparse CLI

**Checks performed (priority order):**

| Severity | Check | Description |
|----------|-------|-------------|
| critical | `frontmatter_exists` | YAML frontmatter (`---` delimited) present |
| critical | `name_field_present` | `name:` in frontmatter |
| critical | `description_field_present` | `description:` in frontmatter |
| critical | `yaml_valid` | Frontmatter parses without error |
| critical | `file_readable` | Non-empty, valid UTF-8 |
| warning | `version_present` | `version:` exists |
| warning | `version_semver` | Version follows `X.Y.Z` |
| warning | `category_present` | `category:` exists |
| warning | `category_matches_dir` | Category aligns with directory |
| warning | `related_skills_resolve` | All `related_skills` map to real skills |
| warning | `required_sections_present` | Quick Start, When to Use, Usage Examples, etc. |
| warning | `quickstart_has_code` | Code blocks in Quick Start |
| warning | `usage_examples_has_code` | Code blocks in Usage Examples |
| warning | `description_word_count` | 10-50 words |
| warning | `no_todo_fixme` | No unresolved markers |
| info | `uses_v2_template` | Has YAML frontmatter (not legacy) |
| info | `has_metrics_section` | Metrics section present |
| info | `duplicate_names` | No two skills share same name |

**CLI options:**
```
--skill <name>       Evaluate single skill
--category <cat>     Filter by category directory
--format json        JSON output (default: human-readable)
--severity <level>   Minimum: critical, warning, info
--summary-only       Summary counts only
--output <path>      Write report to file
```

**Exit codes:** 0 = pass (no critical), 1 = critical failures, 2 = script error

- [ ] Create `eval-skills.py` with all checks
- [ ] Test against actual skills directory
- [ ] Verify JSON output parses cleanly

### Phase 2: Skill Definition & Command

- [ ] Create `SKILL.md` following v2 template format
- [ ] Create `verify/skill-eval.md` command file
- [ ] Add registry entry to `skill-registry.yaml`

### Phase 3: Verification

- [ ] Run full evaluation: `uv run .claude/skills/development/skill-eval/scripts/eval-skills.py`
- [ ] Confirm discovers all ~230 SKILL.md files
- [ ] Confirm JSON output: `... --format json | python -m json.tool`
- [ ] Spot-check known-good skill (e.g., `testing-tdd-london`) passes
- [ ] Spot-check known legacy skill (no frontmatter) flagged as critical
- [ ] Test single-skill mode: `... --skill testing-tdd-london`
- [ ] Test category filter: `... --category development`

---

## Edge Cases

| Case | Handling |
|------|----------|
| 49 skills without YAML frontmatter | Report critical, extract name from `# heading` for display |
| 15 skills with blockquote metadata | Recognize legacy format, info-level migration suggestion |
| YAML parse errors | Catch with try/except, report as critical (don't crash) |
| Duplicate skill names | Detect and warn |
| Case-varied headings | Match case-insensitively |
| Empty files | Report as critical |
| Encoding issues | Read with `errors='replace'` |

---

## Key Files

| File | Role |
|------|------|
| `.claude/skills/` (root) | All SKILL.md files to evaluate |
| `.claude/skill-registry.yaml` | Command registry for consistency checks |
| `.claude/skills/development/verification-loop/SKILL.md` | Reference pattern (v2 template) |
| `.claude/skills/_internal/builders/skill-creator/SKILL.md` | Reference for SKILL.md structure |
| `.claude/skills/development/testing/testing-tdd-london/SKILL.md` | Example well-structured skill |

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Review Iteration 1 | Pending | |
| Review Iteration 2 | Pending | |
| Review Iteration 3 | Pending | |
| Plan Approved | Pending | |
| Phase 1: Script | Pending | |
| Phase 2: Skill & Command | Pending | |
| Phase 3: Verification | Pending | |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-01-29 | 2026-01-29-skill-eval | claude-opus-4.5 | Plan created |
