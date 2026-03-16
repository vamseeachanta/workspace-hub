---
name: engineering-context-loader-step-1-resolve-the-active-wrk-item
description: "Sub-skill of engineering-context-loader: Step 1 \u2014 Resolve the Active\
  \ WRK Item (+5)."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 1 — Resolve the Active WRK Item (+5)

## Step 1 — Resolve the Active WRK Item


Look for the active WRK item in this priority order:

1. `.claude/state/active-wrk` — if file exists and is non-empty, read its
   contents for the WRK ID (e.g. `WRK-175`)
2. Most recently modified file in `.claude/work-queue/working/`
3. Current git branch name (e.g. `feature/WRK-175-...` → extract `WRK-175`)
4. Ask the user: "Which WRK item should I load context for?"

Once the WRK ID is known, read the file at:
`.claude/work-queue/pending/<WRK-ID>.md` or
`.claude/work-queue/working/<WRK-ID>.md`


## Step 2 — Extract Tags


Read the YAML frontmatter of the WRK file. Extract the `tags:` list.
Also check the `module:` field for supplementary domain hints.

If no tags are found or none match the domain map, output:
> "No engineering domain tags detected in <WRK-ID>. Returning full skill catalog."
Then stop — do not proceed with domain filtering.


## Step 3 — Map Tags to Domain(s)


Apply the domain map table above. A single WRK item may match multiple domains
(e.g. `mooring` + `fatigue` is common for mooring fatigue studies).

Collect the union of all matched entries:
- All matched skill names (deduplicated)
- All matched design codes (deduplicated)


## Step 4 — Resolve Skill Paths


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


## Step 5 — Discover Memory and Spec Files


**Memory files**: Scan `.claude/memory/` for files whose name or first heading
matches any resolved domain keyword (mooring, fatigue, riser, hull, pipeline,
structural, cathodic, drilling, economics). List any matches.

**Spec files**: Scan `specs/` for files whose name or first heading matches
the WRK item's `module:` field or `tags:`. List the top 3 most-recently-modified
matches. If `spec_ref:` is set in the WRK frontmatter, always include that file
regardless of age.


## Step 6 — Output Focused Context


Print the context block in this format:

```
