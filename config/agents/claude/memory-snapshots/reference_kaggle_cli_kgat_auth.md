---
name: Kaggle CLI auth via KGAT access token
description: Modern Kaggle CLI 2.x reads `~/.kaggle/access_token` (38-byte ASCII, KGAT prefix), not legacy `~/.kaggle/kaggle.json` JSON wrapper
type: reference
originSessionId: 5f3bc58a-2c99-432c-bb4f-e70962bc3556
---
The Kaggle CLI (≥2.0, verified at 2.1.1 on 2026-05-05) supports two credential formats:

1. **Legacy** (most online docs still show this): `~/.kaggle/kaggle.json` containing `{"username":"...","key":"..."}` — generated via Kaggle Settings → API → "Create API Token" (downloads `kaggle.json`)
2. **Modern** (Kaggle Access Token / KGAT): `~/.kaggle/access_token` containing a single 38-byte ASCII line beginning with `KGAT` — generated via Kaggle Settings → API → "Personal Access Token"

**Both work.** The CLI checks `access_token` first, falls back to `kaggle.json`. If only one is present and it's the right format, no further config is needed.

When verifying, "No datasets found" from `kaggle datasets list -s "<term>" --max-size 1` is a **success signal** (auth accepted, query returned 0 results due to size filter). Auth failure surfaces as `401`/`403`.

Install path on Linux with uv-managed tooling:
```bash
uv tool install kaggle             # binary lands at ~/.local/bin/kaggle
export PATH="$HOME/.local/bin:$PATH"  # not on default PATH; needed in scripts/cron
```
