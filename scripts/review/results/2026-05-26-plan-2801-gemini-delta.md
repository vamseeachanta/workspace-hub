# Plan Review — #2801 — Gemini (delta on D1/D2/D3, adversarial)

**Provider:** Gemini CLI 0.43.0 (GEMINI_CLI_TRUST_WORKSPACE=true to clear trust-folder gate). Delta only.
**Verdict:** MAJOR (4 MAJOR). Converges with Codex delta on 4 of 5 — cross-provider CONSENSUS.

## MAJOR (consensus with Codex noted)
- **DG1 — commit-on-change broken by volatile fields** [= Codex DC4]. Free disk ('881G') + avail RAM change every run → hash changes → idempotency defeated. Fix: hash + report STATIC fields only (total cores, total RAM capacity, GPU model); volatile headroom is display-only, excluded from hash.
- **DG2 — compute coercion ignores units** [= Codex DC3]. '512Mi'→512 passes a '16Gi'→16 floor. Fix: normalize RAM/disk to a common unit (MiB) before compare; typed floor.
- **DG3 — data_access subset string mismatch** [= Codex MC2]. baseline ['assetutilities'] vs actual ['sibling:/mnt/local-analysis/assetutilities'] never matches. Fix: strip prefix/path → compare bare repo names.
- **DG4 — behavior probe side-effects** [= Codex DC1]. plan-approval-gate.sh likely writes audit log → violates read-only. Fix: verified `--dry-run --no-log` OR mock logging OR redirect HOME/XDG/log to temp; readonly test must cover writes OUTSIDE fixture root.

## Author questions
- Hash stability with fluctuating disk-free? (→ exclude volatile)
- Unit standardization for floor compare? (→ normalize to MiB)
- Does plan-approval-gate.sh have a safe --dry-run/no-log? (→ verify or isolate)
- data_access label vs path normalization for subset? (→ bare repo name)
