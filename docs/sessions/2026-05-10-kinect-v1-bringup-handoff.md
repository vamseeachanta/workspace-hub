# 2026-05-10 — Kinect v1 bring-up on ace-linux-1 (handoff)

## Status: paused at "ready to install"

User plugged a **Kinect for Xbox 360 (v1)** into `ace-linux-1` and asked Claude to verify the device was visible from Linux. Verified, then took the first reconnaissance step (read-only probes only). Install + udev + smoke-test was prepared but **not executed** — paused for user review before any `sudo` action.

## Hardware confirmed

| USB ID | Sub-device | Bus / Device |
|---|---|---|
| `045e:02c2` | Motor (tilt + accelerometer) | Bus 2 Device 63 |
| `045e:02be` | Audio (4-mic array) | Bus 2 Device 64 |
| `045e:02bf` | Camera (RGB + IR + depth) | Bus 2 Device 65 |

- Host: `ace-linux-1`, Linux 6.17.0-23-generic, Ubuntu 24.04
- All three endpoints enumerated; descriptor string is "Kinect for Windows NUI" (Microsoft's branding — still the original v1, not v2 `02c4/02d8` nor Azure Kinect `097a`)
- Requires the 12V external power brick (confirmed all three sub-devices visible → power is fine)

## Current driver state (the blocker)

| Item | State | Notes |
|---|---|---|
| `gspca_kinect` kernel module | LOADED, bound to `/dev/video0` | Exposes RGB only as a generic V4L2 webcam. **Claims the camera USB endpoint** and will prevent `libfreenect` from opening it. |
| `/dev/video0` consumer | None (`lsof` empty) | Free to release. |
| `libfreenect` (apt + libs) | NOT installed | `dpkg -l | grep freenect` empty; no `libfreenect.so` in linker cache. |
| `freenect-glview` / `freenect-camtest` | NOT installed | |
| Python `freenect` binding | NOT installed | Miniforge `python3` present; `uv` available at `~/.local/bin/uv`. |
| Udev rules for Kinect | NOT present | USB nodes are `crw-rw-r-- root:root` — `vamsee` can read but **not write**. libusb control transfers need write → libfreenect would fail with `LIBUSB_ERROR_ACCESS`. |
| User group membership | `vamsee` already in `plugdev` | No `usermod` needed; a udev rule with `GROUP="plugdev"` will unlock it without sudo on every run. |

## Resume sequence (reversible, no reboot)

When the user is ready to proceed, execute these four blocks in order. Each is reversible.

### 1. Release `gspca_kinect` (runtime + persistent)

```bash
sudo modprobe -r gspca_kinect gspca_main
echo 'blacklist gspca_kinect' | sudo tee /etc/modprobe.d/blacklist-kinect.conf
```

Reverse: `sudo rm /etc/modprobe.d/blacklist-kinect.conf && sudo modprobe gspca_kinect`.

### 2. Install libfreenect from apt

```bash
sudo apt update
sudo apt install -y libfreenect0.5 libfreenect-dev libfreenect-bin python3-freenect
```

Reverse: `sudo apt remove --purge libfreenect0.5 libfreenect-dev libfreenect-bin python3-freenect`.

### 3. Udev rule (covers v1 PIDs only — extend if a v2 or Azure Kinect ever lands)

```bash
sudo tee /etc/udev/rules.d/51-kinect.rules >/dev/null <<'EOF'
# Microsoft Kinect for Xbox 360 (v1)
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02bf", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02be", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02c2", MODE="0660", GROUP="plugdev"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
```

After this, unplug + replug the Kinect (or `udevadm trigger` alone usually suffices). USB nodes for `045e:02bf/02be/02c2` should become `crw-rw---- root:plugdev`.

Reverse: `sudo rm /etc/udev/rules.d/51-kinect.rules && sudo udevadm control --reload-rules`.

### 4. Smoke test (one depth frame + one RGB frame, no sudo)

```bash
python3 -c "
import freenect, numpy as np
depth, _ = freenect.sync_get_depth()
rgb,   _ = freenect.sync_get_video()
np.save('/tmp/kinect_depth.npy', depth)
np.save('/tmp/kinect_rgb.npy', rgb)
print('depth:', depth.shape, depth.dtype, 'min', int(depth.min()), 'max', int(depth.max()))
print('rgb:  ', rgb.shape, rgb.dtype)
"
```

Expected:
- `depth: (480, 640) uint16  min ~0  max ~2047` (11-bit raw disparity; ~0 = invalid pixel)
- `rgb:   (480, 640, 3) uint8`

If this prints both lines, the bring-up is complete. Frames are saved to `/tmp/` (ephemeral) — fine for smoke test.

## What we have NOT decided yet

User has not specified the **end use**. Branching choices once the smoke test passes:

| Goal | Toolchain to add next |
|---|---|
| Depth → point cloud / 3D scan | `open3d` (`uv pip install open3d`) — registers RGB + depth into colored point clouds, exports `.ply` |
| Body / pose tracking | MediaPipe Pose on the RGB feed; optional fusion with depth for 3D joint coords. Avoid the legacy OpenNI/NiTE stack unless specifically needed |
| Mic-array beamforming / voice direction | libfreenect's audio API (firmware upload required on first connect — handled automatically by `libfreenect-bin`) |
| RGB-as-virtual-webcam for Zoom/OBS | `v4l2loopback-dkms` + a `freenect-camtest` → `/dev/video10` bridge. Skip until needed |
| Marine/engineering visualization (e.g., motion capture for OrcaFlex overlay) | Open3D point clouds; possibly export `.ply` per frame for offline registration |

## Gotchas captured for next session

1. **`gspca_kinect` is a trap.** It will silently claim the camera USB endpoint and libfreenect will fail with cryptic libusb errors. Always blacklist before troubleshooting depth.
2. **`LIBUSB_ERROR_ACCESS` ≠ broken Kinect.** It almost always means the udev rule is missing or stale. Re-check `ls -la /dev/bus/usb/002/{063,064,065}` for `plugdev` ownership.
3. **`dmesg` permission denied on this host.** `kernel.dmesg_restrict=1` (Ubuntu default). Use `sudo dmesg` or `journalctl -k` instead.
4. **Don't trust the USB descriptor string.** It says "Kinect for Windows" but the PIDs are the original Xbox 360 v1 — the "Kinect for Windows" SKU (model 1517) used the same PIDs. Both work identically under libfreenect.
5. **v1 depth range is ~0.8 m to ~4 m.** Closer or farther returns invalid pixels (raw value `2047`). If smoke test shows `max == 2047` and `min == 2047`, the sensor is pointed at something too close or too dark — point it at a wall ~2 m away.

## How to resume next session

```
cd /mnt/local-analysis/workspace-hub
cat docs/sessions/2026-05-10-kinect-v1-bringup-handoff.md
# Then run blocks 1-4 above, or ask Claude to run them.
```

No GitHub issue filed — this is a personal-machine hardware experiment, not workspace-hub project work. If the use case crystallizes into something repo-relevant (e.g., motion-capture overlay for marine viz), open an issue then.
