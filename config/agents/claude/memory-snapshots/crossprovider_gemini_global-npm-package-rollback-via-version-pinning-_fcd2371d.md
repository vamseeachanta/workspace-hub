---
name: crossprovider gemini global-npm-package-rollback-via-version-pinning-
description: Global npm package rollback via version pinning requires hash-pinning or lockfiles
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, supply-chain, npm-packages, dependency-pinning]
---

Simple version constraints or major-version blocking is insufficient against supply chain attacks. Global npm packages need cryptographic hash pinning or lockfile-based reproducible installs. Direct `npm install -g pkg@version` is vulnerable to minor/patch compromise.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
