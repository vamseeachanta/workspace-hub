---
name: client-llm-wiki-factory
description: Bootstrap a registered private client wiki from the committed generic template.
version: 2.0.0
category: coordination
tags:
- client-wiki
- factory
- privacy-firewall
- metadata-only
---

# Client LLM-Wiki Factory

## Use when

- An approved issue authorizes one new private client-wiki bootstrap.
- The authoritative private registry has an exact schema-`0.2` row with
  `status: planned`, `visibility: PRIVATE`, `posture: client-private`, and
  `ingestion_enabled: false`.
- The row is either metadata-only or source-registered-disabled.

Do not use this factory for an existing bootstrapped/live wiki, a migration, raw
ingestion enablement, project setup, or client-specific content. The public
relocated registry stub never grants bootstrap authority.

## Required environment

```bash
set -euo pipefail
while IFS='=' read -r name _; do
  [[ "$name" == GIT_* ]] && unset "$name"
done < <(env)
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
WORKSPACE_HUB="$(git rev-parse --show-toplevel)"
REGISTRY="${WIKI_SIBLING_REGISTRY_PATH:?set the authoritative private registry path}"
SHORT="${CLIENT_WIKI_SHORT_NAME:?set the approved registry short_name}"
AUTHOR_NAME="${CLIENT_WIKI_GIT_AUTHOR_NAME:?set the approved author name}"
AUTHOR_EMAIL="${CLIENT_WIKI_GIT_AUTHOR_EMAIL:?set the approved author email}"
MANIFEST_DIR="${CLIENT_WIKI_MANIFEST_DIR:?set an external private evidence directory}"
REGISTRY_UPDATE_TOOL="${CLIENT_WIKI_REGISTRY_UPDATE_TOOL:?set the authoritative registry updater}"
export CLIENT_WIKI_GIT_AUTHOR_NAME="$AUTHOR_NAME"
export CLIENT_WIKI_GIT_AUTHOR_EMAIL="$AUTHOR_EMAIL"
export PYTHONPATH="$WORKSPACE_HUB/scripts${PYTHONPATH:+:$PYTHONPATH}"
```

The registry path must point to the owning private repository or its approved
provisioned copy. Raw-root availability is not a bootstrap prerequisite, and no
raw path is accepted as a command-line argument.

## Bootstrap sequence

Run the steps in this order. Stop on every failed command.

### 1. Validate and classify registered state

```bash
uv run --directory "$WORKSPACE_HUB" --frozen python -m client_llm_wiki.bootstrap_contract validate-registry --registry "$REGISTRY"
PREFLIGHT="$(uv run --directory "$WORKSPACE_HUB" --frozen python -m client_llm_wiki.bootstrap_contract classify --registry "$REGISTRY" --short-name "$SHORT")"
REPO="$(yq -r '.repo' <<<"$PREFLIGHT")"
TARGET="$(yq -r '.target' <<<"$PREFLIGHT")"
MODE="$(yq -r '.mode' <<<"$PREFLIGHT")"
STATUS="$(yq -r '.status' <<<"$PREFLIGHT")"
test "$STATUS" = "planned"
printf 'mode=%s status=%s repo=%s target=%s\n' "$MODE" "$STATUS" "$REPO" "$TARGET"
```

`classify` is the single target-derivation authority. Do not reconstruct the
checkout path in shell, pass a destination override, or edit the public stub.

### 2. Create the remote as private

```bash
gh repo create "$REPO" --private --description "Private client knowledge wiki"
```

Immediately attest the live state:

```bash
uv run --directory "$WORKSPACE_HUB" --frozen python -m client_llm_wiki.bootstrap_contract verify-private-repo --repo "$REPO"
```

### 3. Clone the registered repository into the derived target

```bash
git clone "https://github.com/$REPO.git" "$TARGET"
```

The remote must be empty, so the clone has an unborn HEAD, an empty worktree,
the registered origin, and only a real `.git` directory at top level. The
renderer will reject any mismatch before writing.

### 4. Render and finalize the pinned committed template

Capture `.git` identity before rendering, then invoke the contract with only
the authoritative registry and short name:

```bash
test -d "$MANIFEST_DIR"
test ! -L "$MANIFEST_DIR"
test -x "$REGISTRY_UPDATE_TOOL"
MANIFEST="$(mktemp -u --tmpdir="$MANIFEST_DIR" 'client-wiki-render.XXXXXXXX.json')"
uv run --directory "$WORKSPACE_HUB" --frozen python -m client_llm_wiki.bootstrap_contract render \
  --registry "$REGISTRY" --short-name "$SHORT" --manifest "$MANIFEST"
test -s "$MANIFEST"
uv run --directory "$WORKSPACE_HUB" --frozen python -m client_llm_wiki.bootstrap_contract finalize-scaffold \
  --registry "$REGISTRY" --short-name "$SHORT" --manifest "$MANIFEST"
uv run --directory "$WORKSPACE_HUB" --frozen python -m client_llm_wiki.bootstrap_contract verify-private-repo --repo "$REPO"
"$REGISTRY_UPDATE_TOOL" --registry "$REGISTRY" --short-name "$SHORT" \
  --status bootstrapped --local-working-clone "$TARGET"
```

The renderer reads `templates/client-llm-wiki` from the pinned workspace Git
object, ignores dirty/untracked template files, preserves
`<PROJECT_SHORT_NAME>`, and refuses unknown client placeholders.

### 5. Verify the rendered privacy boundary

```bash
test -f "$TARGET/.gitignore"
test -f "$TARGET/.claude/CLAUDE.md"
test -s "$MANIFEST"
if rg --hidden -n '<CLIENT_[A-Z0-9_]+>|<RAW_SOURCE_STATUS>|<INGESTION_ENABLED>' "$TARGET" --glob '!.git/**'; then
  echo >&2 "ABORT: unresolved bootstrap placeholder"
  exit 1
fi
```

No project folders or client-specific rules are added in this initial commit.
The structural ledger example deliberately keeps `source_path: null`.

### 6. Update the authoritative private registry

Only after the scaffold push succeeds, update the same authoritative row:

- `status: planned` → `status: bootstrapped`
- add the approved bootstrap date
- add `local_working_clone` with the exact derived `$TARGET`
- retain `ingestion_enabled: false`
- retain the classified raw-source state unchanged

The required updater belongs to the authoritative private registry repository.
It must perform that repository's reviewed update workflow; this public skill
does not prescribe pathname `git` mutations. Refresh any provisioned local copy
only after the authoritative update succeeds. Because `set -e` places this call
after render, finalization, and PRIVATE/unarchived attestation, every failure
suppresses the registry update.

The finalizer owns commit and transport. It disables ambient configuration and
uses canonical HTTPS with the fixed `credential.helper=!gh auth git-credential`;
do not add shell-level Git mutation instructions.

### 7. Audit and report evidence

```bash
REGISTRY_PATH="$REGISTRY" "$WORKSPACE_HUB/scripts/enforcement/check-client-wiki-registry.sh"
```

First verify that the implementation issue itself is private. Only a verified
private issue may receive the private repository URL, `$SCAFFOLD_SHA`, registry
commit, or private path evidence. A public issue receives only a redacted
attestation: bootstrap succeeded, PRIVATE/unarchived checks passed, the checker
passed, and raw ingestion remains disabled. Never paste registry rows or client
identity-bearing repository slugs into a public issue.

## Post-bootstrap work

Treat project-folder instantiation and redaction customization as separately
reviewed work after the generic scaffold is committed and the registry status
is bootstrapped. Those operations must preserve the privacy firewall and must
not create, copy, enumerate, or ingest raw-source content without a separately
approved private integration contract.

## Abort conditions

- Registry validation/classification fails or identifies a non-planned row.
- Live repository is public, archived, missing, or does not match the row.
- Derived target already exists outside the expected empty clone lifecycle.
- Clone origin, HEAD, status, top-level inventory, `.git`, or firewall differs.
- Renderer manifest is absent or a bootstrap placeholder remains.
- Either private-state attestation fails.
- Any step would enable ingestion or expose private registry data publicly.

## References

- [Issue #3449](https://github.com/vamseeachanta/workspace-hub/issues/3449)
- `scripts/client_llm_wiki/bootstrap_contract.py`
- `scripts/enforcement/check-client-wiki-registry.sh`
- `.claude/rules/wiki-sibling-routing.md`
