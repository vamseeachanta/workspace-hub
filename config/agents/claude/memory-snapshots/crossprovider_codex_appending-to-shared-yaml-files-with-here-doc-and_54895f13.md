---
name: crossprovider codex appending-to-shared-yaml-files-with-here-doc-and
description: Appending to shared YAML files with here-doc and >> is not concurrency-safe
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, shell-safety, yaml, file-io]
---

Here-doc expansion to YAML append (e.g., `>> file <<'EOF'...EOF`) produces multiple write syscalls; concurrent processes can interleave output and corrupt the file. Use flock-based locking or atomic temp+move for multi-writer safety in nightly and manual runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
