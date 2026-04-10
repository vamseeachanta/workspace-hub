We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2062 — Drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)
Status: Ready only after the operator refines the issue title/body to the realistic v1 scope, completes human review, and labels the issue status:plan-approved.

Hard gate before any implementation write:
- Read CLAUDE.md and AGENTS.md planning rules first.
- Verify issue #2062 is already status:plan-approved by a human and the issue body reflects the ~138-rig v1 scope rather than “2,210 rigs into hull form validation”.
- Do NOT self-approve, do NOT create approval markers, and do NOT edit GitHub labels.
- If the issue is not refined/approved, stop immediately and return a blocked summary with zero implementation writes.

Implementation scope reminder:
- v1 targets drillships and semi-submersibles with LOA+BEAM data (~138 rigs)
- jack-ups remain mapped for coefficient defaults but are expected to skip registration because the CSV lacks geometry
- all heuristic drafts must be flagged draft_estimated=True

Tasks:
1. Read current state:
   - CLAUDE.md lines 8-12
   - AGENTS.md lines 5-8
   - digitalmodel/src/digitalmodel/naval_architecture/hull_form.py
   - digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
   - digitalmodel/tests/naval_architecture/test_hull_form.py
   - digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
   - worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv
2. Follow TDD first.
3. Add tests in digitalmodel/tests/naval_architecture/test_hull_form.py for rig coefficient estimation:
   - drillship coefficient range
   - semi_submersible coefficient range
   - jack_up coefficient range
   - Cp identity equals Cb / Cm
   - unknown rig type raises ValueError
4. Add tests in digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py for:
   - register drillship with estimated draft
   - register semi-submersible with estimated draft
   - skip records missing LOA/BEAM
   - rig_type to hull_form mapping
   - smoke registration counts from representative records or CSV-backed subset
5. Implement digitalmodel/src/digitalmodel/naval_architecture/hull_form.py:
   - add default rig coefficient mapping for drillship, semi_submersible, jack_up
   - add estimate_rig_hull_coefficients(rig_type: str) -> dict with cb, cm, cp, hull_form
6. Implement digitalmodel/src/digitalmodel/naval_architecture/ship_data.py:
   - add _RIG_TYPE_HULL_FORM_MAP
   - add _estimate_draft(record: dict, rig_type: str) -> Optional[float]
   - add register_drilling_rigs(records, *, overwrite=False) -> tuple[int, int]
   - estimate drafts with hull-specific heuristics and set draft_estimated=True when synthetic
   - skip records without sufficient geometry instead of inventing unsupported values
7. Update digitalmodel/src/digitalmodel/naval_architecture/__init__.py exports for the new rig adapter functions.
8. Run verification:
   - cd digitalmodel && PYTHONPATH=src uv run python -m pytest tests/naval_architecture/test_hull_form.py tests/naval_architecture/test_vessel_fleet_adapter.py -v
   - run a CSV-backed smoke check that reports added/skipped counts and confirms the realistic v1 throughput is in the expected ~138 / ~2072 range
9. Post a gh issue comment on #2062 summarizing implementation, the heuristic-draft assumption, and the actual added/skipped counts observed.
10. Request Codex cross-review on the changed files after implementation.

Allowed write paths:
- digitalmodel/src/digitalmodel/naval_architecture/hull_form.py
- digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
- digitalmodel/src/digitalmodel/naval_architecture/__init__.py
- digitalmodel/tests/naval_architecture/test_hull_form.py
- digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT touch:
  - digitalmodel/src/digitalmodel/field_development/
  - digitalmodel/src/digitalmodel/drilling_riser/
  - digitalmodel/tests/field_development/
  - worldenergydata/ except read-only access to drilling_rigs.csv
  - docs/
  - scripts/
  - .claude/
  - .planning/
  - any Git metadata or labels

Verification:
- cd /mnt/local-analysis/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -m pytest tests/naval_architecture/test_hull_form.py tests/naval_architecture/test_vessel_fleet_adapter.py -v
- cd /mnt/local-analysis/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -c "from digitalmodel.naval_architecture import register_drilling_rigs, estimate_rig_hull_coefficients; print('rig adapter imports OK')"
- cd /mnt/local-analysis/workspace-hub/digitalmodel && PYTHONPATH=src uv run python -c "import csv; from digitalmodel.naval_architecture.ship_data import register_drilling_rigs; from pathlib import Path; p = Path('../worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv'); rows = list(csv.DictReader(p.open())); added, skipped = register_drilling_rigs(rows); print({'rows': len(rows), 'added': added, 'skipped': skipped})"
- gh issue view 2062 --repo vamseeachanta/workspace-hub --json title,body,comments --jq '{title: .title, body: .body, last_comment: .comments[-1].body}'
