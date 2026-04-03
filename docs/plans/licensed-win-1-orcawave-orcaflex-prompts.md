# Licensed-Win-1 Execution Prompts — OrcaWave / OrcaFlex

Generated: 2026-04-02
Machine: licensed-win-1 (Windows, OrcaFlex + ANSYS licenses, Git Bash / MINGW64)
Workspace: D:\workspace-hub
Traceability: docs/reports/digitalmodel-orcawave-orcaflex-issue-reconciliation.md

## Prerequisites (run once before starting any prompt)

```
cd D:\workspace-hub
git pull origin main
pip install OrcFxAPI   # if not already installed
pip install pyyaml openpyxl   # support deps
```

Verify OrcFxAPI is working:
```
python -c "import OrcFxAPI; print(OrcFxAPI.version())"
```

---

## PROMPT 1: Validate solver queue and run WAMIT validation batch (#1586)

Priority: HIGH — unblocks all downstream pipeline work.
Estimated time: 30-60 minutes (mostly solver runtime).
Dependencies: none.

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. Use python (not uv run) for commands.
OrcFxAPI is available. Git Bash is available.

TASK: Validate the solver queue infrastructure and run the WAMIT validation
batch to prove the queue works end-to-end.

STEP 1: Pull latest and verify queue health
  cd D:\workspace-hub
  git pull origin main
  dir queue\pending
  dir queue\completed
  dir queue\failed

STEP 2: Run the queue processor directly to prove it works
  python scripts\solver\process-queue.py

  If the queue is empty (no pending jobs), that is expected. Proceed to step 3.

STEP 3: Submit OrcaWave validation jobs via the queue
  Create file: queue\pending\wamit-val-test01.yaml
  Contents:
    solver: orcawave
    input_file: digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.1/OrcaWave v11.0 files/test01.owd
    export_excel: true
    description: "WAMIT validation L00 case 2.1 — unit box"
    submitted_by: licensed-win-1
    submitted_at: 2026-04-02T00:00:00Z

  Then:
    git add queue\pending\wamit-val-test01.yaml
    git commit -m "queue: submit WAMIT validation test01 from licensed-win-1"
    git push origin main

STEP 4: Process the job
    python scripts\solver\process-queue.py

STEP 5: Verify results
  - Check queue\completed\ for the job directory
  - Check that result.yaml shows status: completed
  - Check that .owr file exists
  - Check that .xlsx file exists (if export_excel worked)

STEP 6: If step 4 succeeds, submit 2 more validation cases:
  Create queue\pending\wamit-val-hemisphere.yaml:
    solver: orcawave
    input_file: digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.4/OrcaWave v11.0 files/Hemisphere.owd
    export_excel: true
    description: "WAMIT validation L00 case 2.4 — hemisphere"
    submitted_by: licensed-win-1
    submitted_at: 2026-04-02T00:00:00Z

  Create queue\pending\wamit-val-ellipsoid.yaml:
    solver: orcawave
    input_file: digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.8/OrcaWave v11.0 files/Ellipsoid.owd
    export_excel: true
    description: "WAMIT validation L00 case 2.8 — ellipsoid"
    submitted_by: licensed-win-1
    submitted_at: 2026-04-02T00:00:00Z

  git add queue\pending\
  git commit -m "queue: submit WAMIT validation hemisphere + ellipsoid"
  git push origin main
  python scripts\solver\process-queue.py

STEP 7: Document results
  After all jobs complete, comment on GitHub issue #1586:
    gh issue comment 1586 --body "Queue validation from licensed-win-1: N jobs submitted and processed. Results in queue/completed/. .owr and .xlsx artifacts generated."

COMPLETION CRITERIA:
- At least 1 OrcaWave job processed successfully through the queue
- result.yaml shows status: completed with elapsed_seconds
- .owr output file exists and is non-empty
- git commit + push of results succeeded
```

---

## PROMPT 2: Generate minimal OrcaFlex .sim fixture for test evidence (#1652)

Priority: HIGH — provides fixture for dev-primary snapshot testing.
Estimated time: 15-30 minutes.
Dependencies: none.

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. OrcFxAPI is available.

TASK: Create a minimal OrcaFlex .sim fixture file that can be committed
to the repo for use in integration tests on dev-primary.

REQUIREMENTS:
- File must be < 1 MB
- Must NOT contain any proprietary client data
- Must exercise: vessel + 1 mooring line + environment
- Must complete statics + short dynamics (10 seconds simulation)

STEP 1: Create the model programmatically
  Create file: scripts\solver\generate_minimal_sim_fixture.py

  Contents (adapt as needed):
    import OrcFxAPI
    model = OrcFxAPI.Model()

    # Environment
    env = model.environment
    env.WaterDepth = 100.0
    env.WaveType = "Dean stream"
    env.WaveHeight = 2.0
    env.WavePeriod = 8.0

    # General settings — short simulation
    general = model.general
    general.StageDuration[0] = 5.0    # build-up
    general.StageDuration[1] = 10.0   # simulation

    # Vessel
    vessel = model.CreateObject(OrcFxAPI.ObjectType.Vessel)
    vessel.Name = "TestVessel"
    vessel.Length = 50.0
    vessel.InitialX = 0.0
    vessel.InitialY = 0.0
    vessel.InitialZ = 0.0
    vessel.InitialHeading = 0.0

    # Line (mooring)
    line = model.CreateObject(OrcFxAPI.ObjectType.Line)
    line.Name = "MooringLine1"
    line.EndAConnection = "TestVessel"
    line.EndAX = 25.0
    line.EndAY = 0.0
    line.EndAZ = -5.0
    line.EndBConnection = "Anchored"
    line.EndBX = 200.0
    line.EndBY = 0.0
    line.EndBZ = -100.0
    line.Length[0] = 250.0
    line.NumberOfSections = 1

    # Run
    model.CalculateStatics()
    model.RunSimulation()

    # Save
    output_path = r"digitalmodel\tests\fixtures\minimal_test.sim"
    model.SaveSimulation(output_path)
    print(f"Saved: {output_path}")

    # Also save the .dat for reference
    dat_path = r"digitalmodel\tests\fixtures\minimal_test.dat"
    model.SaveData(dat_path)
    print(f"Saved: {dat_path}")

STEP 2: Run the script
    mkdir digitalmodel\tests\fixtures 2>nul
    python scripts\solver\generate_minimal_sim_fixture.py

  If OrcFxAPI raises errors about line type or vessel type setup,
  adapt the model creation code to satisfy the minimum valid configuration.
  The goal is the smallest possible valid .sim file.

STEP 3: Verify the fixture
    python -c "import OrcFxAPI; m=OrcFxAPI.Model(r'digitalmodel\tests\fixtures\minimal_test.sim'); print('Objects:', m.objectCount); print('State:', m.state)"

STEP 4: Check file size
    dir digitalmodel\tests\fixtures\minimal_test.sim

  If > 1 MB, reduce simulation duration or remove unnecessary objects.

STEP 5: Commit and push
    git add digitalmodel\tests\fixtures\minimal_test.sim
    git add digitalmodel\tests\fixtures\minimal_test.dat
    git add scripts\solver\generate_minimal_sim_fixture.py
    git commit -m "feat(orcaflex): add minimal .sim fixture for integration tests (#1652)"
    git push origin main

STEP 6: Comment on issue
    gh issue comment 1652 --body "Minimal .sim fixture generated on licensed-win-1 and committed. File: digitalmodel/tests/fixtures/minimal_test.sim. Contains: 1 vessel + 1 mooring line, 10s simulation. Ready for dev-primary snapshot testing."

COMPLETION CRITERIA:
- digitalmodel/tests/fixtures/minimal_test.sim exists and is < 1 MB
- File loads successfully in OrcFxAPI
- File is committed and pushed to main
```

---

## PROMPT 3: Generate OrcaWave .owr result fixture for RAO extraction (#1597)

Priority: HIGH — provides real .owr data for RAO extractor development on dev-primary.
Estimated time: 15-30 minutes.
Dependencies: Prompt 1 should succeed first (proves queue works).

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. OrcFxAPI is available.

TASK: Run OrcaWave on a simple test case and commit the .owr result file
as a fixture for RAO extraction development on dev-primary.

STEP 1: Run OrcaWave on the L00 test01 case directly (not through queue)
    python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadData(r'digitalmodel\docs\domains\orcawave\L00_validation_wamit\2.1\OrcaWave v11.0 files\test01.owd')
d.Calculate()
d.SaveResults(r'digitalmodel\tests\fixtures\test01_unit_box.owr')
print('Done — saved test01_unit_box.owr')
print('Frequencies:', d.frequencyCount)
print('Headings:', d.headingCount)
"

STEP 2: Extract basic RAO data to prove the .owr is readable
    python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadResults(r'digitalmodel\tests\fixtures\test01_unit_box.owr')
print('Frequency count:', d.frequencyCount)
print('Heading count:', d.headingCount)
print('Body count:', d.bodyCount)
for i in range(min(3, d.frequencyCount)):
    print(f'  freq[{i}] = {d.frequency(i):.4f} rad/s')
for i in range(min(3, d.headingCount)):
    print(f'  heading[{i}] = {d.heading(i):.1f} deg')
"

STEP 3: Also run the hemisphere case for a second fixture
    python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadData(r'digitalmodel\docs\domains\orcawave\L00_validation_wamit\2.4\OrcaWave v11.0 files\Hemisphere.owd')
d.Calculate()
d.SaveResults(r'digitalmodel\tests\fixtures\hemisphere.owr')
print('Done — saved hemisphere.owr')
print('Frequencies:', d.frequencyCount)
"

STEP 4: Verify file sizes
    dir digitalmodel\tests\fixtures\*.owr

  Both files should be < 5 MB each. If larger, they are still committable
  but note the size in the commit message.

STEP 5: Commit and push
    git add digitalmodel\tests\fixtures\test01_unit_box.owr
    git add digitalmodel\tests\fixtures\hemisphere.owr
    git commit -m "feat(orcawave): add .owr result fixtures for RAO extraction (#1597)"
    git push origin main

STEP 6: Comment on issue
    gh issue comment 1597 --body "Two .owr fixtures generated on licensed-win-1 and committed: test01_unit_box.owr (L00 case 2.1) and hemisphere.owr (L00 case 2.4). Ready for RAO extractor development on dev-primary."

COMPLETION CRITERIA:
- Two .owr files committed to digitalmodel/tests/fixtures/
- Both files load successfully with OrcFxAPI.Diffraction().LoadResults()
- Frequency, heading, and body counts are non-zero
- Files pushed to main
```

---

## PROMPT 4: Run OrcaFlex mooring model for handoff validation fixture (#1605)

Priority: MEDIUM — provides cross-tool integration evidence.
Estimated time: 15-30 minutes.
Dependencies: Prompt 2 (proves OrcaFlex execution works).

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. OrcFxAPI is available.

TASK: Run an existing OrcaFlex mooring model to produce a .sim result file
that demonstrates the OrcaWave-to-OrcaFlex import path works.

STEP 1: Find a suitable existing .dat model with RAO/vessel data
    dir /s /b digitalmodel\docs\domains\orcaflex\mooring\*.dat

  Pick the simplest model that includes a vessel with imported RAOs.
  Good candidates: simplified RAOs.dat, or any model in the mooring_fender directory.

STEP 2: Load, run, and save
    python -c "
import OrcFxAPI
import sys

model_path = r'digitalmodel\docs\domains\orcaflex\mooring_fender\simple1\simplified RAOs.dat'
model = OrcFxAPI.Model(model_path)
print('Objects:', model.objectCount)

# Reduce simulation time for speed
general = model.general
general.StageDuration[1] = 30.0  # 30 seconds instead of full sim
model.CalculateStatics()
model.RunSimulation()
model.SaveSimulation(r'digitalmodel\tests\fixtures\mooring_with_raos.sim')
print('Saved: mooring_with_raos.sim')
"

  If the chosen model fails (missing files, too complex), try another .dat.

STEP 3: Verify
    python -c "
import OrcFxAPI
m = OrcFxAPI.Model(r'digitalmodel\tests\fixtures\mooring_with_raos.sim')
print('Objects:', m.objectCount)
print('State:', m.state)
for obj in m.objects:
    print(f'  {obj.type}: {obj.name}')
"

STEP 4: Commit and push
    git add digitalmodel\tests\fixtures\mooring_with_raos.sim
    git commit -m "feat(orcaflex): add mooring .sim fixture with RAO vessel (#1605)"
    git push origin main

STEP 5: Comment on issue
    gh issue comment 1605 --body "Mooring .sim fixture with RAO-imported vessel generated on licensed-win-1 and committed. File: digitalmodel/tests/fixtures/mooring_with_raos.sim. Ready for handoff validation development on dev-primary."

COMPLETION CRITERIA:
- .sim file committed with a vessel that has imported RAO data
- File loads and shows vessel + line objects
- Pushed to main
```

---

## Execution order summary

Run these in order on licensed-win-1:

1. PROMPT 1 (#1586) — queue validation, proves infrastructure works
2. PROMPT 2 (#1652) — minimal OrcaFlex .sim fixture
3. PROMPT 3 (#1597) — OrcaWave .owr result fixtures
4. PROMPT 4 (#1605) — OrcaFlex mooring model with RAO vessel

After all 4 complete, dev-primary can:
- Run snapshot tests against the .sim fixture
- Build the RAO extractor against real .owr data
- Develop handoff validation against the mooring .sim
- Close or narrow #1586, advance #1652, #1597, #1605

## Machine notes

- licensed-win-1 workspace: D:\workspace-hub
- No SSH — physical or GUI access only
- Git Bash (MINGW64) available for shell commands
- Use `python` not `uv run` (Windows, no uv expected)
- Agent CLIs available: claude, codex, gemini
- Always git pull before starting work
- Always git push after completing work
