---
name: phone-media-pull
version: "1.0.0"
category: operations
description: "Run the family iPhone photo/video pull on the archive host with the owner: copy DCIM at full quality, verify, back up to Google Drive, and produce a verified safe-to-delete list. Never deletes on the phone."
tags: [phone-media, iphone, afc, rsync, rclone, backup, family]
type: procedure
---

# Phone media pull (iPhone to archive host and Google Drive)

Script: `scripts/phone_media/phone_pull.sh` (helper `phone_pull.py`).
Issues: #3584 (pull), #3586 (Drive capacity and checks), epic #3589.

## Ground rules

- Private family media. It stays on ace-linux-1 (`/mnt/ace/ws/phone-media`)
  and the owner's Google Drive (`gdrive:backups/phone-media`). Never paste
  file names, counts per file, EXIF data or report contents into an issue,
  PR, commit, chat summary or log off that host. Totals (files, GB) are fine.
- Never on rds02. The phone is plugged into ace-linux-1.
- The script never deletes on the phone. The owner deletes in the Photos app.
- No sudo. If a tool is missing, list it for the owner.

## Steps with the owner

1. **Dry run first if the script changed** (no phone needed):
   `ssh ace-linux-1 'cd ~/workspace-hub && scripts/phone_media/phone_pull.sh --dry-run --simulate-drive-missing 1'`
   Expect one file on the not-safe list.
2. **Ask the owner to prepare the phone** (one message, all items):
   - Plug it into ace-linux-1 with a data cable (not a charge-only cable).
   - Unlock it. When "Trust This Computer?" appears, tap **Trust** and enter
     the passcode. If no prompt appears and the run says the phone is not
     found, unplug, replug and unlock again.
   - Settings > Display & Brightness > **Auto-Lock > Never** for the pull
     (iOS hides photos over USB once it locks). Keep it on the cable.
   - Settings > Photos: if **iCloud Photos** is on with **Optimize iPhone
     Storage**, older items exist on the phone only as small copies. Either
     switch to "Download and Keep Originals" and wait until it finishes, or
     accept that those items are not pulled at full quality.
   - The archive folder name for this phone (`iphone-<name>`, lowercase).
3. **Run it** (long: about 1 minute per 1.4 GB over USB; run in the background
   and watch `reports/run-*/rsync.log`):
   `ssh ace-linux-1 'cd ~/workspace-hub && scripts/phone_media/phone_pull.sh --phone iphone-<name>'`
   Add `--youtube-plan` for the YouTube list, `--jpeg` for JPEG copies of HEIC,
   `--hash-phone` to re-read and hash every phone file (slower, strongest).
4. **Read the outcome** from the terminal: preflight (space on /mnt/ace >= 2x
   the phone, Drive free space), reconcile counts, verify `N of N`, the two
   rclone check exits, then the safe-to-delete summary. Exit 0 = all steps
   passed. Non-zero: read the named log under `<phone>/reports/run-*/` on the
   host and report only the step and exit code.
5. **Tell the owner** the summary lines only: files and GB safe to delete,
   photos vs videos, and the "Everything taken on or before <date>" line. He
   deletes in Photos (Select, bin), then Albums > Recently Deleted > Delete
   All. Warn him: with iCloud Photos on, deleting on the phone also deletes in
   iCloud and on his other devices.
6. **Ask him to set Auto-Lock back** (for example 30 seconds or 1 minute).

## Exit codes

| code | meaning |
|---|---|
| 3 | phone not found, locked, untrusted, or DCIM empty |
| 4 | not enough space on /mnt/ace (needs 2x the phone's DCIM) |
| 5 | Drive not reachable (`rclone about` failed; token may need the owner's sign-in: `rclone config reconnect gdrive:` in his terminal) |
| 9 | reconcile: some phone files were not copied (see `rsync.log`) |
| 6 | verify: some files do not match the phone (see `manifest.tsv` status) |
| 8 | Drive too full: backup skipped, nothing is safe to delete (#3586) |
| 11 | `rclone copy` failed (see `rclone-copy.log`); rerun `--steps backup,safe-list` |
| 10 | a Drive check found missing or different files; they stay off the safe list |
| 7 | optional JPEG step failed for some files |

The highest code wins; the safe-to-delete list is still written and only
holds files that passed every check.

Resume later steps without re-pulling: `--steps verify,backup,safe-list`
(uses `reports/LATEST`; the phone must still be attached for verify).

## Outputs (on ace-linux-1 only)

- `<phone>/usb/` canonical originals (HEIC, JPG, PNG, MOV, MP4, AAE). A phone
  file whose name is taken by a different archive file is kept beside it as
  `<stem>__phone-<sha8><ext>`; nothing is overwritten.
- `<phone>/reports/run-<stamp>/manifest.tsv` path, size, SHA-256, capture
  date (exiftool when installed, else file time), status.
- `<phone>/reports/safe-to-delete-<stamp>.{tsv,txt}` and `not-safe-<stamp>.tsv`.
  Listed only when the local check AND the Drive size check AND the Drive
  hash check (MD5) all passed.
- `<phone>/reports/youtube-plan-<stamp>.{tsv,txt}` (with `--youtube-plan`):
  prepared, never run. Needs the owner's Google Cloud OAuth client and his
  YouTube sign-in on first use; secrets live in `~/.config/phone-media/youtube/`
  on the host, never in a repository.
- `<phone>/usb-jpeg/` (with `--jpeg`): JPEG copies; originals untouched.

## Optional installs (owner, sudo)

None are required. `sudo apt install libimage-exiftool-perl` gives EXIF
capture dates in the manifest (otherwise file time, which AFC sets to the
capture time). `libimobiledevice-utils` is not needed: gvfs (installed)
handles pairing and mounting.
