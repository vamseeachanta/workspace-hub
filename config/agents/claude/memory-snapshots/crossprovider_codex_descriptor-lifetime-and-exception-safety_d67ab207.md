---
name: crossprovider codex descriptor-lifetime-and-exception-safety
description: Descriptor lifetime and exception safety
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [resource-management, exception-safety, descriptors, cleanup]
---

Keep file descriptors open throughout logical operations and close only in finally blocks to prevent leaks on early returns or exceptions. Use context managers to guarantee closure on BaseException; pair each open with corresponding finally-block close.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
