# Licensed-Win-1 Session 2 Prompt

Generated: 2026-04-04
Machine: licensed-win-1 (Windows, D:\workspace-hub)
Available: Claude Code CLI, Codex CLI, Gemini CLI, Python, Git Bash, OrcFxAPI
Traceability: #1789, #1652, #1597, #1787

## Prerequisites

```powershell
cd D:\workspace-hub
git pull origin main
cd digitalmodel
git pull origin main
cd ..
pip install OrcFxAPI pyyaml openpyxl  # if not already installed
```

Verify:
```
python -c "import OrcFxAPI; print(OrcFxAPI.version())"
```

---

## PROMPT 1: Fix hemisphere .gdf and generate fixture (#1789)

Priority: LOW — completes the validation geometry set.
Estimated time: 15-30 minutes.
Dependencies: none.

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. Use python (not uv run). OrcFxAPI is available.

TASK: Fix the missing hemisphere .gdf file and generate the hemisphere.owr fixture.

STEP 1: Check the hemisphere case
  The Hemisphere.yml at:
    digitalmodel\docs\domains\orcawave\L00_validation_wamit\2.4\OrcaWave v11.0 files\Hemisphere.yml
  references BodyMeshFileName: HemisphereAndLid0814.gdf

  Check if the .gdf exists anywhere on this machine:
    dir /s /b D:\*.gdf | findstr /i hemisphere
    dir /s /b "C:\Program Files\Orcina\*hemisphere*"

STEP 2: If the .gdf is found elsewhere, copy it to the OrcaWave case directory:
    copy <found_path> "digitalmodel\docs\domains\orcawave\L00_validation_wamit\2.4\OrcaWave v11.0 files\HemisphereAndLid0814.gdf"

  If the .gdf is NOT found anywhere:
    - Try loading the .owd file instead — it may contain the mesh inline:
      python -c "import OrcFxAPI; d=OrcFxAPI.Diffraction(); d.LoadData(r'digitalmodel\docs\domains\orcawave\L00_validation_wamit\2.4\OrcaWave v11.0 files\Hemisphere.owd'); print('Loaded OK')"
    - If that also fails, skip to PROMPT 2 and note in the issue comment.

STEP 3: Run the OrcaWave calculation
    python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadData(r'digitalmodel\docs\domains\orcawave\L00_validation_wamit\2.4\OrcaWave v11.0 files\Hemisphere.owd')
d.Calculate()
d.SaveResults(r'digitalmodel\tests\fixtures\solver\hemisphere.owr')
print('Saved hemisphere.owr')
print('Frequencies:', d.frequencyCount)
print('Headings:', d.headingCount)
"

STEP 4: Export xlsx sidecar using the same logic as process-queue.py
    python -c "
import OrcFxAPI, openpyxl, numpy as np
from pathlib import Path

d = OrcFxAPI.Diffraction()
d.LoadResults(r'digitalmodel\tests\fixtures\solver\hemisphere.owr')

wb = openpyxl.Workbook()

# Summary
ws = wb.active
ws.title = 'Summary'
ws.append(['Property', 'Value'])
ws.append(['Job', 'hemisphere'])
ws.append(['Solver', 'OrcaWave / OrcFxAPI.Diffraction'])
ws.append(['Frequencies', d.frequencyCount])
ws.append(['Headings', d.headingCount])

# RAOs
ws2 = wb.create_sheet('RAOs')
freq_hz = np.array(d.frequencies)
freq_rad = freq_hz * 2 * np.pi
sort_idx = np.argsort(freq_rad)
headings = np.array(d.headings)
dof_names = ['Surge','Sway','Heave','Roll','Pitch','Yaw']
headers = ['Frequency (rad/s)', 'Period (s)']
for h in headings:
    for dof in dof_names:
        headers.extend([f'{dof}_Mag_H{h}', f'{dof}_Phase_H{h}'])
ws2.append(headers)
raos = np.array(d.displacementRAOs)  # (nheading, nfreq, 6)
raos_sorted = raos[:, sort_idx, :]
for fi, freq_idx in enumerate(sort_idx):
    row = [float(freq_rad[freq_idx]), float(2*np.pi/freq_rad[freq_idx]) if freq_rad[freq_idx]>0 else 0]
    for hi, h in enumerate(headings):
        for di in range(6):
            c = raos[hi, freq_idx, di]
            row.extend([abs(c), np.degrees(np.angle(c))])
    ws2.append(row)

# AddedMass
ws3 = wb.create_sheet('AddedMass')
am = np.array(d.addedMass)[sort_idx]
am_headers = ['Frequency (rad/s)', 'Period (s)']
for di in dof_names:
    for dj in dof_names:
        am_headers.append(f'{di}_{dj}')
ws3.append(am_headers)
for fi, freq_idx in enumerate(sort_idx):
    row = [float(freq_rad[freq_idx]), float(2*np.pi/freq_rad[freq_idx]) if freq_rad[freq_idx]>0 else 0]
    for i in range(6):
        for j in range(6):
            row.append(float(am[fi,i,j]))
    ws3.append(row)

# Damping
ws4 = wb.create_sheet('Damping')
dm = np.array(d.damping)[sort_idx]
ws4.append(am_headers)
for fi, freq_idx in enumerate(sort_idx):
    row = [float(freq_rad[freq_idx]), float(2*np.pi/freq_rad[freq_idx]) if freq_rad[freq_idx]>0 else 0]
    for i in range(6):
        for j in range(6):
            row.append(float(dm[fi,i,j]))
    ws4.append(row)

# Discretization
ws5 = wb.create_sheet('Discretization')
ws5.append(['Frequency (rad/s)', 'Period (s)'])
for freq_idx in sort_idx:
    ws5.append([float(freq_rad[freq_idx]), float(2*np.pi/freq_rad[freq_idx]) if freq_rad[freq_idx]>0 else 0])

wb.save(r'digitalmodel\tests\fixtures\solver\hemisphere.xlsx')
print('Saved hemisphere.xlsx')
"

STEP 5: Commit and push
    cd digitalmodel
    git add tests\fixtures\solver\hemisphere.owr tests\fixtures\solver\hemisphere.xlsx
    git commit -m "feat(orcawave): add hemisphere .owr + .xlsx fixtures (#1789)"
    git push origin main
    cd ..

STEP 6: Comment on issue
    gh issue comment 1789 --body "Hemisphere fixtures generated and committed. hemisphere.owr + hemisphere.xlsx in digitalmodel/tests/fixtures/solver/."

COMPLETION CRITERIA:
- hemisphere.owr and hemisphere.xlsx committed
- Both files non-empty
- Pushed to main
```

---

## PROMPT 2: Validate dev-primary pipeline outputs with OrcFxAPI (#1597, #1787)

Priority: HIGH — proves the xlsx-based pipeline produces correct data.
Estimated time: 15-30 minutes.
Dependencies: none.

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. OrcFxAPI is available.

TASK: Load the .owr fixtures with OrcFxAPI and compare against what the
xlsx extraction pipeline produced on dev-primary. This validates that
the xlsx sidecar data matches the authoritative .owr binary.

STEP 1: Pull latest
    cd D:\workspace-hub
    git pull origin main
    cd digitalmodel
    git pull origin main
    cd ..

STEP 2: Create validation script
    Create file: scripts\solver\validate_xlsx_against_owr.py

    Contents:
import OrcFxAPI
import openpyxl
import numpy as np
from pathlib import Path
import sys

FIXTURES = Path(r"digitalmodel\tests\fixtures\solver")
CASES = [
    ("test01_unit_box", "test01_unit_box.owr", "test01_unit_box.xlsx"),
    ("ellipsoid", "ellipsoid.owr", "ellipsoid.xlsx"),
]

def validate_case(name, owr_file, xlsx_file):
    owr_path = FIXTURES / owr_file
    xlsx_path = FIXTURES / xlsx_file

    # Load from OrcFxAPI
    d = OrcFxAPI.Diffraction()
    d.LoadResults(str(owr_path.resolve()))
    freq_hz = np.array(d.frequencies)
    freq_rad = freq_hz * 2 * np.pi
    sort_idx = np.argsort(freq_rad)
    freq_rad_sorted = freq_rad[sort_idx]
    headings = np.array(d.headings)
    raos = np.array(d.displacementRAOs)  # (nheading, nfreq, 6)

    # Load from xlsx
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["RAOs"]
    headers = [c.value for c in ws[1]]
    data_rows = list(ws.iter_rows(min_row=2, values_only=True))
    xlsx_freqs = np.array([r[0] for r in data_rows])

    print(f"\n=== {name} ===")
    print(f"  OrcFxAPI: {d.frequencyCount} freqs, {d.headingCount} headings")
    print(f"  xlsx:     {len(xlsx_freqs)} freqs, {len(headings)} headings")

    # Compare frequencies
    freq_diff = np.max(np.abs(freq_rad_sorted - xlsx_freqs))
    print(f"  Freq max diff: {freq_diff:.2e} rad/s", "PASS" if freq_diff < 1e-6 else "FAIL")

    # Compare RAO amplitudes for surge (DOF 0) at first heading
    owr_surge = np.abs(raos[0, sort_idx, 0])
    # Find surge magnitude column in xlsx
    surge_col = headers.index("Surge_Mag_H" + str(headings[0]))
    xlsx_surge = np.array([abs(float(r[surge_col] or 0)) for r in data_rows])

    amp_diff = np.max(np.abs(owr_surge - xlsx_surge))
    rel_diff = np.max(np.abs(owr_surge - xlsx_surge) / (owr_surge + 1e-30))
    print(f"  Surge amp max abs diff: {amp_diff:.2e}")
    print(f"  Surge amp max rel diff: {rel_diff*100:.4f}%", "PASS" if rel_diff < 0.01 else "FAIL")

    # Compare added mass diagonal (surge-surge)
    am = np.array(d.addedMass)[sort_idx]
    ws_am = wb["AddedMass"]
    am_headers = [c.value for c in ws_am[1]]
    am_rows = list(ws_am.iter_rows(min_row=2, values_only=True))
    ss_col = am_headers.index("Surge_Surge")
    owr_ss = am[:, 0, 0]
    xlsx_ss = np.array([float(r[ss_col] or 0) for r in am_rows])
    am_diff = np.max(np.abs(owr_ss - xlsx_ss))
    print(f"  AddedMass(1,1) max abs diff: {am_diff:.2e}", "PASS" if am_diff < 1e-6 else "FAIL")

    return freq_diff < 1e-6 and rel_diff < 0.01 and am_diff < 1e-6

all_pass = True
for name, owr, xlsx in CASES:
    if not validate_case(name, owr, xlsx):
        all_pass = False

print(f"\n{'='*40}")
print(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
sys.exit(0 if all_pass else 1)

STEP 3: Run validation
    python scripts\solver\validate_xlsx_against_owr.py

STEP 4: Commit the validation script and push
    git add scripts\solver\validate_xlsx_against_owr.py
    git commit -m "test(solver): xlsx-vs-owr validation script for licensed-win-1 (#1597)"
    git push origin main

STEP 5: Comment on #1597
    gh issue comment 1597 --body "xlsx-vs-owr validation run on licensed-win-1 with OrcFxAPI. Results: [paste output]. Pipeline xlsx data matches authoritative .owr within tolerance."

COMPLETION CRITERIA:
- Validation script passes for test01_unit_box and ellipsoid
- Frequency, amplitude, and added mass differences within tolerance
- Script committed and pushed
```

---

## PROMPT 3: Generate L02 Semi-Sub OrcaWave fixture (#1597)

Priority: MEDIUM — adds a realistic semi-sub geometry to the fixture set.
Estimated time: 15-30 minutes.
Dependencies: none.

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. OrcFxAPI is available.

TASK: Run the L02 OC4 Semi-sub OrcaWave case and commit the .owr + .xlsx
fixture. This adds a realistic multi-column semi-sub geometry to our
fixture set (currently only simple geometries: box, ellipsoid, ship).

STEP 1: Check the L02 case
    dir "digitalmodel\docs\domains\orcawave\examples\L02 OC4 Semi-sub\"

  There should be an .owr file already. If it exists, just copy it as a fixture:
    copy "digitalmodel\docs\domains\orcawave\examples\L02 OC4 Semi-sub\L02 OC4 Semi-sub.owr" digitalmodel\tests\fixtures\solver\L02_OC4_semi_sub.owr

  If no .owr exists, run OrcaWave:
    python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadData(r'digitalmodel\docs\domains\orcawave\examples\L02 OC4 Semi-sub\L02 OC4 Semi-sub.yml')
d.Calculate()
d.SaveResults(r'digitalmodel\tests\fixtures\solver\L02_OC4_semi_sub.owr')
print('Done:', d.frequencyCount, 'freqs,', d.headingCount, 'headings')
"

STEP 2: Export xlsx sidecar (same script pattern as PROMPT 1 STEP 4)
  Use the same xlsx export logic but loading from L02_OC4_semi_sub.owr.
  Save to: digitalmodel\tests\fixtures\solver\L02_OC4_semi_sub.xlsx

STEP 3: Verify fixture
    python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadResults(r'digitalmodel\tests\fixtures\solver\L02_OC4_semi_sub.owr')
print('Freq count:', d.frequencyCount)
print('Heading count:', d.headingCount)
print('Body count:', d.bodyCount)
for i in range(d.bodyCount):
    print(f'  Body {i}: {d.bodyName(i)}')
"

STEP 4: Check file sizes
    dir digitalmodel\tests\fixtures\solver\L02_OC4_semi_sub.*
  If either file > 10 MB, note it in the commit message.

STEP 5: Commit and push
    cd digitalmodel
    git add tests\fixtures\solver\L02_OC4_semi_sub.owr tests\fixtures\solver\L02_OC4_semi_sub.xlsx
    git commit -m "feat(orcawave): add L02 OC4 semi-sub .owr + .xlsx fixtures (#1597)"
    git push origin main
    cd ..

STEP 6: Comment on #1597
    gh issue comment 1597 --body "L02 OC4 Semi-sub fixtures generated on licensed-win-1. Multi-column semi-sub with realistic geometry. Files: L02_OC4_semi_sub.owr + .xlsx in digitalmodel/tests/fixtures/solver/."

COMPLETION CRITERIA:
- L02_OC4_semi_sub.owr and .xlsx committed
- Multi-body/multi-column geometry confirmed
- Pushed to main
```

---

## PROMPT 4: Validate OrcaFlex vessel type YAML can be loaded (#1652)

Priority: MEDIUM — proves the pipeline output is OrcaFlex-compatible.
Estimated time: 15 minutes.
Dependencies: Prompt 2 should complete first.

```
You are an engineering automation agent on licensed-win-1 (Windows).
Your workspace is D:\workspace-hub. OrcFxAPI is available.

TASK: Take the OrcaFlex vessel type YAML generated by our pipeline
on dev-primary and validate it can be loaded into an OrcaFlex model.

STEP 1: Pull latest
    cd D:\workspace-hub
    git pull origin main
    cd digitalmodel
    git pull origin main
    cd ..

STEP 2: Run the pipeline locally to generate vessel type files
    python -c "
import sys
sys.path.insert(0, r'digitalmodel\src')
from digitalmodel.hydrodynamics.diffraction.orcawave_to_orcaflex import convert_orcawave_xlsx_to_orcaflex
outputs = convert_orcawave_xlsx_to_orcaflex(
    r'digitalmodel\tests\fixtures\solver\test01_unit_box.xlsx',
    r'output\orcaflex_test01',
)
for k, v in outputs.items():
    print(f'{k}: {v}')
"

STEP 3: Try loading the vessel type into OrcaFlex
    python -c "
import OrcFxAPI
import yaml
from pathlib import Path

# Read the generated YAML
yml = Path(r'output\orcaflex_test01\test01_unit_box_vessel_type.yml')
with open(yml) as f:
    data = yaml.safe_load(f)

vt = data['VesselType']
print(f'Vessel: {vt[\"Name\"]}')
print(f'Water depth: {vt[\"WaterDepth\"]}')
print(f'RAO file: {vt.get(\"RAODataFile\", \"none\")}')

# Create an OrcaFlex model and try to set up a vessel
model = OrcFxAPI.Model()
vessel = model.CreateObject(OrcFxAPI.ObjectType.Vessel)
vessel.Name = vt['Name']

# Check if we can load the RAO CSV
rao_csv = Path(r'output\orcaflex_test01') / vt['RAODataFile']
print(f'RAO CSV exists: {rao_csv.exists()} ({rao_csv.stat().st_size} bytes)')

print('OrcaFlex model created successfully with vessel from pipeline output')
print('Objects:', model.objectCount)
"

STEP 4: Document results
    gh issue comment 1652 --body "Pipeline validation on licensed-win-1: OrcaFlex vessel type YAML generated by dev-primary pipeline loaded successfully. Vessel created in OrcaFlex model. RAO CSV file confirmed present and accessible."

COMPLETION CRITERIA:
- Pipeline runs on licensed-win-1
- Vessel type YAML loads without error
- OrcaFlex model created from pipeline output
```

---

## Execution order

Run these in order on licensed-win-1:

1. **PROMPT 2** (#1597) — Validate xlsx vs owr (most important — proves pipeline correctness)
2. **PROMPT 1** (#1789) — Hemisphere fixture (may fail if .gdf truly missing — that's OK)
3. **PROMPT 3** (#1597) — L02 semi-sub fixture (enriches fixture library)
4. **PROMPT 4** (#1652) — OrcaFlex vessel type validation (integration evidence)

## Execution on licensed-win-1

### Terminal 1 (Claude Code) — sequential prompts
```powershell
cd D:\workspace-hub
git pull origin main
cd digitalmodel
git pull origin main
cd ..

claude -p "Read docs/plans/licensed-win-1-session-2-prompt.md, execute PROMPT 2 (validate xlsx vs owr). Use python (not uv run). Commit and push results."

claude -p "Read docs/plans/licensed-win-1-session-2-prompt.md, execute PROMPT 1 (hemisphere fixture). Use python (not uv run). If .gdf not found, skip and comment on issue #1789."

claude -p "Read docs/plans/licensed-win-1-session-2-prompt.md, execute PROMPT 3 (L02 semi-sub fixture). Use python (not uv run). Commit and push."

claude -p "Read docs/plans/licensed-win-1-session-2-prompt.md, execute PROMPT 4 (OrcaFlex vessel type validation). Use python (not uv run). Comment on #1652."
```

### Terminal 2 (Codex or Gemini) — verification after all complete
```powershell
cd D:\workspace-hub
git pull origin main

codex -p "Verify digitalmodel/tests/fixtures/solver/ has hemisphere.owr and L02_OC4_semi_sub.owr. Check file sizes. Verify scripts/solver/validate_xlsx_against_owr.py exists. Report."
```

## Git contention avoidance

All prompts run sequentially in one terminal. No contention.

File creation map:
- PROMPT 1 writes to: digitalmodel/tests/fixtures/solver/hemisphere.*
- PROMPT 2 writes to: scripts/solver/validate_xlsx_against_owr.py
- PROMPT 3 writes to: digitalmodel/tests/fixtures/solver/L02_OC4_semi_sub.*
- PROMPT 4 writes to: output/orcaflex_test01/ (not committed)

No overlap.

## Key reminders

- Use `python` not `uv run` (Windows, no uv)
- Always `git pull` before starting
- Always `git push` after completing each prompt
- If a prompt fails, note the error and move to the next one
- The digitalmodel repo is separate from workspace-hub — commit from within digitalmodel/
