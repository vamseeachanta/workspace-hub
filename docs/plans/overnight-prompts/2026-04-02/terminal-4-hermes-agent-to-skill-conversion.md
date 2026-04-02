# Terminal 4 — Hermes: Convert digitalmodel agent files to SKILL.md format

## Context
We are in /mnt/local-analysis/workspace-hub on ace-linux-1.
This executes GH issue #1721.
Use `uv run` for all Python. Do NOT ask the user any questions.
Commit to main and push after each task.
`git pull origin main --rebase` before every push.

## YOUR WRITE TERRITORY
- `scripts/skills/convert-agent-to-skill.py` (new conversion script)
- `scripts/skills/tests/test_convert_agent_to_skill.py` (tests)
- `digitalmodel/.claude/skills/` (new skill files — this is a SEPARATE git repo)
- `config/agents/hermes/config.yaml.template` (add digitalmodel external_dir)

## DO NOT WRITE TO
- `analysis/` (owned by #1720 terminals)
- `scripts/cron/` (already done in #1719)
- Any `.claude/agents/` or `.claude/commands/` file (read-only sources)

---

## TASK 1: Build the conversion script

Create `scripts/skills/convert-agent-to-skill.py` — a Python script that converts Claude Code agent .md files to Hermes SKILL.md format.

### Input format (Claude agent .md)
Agent files are markdown with optional YAML frontmatter:
```markdown
---
name: cathodic-protection-engineer
description: Use this agent when you need expertise in cathodic protection systems
---
# Agent content here...
```

Some agents are in directories with multiple files:
```
agents/orcaflex/
  README.md
  BATCH_PROCESSING_NOTES.md
  other-files.md
```
For directory-based agents, concatenate README.md + other .md files into one skill.

### Output format (Hermes SKILL.md)
```markdown
---
name: <agent-name>
version: 1.0.0
category: <inferred-from-path>
description: <from-agent-description-or-first-paragraph>
type: reference
tags: []
scripts_exempt: true
---
# <Title>

<agent body content preserved>
```

### Category inference rules
- Path contains `orcaflex` → category: `engineering`
- Path contains `orcawave` → category: `engineering`
- Path contains `aqwa` → category: `engineering`
- Path contains `freecad` or `cad` → category: `engineering`
- Path contains `gmsh` or `mesh` → category: `engineering`
- Path contains `cathodic` or `cp` → category: `engineering`
- Path contains `github` → category: `development`
- Path contains `testing` → category: `development`
- Path contains `sparc` → category: `development`
- Path contains `data` → category: `data`
- Path contains `documentation` → category: `documentation`
- Default → category: `general`

### Script requirements
1. `uv run python scripts/skills/convert-agent-to-skill.py --input <agent-path> --output <skills-dir>`
2. `--input` can be a single .md file or a directory containing .md files
3. `--output` is the target skills directory (e.g., `digitalmodel/.claude/skills/engineering/`)
4. `--dry-run` flag to preview without writing
5. `--batch <agents-dir>` to convert all agents in a directory tree
6. Handle both single-file agents and directory-based agents
7. Skip if SKILL.md already exists in output path
8. Log conversions to stdout

### Test it
Write `scripts/skills/tests/test_convert_agent_to_skill.py`:
- Test frontmatter parsing (with and without frontmatter)
- Test category inference from paths
- Test single-file conversion
- Test directory-based agent conversion
- Test --dry-run produces no files
- Test skip-if-exists behavior
- Run: `uv run python -m pytest scripts/skills/tests/test_convert_agent_to_skill.py -v`

### Commit
```
feat(skills): add convert-agent-to-skill.py — bridges Claude agents to Hermes SKILL.md (#1721)
```

---

## TASK 2: Convert digitalmodel P1 agents (orcaflex, orcawave, aqwa)

Using the script from Task 1, convert the high-value digitalmodel engineering agents.

### Priority 1 conversions (13 + 5 + 7 = 25 agent files)

**OrcaFlex agents** (13 files at `digitalmodel/.claude/agents/orcaflex/`):
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/orcaflex \
  --output digitalmodel/.claude/skills/engineering/orcaflex-agents
```

**OrcaWave agents** (5 files at `digitalmodel/.claude/agents/orcawave/`):
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/orcawave \
  --output digitalmodel/.claude/skills/engineering/orcawave-agents
```

**AQWA agents** (7 files at `digitalmodel/.claude/agents/aqwa/`):
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/aqwa \
  --output digitalmodel/.claude/skills/engineering/aqwa-agents
```

### Priority 2 conversions

**FreeCAD agents** (17 files at `digitalmodel/.claude/agents/freecad/`):
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/freecad \
  --output digitalmodel/.claude/skills/engineering/freecad-agents
```

**GMSH agents** (24 files at `digitalmodel/.claude/agents/gmsh/`):
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/gmsh \
  --output digitalmodel/.claude/skills/engineering/gmsh-agents
```

**CAD engineering specialist** (5 files at `digitalmodel/.claude/agents/cad-engineering-specialist/`):
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/cad-engineering-specialist \
  --output digitalmodel/.claude/skills/engineering/cad-agents
```

**Top-level specialist agents** (single .md files):
```bash
for agent in cathodic-protection-engineer cad-engineering-specialist base-template-generator; do
  uv run python scripts/skills/convert-agent-to-skill.py \
    --input "digitalmodel/.claude/agents/${agent}.md" \
    --output digitalmodel/.claude/skills/engineering/
done
```

### After conversion, verify
```bash
echo "=== New skills created ==="
find digitalmodel/.claude/skills -name 'SKILL.md' | wc -l

echo "=== Categories ==="
find digitalmodel/.claude/skills -name 'SKILL.md' -exec dirname {} \; | sort -u
```

### IMPORTANT: digitalmodel is a separate git repo
digitalmodel/ is a nested git repo (gitignored by workspace-hub). You must:
```bash
cd digitalmodel
git add .claude/skills/
git commit -m "feat(skills): convert 71+ Claude agents to Hermes SKILL.md format (#1721)

P1: orcaflex (13), orcawave (5), aqwa (7) = 25 engineering skills
P2: freecad (17), gmsh (24), cad (5) = 46 engineering skills
Plus 3 top-level specialist agents"
git push origin main
cd ..
```

### Commit for workspace-hub (the conversion script)
```
feat(skills): convert digitalmodel P1+P2 agents — 71+ new skills (#1721)
```

---

## TASK 3: Wire digitalmodel skills into Hermes external_dirs

### Update the config template
In `config/agents/hermes/config.yaml.template`, add digitalmodel to external_dirs:
```yaml
skills:
  external_dirs:
    - __WS_HUB_PATH__/.claude/skills
    - __WS_HUB_PATH__/CAD-DEVELOPMENTS/.claude/skills
    - __WS_HUB_PATH__/worldenergydata/.claude/skills
    - __WS_HUB_PATH__/achantas-data/.claude/skills
    - __WS_HUB_PATH__/assetutilities/.claude/skills
    - __WS_HUB_PATH__/digitalmodel/.claude/skills    # NEW
```

### Update the live Hermes config
In `~/.hermes/config.yaml`, add:
```yaml
    - /mnt/local-analysis/workspace-hub/digitalmodel/.claude/skills
```

### Run the config sync to verify
```bash
bash scripts/_core/sync-agent-configs.sh --dry-run 2>&1 | grep -i hermes
```

### Verify skill count increase
```bash
total=86
for d in \
  /mnt/local-analysis/workspace-hub/.claude/skills \
  /mnt/local-analysis/workspace-hub/CAD-DEVELOPMENTS/.claude/skills \
  /mnt/local-analysis/workspace-hub/worldenergydata/.claude/skills \
  /mnt/local-analysis/workspace-hub/achantas-data/.claude/skills \
  /mnt/local-analysis/workspace-hub/assetutilities/.claude/skills \
  /mnt/local-analysis/workspace-hub/digitalmodel/.claude/skills; do
  count=$(find "$d" -name 'SKILL.md' -not -path '*/_archive/*' 2>/dev/null | wc -l)
  total=$((total + count))
  echo "  $(basename $(dirname $(dirname $d))): $count"
done
echo "Total: $total (was 691, target ≥750)"
```

### Commit
```
feat(harness): add digitalmodel/.claude/skills to Hermes external_dirs (#1721)
```

---

## TASK 4: Convert GSD template agents (top 20)

The 74 template agents are shared across 18 repos. Convert the most useful general-purpose ones to SKILL.md in workspace-hub.

### Audit first — read each template agent and classify:
For each of the 20 template agent directories in `assetutilities/.claude/agents/`:
- Read README.md or main .md file
- Classify as: CONVERT (general-purpose, useful) or SKIP (Claude-specific, or already covered by existing skills)

### Expected CONVERT candidates (based on names):
- `analysis/` — data analysis patterns
- `architecture/` — architecture review
- `core/` — core coding patterns
- `development/` — development workflows
- `documentation/` — documentation generation
- `github/` — GitHub workflows (but check overlap with existing Hermes github skills)
- `sparc/` — SPARC methodology
- `testing/` — testing patterns

### Expected SKIP candidates:
- `flow-nexus/` — Claude-specific orchestration
- `hive-mind/` — Claude-specific multi-agent
- `swarm/` — Claude-specific swarm
- `neural/` — Claude-specific
- `consensus/` — Claude-specific
- `templates/` — agent templates, meta
- `optimization/` — likely Claude-specific tuning
- `goal/` — Claude-specific goal tracking

### Convert the CONVERT candidates:
```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --batch assetutilities/.claude/agents \
  --output .claude/skills/gsd-agents/ \
  --include analysis,architecture,core,development,documentation,github,sparc,testing \
  --dry-run
```
Review dry-run output, then run without --dry-run.

### Check for overlap with existing Hermes skills
Before committing, verify no name collisions:
```bash
for skill in $(find .claude/skills/gsd-agents -name 'SKILL.md' -exec grep -l 'name:' {} \;); do
  name=$(grep '^name:' "$skill" | head -1 | sed 's/name: //')
  existing=$(find ~/.hermes/skills -name 'SKILL.md' -exec grep -l "name: $name" {} \;)
  [ -n "$existing" ] && echo "COLLISION: $name exists in Hermes local skills"
done
```

### Commit
```
feat(skills): convert top 20 GSD template agents to SKILL.md (#1721)
```

---

Post a progress comment on GH issue #1721 when done:
```
Terminal 4 (Hermes) complete:
- Task 1: convert-agent-to-skill.py built + tested
- Task 2: [N] digitalmodel agents converted (P1: orcaflex/orcawave/aqwa, P2: freecad/gmsh/cad)
- Task 3: digitalmodel/.claude/skills wired to Hermes external_dirs
- Task 4: [N] GSD template agents converted
- Hermes skill count: [N] (was 691)
```
