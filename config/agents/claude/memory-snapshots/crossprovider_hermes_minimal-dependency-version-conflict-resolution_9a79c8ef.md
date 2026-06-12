---
name: crossprovider hermes minimal-dependency-version-conflict-resolution
description: Minimal dependency version conflict resolution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-resolution, version-conflict, testing-first]
---

When base requires >=8.0.0 but a sub-dependency allows <8.0.0, resolve by finding shared range (e.g. >=6.7.0,<8.0.0) and testing actual code compatibility rather than forcing latest version. Check if code uses only basic APIs compatible with older versions before assuming incompatibility.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
