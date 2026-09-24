---
name: crossprovider gemini hull-library-architecture-profiles-meshes-catalo
description: Hull library architecture: profiles → meshes → catalog → tests
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, hull-library, validation-pattern]
---

The hull library pattern separates YAML profiles (station offsets, dimensions), GDF panel meshes (2000–2400 panels, Y-symmetric), catalog entries (metadata + dimensions), and comprehensive test coverage (26+ tests per expansion). This separation enables independent validation of each layer and supports rapid library expansion.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
