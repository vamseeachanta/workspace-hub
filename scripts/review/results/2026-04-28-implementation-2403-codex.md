# Implementation Review: #2403 embedding backend clients

Verdict: APPROVE
Reviewer: Codex local lane
Date: 2026-04-28
Commit reviewed: 7b8a54e2e

## Scope Reviewed

- `scripts/knowledge/run_embeddings_spike.py`
- `tests/knowledge/test_embeddings_spike.py`

## Findings

No blocking findings.

## Evidence

- Backend factories still return `_StubRunner` when the required runtime/auth prerequisite is absent.
- OpenAI and Voyage clients load API keys from `SpikeConfig` populated by environment variables; no secrets are hardcoded.
- BGE-M3 remains local-only and requires `ollama` on `PATH` before it is considered runnable.
- HTTP payloads and response parsing are covered with mocked unit tests, so no live API calls are required for this tranche.

## Residual Risk

The full recall/cost/latency measurement loop remains gated on provisioning `OPENAI_API_KEY`, `VOYAGE_API_KEY`, or local `ollama` with `bge-m3`. This tranche wires backend clients only; it does not claim model-selection completion.
