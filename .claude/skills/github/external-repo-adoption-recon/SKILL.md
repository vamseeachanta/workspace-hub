---
name: external-repo-adoption-recon
description: Clone and analyze an external open-source repo (best practices, frameworks,
  workflow toolkits) to produce a gap analysis against our ecosystem and an adoption
  cadence plan. Use when a user shares a GitHub URL of a methodology/tooling repo
  and wants to extract what's useful.
version: 1.0.0
category: github
type: skill
tags:
- recon
- adoption
- gap-analysis
- best-practice
- external-repo
related_skills:
- engineering-solver-domain-recon
- codebase-inspection
---

# External Repo Adoption Reconnaissance

Systematic workflow for evaluating an external open-source repo (best-practice guides, workflow frameworks, tooling kits) against our ecosystem, producing a gap analysis and a time-boxed adoption plan.

## When to Use

- User shares a GitHub URL of a methodology/best-practice/framework repo
- User says "what can we learn from this?" or "review this repo"
- Planning adoption of external workflows, plugins, or patterns
- Benchmarking our ecosystem against community standards

## Why This Exists

Naive approach: skim README, cherry-pick one or two ideas. This misses the structured knowledge.
Learned the hard way: we planned to BUILD /powerup and /insights from scratch (#1760) before
discovering they were NATIVE Claude Code commands — a fact buried in the external repo's docs
that only surfaced through systematic file-by-file reading.

## 5-Phase Workflow

### Phase 1: Clone and Inventory (5 min)

```bash
cd /tmp && git clone --depth 1 <URL>
```

Then enumerate ALL files — don't just read README:

```bash
search_files(pattern="*", target="files", path="/tmp/<repo>")
```

**Why full inventory matters:** READMEs are marketing. The real knowledge is in:
- Best-practice markdown files (not linked from README)
- Implementation examples (.claude/agents/, .claude/commands/, .claude/skills/)
- Config files (.claude/settings.json, .mcp.json, .codex/)
- Tips/videos directories (curated expert knowledge)
- Reports/analysis directories (comparative studies)

### Phase 2: Systematic Reading — Parallel Where Possible (15-20 min)

Read ALL substantive files. Group into parallel batches:

**Batch 1 (concepts):** README, best-practice docs, settings references
**Batch 2 (implementation):** Agent definitions, command files, skill files
**Batch 3 (workflow):** Development workflow docs, orchestration patterns
**Batch 4 (tips/reports):** Expert tips, comparison reports, video summaries

Key: read the FULL file, not just first 80 lines. Settings references and
command catalogs often have critical fields buried at line 400+.

### Phase 3: Gap Analysis — Diff Against Our Ecosystem (10 min)

Structure findings into 3 tiers:

**TIER 1 — HIGH VALUE, LOW EFFORT (just use them):**
Native features/commands we are not using. These are free — no build needed.
This tier consistently produces the highest ROI because it catches "reinventing
the wheel" anti-patterns.

**TIER 2 — STRUCTURAL IMPROVEMENTS (config/setup work):**
Features that need configuration, file creation, or settings changes.
E.g., frontmatter fields, settings.json keys, hook definitions.

**TIER 3 — WORKFLOW PATTERNS (planning + implementation):**
Patterns that need design, multi-file implementation, and testing.
E.g., new orchestration commands, agent definitions, workflow frameworks.

**Also track GAPS IN THE EXTERNAL REPO:**
What do WE have that they don't? This validates our existing investments.

### Phase 4: Create Adoption Issue (5 min)

Create a GitHub issue with:
1. Source repo link and clone location
2. Key findings summary (especially Tier 1 "just use it" items)
3. Time-boxed adoption plan (weekly cadence preferred)
4. Success metrics table (baseline vs target)
5. Links to related existing issues

### Phase 5: Update Existing Issues If Needed

If the findings change the scope of existing issues, comment on them immediately.
Don't let stale issue descriptions persist when you now know better.

## Gotchas

### The Native Feature Trap
The #1 finding from this pattern: external repos catalog NATIVE features of tools
you already have but aren't using. Always separate "features to adopt" from
"features to build". The shanraisshan/claude-code-best-practice repo documented
64 native CC slash commands — we were using ~3.

### Don't Trust Summaries — Read Source Files
A repo's README may say "10 power-ups" but the actual power-ups doc reveals
they are NATIVE interactive lessons, not custom scripts. The distinction between
"native command" and "custom command" is often only clear from the implementation
files, not the summary.

### Frontmatter Is the API Contract
For Claude Code repos specifically, the frontmatter fields in agents/commands/skills
are the most actionable content. A single field like `context: fork` or
`paths: "*.dat,*.yml"` can fundamentally change how a skill behaves. Catalog
ALL frontmatter fields you find — they are the "API" of the extension system.

### Scope Creep Prevention
External repos are aspirational — they show the ideal state. Don't try to adopt
everything at once. The weekly cadence pattern (8 weeks, one theme per week)
works better than a Big Bang adoption.

### Video/Podcast Summaries Are Gold
If the repo includes video notes (e.g., Boris Cherny interviews), read them.
These often contain workflow philosophy that explains WHY patterns exist,
not just WHAT they are. E.g., "prototype > PRD — build 20-30 versions
instead of writing specs" changes how you think about planning.

## Output Template

```markdown
# External Repo Adoption Analysis: <repo-name>

## Source
- Repo: <URL>
- Stars: <N>
- Last updated: <date>
- Clone: /tmp/<repo-name>

## Key Finding
<One-paragraph summary of the single most impactful discovery>

## Tier 1: Just Use It (native features we're ignoring)
| Feature | What it does | Our current usage |
|---------|-------------|------------------|

## Tier 2: Config/Setup Work Needed
| Feature | What it needs | Effort estimate |
|---------|--------------|----------------|

## Tier 3: Build Needed
| Feature | What to build | Effort estimate |
|---------|--------------|----------------|

## Adoption Cadence
Week 1: ...
Week 2: ...
...

## Success Metrics
| Metric | Baseline | Target |
|--------|----------|--------|

## Related Issues
- #NNN — ...
```

## When NOT to Use This Skill

- For engineering solver domain recon → use `engineering-solver-domain-recon`
- For analyzing our OWN repos → use `repo-capability-map` or `codebase-inspection`
- For one-off "what does this function do" questions → just read the file
- For repos with < 100 stars or no documentation → not worth the full workflow
