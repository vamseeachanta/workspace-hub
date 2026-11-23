# CLI-Anything Evaluation — Auto-Generated CLIs for Blender, OpenFOAM, QGIS

**Date:** 2026-03-31
**Issue:** vamseeachanta/workspace-hub#1475
**Evaluated by:** Research agent (web research + installation verified)

---

## Summary

CLI-Anything (v1.x, 21k+ GitHub stars, HKUDS/HKU) is an open-source Claude Code plugin that auto-generates production-ready CLI wrappers for GUI software by analyzing source code. It uses a 7-phase LLM-driven pipeline (Analyze, Design, Implement, Plan Tests, Write Tests, Document, Publish) to produce Click-based Python CLIs with JSON output, REPL mode, and SKILL.md files for AI agent discovery.

**Recommendation:** Trial CLI-Anything for Blender CLI generation. Defer for OpenFOAM (already CLI-native). Defer for QGIS (has `qgis_process` CLI). The tool's primary value is for GUI-first applications lacking headless automation — Blender fits this best among the three targets.

---

## What CLI-Anything Is

### Origin and Purpose

CLI-Anything was created by the University of Hong Kong's Data Science Lab (HKUDS). Launched March 8, 2026, it reached 13,400+ stars in under 6 days. The core innovation is HARNESS.md — a structured SOP that teaches AI agents to systematically analyze GUI software source code and generate production-grade CLI wrappers.

### How It Works

1. **Analyze** — scans source code, maps GUI actions to underlying APIs
2. **Design** — architects Click command groups and state model
3. **Implement** — builds Python CLI with `--json` output on every command
4. **Plan Tests** — creates TEST.md with unit/E2E/subprocess test plan
5. **Write Tests** — implements tests (1,508 tests, 100% pass rate reported across 11 apps)
6. **Document** — generates SKILL.md for AI agent discovery
7. **Publish** — creates setup.py, installs to PATH

### Key Properties

| Property | Detail |
|---|---|
| **License** | MIT |
| **GitHub** | [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) |
| **Stars** | 21k+ |
| **Plugin for** | Claude Code (also OpenClaw, Cursor, Codex, others) |
| **CLI-Hub** | [hkuds.github.io/CLI-Anything](https://hkuds.github.io/CLI-Anything/) — registry of pre-built CLIs |
| **Requirements** | Source code access; frontier LLM (Claude Opus/Sonnet, GPT-5.4) |
| **Tested apps** | GIMP, Blender, LibreOffice, Inkscape, Audacity, Kdenlive, Shotcut, OBS Studio, Stable Diffusion, ComfyUI |

### Limitations

- Requires source code (compiled-only binaries degrade quality)
- Frontier LLM required for reliable generation — weaker models produce incomplete CLIs
- Token cost: full 7-phase pipeline consumes significant LLM tokens per application
- Generated CLIs call the real software backend — target app must be installed

---

## Application-Specific Assessment

### Blender

**Current state of headless automation:**

Blender has mature headless support via the `-b` / `--background` flag and Python scripting:

```bash
blender -b scene.blend --python render_script.py    # headless render
blender -b --python-expr "import bpy; bpy.ops.wm.save_as_mainfile(filepath='out.blend')"
```

Blender's Python API (`bpy`) is comprehensive — nearly every GUI action has a Python equivalent. However, discovering the right `bpy.ops.*` call for a given task requires deep Blender knowledge.

**CLI-Anything value-add for Blender:**

- CLI-Anything has already generated a Blender CLI (listed in CLI-Hub)
- Provides discoverable, structured commands (e.g., `blender-cli render --scene file.blend --output /tmp/render.png --json`)
- `--json` output on every command enables agent parsing without scraping stdout
- SKILL.md makes Blender capabilities discoverable to Claude Code without prior knowledge

**Alternative: Blender MCP Server**

Multiple Blender MCP servers exist (ahujasid/blender-mcp, djeada/blender-mcp-server, bpype/blender). These provide bidirectional socket communication with Blender's running instance, supporting object creation, material control, scene inspection, and arbitrary Python execution. However, MCP requires a running Blender instance and adds protocol overhead.

| Approach | Headless | Token cost | Discovery | Complexity |
|---|---|---|---|---|
| Raw `blender -b --python` | Yes | Zero | None (must know bpy API) | Low |
| CLI-Anything generated CLI | Yes | One-time generation | SKILL.md | Medium |
| Blender MCP server | Needs running instance | Per-call | MCP tool listing | High |

**Recommendation: Trial** — CLI-Anything's Blender CLI is the sweet spot between raw Python scripting (requires expertise) and MCP (requires running instance). Generate once, use from any agent session.

### OpenFOAM

**Current state of headless automation:**

OpenFOAM is already CLI-native by design. Every solver, utility, and post-processor runs from the command line:

```bash
blockMesh                           # generate mesh
simpleFoam                          # run solver
foamPostProcess -func "wallShearStress"  # post-process
foamDictionary -entry "internalField" -set "uniform (0 0 0)" 0/U  # edit case files
```

The entire OpenFOAM workflow — case setup, meshing, solving, post-processing — is driven by text dictionary files and CLI commands. Automation is typically done via shell scripts (e.g., `Allrun`, `Allclean`).

**CLI-Anything value-add for OpenFOAM:**

Minimal. OpenFOAM is already fully CLI-driven. A CLI-Anything wrapper would add a layer of abstraction over commands that are already well-structured for terminal use. The `foamDictionary` utility already provides structured dictionary editing from the command line.

What would help more: a SKILL.md file documenting common OpenFOAM workflows for agent discovery, without the overhead of a wrapper CLI.

**Recommendation: Defer** — OpenFOAM does not need a CLI wrapper. Write a SKILL.md manually instead.

### QGIS

**Current state of headless automation:**

QGIS ships `qgis_process`, a standalone CLI for running Processing algorithms headlessly:

```bash
qgis_process run native:buffer -- INPUT=source.shp DISTANCE=2 OUTPUT=buffered.shp
qgis_process run native:buffer -- INPUT=source.shp DISTANCE=2 OUTPUT=buffered.shp --json
qgis_process list                   # list all available algorithms
qgis_process help native:buffer     # show algorithm parameters
```

Key capabilities:
- Runs without QGIS GUI / window manager
- Supports `--json` output natively
- Exposes all Processing algorithms (native, GDAL, GRASS, SAGA)
- PyQGIS scripting available for complex workflows

**CLI-Anything value-add for QGIS:**

Low. `qgis_process` already provides structured CLI access with JSON output — exactly what CLI-Anything generates. The existing tool has better coverage since it wraps the entire Processing framework (500+ algorithms) and is maintained by the QGIS team.

What would help more: a SKILL.md cataloging common `qgis_process` workflows for GIS operations relevant to our pipelines.

**Recommendation: Defer** — `qgis_process` already provides what CLI-Anything would generate. Write a SKILL.md for agent discovery.

---

## Feasibility of Unified CLI Wrapper Approach

The issue asks about a unified approach. Assessment:

| Factor | Assessment |
|---|---|
| **GUI-first apps (Blender)** | High value — CLI-Anything bridges the discoverability gap |
| **CLI-native apps (OpenFOAM)** | Low value — wrapper adds unnecessary abstraction |
| **Apps with existing CLI (QGIS)** | Low value — `qgis_process` already covers this |
| **Token cost** | One-time per app, but significant (full 7-phase pipeline) |
| **Maintenance** | Generated CLIs may drift from upstream app updates |
| **CLI-Hub reuse** | Blender CLI already in CLI-Hub; reduces generation cost to install |

The unified approach makes sense only for applications that lack structured CLI interfaces. For CLI-native tools, a SKILL.md file providing agent-discoverable documentation is cheaper and more maintainable.

---

## Comparison: CLI-Anything vs MCP vs Manual SKILL.md

| Dimension | CLI-Anything | MCP Server | Manual SKILL.md |
|---|---|---|---|
| **Setup cost** | Medium (install plugin, run generation or install from CLI-Hub) | High (install server, configure socket) | Low (write documentation) |
| **Runtime cost** | Zero tokens (CLI calls) | Per-call token cost | Zero (agent reads once) |
| **Headless** | Yes | Requires running app instance | N/A (documentation) |
| **Discoverability** | SKILL.md auto-generated | MCP tool listing | Manual |
| **Maintenance** | Re-generate on app updates | Server must track API changes | Manual updates |
| **Best for** | GUI apps without CLI | Interactive/stateful workflows | CLI-native apps |

---

## Recommendation Summary

| Application | Recommendation | Rationale |
|---|---|---|
| **CLI-Anything (tool)** | **Trial** | Promising for GUI-first apps; install plugin and test with Blender |
| **Blender** | **Trial via CLI-Anything** | Install pre-built CLI from CLI-Hub; test with existing 3D/viz workflows |
| **OpenFOAM** | **Defer CLI-Anything** | Already CLI-native; write SKILL.md for agent discovery instead |
| **QGIS** | **Defer CLI-Anything** | `qgis_process` already provides structured CLI + JSON; write SKILL.md instead |

---

## Installation

**Installed:** 2026-03-31

CLI-Anything is not a single PyPI package. It is a plugin framework + registry of per-application CLI harnesses. Each harness (Blender, GIMP, etc.) is installed separately from the GitHub repo.

### Venv Setup

```
Path:    /mnt/local-analysis/cli-anything-env
Python:  3.12.3
Created: python3 -m venv --without-pip (bootstrapped pip via get-pip.py)
```

### Blender CLI Harness

```
Package: cli-anything-blender 1.0.0
Install: pip install -e . (from cloned repo: /mnt/local-analysis/cli-anything-repo/blender/agent-harness/)
Entry:   cli-anything-blender
Deps:    click 8.3.1, prompt-toolkit 3.0.52
```

Verified working:

```
$ cli-anything-blender --help
Commands: animation, camera, light, material, modifier, object, render, repl, scene, session
Options:  --json (JSON output), --project (path to .blend-cli.json)
```

Note: The CLI itself is a wrapper — it requires Blender >= 4.2 installed on the system to execute actual 3D operations. The CLI was installed and verified to load; actual Blender operations require the Blender binary.

### PyPI Availability

There is **no** `cli-anything` package on PyPI. Individual harnesses can be installed directly from GitHub:

```bash
pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=blender/agent-harness
```

### Registry (CLI-Hub)

The repo includes `registry.json` with 30 pre-built CLI harnesses covering: 3D (Blender, FreeCAD, CloudCompare), image (GIMP, Inkscape, Krita), video (Kdenlive, Shotcut), audio (Audacity, MuseScore), office (LibreOffice, Zotero), AI (ComfyUI, Ollama, Novita), diagrams (Draw.io, Mermaid), and others. No OpenFOAM harness exists (as expected — OpenFOAM is already CLI-native).

### FreeCAD Harness (Notable)

FreeCAD CLI harness is also available (v1.1.0, 258 commands covering Part, Sketcher, PartDesign, Assembly, Mesh, TechDraw, Draft, FEM, CAM). This could be relevant for parametric CAD workflows.

---

## Next Steps

1. **Install CLI-Anything plugin** in Claude Code on dev-secondary (per issue label)
2. **Install Blender CLI from CLI-Hub** — `pip install blender-cli` (or equivalent from registry)
3. **Test Blender CLI** with a headless render workflow: load .blend, modify parameters, render
4. **Write SKILL.md files** for OpenFOAM and QGIS `qgis_process` (manual, no CLI-Anything needed)
5. **Evaluate token cost** of running CLI-Anything generation on a small app to calibrate cost expectations
6. **Check CLI-Hub** for other domain tools relevant to engineering workflows (e.g., FreeCAD, ParaView)

---

## References

- [CLI-Anything GitHub](https://github.com/HKUDS/CLI-Anything) — 21k+ stars, MIT
- [CLI-Hub Registry](https://hkuds.github.io/CLI-Anything/) — browse/install pre-built CLIs
- [CLI-Anything HARNESS.md](https://github.com/HKUDS/CLI-Anything/blob/main/cli-anything-plugin/HARNESS.md) — core SOP document
- [CLI-Anything Deep Dive (yage.ai)](https://yage.ai/share/cli-anything-harness-survey-en-20260316.html) — technical analysis
- [CLI-Anything Guide (apidog)](https://apidog.com/blog/how-to-use-cli-anything/) — usage tutorial
- [CLI-Anything Medium Article](https://medium.com/@mingyang.heaven/cli-anything-turning-any-gui-software-into-an-ai-agent-tool-in-one-command-0255115bc397) — overview
- [Blender CLI Reference](https://docs.blender.org/api/current/info_tips_and_tricks.html) — Python API tips
- [Blender Headless Guide](https://renderday.com/blog/mastering-the-blender-cli) — CLI automation
- [Blender MCP (ahujasid)](https://github.com/ahujasid/blender-mcp) — MCP server alternative
- [OpenFOAM CLI Guide](https://www.openfoam.com/documentation/guides/latest/doc/openfoam-guide-command-line.html) — official CLI docs
- [OpenFOAM Post-processing CLI](https://doc.cfd.direct/openfoam/user-guide-v13/post-processing-cli) — foamPostProcess
- [QGIS qgis_process](https://docs.qgis.org/3.44/en/docs/user_manual/processing/standalone.html) — standalone CLI
- [QGIS Processing Command Line (Spatial Thoughts)](https://spatialthoughts.com/2022/07/30/qgis_process_command_line/) — practical guide
- [Chase AI Source Article](https://www.chaseai.io/blog/10-cli-tools-that-make-claude-code-unstoppable) — original reference from issue
