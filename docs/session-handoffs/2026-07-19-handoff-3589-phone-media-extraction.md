# Session Handoff — Family Phone-Media Extraction Pipeline (EPIC #3589)

**Date:** 2026-07-18 → 2026-07-19 · **Host:** ace-linux-1 · **Epic:** #3589 (children #3584–#3588)

## Outcome

Both available family iPhones fully extracted at ORIGINAL quality and archived 3-2-1
(phone + ace-linux-1 disk + Google Drive, every copy count-verified):

| Device | Files | Size | Local | Drive (`gdrive:backups/phone-media`) |
|---|---|---|---|---|
| iphone-14 | 958 | 6.0 GB | `phone-media/iphone-14/usb/` | rclone check 958/958, 0 diff |
| iphone-sabitha | 711 | 22 GB | `phone-media/iphone-sabitha/usb/` | rclone check 711/711, 0 diff |

Drive after upload: 27.3 GiB used in backups/phone-media, **30.4 GiB free** —
capacity decision (#3586) gates the next video-heavy phone. Krishna has no phone.

## What was built (all persistent)

- **USB/AFC pull playbook** — the winning bulk path (~24 MB/s, guaranteed originals).
  Full runbook in `/mnt/local-analysis/phone-media/README.md`.
- **Taildrop lane** — `taildrop-receive.service` drains phone share-sheet sends into
  `iphone-14/inbox/` (verified end-to-end).
- **WebDAV lane** — `webdav-photosync.service`, rclone WebDAV on 127.0.0.1:8080
  (tailnet-reachable via userspace-tailscaled localhost proxy), serving `auto/`;
  kept alive for future PhotoSync use. Creds: `~/.config/webdav-photosync.env`.
- **tailscaled migrated nohup → systemd** (`tailscaled-userspace.service`) after the
  socket-clash crash-loop was diagnosed and fixed.

## Key traps discovered (banked in auto-memory topic file)

1. PhotoSync free tier silently downsizes photos to **800×600** (videos untouched) —
   verify with `file` (pixel dims), not byte counts. Fix: Photo Transfer Size → Actual Size.
2. iOS exposes DCIM over USB **only while unlocked**; gvfs `...,port=3` mount is
   app-documents, media needs `gio mount afc://<UDID>/`.
3. nohup daemon + systemd unit on one socket → `address already in use` crash-loop
   every 5 s; `Requires=` propagates the bounce to dependent units. Journal verb
   tells the story: "Stopping" = dependency bounce, "Failed" = own crash.
4. iOS is push-only — no remote pull of a camera roll exists. Taildrop renames to
   UUIDs (EXIF intact); AFC/USB keeps IMG_xxxx names and capture-date mtimes.

## Open work (epic #3589)

- #3584 pull remaining family phones (playbook in phone-media README)
- #3585 EXIF-date organizer + cross-phone dedupe
- #3586 **off-site capacity plan** + weekly rclone-check cron ← work this first
- #3587 choose ongoing incremental sync lane (USB habit / PhotoSync Premium / icloudpd)
- #3588 evaluate Immich/PhotoPrism family photo browser (tailnet-only)
