---
name: crossprovider codex node-env-production-omits-npm-dev-dependencies
description: NODE_ENV=production omits npm dev dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [nodejs, npm, environment]
---

`npm ci` skips dev dependencies when `NODE_ENV=production` is set, even for explicit `devDependencies` in package.json. Solution: explicitly `npm install --save-dev` or unset `NODE_ENV` for validation runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
