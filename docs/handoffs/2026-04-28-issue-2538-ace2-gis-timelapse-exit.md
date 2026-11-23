# Exit handoff — Issue #2538 ace-linux-2 GIS timelapse setup

Date: 2026-04-28T19:32-05:00

## GitHub issue

- Issue: https://github.com/vamseeachanta/workspace-hub/issues/2538
- Title: `ace2: generate lifetime property imagery timelapse for 11511 Piping Rock`
- State at handoff: OPEN
- Labels verified: `enhancement`, `priority:medium`, `cat:data-pipeline`, `domain:gis`
- Related umbrella: https://github.com/vamseeachanta/workspace-hub/issues/18

## User request captured

Prepare a Google Earth / satellite-style lifetime visual timeline for:

- `11511 Piping Rock Dr., Houston, TX 77077`
- Approx geocode: `29.7397219, -95.5971637`

Goal: understand how the property and neighborhood changed over time.

## What was completed this session

1. Created focused execution/setup issue #2538 rather than duplicating umbrella #18.
2. Verified ace-linux-2 reachability via SSH.
3. Installed GIS/timelapse Python environment on ace-linux-2, not ace-linux-1.
4. Verified the Python imports on ace-linux-2.
5. Posted setup evidence to issue #2538 as a GitHub comment.
6. Saved durable memory noting the ace-linux-2 environment path and report/log locations.

## ace-linux-2 environment

Working directory:

```text
/mnt/local-analysis/ace2-gis-timelapse
```

Virtual environment:

```text
/mnt/local-analysis/ace2-gis-timelapse/.venv
```

Setup report:

```text
/mnt/local-analysis/ace2-worker-reports/issue-2538-ace2-setup-report.md
```

Setup log:

```text
/mnt/local-analysis/ace2-worker-logs/issue-2538-setup.log
```

Installed/verified packages:

- `earthengine-api`
- `geemap`
- `rasterio`
- `imageio`
- `pillow`
- `geopandas`
- `shapely`
- `folium`
- `matplotlib`
- `contextily`
- `requests`
- `numpy`
- `pandas`

System tools observed on ace-linux-2 setup report:

- Python 3.12 system; venv Python 3.11.15 via uv
- GDAL 3.8.4
- QGIS 3.44.9
- ffmpeg 6.1.1
- uv 0.11.1

## Current execution state

- Remote setup tmux session `ace2-gis-2538-setup` completed before this handoff.
- Follow-up SSH readiness check confirmed:
  - `ace-linux-2` resolves to `192.168.1.103`
  - `ssh ace-linux-2 'hostname; whoami; pwd'` returns `ace-linux-2`, `vamsee`, `/home/vamsee`
- A later quick `tmux list-sessions` command initially printed `host=ace-linux-1`; this appears to have been a quoting/command issue, because a direct host check immediately after returned `ace-linux-2`. Treat direct host check as authoritative.

## Important guardrails

- Keep ace-linux-1 as GitHub/control-plane machine.
- ace-linux-2 `gh auth` was invalid during setup; do not rely on ace-linux-2 for GitHub comments, PRs, pushes, or issue label changes until reauthenticated.
- Do not claim parcel-scale lifetime history from Landsat/Sentinel; use them for broad neighborhood context only.
- For property-scale visuals, prefer NAIP/open aerial imagery where available; Google Earth Pro historical imagery remains the highest-resolution manual/API-limited option.
- Earth Engine may require browser/user auth before Landsat/Sentinel/NAIP workflows can run through `earthengine-api`/`geemap`.

## Next session recommended steps

1. From ace-linux-1, verify no remote worker is still running:

```bash
ssh ace-linux-2 "bash -lc 'tmux list-sessions 2>/dev/null || echo no-tmux-sessions'"
```

2. Activate the ace-linux-2 environment:

```bash
ssh ace-linux-2 "bash -lc 'cd /mnt/local-analysis/ace2-gis-timelapse && source .venv/bin/activate && python - <<\'PY\'
import ee, geemap, rasterio, imageio
print("imports ok")
PY'"
```

3. Check Earth Engine auth state:

```bash
ssh ace-linux-2 "bash -lc 'cd /mnt/local-analysis/ace2-gis-timelapse && source .venv/bin/activate && python - <<\'PY\'
import ee
try:
    ee.Initialize()
    print("earthengine initialized")
except Exception as exc:
    print(type(exc).__name__)
    print(exc)
PY'"
```

4. Build the data-source feasibility matrix for the address:

- Google Earth Pro historical imagery: manual highest-resolution route.
- NAIP: likely best open high-resolution property/neighborhood option, roughly 2003-present depending availability.
- Landsat: 1984-present, neighborhood/urbanization only.
- Sentinel-2: 2015-present, recent medium-resolution context.

5. Generate first artifacts on ace-linux-2:

- property-scale contact sheet / GIF for ~0.15–0.25 mile radius
- neighborhood-scale contact sheet / GIF for ~1–2 mile radius
- frame labels with year/date/source
- short HTML/Markdown report with interpretation and limitations

6. Post resulting artifact paths and summary back to issue #2538 from ace-linux-1.

## Local repo status caveat

Attempts to run `git status` in `/mnt/local-analysis/workspace-hub` timed out during exit documentation. Earlier in the session, before the timeout, the workspace-hub root had unrelated modified provider/session telemetry files. This handoff file is intentionally docs-only; do not assume it has been committed or pushed.

Recommended next operator action before committing anything:

```bash
cd /mnt/local-analysis/workspace-hub
git status --short --branch -- docs/handoffs/2026-04-28-issue-2538-ace2-gis-timelapse-exit.md
git diff -- docs/handoffs/2026-04-28-issue-2538-ace2-gis-timelapse-exit.md
```

If committing, stage only this handoff file unless the operator explicitly wants to include unrelated telemetry changes.
