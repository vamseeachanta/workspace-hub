We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2056 — Session Governance Phase 2 (Runtime Hook Enforcement)
Status: Implementation ~90% complete. One threshold regression bug remains.

Context:
- `scripts/workflow/governance-checkpoints.yaml` currently has `threshold: 5000` for the tool-call ceiling, but the intended/documented ceiling is 200.
- `.claude/hooks/session-governor-check.sh` has partial fast-path coverage, but the YAML regression leaves the governor-level ceiling ineffective.
- `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` has stale default text.

Tasks:
1. Fix `scripts/workflow/governance-checkpoints.yaml`: change the tool-call threshold from 5000 to 200.
2. Update `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` to reflect the 200-call ceiling and reference the governor check hook.
3. Add an integration test reading the production YAML and asserting the tool-call threshold is 200.
   - Path: `tests/governance/test_checkpoints_yaml.py`
   - Create `tests/governance/__init__.py` only if needed.
4. Run verification:
   - `grep 'threshold:' scripts/workflow/governance-checkpoints.yaml`
   - `uv run pytest tests/governance/test_checkpoints_yaml.py -v`
5. Post a GitHub issue comment on #2056 summarizing bug found, fix applied, test added.

Allowed write paths:
- `scripts/workflow/governance-checkpoints.yaml`
- `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`
- `tests/governance/test_checkpoints_yaml.py`
- `tests/governance/__init__.py`

Negative write boundaries:
- `.claude/hooks/session-governor-check.sh`
- `.claude/hooks/error-loop-tracker.sh`
- `.claude/settings.json`
- any file under `digitalmodel/`
- any file under `worldenergydata/`

Cross-review: not required.

End state:
- the YAML threshold is 200
- the new integration test passes
- a GitHub issue comment is posted
