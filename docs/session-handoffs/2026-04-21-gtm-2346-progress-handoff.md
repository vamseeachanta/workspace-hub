# Session Hand-off — GTM #2346 Progress (2026-04-21)

Copy the block below into the next session's opening prompt.

---

## Hand-off prompt (paste-ready)

We are resuming the GTM implementation stream, focused on **#2346** after the #2357 plan-review loop stalled on repeated Codex MAJOR findings. Do not resume #2357 first unless the explicit goal is another plan-revision cycle.

### What landed this session for #2346 (workspace-hub)

All of the following are already on `origin/main` and should be treated as landed state:

1. **Canonical vessel 2** — pipelay barge
   - Commit: `ab90c5428`
   - File: `docs/gtm/intake/canonical-vessels/pipelay-barge.yaml`
   - Adds Lorelay-class S-lay canonical fallback.

2. **demo_04 materialization**
   - Commit: `c966bebb4`
   - Files:
     - `scripts/gtm/prospect_adapter.py`
     - `scripts/gtm/tests/test_prospect_adapter.py`
     - `docs/gtm/intake/IMPLEMENTATION-STATUS.md`
   - `materialize_demo_inputs()` now supports **demo_04** and writes:
     - `tmpdir/data/pipelay_vessels.json`
     - `tmpdir/data/pipelines.json`
     - optional `tmpdir/data/prospect_env.json`
   - Added guard so `demo_04` cannot silently accept a wrong-shape canonical ref (e.g. `seven-borealis`).

3. **Canonical vessel 3** — PLSV
   - Commit: `eadd77e5b`
   - File: `docs/gtm/intake/canonical-vessels/plsv.yaml`
   - Completes the canonical vessel trio.

4. **demo_05 materialization**
   - Commit: `050668522`
   - Files:
     - `scripts/gtm/prospect_adapter.py`
     - `scripts/gtm/tests/test_prospect_adapter.py`
     - `docs/gtm/intake/IMPLEMENTATION-STATUS.md`
   - `materialize_demo_inputs()` now supports **demo_05** and writes:
     - `tmpdir/data/csv_hlv_vessels.json`
     - `tmpdir/data/rigid_jumpers.json`
     - optional `tmpdir/data/prospect_env.json`
   - Supports both csv_hlv-shaped canonical refs:
     - `seven-borealis`
     - `plsv`

### Current test state

Latest verified command:
- `uv run pytest scripts/gtm/tests/test_prospect_adapter.py -q`
- Result at session end: **13 passed**

This covers:
- demo_05 canonical Seven Borealis validation
- demo_05 canonical PLSV validation
- demo_04 canonical pipelay-barge validation
- wrong-shape canonical-ref rejection
- malformed YAML rejection
- Q6 vessel-presence/absence constraints
- demo_04 materialization
- demo_05 materialization
- remaining unimplemented paths still explicitly stubbed

### Current #2346 state

`docs/gtm/intake/IMPLEMENTATION-STATUS.md` is the authoritative tracker.

What is now done in workspace-hub:
- `prospect-schema.json`
- `prospect-template.yaml`
- intake README
- canonical vessels:
  - `seven-borealis.yaml`
  - `pipelay-barge.yaml`
  - `plsv.yaml`
- `load_and_validate()`
- partial `materialize_demo_inputs()` for:
  - demo_04
  - demo_05
- 13 passing tests for the current adapter surface

### Best next bounded slice

**Recommended next step: implement demo_03 materialization** in `scripts/gtm/prospect_adapter.py` with TDD first.

Target behavior:
- `materialize_demo_inputs()` supports **demo_03** and writes:
  - `tmpdir/data/csv_hlv_vessels.json`
  - `tmpdir/data/mudmat_structures.json`
  - optional `tmpdir/data/prospect_env.json`

Suggested RED tests to add first in `scripts/gtm/tests/test_prospect_adapter.py`:
- `test_materialize_demo_03_writes_csv_hlv_and_mudmat_files`
- `test_materialize_demo_03_accepts_canonical_plsv_or_seven_borealis_if_shape_is_csv_hlv` (or choose one canonical fixture and keep scope tight)
- keep a stub test proving unimplemented paths still raise for demos not yet supported

### After demo_03 materialization

Then move in this order:
1. `run_demo()` subprocess dispatch in workspace-hub
2. cross-repo `digitalmodel/` CLI flags (`--prospect-data-dir`, `--prospect-env`, etc.)
3. branded report wrapper
4. dual-delivery state machine
5. SOP / fallback sidecar / E2E work

### Important boundaries

1. **Do not treat #2346 as done.**
   `docs/gtm/intake/IMPLEMENTATION-STATUS.md` still has a substantial "Not done" section.

2. **Do not switch back to #2357 by default.**
   The #2357 plan exists locally and has many review artifacts, but repeated Codex MAJOR findings still blocked approval readiness at session end.

3. **Do not touch #2348 unless explicitly requested.**
   Earlier in the session there was already an active overnight Claude worker on #2348.

### Useful files

- Plan: `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md`
- Status tracker: `docs/gtm/intake/IMPLEMENTATION-STATUS.md`
- Adapter: `scripts/gtm/prospect_adapter.py`
- Tests: `scripts/gtm/tests/test_prospect_adapter.py`
- Canonical vessel dir: `docs/gtm/intake/canonical-vessels/`
- This handoff: `docs/session-handoffs/2026-04-21-gtm-2346-progress-handoff.md`

### First commands for next session

```bash
cd /mnt/local-analysis/workspace-hub
git status
git log --oneline -8 -- scripts/gtm/prospect_adapter.py scripts/gtm/tests/test_prospect_adapter.py docs/gtm/intake/IMPLEMENTATION-STATUS.md docs/gtm/intake/canonical-vessels/
uv run pytest scripts/gtm/tests/test_prospect_adapter.py -q
```

Then start the next TDD loop for demo_03 materialization.

---

**End hand-off prompt.**
