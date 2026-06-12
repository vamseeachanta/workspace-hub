---
name: crossprovider hermes remove-transient-local-paths-from-tracked-artifa
description: Remove transient local paths from tracked artifacts before merge
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-hygiene, merge-blocking]
---

`.planning/quick/` and similar tracked artifacts containing absolute local paths (`/mnt/`, `/home/`), virtualenv details, or test output must not land in product repos. Remove before merge even if other changes pass review; they add noise and leak environment details.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
