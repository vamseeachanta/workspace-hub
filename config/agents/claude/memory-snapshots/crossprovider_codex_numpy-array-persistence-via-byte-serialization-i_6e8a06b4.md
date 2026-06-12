---
name: crossprovider codex numpy-array-persistence-via-byte-serialization-i
description: Numpy array persistence via byte serialization in Parquet
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [serialization, parquet, numpy, dependencies, data-persistence]
---

Serialize numpy arrays to bytes using numpy.save() into single Parquet columns, avoiding heavy dependencies like polars while maintaining round-trip fidelity. Store metadata as JSON strings in adjacent columns for fully self-contained, dependency-light persistence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
