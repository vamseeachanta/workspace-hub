---
name: reference_rclone_gdrive_setup
description: rclone is installed and a Google Drive remote (gdrive:) is configured/authorized on this box
metadata: 
  node_type: memory
  type: reference
  originSessionId: 644a1a4e-249f-4334-8181-3612f7e0c4e8
---

rclone v1.74.3 installed at `~/.local/bin/rclone` (no sudo — static binary). A Google Drive remote `gdrive:` is configured and OAuth-authorized as `vamsee.achanta@aceengineer.com`; token persisted in `~/.config/rclone/rclone.conf`, so re-syncs need no re-login.

OAuth was completed via the **Chrome running on this server** (DISPLAY=:1, `/opt/google/chrome/chrome`) — rclone's auto-config callback on `127.0.0.1:53682` is reachable because the browser is local to the box. Same trick works for any future rclone/headless OAuth here.

2026-06-20: mirrored full Drive to `/mnt/ace/gdrive/{my-drive,shared-with-me}` (~4.4 GB, ~8,250 files). No Shared/Team drives exist on the account. Gotchas: rclone's DEFAULT shared OAuth client hits Google's per-minute query quota on big tree walks → throttle with `--tpslimit 5-8`. Google-native Docs/Sheets/Slides export to `.docx/.xlsx/.pptx` (1029 such files). 2 files permanently un-downloadable (Google "cannotDownloadAbusiveFile"; `--drive-acknowledge-abuse` only works for files you OWN) — logged in `/mnt/ace/gdrive/failed-files.txt`. Re-run `rclone copy` to incrementally refresh. NOTE: `/mnt/ace` was 95% full (only ~376 GB free) — size-check with `rclone size` before large pulls.
