---
name: resource-intelligence-step-by-step-for-authors
description: 'Sub-skill of resource-intelligence: Step-by-Step for Authors (+2).'
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step-by-Step for Authors (+2)

## Step-by-Step for Authors


1. **Scaffold**: `bash .claude/skills/workspace-hub/resource-intelligence/scripts/init-resource-pack.sh WRK-NNN`
2. **Mine**: follow the Resource Mining Checklist and Category→Mining Map for `target_repos`
3. **Fill artifacts**: `resource-pack.md`, `sources.md`, `resources.yaml`, `resource-intelligence-summary.md`, `constraints.md`, `domain-notes.md`, `open-questions.md`
4. **Fill gate artifact**: `evidence/resource-intelligence.yaml` with `skills.core_used ≥3`, `completion_status`, `top_p1_gaps`
5. **Validate**: `bash .claude/skills/workspace-hub/resource-intelligence/scripts/validate-resource-pack.sh WRK-NNN` — must exit 0
6. **Record quality**: populate `quality_signals` block in `evidence/resource-intelligence.yaml`


## Confidence Derivation Rule


`confidence = high` iff ALL of:

- `missing_artifact_rate == 0.0` (all required artifacts present)
- `top_p1_gaps` is empty **or** ≥1 P1 gap was resolved and documented
- Provenance complete — every `resources.yaml` source has `retrieval_date` and `canonical_storage_path`

Set `confidence: medium` when one of those conditions is not met; `confidence: low` when two or more are not met.


## Measurable Quality Signals


| Signal | Good | Needs work |
|--------|------|------------|
| `missing_artifact_rate` | 0.0 | > 0.0 |
| `plan_edits_required` | 0–1 | ≥ 3 |
| `confidence` | `high` | `medium` or `low` |

See `evidence/ri-comparison-examples.md` for before/after WRK pairs with rubric.

---
