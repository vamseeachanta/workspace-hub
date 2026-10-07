---
name: claude-plugin-update-id-scope
description: Fix Claude plugin update failures caused by using the short plugin name instead of the installed plugin id and wrong scope.
---

# Claude plugin update: use installed id + scope

Use this when `claude plugin update <name>` reports `Plugin "<name>" not found` even though `claude plugin list` shows the plugin installed.

## Root cause

Claude plugin updates can fail when automation uses only the short plugin name (for example `superpowers`) and/or assumes the default scope (`user`).

In practice, the updater may require:
- the actual installed plugin id from `claude plugin list --json`, such as `superpowers@claude-plugins-official`
- the actual installed scope, such as `project`

Example failure:
- Installed: `superpowers@claude-plugins-official`, scope `project`
- Failing command: `claude plugin update superpowers`
- Working command: `claude plugin update superpowers@claude-plugins-official --scope project`

## Debug workflow

1. Inspect help first:
```bash
claude plugin update --help
claude plugin list --help
```

2. Read installed plugins as JSON:
```bash
claude plugin list --json
```

3. Extract the target plugin entry and capture:
- `id`
- `scope`
- `version`
- `enabled`

4. Retry update using the full installed id and explicit scope:
```bash
claude plugin update <plugin-id> --scope <scope>
```

5. Re-run inventory after update and compare before/after.

## Automation pattern

For scripts:
1. call `claude plugin list --json`
2. parse plugin entries where `id` matches the target family (for example startswith `superpowers@`)
3. for each installed scope, run:
```bash
claude plugin update "$plugin_id" --scope "$scope"
```
4. treat the JSON inventory as the health source of truth
5. only fall back to legacy git checkout logic if JSON inventory returns no installed plugin

## Verification

- Dry run or summary should show the detected scope/version, e.g.:
  - `project:5.0.7:true`
- Successful update output should mention the full plugin id and correct scope.
- Regression test should assert all of:
  - script uses `claude plugin list --json`
  - script filters installed entries by plugin family (for example `plugin_id.startswith("superpowers@")`)
  - script updates with `claude plugin update "$plugin_id" --scope "$scope"`
- In workspace-hub, a concrete regression test was added at:
  - `tests/work-queue/test-harness-update-superpowers.sh`

## Known working example

For an installed entry:
- id: `superpowers@claude-plugins-official`
- scope: `project`

The short-name command fails:
```bash
claude plugin update superpowers --scope project
```

The full-id command succeeds:
```bash
claude plugin update superpowers@claude-plugins-official --scope project
```

## Pitfalls

- Default update scope is `user`; project-installed plugins will fail if scope is omitted.
- `claude plugin list` text output is less reliable than `--json` for automation.
- A plugin can appear installed locally while automation still fails if it uses the short name rather than the installed id.
- Windows rollout depends on repo sync actually pulling latest `main`; verify scheduler cadence and machine reachability separately.
