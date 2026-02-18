---
title: "Legal Sanity Agent"
description: "Automated legal compliance scanner for workspace-hub — catches client project names, proprietary tool references, and legally sensitive content across all repos, plans, and PRs"
version: "1.0"
module: "workspace-hub/legal-sanity"

session:
  id: "670f764e-5eca-4586-b6fe-6e1f0dc61773"
  agent: "claude-opus-4-5"

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
created: "2026-02-02"
updated: "2026-02-02"
priority: "high"
tags: [legal, compliance, cross-review, automation]

links:
  spec: "specs/modules/harmonic-squishing-acorn.md"
  branch: ""
---

# Legal Sanity Agent

> **Module**: workspace-hub/legal-sanity | **Status**: draft | **Created**: 2026-02-02

## Summary

After porting code from a client project (ENIGMA) into `worldenergydata/safety_analysis`, 9 source files contained explicit client project names, Databricks references, and client-specific tool names. These were caught manually but could have caused legal issues with past clients.

This plan creates an automated legal sanity system that:
1. Scans code against a configurable deny-list of legally sensitive terms
2. Runs as a mandatory gate in the cross-review cycle (before Codex/Gemini)
3. Integrates into PR creation and code review workflows
4. Provides per-project deny lists for different submodules

---

## Phases

### Phase 1: Foundation (4 new files)

- [ ] **1a.** Create global deny list: `.legal-deny-list.yaml` (workspace-hub root)
- [ ] **1b.** Create project deny list: `worldenergydata/.legal-deny-list.yaml`
- [ ] **1c.** Create scan script: `scripts/legal/legal-sanity-scan.sh`
- [ ] **1d.** Create rule file: `.claude/rules/legal-compliance.md`

### Phase 2: Skill & Workflow (2 new files)

- [ ] **2a.** Create skill: `.claude/skills/coordination/workspace/legal-sanity/SKILL.md`
- [ ] **2b.** Create workflow: `.claude/skills/_internal/workflows/legal-sanity-review/SKILL.md`

### Phase 3: Integration (5 file modifications)

- [ ] **3a.** Update `specs/templates/plan-template.md` — add `legal_sanity` reviewer
- [ ] **3b.** Update `specs/templates/plan-template-minimal.md` — add `legal_sanity` reviewer
- [ ] **3c.** Update `.claude/skills/_internal/workflows/cross-review-policy/SKILL.md` — add legal pre-gate
- [ ] **3d.** Update `.claude/agent-library/github/code-review-swarm.md` — add Legal agent
- [ ] **3e.** Update `.claude/agent-library/github/pr-manager.md` — add legal scan to pre-hooks

### Phase 4: Validation

- [ ] **4a.** Run scan against worldenergydata (should pass — ENIGMA already cleaned)
- [ ] **4b.** Inject temporary test violation, verify detection, remove
- [ ] **4c.** Verify plan template renders correctly with legal_sanity gate

---

## File Details

### 1a. `.legal-deny-list.yaml` (workspace-hub root — global baseline)

```yaml
# Global Legal Deny List — applies to ALL submodules
version: "1.0"
updated: "2026-02-02"

# Client project names and codenames
client_references: []
  # Add workspace-wide denied client names here

# Proprietary platform/tool references
proprietary_tools: []
  # Add workspace-wide denied tool names here

# Client-specific infrastructure
client_infrastructure: []
  # Add workspace-wide denied infra names here

# Files excluded from scanning
exclusions:
  - ".legal-deny-list.yaml"
  - ".git/"

default_severity: "block"
```

### 1b. `worldenergydata/.legal-deny-list.yaml` (project-specific)

```yaml
version: "1.0"
updated: "2026-02-02"

client_references:
  - pattern: "ENIGMA"
    case_sensitive: true
    description: "Client project codename"
  - pattern: "enigma"
    case_sensitive: true
    description: "Client project codename (lowercase)"

proprietary_tools:
  - pattern: "Databricks"
    case_sensitive: false
    description: "Client cloud platform"
  - pattern: "dbutils"
    case_sensitive: false
    description: "Databricks utility"
  - pattern: "dbfs:"
    case_sensitive: false
    description: "Databricks file system path"
  - pattern: "spark.databricks"
    case_sensitive: false
    description: "Databricks Spark config"

client_infrastructure: []

exclusions:
  - ".legal-deny-list.yaml"
  - ".git/"
  - "*.md"

default_severity: "block"
```

### 1c. `scripts/legal/legal-sanity-scan.sh`

Bash script (~100 lines). Core logic:
- Reads `.legal-deny-list.yaml` from target repo + workspace root (merges both)
- Parses YAML patterns using `grep`/`awk` (no `yq` dependency required)
- Runs `rg` (ripgrep) for each pattern with exclusion globs
- `--diff-only` flag: scan only `git diff --name-only` files (fast, for PRs)
- `--repo=<name>` flag: scan specific submodule
- `--all` flag: scan all submodules
- Outputs JSON report to stdout
- Exit code: 0=pass, 1=block violations found

### 1d. `.claude/rules/legal-compliance.md`

Follows `security.md` format. Sections:
- **Client Reference Prevention** — never include client names, codenames, tool refs
- **Code Porting Rules** — scan immediately after import, replace all client-specific refs
- **Deny List Management** — every repo must have `.legal-deny-list.yaml`
- **Scanning Requirements** — must run before PRs, part of cross-review cycle

### 2a. `.claude/skills/coordination/workspace/legal-sanity/SKILL.md`

```yaml
---
name: legal-sanity
description: "Scan code for client project names, proprietary tool references, and legally sensitive content"
version: 1.0.0
category: workspace-hub
capabilities:
  - legal_reference_scanning
  - client_name_detection
  - deny_list_management
tools:
  - Bash
  - Read
  - Glob
  - Grep
related_skills:
  - compliance-check
---
```

Body: Quick Start commands, When to Use, Scan Logic, Execution Checklist, Output Format.

### 2b. `.claude/skills/_internal/workflows/legal-sanity-review/SKILL.md`

```yaml
---
name: legal-sanity-review
version: "1.0.0"
category: _internal
description: "Legal Sanity Review Workflow Skill"
---
```

Body: Defines legal scan as pre-gate in cross-review cycle. Flow:
```
Commit → Legal Scan → Block? → Fix required
                    → Pass  → Proceed to Codex/Gemini
```

### 3a–3b. Plan template updates

Add to `review.reviewers` in YAML frontmatter:
```yaml
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
```

Add to approval gate:
```yaml
    legal_sanity_passed: false
```

Add row to Review Status table:
```
| Legal Sanity | ⬜ pending |
```

### 3c. Cross-review-policy update

Update Review Flow diagram to add legal scan before Codex:
```
Claude/Gemini performs task → Legal Sanity Scan → Pass? → Codex reviews
```

Add to Review Types table: `| Legal Sanity | Every commit, plan, PR |`
Add to Exit Conditions: `5. LEGAL_BLOCK: Legal scan found block-severity violations`

### 3d. Code-review-swarm update

Add `Legal compliance scanning` to capabilities list. Add Legal Agent section after Architecture Agent with `rg`-based scanning commands and `legal: block` threshold.

### 3e. PR-manager hooks update

Add to `hooks.pre` array (line 27):
```yaml
- "./scripts/legal/legal-sanity-scan.sh --diff-only || (echo 'Legal sanity FAILED' && exit 1)"
```

---

## Verification

1. **Unit test the script**: Run `scripts/legal/legal-sanity-scan.sh` against `worldenergydata/` — expect PASS (ENIGMA refs already removed)
2. **Negative test**: Temporarily add `ENIGMA` to a `.py` file, run scan, verify it's caught with file:line detail, then revert
3. **Template test**: Create a new spec using the updated minimal template, verify `legal_sanity` appears in Review Status
4. **Integration test**: Run the PR-manager pre-hook sequence manually to verify the legal scan gate works

---

## File Summary

| # | Path | Type | Lines (est) |
|---|------|------|-------------|
| 1a | `.legal-deny-list.yaml` | New | ~20 |
| 1b | `worldenergydata/.legal-deny-list.yaml` | New | ~35 |
| 1c | `scripts/legal/legal-sanity-scan.sh` | New | ~120 |
| 1d | `.claude/rules/legal-compliance.md` | New | ~60 |
| 2a | `.claude/skills/.../legal-sanity/SKILL.md` | New | ~80 |
| 2b | `.claude/skills/.../legal-sanity-review/SKILL.md` | New | ~60 |
| 3a | `specs/templates/plan-template.md` | Modify | +15 |
| 3b | `specs/templates/plan-template-minimal.md` | Modify | +12 |
| 3c | `cross-review-policy/SKILL.md` | Modify | +10 |
| 3d | `code-review-swarm.md` | Modify | +20 |
| 3e | `pr-manager.md` | Modify | +1 |

**New files: 6 | Modified files: 5 | Total: 11**
