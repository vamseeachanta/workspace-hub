# Rawvideo + ffmpeg Headless Rendering Fallback

Use this pattern when the task is to deliver a visual engineering animation/video and a full VTK/PyVista/ParaView rendering stack is temporarily unavailable, unstable in the current runtime, or unnecessarily heavy for a first-pass visualization.

This is not a replacement for validated CFD/FSI/FEA visualization. It is a deterministic fallback for producing a clearly labeled approximation, proof-of-concept animation, or progress artifact.

## Pattern

1. Define the physical scope and label simplifications up front:
   - geometry and units,
   - simulated duration vs video duration/time compression,
   - whether the model is visualization-only or solver-backed,
   - omitted physics.
2. Generate RGB frames directly with Python numeric code.
3. Pipe frames to `ffmpeg` using `rawvideo` to avoid dependencies on PIL, matplotlib, imageio, OpenCV, or GUI backends.
4. Verify with `ffprobe` and extract one preview frame for visual sanity checking before delivery.
5. In the final response, distinguish:
   - requested renderer/solver path,
   - actual renderer used,
   - verification evidence,
   - assumptions/limitations.

## Minimal skeleton

```python
import subprocess
import numpy as np

width, height = 1280, 720
fps = 12
frames = 360
out = "animation.mp4"

cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-pix_fmt", "rgb24",
    "-s", f"{width}x{height}",
    "-r", str(fps),
    "-i", "-",
    "-an",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    out,
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
try:
    for i in range(frames):
        # Replace with deterministic engineering visualization logic.
        img = np.zeros((height, width, 3), dtype=np.uint8)
        t = i / fps
        img[..., 2] = 80
        img[..., 1] = np.clip(80 + 40*np.sin(t), 0, 255).astype(np.uint8)
        proc.stdin.write(img.tobytes())
finally:
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {rc}")
```

## Verification commands

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,duration,nb_frames \
  -show_entries format=size,duration \
  -of default=noprint_wrappers=1 animation.mp4

ffmpeg -y -ss 1 -i animation.mp4 -frames:v 1 preview.jpg
```

## Reporting contract

Never imply the fallback artifact was rendered by PyVista/ParaView/VTK if it was not. Say exactly what rendered it, why that route was used, and what validation was performed.
