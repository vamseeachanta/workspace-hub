---
name: harness-audit
description: >
  Audit all agent harness files for line limits, content duplication, and correct
  layer placement. Use this skill whenever harness files are edited (AGENTS.md,
  CLAUDE.md, GEMINI.md, rules/*.md, MEMORY.md), before committing harness changes,
  when running /improve, or when the user asks to check harness health. Also use
  proactively after any session that modifies rules, skills, or micro-skills to
  catch layer violations before they pollute future sessions.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# Harness Audit

Validates the agent harness stack against the layer architecture established in WRK-1384.

## Architecture (what goes where)

| Layer | Location | Loaded when | Max size | Content |
|-------|----------|------------|----------|---------|
| 0 | AGENTS.md | Every session | 20 lines | Canonical: hard gates, commands, policies |
| 0 | CLAUDE.md | Every session | 20 lines | Thin adapter: points to AGENTS.md + Claude-specific |
| 0 | GEMINI.md | Every session | 20 lines | Thin adapter: points to AGENTS.md + Gemini-specific |
| 0 | rules/*.md | Every session | 50 lines total | Universal constraints only (edit safety, enforcement gradient) |
| 0 | MEMORY.md | Every session | 20 lines | Feedback + project file index only |
| 1 | Stage micro-skills | At stage entry | 35 lines each | Stage-specific rules (coding, testing, git, legal) |
| 2 | .claude/docs/ | On-demand | No limit | Reference material |

## Audit Checklist

Run these checks in order. Stop on first FAIL if `--strict`, otherwise report all.

### 1. Line Limits
```bash
bash scripts/work-queue/check-claude-md-limits.sh
```
Files checked: AGENTS.md, CLAUDE.md, GEMINI.md (20-line limit each).
Also check: rules/*.md total ≤ 50 lines, MEMORY.md ≤ 20 lines.

### 2. CODEX.md Must Not Exist
Codex reads AGENTS.md natively. A CODEX.md file at repo root is a dead file.
```bash
test ! -f CODEX.md || echo "FAIL: CODEX.md exists — delete it (Codex reads AGENTS.md)"
```

### 3. AGENTS.md Is Canonical
Verify AGENTS.md contains the 5 hard gates and the Commands section.
CLAUDE.md and GEMINI.md must point to AGENTS.md, not duplicate its content.
Check: no hard gate text (orchestrate, plan, TDD, WRK, gate evidence) appears in CLAUDE.md.

### 4. No Stage-Specific Rules in rules/
Scan rules/*.md for content that belongs in stage micro-skills:
- Coding style (naming, size limits, imports) → stage 10 micro-skill
- Testing rules (TDD, coverage, mocks) → stage 10/12 micro-skill
- Git workflow (commit format, branch naming) → stage 10/19 micro-skill
- Legal compliance (deny lists, scanning) → stage 19 micro-skill
- Python runtime (per-repo commands) → on-demand via repo-map.yaml
- Security (OWASP, injection) → remove (irrelevant to this workspace)

Grep for keywords that signal misplaced content:
```bash
grep -l "snake_case\|PascalCase\|pytest\|TDD\|commit.*format\|deny.list\|XSS\|CSRF" .claude/rules/*.md
```
Any match = WARN (content may belong in a micro-skill instead).

### 5. No @imports Loading Large Files
CLAUDE.md must not use @config/deps/ or @config/onboarding/ references.
These load 98+ lines every session. Use on-demand reads instead.

### 6. MEMORY.md Contains Only Index
MEMORY.md should contain only pointers to feedback and project memory files.
No WRK status lists, no environment details, no test counts, no machine details.
Grep for signals of content bloat:
```bash
grep -c "ARCHIVED\|working\|pending\|test.*pass\|uv run" MEMORY.md
```
Any match > 0 = WARN (stale content in MEMORY.md).

### 7. Stage Micro-Skills Have Required Content
For stages that write code (10, 11, 12), verify micro-skills contain:
- Coding style rules (naming, size limits)
- Testing rules (TDD, no mocks, test data sources)
- Python runtime (uv run)
- Git commit format
- Legal scan instruction

```bash
for stage in 10 12 19; do
  f=".claude/skills/workspace-hub/stages/stage-$(printf '%02d' $stage)-*.md"
  echo "=== Stage $stage ==="
  grep -c "snake_case\|uv run\|commit\|legal" $f 2>/dev/null || echo "MISSING content"
done
```

## Output Format

```
HARNESS AUDIT — <timestamp>
Layer 0:
  AGENTS.md:  OK (18 lines)
  CLAUDE.md:  OK (7 lines)
  GEMINI.md:  OK (6 lines)
  CODEX.md:   OK (not present)
  rules/:     OK (29 lines total)
  MEMORY.md:  OK (16 lines)
Layer 1:
  Canonical:  OK (AGENTS.md has 5 gates + commands)
  No duplication: OK (CLAUDE.md has no gate text)
  No @imports: OK
Stage micro-skills:
  Stage 10:   OK (coding + testing + git + legal present)
  Stage 12:   OK (testing present)
  Stage 19:   OK (git + legal present)
Result: PASS (0 failures, 0 warnings)
```
