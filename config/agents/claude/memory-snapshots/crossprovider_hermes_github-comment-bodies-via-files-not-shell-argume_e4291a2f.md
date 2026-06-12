---
name: crossprovider hermes github-comment-bodies-via-files-not-shell-argume
description: GitHub comment bodies via files, not shell arguments
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github, safety, secrets, shell]
---

For issue/PR comments containing evidence, logs, or structured data, write body to `/tmp/<name>.md` first, then post via `gh issue comment --body-file <path>`. Never pass multiline content or sensitive values as direct shell arguments; they leak to shell history, environment variables, and process listings. Redaction mechanisms fail on command-line args.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
