# GTM Demo GIF Screencast Scripts

Production guide for recording 5 ACE Engineer parametric demo screencasts.
Target: ~30s each, 1200x800px GIF, dark terminal + browser HTML report.

---

## Global Setup (do once before recording session)

### Recording Tools

| Tool | Use Case | Install |
|---|---|---|
| **Peek** (recommended) | Screen-region GIF recording on Linux | `sudo apt install peek` |
| **OBS Studio** | Full-screen capture, export to GIF via ffmpeg | `sudo apt install obs-studio` |
| **gifcap** | Browser-based, no install | https://gifcap.dev |
| **asciinema + svg-term** | Terminal-only (no browser capture) | `pip install asciinema` |

Recommended pipeline: **OBS** records MP4 at 15fps, then convert:
```bash
ffmpeg -i demo_0X.mp4 -vf "fps=12,scale=1200:-1:flags=lanczos" -loop 0 demo_0X.gif
```

### Terminal Settings

```
Font:           JetBrains Mono or Fira Code, 16pt
Theme:          Dark background (#1a1a2e), bright green (#00ff88) for stdout
Prompt:         Minimal — just "$ " (hide user/host/path clutter)
Window size:    120 columns x 30 rows
Cursor:         Block, blinking off (less visual noise in GIF)
```

Temporary prompt override before recording:
```bash
export PS1='$ '
```

### Browser Settings

```
Browser:        Chrome or Firefox
Zoom:           110% (charts readable at GIF resolution)
Dev tools:      Closed
Bookmarks bar:  Hidden (Ctrl+Shift+B)
Tab bar:        Only one tab open
Address bar:    Acceptable — shows file:// path which reinforces "local report"
```

### File Naming Convention

```
docs/gtm/media/demo_01_dnv_freespan_viv.gif
docs/gtm/media/demo_02_wall_thickness_multicode.gif
docs/gtm/media/demo_03_deepwater_mudmat_installation.gif
docs/gtm/media/demo_04_shallow_water_pipelay.gif
docs/gtm/media/demo_05_deepwater_rigid_jumper.gif
```

### Pre-Recording Checklist

- [ ] `mkdir -p docs/gtm/media`
- [ ] Run each demo once to warm caches and confirm output files exist
- [ ] Close all notifications (Do Not Disturb mode)
- [ ] Hide desktop icons, taskbar auto-hide
- [ ] Pre-open terminal and browser side by side (70/30 split or terminal-first then switch)
- [ ] Set recording region to exactly 1200x800px in Peek/OBS

---

## Demo 1: DNV Freespan/VIV (680 cases)

### Pre-Recording Commands

```bash
cd digitalmodel
# Dry run to confirm it works and warm up
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_01_dnv_freespan_viv.py
# Note the output HTML path for browser step
```

### Storyboard

| Scene | Time | What to Show | Action |
|---|---|---|---|
| 1 | 0-3s | Terminal, cursor at prompt | Type: `PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_01_dnv_freespan_viv.py` and press Enter. Type at natural speed (not instant-paste). |
| 2 | 3-8s | Progress output scrolling | Output appears: `[1/7] Loading pipeline parameters...` `[2/7] Building parameter sweep (680 cases)...` `[3/7] Running VIV onset screening...` |
| 3 | 8-13s | Case counter ticking up | `[4/7] Processing cases... 340/680... 680/680` then `[5/7] Generating report...` Final line: `Done. 680 cases completed in 1.8s` |
| 4 | 13-18s | Browser opens HTML report | Click/Alt-Tab to browser showing the report. Scroll slowly past the summary table to the hero chart. |
| 5 | 18-25s | VIV onset screening heatmap | Hover over a green cell (safe), then a red cell (VIV onset). Tooltip shows span length, current velocity, and screening result. Pause on a yellow boundary cell. |
| 6 | 25-30s | End card area | Scroll to bottom or overlay text fades in: **"680 freespan cases screened in under 2 seconds"**. Hold 2s, stop recording. |

### Expected Terminal Output (approximate)

```
$ PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_01_dnv_freespan_viv.py
[1/7] Loading pipeline parameters...
[2/7] Building parameter sweep (680 cases)...
[3/7] Running VIV onset screening...
[4/7] Processing cases... ████████████████████ 680/680
[5/7] Applying DNV-RP-F105 acceptance criteria...
[6/7] Generating HTML report...
[7/7] Opening report in browser...
Done. 680 cases completed in 1.8s
Report: results/demo_01_freespan_viv_report.html
```

### Chart Interaction Script

1. Hover over a **green cell** at (span=20m, current=0.3m/s) -- tooltip shows "PASS"
2. Move to a **red cell** at (span=60m, current=1.2m/s) -- tooltip shows "FAIL - VIV onset"
3. Hover along the yellow diagonal boundary between pass/fail zones
4. Pause on the heatmap for 2 seconds so the viewer absorbs the color pattern

### LinkedIn/README Caption

> 680 DNV freespan VIV screening cases in 1.8 seconds. Green = safe. Red = vortex-induced vibration onset. Every span-current combination answered before your next sip of coffee.

---

## Demo 2: Wall Thickness Multi-Code (72 cases)

### Pre-Recording Commands

```bash
cd digitalmodel
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_02_wall_thickness_multicode.py
```

### Storyboard

| Scene | Time | What to Show | Action |
|---|---|---|---|
| 1 | 0-3s | Terminal, cursor at prompt | Type: `PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_02_wall_thickness_multicode.py` and press Enter. |
| 2 | 3-8s | Progress output | `[1/6] Loading pipe catalog...` `[2/6] Running wall thickness for API 1111...` `[3/6] Running wall thickness for DNV-OS-F101...` |
| 3 | 8-13s | Completion | `[4/6] Running wall thickness for PD 8010...` `[5/6] Comparing 3 codes across 24 pipe sizes...` `Done. 72 cases (3 codes x 24 pipes) in 0.9s` |
| 4 | 13-18s | Browser report opens | Navigate to the lifecycle utilisation chart. The chart has a dropdown code selector at top. |
| 5 | 18-25s | Interactive dropdown | Click dropdown, switch from API 1111 to DNV-OS-F101. Chart updates. Then switch to PD 8010. Hover over the highest-utilisation pipe showing the exact value. |
| 6 | 25-30s | End card | Overlay or scroll to: **"3 design codes compared overnight -- your team does 1 in a week"**. Hold 2s, stop. |

### Expected Terminal Output (approximate)

```
$ PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_02_wall_thickness_multicode.py
[1/6] Loading pipe catalog (24 sizes)...
[2/6] Running wall thickness — API 1111...
[3/6] Running wall thickness — DNV-OS-F101...
[4/6] Running wall thickness — PD 8010...
[5/6] Comparing 3 codes x 24 pipe sizes = 72 cases...
[6/6] Generating HTML report...
Done. 72 cases completed in 0.9s
Report: results/demo_02_wall_thickness_report.html
```

### Chart Interaction Script

1. Chart loads showing API 1111 lifecycle utilisation bars
2. Click the **code selector dropdown** -- switch to "DNV-OS-F101" -- bars shift
3. Switch to "PD 8010" -- bars shift again, some pipes now exceed 1.0 utilisation (red)
4. Hover over the pipe with highest utilisation -- tooltip shows exact value and code limit

### LinkedIn/README Caption

> 3 international design codes. 24 pipe sizes. 72 wall thickness calculations. Side-by-side in 0.9 seconds. Your team does one code in a week.

---

## Demo 3: Deepwater Mudmat Installation (180 cases)

### Pre-Recording Commands

```bash
cd digitalmodel
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_03_deepwater_mudmat_installation.py
```

### Storyboard

| Scene | Time | What to Show | Action |
|---|---|---|---|
| 1 | 0-3s | Terminal, cursor at prompt | Type the run command and press Enter. |
| 2 | 3-8s | Progress output | `[1/5] Loading vessel and structure data...` `[2/5] Building installation matrix (3 vessels x 6 structures x 10 depths)...` |
| 3 | 8-13s | Fast completion | `[3/5] Running lift analysis... 180/180` `[4/5] Classifying Go/No-Go...` `Done. 180 cases in 0.8s` |
| 4 | 13-18s | Browser report | Navigate to the Go/No-Go heatmap. Two vessel panels side by side, cells colored green/yellow/red by structure-depth combination. |
| 5 | 18-25s | Heatmap interaction | Hover over a green cell (Go) on Vessel A, then the same structure-depth on Vessel B showing red (No-Go). This contrast is the money shot. Then hover over a yellow (marginal) cell. |
| 6 | 25-30s | End card | **"Can your vessel install this structure at this depth? 180 answers in 1 second."** Hold 2s, stop. |

### Expected Terminal Output (approximate)

```
$ PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_03_deepwater_mudmat_installation.py
[1/5] Loading vessel and structure data...
[2/5] Building installation matrix (3 vessels x 6 structures x 10 depths)...
[3/5] Running lift analysis... ████████████████████ 180/180
[4/5] Classifying Go/No-Go zones...
[5/5] Generating HTML report...
Done. 180 cases completed in 0.8s
Report: results/demo_03_mudmat_installation_report.html
```

### Chart Interaction Script

1. Show the side-by-side vessel heatmaps -- Vessel A (larger crane) mostly green, Vessel B more red
2. Hover over **Vessel A, Structure 3, 1500m depth** -- tooltip: "GO - Crane utilisation 72%"
3. Move to **Vessel B, same cell** -- tooltip: "NO-GO - Crane utilisation 118%"
4. Hover a **yellow marginal cell** -- tooltip: "MARGINAL - Crane utilisation 95%"
5. Pause so viewer sees the contrast pattern

### LinkedIn/README Caption

> Can your vessel install this structure at this depth? 180 answers in 1 second. Green = go. Red = no-go. The decision matrix your tender team builds in a week, delivered before the call starts.

---

## Demo 4: Shallow Water Pipelay (60 cases)

### Pre-Recording Commands

```bash
cd digitalmodel
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_04_shallow_water_pipelay.py
```

### Storyboard

| Scene | Time | What to Show | Action |
|---|---|---|---|
| 1 | 0-3s | Terminal, cursor at prompt | Type the run command and press Enter. |
| 2 | 3-8s | Progress output | `[1/5] Loading pipe catalog and vessel specs...` `[2/5] Running S-lay catenary analysis (60 cases)...` |
| 3 | 8-13s | Completion | `[3/5] Computing required tension vs water depth...` `[4/5] Classifying feasibility...` `Done. 60 cases in 1.2s` |
| 4 | 13-18s | Browser report | Scroll to the Go/No-Go matrix. Rows = pipe diameters, columns = water depths. Green/red cells. |
| 5 | 18-25s | Two-chart interaction | First: hover Go/No-Go matrix cells. Then scroll to the **required tension vs depth** curve chart. Hover a curve showing tension rising steeply in shallow water. |
| 6 | 25-30s | End card | **"S-lay catenary screening for your full pipe catalog -- overnight."** Hold 2s, stop. |

### Expected Terminal Output (approximate)

```
$ PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_04_shallow_water_pipelay.py
[1/5] Loading pipe catalog and vessel specifications...
[2/5] Running S-lay catenary analysis (60 cases)...
[3/5] Computing required tension vs water depth...
[4/5] Classifying Go/No-Go feasibility...
[5/5] Generating HTML report...
Done. 60 cases completed in 1.2s
Report: results/demo_04_pipelay_report.html
```

### Chart Interaction Script

1. Go/No-Go matrix: hover a **green cell** (12" pipe, 30m depth) -- "GO - tension 45 Te (vessel max 120 Te)"
2. Hover a **red cell** (24" pipe, 8m depth) -- "NO-GO - tension 155 Te exceeds vessel max 120 Te"
3. Scroll to **tension vs depth curves** -- multiple pipe sizes plotted
4. Hover the 24" curve at 8m showing the steep tension spike
5. Hover the 12" curve showing flat, comfortable tension

### LinkedIn/README Caption

> S-lay catenary feasibility for your full pipe catalog. 60 pipe-depth combinations screened in 1.2 seconds. The tension curves your engineers calculate by hand? Automated overnight.

---

## Demo 5: Deepwater Rigid Jumper (300 cases)

### Pre-Recording Commands

```bash
cd digitalmodel
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py
```

### Storyboard

| Scene | Time | What to Show | Action |
|---|---|---|---|
| 1 | 0-3s | Terminal, cursor at prompt | Type the run command and press Enter. |
| 2 | 3-8s | Progress output | `[1/6] Loading jumper geometry and connection data...` `[2/6] Building scenario matrix (300 cases)...` `[3/6] Running installation analysis...` |
| 3 | 8-13s | Case counter and completion | `[4/6] Processing... 150/300... 300/300` `[5/6] Checking tie-in alignment tolerances...` `Done. 300 cases in 1.5s` |
| 4 | 13-18s | Browser report | Navigate to Go/No-Go heatmap. Rows = jumper configs, columns = sea states or vessel combos. |
| 5 | 18-25s | Two-chart interaction | Hover heatmap cells (Go/No-Go). Then scroll to the **bending stress profile** chart -- hover along the jumper length showing stress distribution, highlight the peak stress point. |
| 6 | 25-30s | End card | **"300 jumper installation scenarios. Tie-in alignment checked. Before coffee."** Hold 2s, stop. |

### Expected Terminal Output (approximate)

```
$ PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py
[1/6] Loading jumper geometry and connection data...
[2/6] Building scenario matrix (300 cases)...
[3/6] Running installation analysis...
[4/6] Processing cases... ████████████████████ 300/300
[5/6] Checking tie-in alignment tolerances...
[6/6] Generating HTML report...
Done. 300 cases completed in 1.5s
Report: results/demo_05_rigid_jumper_report.html
```

### Chart Interaction Script

1. Heatmap: hover a **green cell** -- "GO - Max stress 285 MPa (limit 450 MPa), alignment OK"
2. Hover a **red cell** -- "NO-GO - Tie-in misalignment 12mm exceeds 5mm tolerance"
3. Scroll to **bending stress profile** chart
4. Hover along the jumper arc -- stress rises at the bends
5. Pause at **peak stress point** -- tooltip shows location and value
6. Move to a second jumper config overlay showing different stress profile

### LinkedIn/README Caption

> 300 rigid jumper installation scenarios. Bending stress profiled. Tie-in alignment checked against tolerances. All before your first coffee of the day.

---

## Recording Session Workflow

Follow this sequence to record all 5 GIFs in one session (~45 minutes total):

### 1. Environment Setup (10 min)

```bash
# Terminal prep
export PS1='$ '
cd digitalmodel

# Warm up all demos (cache dependencies, confirm outputs)
for i in 01 02 03 04 05; do
  script="examples/demos/gtm/demo_${i}_*.py"
  PYTHONPATH=examples/demos/gtm:src uv run python $script
done

# Create output directory
mkdir -p docs/gtm/media

# Set Do Not Disturb, hide taskbar, close other apps
```

### 2. Configure Recording Tool (5 min)

```bash
# Peek settings
# - Output format: GIF
# - Framerate: 12 fps
# - Downscale: 1x
# - Size recording area to 1200x800 exactly

# OR OBS settings
# - Canvas: 1200x800
# - Output: MP4 (convert later)
# - Framerate: 15 fps
```

### 3. Record Each Demo (5 min each x 5 = 25 min)

For each demo:
1. Clear terminal (`clear`)
2. Start recording (Peek: Ctrl+Alt+R, or OBS: Start Recording)
3. Follow the storyboard scene by scene
4. Stop recording at the end card
5. Save with the naming convention
6. Review the GIF -- re-record if needed

### 4. Post-Processing (5 min)

```bash
# If recorded as MP4, convert to optimized GIF
for f in docs/gtm/media/demo_*.mp4; do
  out="${f%.mp4}.gif"
  ffmpeg -i "$f" \
    -vf "fps=12,scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
    -loop 0 "$out"
done

# Check file sizes -- target under 5MB each for GitHub/LinkedIn
ls -lh docs/gtm/media/*.gif
```

### Size Optimization (if GIF exceeds 5MB)

```bash
# Reduce colors
ffmpeg -i input.gif -vf "fps=10,scale=1000:-1:flags=lanczos" -loop 0 output.gif

# Or use gifsicle
gifsicle -O3 --colors 96 --lossy=80 input.gif -o output.gif
```

---

## Platform-Specific Dimensions

| Platform | Max GIF Size | Recommended Dimensions | Auto-plays? |
|---|---|---|---|
| GitHub README | 10MB | 1200x800 | Yes |
| LinkedIn post | 5MB | 1200x800 | Converts to video |
| aceengineer.com | No limit | 1200x800 | Yes (lazy-load) |
| Cold email | 3MB (inline) | 800x533 (scaled down) | Depends on client |

For email, create a smaller variant:
```bash
ffmpeg -i demo_0X.gif -vf "fps=10,scale=800:-1:flags=lanczos" demo_0X_email.gif
```

---

## Quick Reference: All Run Commands

```bash
cd digitalmodel

# Demo 1: DNV Freespan/VIV (680 cases)
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_01_dnv_freespan_viv.py

# Demo 2: Wall Thickness Multi-Code (72 cases)
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_02_wall_thickness_multicode.py

# Demo 3: Deepwater Mudmat Installation (180 cases)
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_03_deepwater_mudmat_installation.py

# Demo 4: Shallow Water Pipelay (60 cases)
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_04_shallow_water_pipelay.py

# Demo 5: Deepwater Rigid Jumper (300 cases)
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py
```
