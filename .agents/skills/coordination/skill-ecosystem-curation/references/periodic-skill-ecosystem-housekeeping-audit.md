# Archived Skill: `periodic-skill-ecosystem-housekeeping-audit`

Original path: `/home/vamsee/.hermes/skills/coordination/periodic-skill-ecosystem-housekeeping-audit`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/periodic-skill-ecosystem-housekeeping-audit`
Consolidation date: 2026-04-29

---

---
name: periodic-skill-ecosystem-housekeeping-audit
version: 1.0.0
category: coordination
description: Maintain a deterministic recurring skill ecosystem housekeeping audit covering skill content quality, grouping/taxonomy drift, size, waivers, baselines, and local-only GitHub payloads.
tags: [skills, audit, housekeeping, taxonomy, scheduled-tasks, github-issues, tdd, adversarial-review]
---

# Periodic Skill Ecosystem Housekeeping Audit

## When to Use

Use this when creating, maintaining, or reviewing a recurring audit for the skill ecosystem, especially when the task is to identify improvement areas in skill content, grouping/category structure, duplicate names, alias drift, oversized skills, missing required sections, or stale/low-quality skill metadata.

This skill complements `coordination/cross-agent-skill-audit`: that skill checks whether skills are visible across Hermes/Claude/Codex/Gemini; this one checks whether the skills themselves are healthy and whether the audit can run safely as housekeeping.

## Core Pattern

1. **Keep the scheduled path singular**
   - Prefer extending the existing scheduled housekeeping/curation job over adding a parallel cron path.
   - In workspace-hub, the recurring path is the skills curation wrapper plus its schedule documentation.
   - The audit should produce deterministic local artifacts; avoid auto-posting to GitHub unless the plan explicitly asks for writeful behavior.

2. **Make the schema append-only and stable**
   - Keep existing finding keys stable across versions.
   - Add new optional sections rather than renaming/removing old ones.
   - Include a policy/version contract in the JSON output.
   - Include source metadata such as `source_id: local-skill-filesystem` so future readers can distinguish local inventory from usage telemetry or remote APIs.

3. **Separate finding families**
   - Content quality: missing required sections, weak metadata, empty/placeholder sections, low-actionability descriptions.
   - Grouping/taxonomy: duplicate leaf names, alias drift, category naming inconsistencies, category collisions.
   - Size/maintainability: oversized `SKILL.md`, too many linked files, excessive category depth, too-large markdown sections.
   - Inventory/accounting: active-vs-archived counts, canonical-vs-mirror paths, tracked-vs-filesystem presence, and untracked active skills.
   - Follow-up candidates: issue-worthy actionable items, not every low-confidence unresolved finding.

4. **Avoid false “skill loss” conclusions**
   - Treat `.claude/skills` as the canonical repo skill tree when `.codex/skills` and `.gemini/skills` are symlink mirrors such as `../.claude/skills`; do not triple-count mirror trees as separate ecosystems.
   - Report total skill files separately from active skill files. A large apparent reduction is often archive filtering, not deletion: compare all `SKILL.md` files against active counts that exclude `/_archive/` and, where applicable, `/_archived/`.
   - Check Git-tracked active path deltas against a baseline ref before claiming loss: `git ls-tree -r --name-only <ref> -- .claude/skills | grep '/SKILL.md$'` with archive filters is enough for a first-pass path-level audit.
   - Normalize path prefixes when comparing tracked paths to filesystem paths; mismatched `.claude/skills/...` versus relative `_archive/...` prefixes can create false missing-skill counts.
   - Distinguish tracked inventory from filesystem inventory. Untracked active skills are not evidence of deletion, but they are loss-risk candidates and should be triaged for commit/archive/delete.

5. **Baseline and waiver all new finding families**
   - Route new v2 findings through the same baseline/waiver path as older findings.
   - Do not keep a parallel unwaived/unbaselined list for new families.
   - Report suppressed findings separately.
   - When upgrading v1 -> v2, allow compatible v1 baseline artifacts if the policy declares append-only compatibility. Otherwise the first v2 run can falsely mark every legacy finding as new.

6. **Make Markdown actionable**
   - Show summary counts for all finding families.
   - In detailed sections, prioritize new/high-confidence/unresolved findings and follow-up candidates.
   - Avoid flooding the Markdown report with low-confidence carry-forward noise.
   - If a local GitHub payload is generated, make it a payload file only; do not post automatically in the audit script.

7. **Use TDD and adversarial review for audit changes**
   - Start with RED tests for the schema and the new finding families.
   - Add regression tests for each adversarial review blocker before fixing it.
   - Run existing v1 tests and cron wrapper tests so a v2 audit does not regress older contracts.

## Regression Tests to Add

For a v2 housekeeping audit, include tests for:

- Stable optional JSON sections even when there are no findings.
- Policy-driven grouping/content/size signals.
- Local-only GitHub payload generation.
- No writeful `.claude/state/skill-usage-report` or equivalent usage telemetry side effects.
- V2 findings are baseline-aware and can be carried forward.
- V2 findings can be waived and appear in `suppressed_findings`.
- Markdown report includes v2 summary counts and actionable v2 sections.
- Inventory records include a stable `source_id`.
- Alias-drift detector avoids false positives when only one canonical spelling exists.
- v1 -> v2 baseline continuity works when append-only compatibility is declared.
- Slash-based alias families such as `business/admin` are not compared against unrelated top-level categories such as `business`.

## Validation Checklist

Before commit/closeout:

```bash
uv run pytest tests/cron/test_skills_curation.py tests/skills/test_weekly_skills_audit.py tests/skills/test_weekly_skills_audit_v2.py -q
uv run --no-project python -m py_compile scripts/skills/weekly_skills_audit.py
uv run --no-project python scripts/cron/validate-schedule.py
bash scripts/cron/skills-curation.sh --dry-run
git diff --check -- config/skills/weekly-audit-policy.yaml docs/ops/scheduled-tasks.md scripts/skills/weekly_skills_audit.py tests/skills/test_weekly_skills_audit_v2.py
```

Also run a manual redirected artifact proof in a temp output directory and verify:

- JSON artifact exists.
- Markdown artifact exists.
- local `github-update-payload.md` exists if requested.
- audit exits with `0 errors`.
- no usage-report/state file is newly dirtied.

## Adversarial Review Prompts

Ask reviewers to specifically look for:

- New findings bypassing baseline or waiver logic.
- Markdown output omitting new finding families.
- Version upgrades breaking carry-forward semantics.
- Alias/grouping detectors mixing slash-family aliases with unrelated top-level categories.
- The audit script accidentally becoming writeful against GitHub or `.claude/state`.

## Commit Hygiene Pitfall

Raw review artifacts often contain trailing whitespace or extra blank lines at EOF. If committing archived adversarial review artifacts under `scripts/review/results/`, normalize them before commit:

```python
from pathlib import Path
for p in Path('scripts/review/results').glob('*code-ISSUE-*.md'):
    lines = p.read_text(encoding='utf-8', errors='replace').splitlines()
    p.write_text('\n'.join(line.rstrip() for line in lines).rstrip() + '\n', encoding='utf-8')
```

Then run:

```bash
git diff --cached --check
```

Keep unrelated provider/state/report dirt unstaged when closing the issue.
