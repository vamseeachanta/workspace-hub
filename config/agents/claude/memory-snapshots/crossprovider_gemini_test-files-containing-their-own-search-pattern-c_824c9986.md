---
name: crossprovider gemini test-files-containing-their-own-search-pattern-c
description: Test files containing their own search pattern cause CI self-referential loops
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, self-reference, ci-loops]
---

A test scanning for deleted paths like `test_no_deleted_path_fragments_in_control_plane_surfaces` will fail if the test file itself (or plan documents) contain the string it's searching for. Whitelist test/plan files or search with explicit path exclusions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
