# Next-Wave Handoff — #2560 Evidence Fill for #2554 Contractor Matrix

- **Date:** 2026-04-30
- **Parent:** #2554 — vessel-contractor outreach matrix
- **GTM command center:** #2016
- **Downstream dependency:** #2556 remains blocked until #2554 clears evidence/re-review or the owner explicitly waives the gap.
- **Current blocker:** high-priority contractor rows still use scaffold placeholders for `deep_link_evidence` and `pain_point_evidence`.

## Objective

Fill public, official-domain evidence for the 12 High-priority vessel-contractor rows in:

`docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`

Then rerun review for #2554. Do **not** send outreach, add personal contacts, or mutate #2556 send mechanics in this lane.

## Target rows

1. Subsea7
2. TechnipFMC
3. Saipem
4. McDermott
5. Allseas
6. Heerema
7. Boskalis
8. DOF Group
9. Sapura Energy
10. Helix
11. Hornbeck Offshore Services
12. Edison Chouest Offshore

## Evidence requirements per row

For each target, replace placeholders with either evidence or explicit boundary text:

- `corporate_root_evidence`: keep official corporate root if valid.
- `deep_link_evidence`: official-domain fleet/project/vessel/service subpage(s), with enough description that a reviewer can see why it supports the target fit.
- `pain_point_evidence`: public proof supporting the outreach hook, or exact boundary `no-public-proof-found — retain hypothesis as internal only`.

Do not invent project facts. Do not use LinkedIn/private-contact data. Do not include individual names, emails, or phone numbers in public artifacts.

## Search protocol

For each company:

1. Start at official corporate site and fleet/project/service pages.
2. Prefer official fleet/vessel/project pages over third-party vessel databases.
3. If official deep links are unavailable, use an explicit `no-public-proof-found` boundary instead of weak third-party inference.
4. Record URL + short support statement inline in the row.
5. Update summary counts in #2554 scaffold and plan if row status changes.

Suggested query patterns:

```text
site:<official-domain> fleet vessel offshore construction pipelay heavy lift subsea installation
site:<official-domain> projects offshore installation subsea Gulf of Mexico
site:<official-domain> vessel fleet CSV pipelay crane construction support
```

## Acceptance criteria

- [ ] All 12 High-priority rows have verified official deep-link evidence or explicit `no-public-proof-found` boundary.
- [ ] All 12 High-priority rows have non-inferred public pain-point evidence or explicit boundary text.
- [ ] No individual contact details are added to public repo artifacts.
- [ ] #2554 matrix summary counts and blocker text are updated.
- [ ] At least one live adversarial re-review of #2554 is run after evidence fill.
- [ ] #2554 is promoted only if no `MAJOR` remains.

## Allowed paths

- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- `scripts/review/results/2026-04-30-plan-2554-*.md`
- optional: `docs/plans/overnight-prompts/2026-04-30-2560-evidence-fill-results.md`

## Forbidden paths / boundaries

- Do not edit #2555 chart renderer/assets.
- Do not edit #2556 brochure/send tracker except to note it remains blocked.
- Do not send external outreach.
- Do not add private routing details or personal contact information.
- Do not claim named-vessel/client project validation unless the evidence is public and official.

## Recommended next command sequence

```bash
# 1) inspect current high-priority rows
uv run python - <<'PY'
from pathlib import Path
p = Path('docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md')
text = p.read_text()
for block in text.split('\n### Target ')[1:]:
    head = block.split('\n', 1)[0]
    if '**High**' in block:
        print('Target ' + head)
PY

# 2) fill official evidence row-by-row, preserving anti-fabrication boundaries
# 3) run targeted placeholder scan
uv run python - <<'PY'
from pathlib import Path
p = Path('docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md')
text = p.read_text()
missing = []
for block in text.split('\n### Target ')[1:]:
    head = block.split('\n', 1)[0]
    if '**High**' in block and ('PENDING' in block or 'inferred-from-demo-coverage' in block):
        missing.append(head)
print('\n'.join(missing) or 'all high-priority rows filled/bounded')
PY

# 4) rerun legal scan and at least one live review before promotion
scripts/legal/legal-sanity-scan.sh --diff-only
```

## Exit condition for next worker

If evidence fill cannot be completed for all 12 targets in one lane, stop with a results file listing:

- rows completed,
- rows explicitly bounded,
- rows still pending,
- URLs checked,
- whether #2554 can be re-reviewed or must remain blocked.
