---
name: crossprovider codex false-green-tests-from-subprocess-and-execution-
description: False-green tests from subprocess and execution environment asymmetry
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, false-positives, git-subprocess, shell-execution, environment-asymmetry]
---

Tests using Python subprocess mocking, environment variable mocking, or isolated subprocess APIs pass while actual shell execution, Git subprocesses, or string interpolation would fail. Git subprocess reads local `.git/config` includes despite global/system config being disabled; shell string interpolation behaves differently than Python subprocess API calls. Fix: test with actual execution environments, not mocked/isolated ones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
