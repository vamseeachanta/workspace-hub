---
name: crossprovider codex guard-optional-dependencies-outside-generator-fr
description: Guard optional dependencies outside generator frames
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, generators, optional-dependencies, error-handling]
---

Place dependency checks (try/except ImportError) in the public method—before the generator is created—and defer generator logic to a private _generate() method. This ensures ImportError is raised eagerly on method call, not lazily inside the generator frame during iteration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
