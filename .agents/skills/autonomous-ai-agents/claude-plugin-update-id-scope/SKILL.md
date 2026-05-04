---
name: Codex-plugin-update-id-scope
description: Fix Codex plugin update failures caused by using the short plugin name instead of the installed plugin id and wrong scope.
---

# Codex plugin update: use installed id + scope

Use this when `Codex plugin update <name>` reports `Plugin "<name>" not found` even though `Codex plugin list` shows the plugin installed.

## Root cause

Codex plugin updates can fail when automation uses only the short plugin name (for example `superpowers`) and/or assumes the default scope (`user`).

In practice, the updater may require:
- the actual installed plugin id from `Codex plugin list --json`, such as `superpowers@Codex-plugins-official`
- the actual installed scope, such as `project`

Example failure:
- Installed: `superpowers@Codex-plugins-official`, scope `project`
- Failing command: `Codex plugin update superpowers`
- Working command: `Codex plugin update superpowers@Codex-plugins-official --scope project`

## Debug workflow

1. Inspect help first:
```bash
Codex plugin update --help
Codex plugin list --help
```

2. Read installed plugins as JSON:
```bash
Codex plugin list --json
```

3. Extract the target plugin entry and capture:
- `id`
- `scope`
- `version`
- `enabled`

4. Retry update using the full installed id and explicit scope:
```bash
Codex plugin update <plugin-id> --scope <scope>
```

5. Re-run inventory after update and compare before/after.

## Automation pattern

For scripts:
1. call `Codex plugin list --json`
2. parse plugin entries where `id` matches the target family (for example startswith `superpowers@`)
3. for each installed scope, run:
```bash
Codex plugin update "$plugin_id" --scope "$scope"
```
4. treat the JSON inventory as the health source of truth
5. only fall back to legacy git checkout logic if JSON inventory returns no installed plugin

## Verification

- Dry run or summary should show the detected scope/version, e.g.:
  - `project:5.0.7:true`
- Successful update output should mention the full plugin id and correct scope.
- Regression test should assert all of:
  - script uses `Codex plugin list --json`
  - script filters installed entries by plugin family (for example `plugin_id.startswith("superpowers@")`)
  - script updates with `Codex plugin update "$plugin_id" --scope "$scope"`
- In workspace-hub, a concrete regression test was added at:
  - `tests/work-queue/test-harness-update-superpowers.sh`

## Known working example

For an installed entry:
- id: `superpowers@Codex-plugins-official`
- scope: `project`

The short-name command fails:
```bash
Codex plugin update superpowers --scope project
```

The full-id command succeeds:
```bash
Codex plugin update superpowers@Codex-plugins-official --scope project
```

## Pitfalls

- Default update scope is `user`; project-installed plugins will fail if scope is omitted.
- `Codex plugin list` text output is less reliable than `--json` for automation.
- A plugin can appear installed locally while automation still fails if it uses the short name rather than the installed id.
- Windows rollout depends on repo sync actually pulling latest `main`; verify scheduler cadence and machine reachability separately.
