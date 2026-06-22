> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_browser_capture_to_disk_webgl.md

---
name: feedback-browser-capture-to-disk-webgl
description: How to get web imagery into a file for video/PDF pipelines — bridge save_to_disk writes no host file; headless chrome --screenshot works but has no WebGL (no Google Earth/Street View)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0c5c8b5b-c073-4d66-9dca-4e4fae000083
---

When a deliverable needs web imagery baked into a **file** (video frames, PDF figures), the claude-in-chrome browser bridge is the wrong tool, and Google Earth/Street View are partly impossible.

**Rule:**
- The browser bridge (`mcp__claude-in-chrome__computer` screenshot, even with `save_to_disk:true`) returns the image **in-context only — it does NOT write a host file path** the pipeline (ffmpeg/PIL) can read. Confirmed 2026-05-28; consistent with [[feedback_claude_in_chrome_file_upload_no_host_paths]].
- Use **`google-chrome --headless=new --screenshot=OUT.png --window-size=W,H --virtual-time-budget=16000 URL`** instead → real PNG on disk, scriptable, delegable to Codex.
- **Headless Chrome WebGL:** with plain `--disable-gpu` it's off ("WebGL is not supported"); `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader` *initializes* a software WebGL context, BUT `--virtual-time-budget` screenshots before async WebGL textures upload, so tile-streaming scenes (**Google Earth 3D globe, Street View pano sphere**) render **black/blank**. Treat Earth-3D/SV-sphere as NOT headless-capturable.
- **Street View workaround that WORKS (no WebGL):** Google serves a flat-raster **thumbnail** per panorama:
  `https://streetviewpixels-pa.googleapis.com/v1/thumbnail?cb_client=maps_sv.tactile&w=1600&h=900&pitch=P&fov=90&panoid=PANOID&yaw=HEADING` → real JPEG via `curl`, any heading/pitch/fov. Get the **panoid** by navigating the interactive bridge to a Street View URL (`.../@lat,lng,3a,75y,Hh,Tt/data=!3m1!1e1`) and reading it from the resolved tab URL (`!1s<PANOID>` and the embedded thumbnail URL). Modular: fetch each heading as a piece, composite.
- **Google Maps satellite** captures fine headless (raster `<img>` tiles, no WebGL).

**Why:** FD30150 south-side deliverable (sabithaandkrishnaestates) needed Maps/Earth/Street View embedded in a video + PDF. Bridge screenshots can't reach ffmpeg; headless solved Maps; SV solved via the thumbnail endpoint; Earth-3D dropped (too slow).

**How to apply:** "Put this web view in a video/PDF" → headless `google-chrome --screenshot` for raster pages, `--print-to-pdf` for HTML→PDF. For Street View frames, use the **thumbnail-endpoint curl** trick (panoid from the bridge), not screenshots. Earth-3D: flag the limit, substitute Maps satellite. Keep provider attribution ("Imagery ©Google, Airbus, Maxar" / "Street View ©Google") on every embedded frame for ToS. See [[project_skestates_facility_evidence_timeline]].
