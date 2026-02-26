---
name: engineering-context-loader
description: >
  Auto-detects the active engineering domain from a WRK item's tags and
  outputs a focused context: which skills to load, which design codes apply,
  and which memory/spec files to read. Prevents loading the full 350+ skill
  catalog when only ~20 domain-relevant skills are needed.
version: 1.0.0
updated: 2026-02-24
category: workspace-hub
triggers:
  - engineering context
  - load engineering context
  - context loader
  - domain context
  - engineering session start
  - what skills do I need
  - domain-aware session start
related_skills:
  - workspace-hub/session-start
  - workspace-hub/workstations
  - workspace-hub/save
capabilities:
  - domain-detection
  - skill-subset-selection
  - design-code-surfacing
  - memory-file-routing
  - spec-file-discovery
requires: []
tags:
  - session-lifecycle
  - engineering
  - context-optimization
  - naval-architecture
invoke: engineering-context-loader
---

# Engineering Context Loader

Auto-detect the active engineering domain from a WRK item's `tags:` field and
output a focused context block. Run at session start for any WRK item that
contains engineering domain tags.

## When to Use

- After `/session-start` when the top unblocked item has engineering tags
- When switching to a new WRK item mid-session
- Manually via `/engineering-context-loader` whenever domain context is stale

## Domain Map

| Tag(s) | Key Skills | Design Codes |
|--------|-----------|--------------|
| `mooring` | mooring-design, orcaflex-mooring-iteration, hydrodynamics | API RP 2SK, DNV-OS-E301 |
| `fatigue` | fatigue-analysis, signal-analysis, orcaflex-post-processing | DNV-RP-C203, BS 7608 |
| `riser` | catenary-riser, viv-analysis, structural-analysis | API RP 2RD, DNV-ST-F201 |
| `hull` | hydrodynamics, diffraction-analysis, orcawave-analysis | DNV-OS-C105 |
| `pipeline` | structural-analysis, orcaflex-modeling | DNV-ST-F101, API RP 1111 |
| `structural` | structural-analysis, orcaflex-code-check | API RP 2A, ISO 19902 |
| `cp` / `cathodic-protection` | cathodic-protection | DNV-RP-B401 |
| `drilling` | api12-drilling-analyzer | API TR 5C3 |
| `energy-economics` / `field-development` | fdas-economics, field-analyzer | N/A |
| `portfolio` / `investments` | data-management, plotly-visualization | N/A |

## Steps Claude Follows

### Step 1 — Resolve the Active WRK Item

Look for the active WRK item in this priority order:

1. `.claude/state/active-wrk` — if file exists and is non-empty, read its
   contents for the WRK ID (e.g. `WRK-175`)
2. Most recently modified file in `.claude/work-queue/working/`
3. Current git branch name (e.g. `feature/WRK-175-...` → extract `WRK-175`)
4. Ask the user: "Which WRK item should I load context for?"

Once the WRK ID is known, read the file at:
`.claude/work-queue/pending/<WRK-ID>.md` or
`.claude/work-queue/working/<WRK-ID>.md`

### Step 2 — Extract Tags

Read the YAML frontmatter of the WRK file. Extract the `tags:` list.
Also check the `module:` field for supplementary domain hints.

If no tags are found or none match the domain map, output:
> "No engineering domain tags detected in <WRK-ID>. Returning full skill catalog."
Then stop — do not proceed with domain filtering.

### Step 3 — Map Tags to Domain(s)

Apply the domain map table above. A single WRK item may match multiple domains
(e.g. `mooring` + `fatigue` is common for mooring fatigue studies).

Collect the union of all matched entries:
- All matched skill names (deduplicated)
- All matched design codes (deduplicated)

### Step 4 — Resolve Skill Paths

For each skill name from Step 3, locate the SKILL.md under
`.claude/skills/engineering/marine-offshore/<skill-name>/SKILL.md` or the
relevant subdirectory. Use the path table below as a quick reference:

| Skill Name | Path |
|-----------|------|
| mooring-design | `.claude/skills/engineering/marine-offshore/mooring-design/` |
| orcaflex-mooring-iteration | `.claude/skills/engineering/marine-offshore/orcaflex-mooring-iteration/` |
| hydrodynamics | `.claude/skills/engineering/marine-offshore/hydrodynamics/` |
| fatigue-analysis | `.claude/skills/engineering/marine-offshore/fatigue-analysis/` |
| signal-analysis | `.claude/skills/engineering/marine-offshore/signal-analysis/` |
| orcaflex-post-processing | `.claude/skills/engineering/marine-offshore/orcaflex-post-processing/` |
| catenary-riser | `.claude/skills/engineering/marine-offshore/catenary-riser/` |
| viv-analysis | `.claude/skills/engineering/marine-offshore/viv-analysis/` |
| structural-analysis | `.claude/skills/engineering/marine-offshore/structural-analysis/` |
| diffraction-analysis | `.claude/skills/engineering/marine-offshore/diffraction-analysis/` |
| orcawave-analysis | `.claude/skills/engineering/marine-offshore/orcawave-analysis/` |
| orcaflex-modeling | `.claude/skills/engineering/marine-offshore/orcaflex-modeling/` |
| orcaflex-code-check | `.claude/skills/engineering/marine-offshore/orcaflex-code-check/` |
| cathodic-protection | `.claude/skills/engineering/marine-offshore/cathodic-protection/` |
| api12-drilling-analyzer | `.claude/skills/data/energy/api12-drilling-analyzer/` |
| fdas-economics | `.claude/skills/data/energy/fdas-economics/` |
| field-analyzer | `.claude/skills/data/energy/field-analyzer/` |

If a skill path does not resolve to an existing SKILL.md, note it as
"skill not found" in the output — do not raise an error.

### Step 5 — Discover Memory and Spec Files

**Memory files**: Scan `.claude/memory/` for files whose name or first heading
matches any resolved domain keyword (mooring, fatigue, riser, hull, pipeline,
structural, cathodic, drilling, economics). List any matches.

**Spec files**: Scan `specs/` for files whose name or first heading matches
the WRK item's `module:` field or `tags:`. List the top 3 most-recently-modified
matches. If `spec_ref:` is set in the WRK frontmatter, always include that file
regardless of age.

### Step 6 — Output Focused Context

Print the context block in this format:

```
## Engineering Context — <WRK-ID>: <WRK title>

**Detected domain(s):** <comma-separated domains>
**Tags matched:** <list of matched tags from WRK>

### Skills to Load (read these SKILL.md files)
- <skill-name>: <path/to/SKILL.md>
- ...

### Design Codes in Scope
- <CODE-REF>: <short description>
- ...

### Memory Files to Read
- <path> — <reason / matched keyword>
- (none detected)

### Spec Files to Read First
- <path> — <matched field>
- (none detected)

### Notes
- <any multi-domain overlaps, missing skills, or warnings>
```

## Output Example

```
## Engineering Context — WRK-175: Mooring Fatigue Study

**Detected domain(s):** mooring, fatigue
**Tags matched:** mooring, fatigue, naval-architecture

### Skills to Load (read these SKILL.md files)
- mooring-design: .claude/skills/engineering/marine-offshore/mooring-design/SKILL.md
- orcaflex-mooring-iteration: .../orcaflex-mooring-iteration/SKILL.md
- hydrodynamics: .../hydrodynamics/SKILL.md
- fatigue-analysis: .../fatigue-analysis/SKILL.md
- signal-analysis: .../signal-analysis/SKILL.md
- orcaflex-post-processing: .../orcaflex-post-processing/SKILL.md

### Design Codes in Scope
- API RP 2SK: Mooring design for floating structures
- DNV-OS-E301: Offshore mooring chain and components
- DNV-RP-C203: Fatigue design of offshore steel structures
- BS 7608: Fatigue design and assessment of steel structures

### Memory Files to Read
- .claude/memory/orcaflex.md — matched keyword: mooring / fatigue

### Spec Files to Read First
- specs/modules/mooring-fatigue/WRK-175-spec.md — spec_ref match

### Notes
- Domains mooring + fatigue share orcaflex-post-processing — loaded once.
```

## Integration

This skill complements `/session-start`. Typical invocation sequence:

1. `/session-start` → surfaces top unblocked WRK items
2. `/engineering-context-loader` → narrows to domain-relevant skills
3. Read each listed SKILL.md before beginning implementation

## Error Cases

| Situation | Behavior |
|-----------|----------|
| No `tags:` in WRK frontmatter | Warn and return full catalog hint |
| Tags present but no domain match | List unmatched tags; no skill subset emitted |
| WRK file not found at any path | Ask user to provide WRK ID or file path |
| Skill path does not exist on disk | Note as "skill not found — may be planned" |
| Multiple domains detected | Output union of all matched skills + codes |
