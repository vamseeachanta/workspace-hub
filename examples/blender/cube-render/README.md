# Blender cube-render smoke manifest

## Overview

`cube-render` is the canonical repo-tracked Blender smoke case for issue #2270. It uses procedural scene generation only: a default cube, one camera, one light, and a single PNG frame.

## Prerequisites

- Run on `dev-secondary` or another host with Blender available as `blender` on `PATH`.
- Use `BLENDER_BIN=/path/to/blender` when the binary is not on `PATH`.
- Use the workspace root as the command working directory.

## Commands

```bash
bash scripts/blender/verify-blender-baseline.sh
```

Direct smoke script invocation:

```bash
blender -b --factory-startup --python scripts/blender/smoke-render.py -- --output /tmp/cube-render_frame-0001.png --metadata /tmp/cube-render_frame-0001.metadata.yaml
```

## Expected Outputs

- Default verdict: `logs/engineering/blender-baseline/latest-verdict.yaml`
- Render output: `cube-render_frame-0001.png`
- Metadata output: `cube-render_frame-0001.metadata.yaml`
- The validator checks PNG signature, metadata schema, scene name, frame number, EEVEE engine selection, resolution, camera, and cube object structure.

## Failure Modes

- Missing Blender binary: set `BLENDER_BIN` or install Blender on the execution host.
- Headless display crash: run through `xvfb-run -a` or configure the host display/EGL stack.
- Metadata validation failure: inspect the metadata file named in the verdict and compare against the expected `cube-render` schema.
- Render output failure: inspect Blender stderr and confirm the output directory is writable.

Rendered `.png`, `.jpg`, `.jpeg`, and `.blend` outputs are generated artifacts and should not be committed under this manifest path.
