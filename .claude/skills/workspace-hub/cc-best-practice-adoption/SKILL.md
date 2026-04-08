---
name: cc-best-practice-adoption
description: 'Use when onboarding new Claude Code features, reviewing external best-practice
  repos, or expanding the daily learning catalog. Covers: gap analysis against native
  CC capabilities, tips catalog expansion, daily-learning script, native .claude/
  structure (agents, commands, settings).'
version: 1.0.0
updated: 2026-04-03
category: workspace-hub
type: skill
tags:
- learning
- onboarding
- claude-code
- best-practice
- daily-cadence
related_skills:
- comprehensive-learning
platforms:
- linux
---

# CC Best Practice Adoption

Workflow for analyzing external Claude Code best-practice sources, distilling actionable
gaps in our ecosystem, and wiring daily learning into the session lifecycle.

## When to Use

- New Claude Code version ships with features to evaluate
- Reviewing an external repo (e.g., shanraisshan/claude-code-best-practice)
- Expanding the daily learning tip catalog
- Bootstrapping native .claude/ structure (agents, commands, skills)

## Gotchas

### 1. Native vs Custom — Check Before Building
**Critical lesson learned:** `/powerup`, `/insights`, `/stats`, `/context`, `/simplify`,
`/batch`, `/debug`, `/diff`, `/security-review` are all **native CC commands** (v2.1.90+).
We wasted effort planning to build custom versions before discovering they exist.

**Rule:** Before creating any slash command, run `/help` or check
[claude-code-best-practice/best-practice/claude-commands.md](https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-commands.md)
for the 64 native commands.

### 2. Hermes Skills vs Native CC Skills
Our ecosystem has 691 Hermes-style skills but ZERO native CC format. They are different:
- **Native CC skills**: `.claude/skills/<name>/SKILL.md` with CC frontmatter (`context: fork`, `paths`, `model`, `effort`, `hooks`)
- **Hermes skills**: `~/.hermes/skills/<name>/SKILL.md` with Hermes frontmatter
- Both can coexist. Native CC skills show in `/skills` menu and support auto-discovery.

### 3. Tips Catalog YAML Is Not Standard YAML
`config/workflow-tips/tips-catalog.yaml` uses a minimal structure parsed by
`daily-learning.py` without PyYAML. Don't add complex YAML features (anchors, flow
sequences in values). Keep entries as simple `key: value` pairs.

### 4. Deterministic Daily Seed
`daily-learning.py` uses `md5(YYYY-MM-DD)` as seed so the same 2 tips show all day.
Running it multiple times won't cycle tips — that's intentional (spaced repetition).

## Workflow Steps

### Step 1: Clone and Analyze External Source
```bash
cd /tmp && git clone --depth 1 <repo-url>
```
Key files to read first:
- README.md (feature catalog, tip index)
- best-practice/claude-commands.md (native commands list)
- best-practice/claude-skills.md (native skills + frontmatter fields)
- best-practice/claude-subagents.md (native agent frontmatter fields)
- best-practice/claude-settings.md (60+ settings, 170+ env vars)

### Step 2: Gap Analysis
Compare external catalog against:
1. `config/workflow-tips/tips-catalog.yaml` — what tips are we missing?
2. `.claude/settings.json` — what settings are we not using?
3. `.claude/agents/` — do we have native agent definitions?
4. `.claude/commands/` — do we have native command definitions?

Output a structured list: ALREADY DONE / STILL MISSING / NEW TO ADD.

### Step 3: Expand Tips Catalog
Append new tips to `config/workflow-tips/tips-catalog.yaml` following the format:
```yaml
  - id: <prefix>-<slug>      # cc- | eco- | gsd- | bp-
    category: <category>      # claude-code | ecosystem | gsd | practice
    name: <Short Name>
    oneliner: "<one sentence>"
    try_it: "<copy-pasteable command>"
    source: "<provenance>"
    tags: [tag1, tag2]
    added: YYYY-MM-DD
```

Prefixes: `cc-` (Claude Code native), `eco-` (ecosystem), `gsd-` (GSD), `bp-` (best practice).

### Step 4: Update Daily Learning Script
If new tip categories are added, update `scripts/productivity/daily-learning.py`:
- Add category label mapping in `show_daily_tips()`
- Add practice exercises in `generate_practice()` for high-value tips

### Step 5: Bootstrap Native .claude/ Structure
Create files using native CC frontmatter (not Hermes format):

**Agents** (`.claude/agents/<name>.md`):
```yaml
---
name: <name>
description: "<when to invoke — use PROACTIVELY for auto-invocation>"
model: haiku|sonnet|opus
tools: Read, Write, Edit, Bash, Glob, Grep
color: cyan|red|green|blue|magenta
memory: project
effort: low|medium|high|max
isolation: worktree    # optional
skills:                # optional — preloaded into context
  - skill-name
---
```

**Commands** (`.claude/commands/<name>.md`):
```yaml
---
name: <name>
description: "<what it does>"
model: haiku|sonnet|opus
effort: low|medium|high
allowed-tools: Read, Bash, Agent(explorer)
---
Use !`command` for dynamic shell injection — output injected into prompt.
```

**Settings** (`.claude/settings.json`) — key fields often missed:
- `outputStyle: "Explanatory"` — insight boxes
- `effortLevel: "high"` — default reasoning depth
- `worktree.symlinkDirectories` — fast worktree startup
- `spinnerVerbs` — domain-relevant waiting messages
- `spinnerTipsOverride` — ecosystem tips while spinning

### Step 6: Wire Into Session Lifecycle
Add a SessionStart hook for automatic tip surfacing:
```json
{
  "type": "command",
  "command": "bash .claude/hooks/daily-learning-tip.sh 2>/dev/null || true",
  "timeout": 3,
  "statusMessage": "Daily learning tip"
}
```

### Step 7: Track Progress
```bash
uv run scripts/productivity/daily-learning.py --progress    # category coverage
uv run scripts/productivity/daily-learning.py --categories  # browse all tips
```

## Key Files

| File | Purpose |
|------|---------|
| `config/workflow-tips/tips-catalog.yaml` | All tips (67+), 4 categories |
| `config/workflow-tips/tip-history.yaml` | Shown-tip tracking, 30-day window |
| `scripts/productivity/daily-learning.py` | Daily tip picker + practice exercises |
| `.claude/hooks/daily-learning-tip.sh` | SessionStart hook, 1 tip on start |
| `.claude/agents/*.md` | Native CC agent definitions |
| `.claude/commands/*.md` | Native CC slash commands |
| `.claude/settings.json` | CC configuration |

## Reference
- https://github.com/shanraisshan/claude-code-best-practice (133k+ stars)
- 64 native CC commands, 5 official skills, 5 official agents
- CC frontmatter docs: commands, skills, subagents pages in best-practice repo
- GitHub issues: #1775 (8-week cadence), #1760 (self-improvement commands)
- https://github.com/affaan-m/everything-claude-code (50K stars, MIT)
  - Cherry-pick: security guide, pre:config-protection hook, batch-at-Stop pattern,
    context-budget skill, autonomous-loops (6 patterns), continuous-learning-v2 instincts
  - Implemented pattern: add a dedicated Claude Code `PreToolUse` hook entry in `.claude/settings.json`
    for `Write|Edit|MultiEdit`, then delegate the decision to a reusable shell checker
    (example: `.claude/hooks/config-protection-pretooluse.sh` -> `scripts/enforcement/check-config-protection.sh`).
    This keeps policy logic testable outside the hook wrapper.
  - Practical allowlist learned in implementation: permit non-tooling metadata edits in `pyproject.toml`
    and other low-risk config touches, but block broad weakening patterns like `ignore`,
    `extend-ignore`, `per-file-ignores`, `disable`, `skip`, `off`, and block removal of
    core safety-gate text from `CLAUDE.md` / `AGENTS.md` unless an explicit env bypass is set.
  - Testing pattern: write focused pytest coverage for the hook wrapper behavior before implementation,
    including non-protected file pass-through, allowlisted metadata edits, blocked risky config edits,
    blocked safety-gate removal, and explicit bypass env (`CONFIG_PROTECTION_APPROVED=1`).
  - MCP servers to evaluate: evalview, insaits, token-optimizer, omega-memory
  - ~80% overlap with our 691 skills — adopt patterns not bulk content

## Version History
- **1.0.0** (2026-04-03): Initial — gap analysis workflow, tips expansion, native CC structure bootstrap
