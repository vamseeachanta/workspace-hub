# Telegram/Hermes readiness: fail-closed and redaction lessons

Session learning from a Telegram/Hermes multi-machine control-plane readiness implementation.

## Problem class

Readiness scripts that decide whether a workstation may receive automated Telegram/Hermes dispatch must be stricter than ordinary inventory scripts. They often combine:

- local control-plane checks,
- remote worker checks,
- registry metadata,
- provider/program status,
- Git/worktree state,
- and human/private Telegram identifiers.

Two recurring defects are easy to introduce:

1. **OS-scoped readiness gaps** — key fail-closed checks are accidentally placed inside a Linux-only branch, so local dispatch-enabled macOS/Windows hosts can pass without verified workspace, Git, or data-root evidence.
2. **Partial redaction paths** — CLI/report rendering uses a local ad hoc redactor instead of the stronger Telegram dispatch redactor, allowing freeform evidence strings to leak chat IDs, allowlists, invite links, or phone numbers.

## Durable rules

### Dispatch-enabled local hosts fail closed on evidence gaps regardless of OS

For every dispatch-enabled host that represents the current/local machine, apply local evidence checks even when `os` is not `linux`:

- workspace root exists,
- `AGENTS.md`/repo contract exists when required,
- Git metadata is present,
- dirty/ahead/behind state is known,
- required local data roots/mounts exist or are explicitly marked unavailable,
- program/provider status is checked through the same launch environment used for dispatch.

Do not infer readiness from CLI/env checks alone. If workspace/Git/data evidence is missing, emit `status: fail` and `dispatchable: false`.

Remote hosts still need host-local evidence collected through the actual remote launch path; do not substitute control-plane filesystem checks for remote state.

### Readiness output must use Telegram-private redaction

Any CLI/report/JSON/YAML rendering of readiness evidence should use the same redaction path as Telegram dispatch status rendering, or delegate to it.

Redact actual private values in both structured fields and freeform failure/warning strings:

- `chat_id` values such as `-1009876543210`,
- allowlist/user ID values such as `12345,67890`,
- invite URLs such as `https://t.me/+...`,
- phone numbers, including already partially masked forms when they still identify a contact,
- bot tokens or token-shaped values.

Keep env-var **names** visible because they are operational pointers, for example:

- `TELEGRAM_HERMES_BOT_TOKEN`,
- `TELEGRAM_HERMES_ALLOWED_USER_IDS`,
- `bot_token_env`,
- `allowed_user_ids_env`.

## Regression tests to require

Add tests that fail before the fix:

1. **Local non-Linux dispatch host test**
   - Registry host has `dispatch_enabled: true`, `os: macos` or `os: windows`, and matches the current hostname/local host.
   - Workspace/data/git evidence is missing.
   - Assert readiness result is fail-closed: `status == "fail"`, `dispatchable is False`, and failures mention missing workspace/data/git evidence.

2. **Readiness-level Telegram redaction test**
   - Inject remote/local evidence failure text containing values like:
     - `chat_id=-1009876543210`
     - `allowlist=12345,67890`
     - `invite=https://t.me/+abc`
     - `phone=+155****4567`
   - Render the readiness output exactly as the CLI/report path renders it.
   - Assert none of those private values appear, while non-sensitive operational status remains visible.

## Review prompt cue

When adversarially reviewing this class of code, ask reviewers to hunt specifically for:

- readiness checks gated by `if os == "linux"` or equivalent,
- absent-field defaults that imply clean/safe state,
- separate redaction functions that drift apart,
- freeform evidence strings bypassing structured redaction,
- env-var names being over-redacted while actual private values remain.
