#!/usr/bin/env python3
"""Single routing resolver — the ONE place execution-context forbid policy is interpreted (#3205).

Reads `execution_contexts` from config/agents/routing-config.yaml and answers:
  - which providers are forbidden for a context (the cost ceiling),
  - a candidate list with forbidden providers removed (order-preserving),
  - the context's fallback chain (primary + fallbacks), CLI-normalized.

Every executed routing surface (tier_router.sh via route.sh/orchestrate.sh,
provider_filter.sh, task-dispatcher.py, overnight-batch-planner.py) consults
THIS module instead of carrying its own forbid logic.

Provider token-space note: routing-config uses provider tokens (e.g.
`openai-codex`); the bash routers and CLIs use CLI tokens (e.g. `codex`). All
bash-facing output here is CLI-normalized via cli() so callers can use it
directly — there is no second normalizer.

Fail-closed contract (r2-C2): an explicit but UNKNOWN context is an error
(UnknownContextError / CLI exit 3), never a silent pass-through — a typo such as
`hermes-batch` must not let `claude` leak past a cost ceiling. `context=None`
(the interactive path) passes through unchanged by design.

Usage (bash-facing; emit CLI-normalized tokens, one per line, no trailing blank):
  uv run scripts/ai/routing_resolver.py --context hermes_batch --filter claude,codex,gemini
  uv run scripts/ai/routing_resolver.py --context hermes_batch --chain
  uv run scripts/ai/routing_resolver.py --context hermes_batch --forbidden
  uv run scripts/ai/routing_resolver.py --context hermes_batch --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Dependency bootstrap — mirrors task-dispatcher.py / overnight-batch-planner.py
# so the module works under `uv run` (pyyaml is a project dep) AND under a bare
# `python3` fallback when uv is unavailable.
try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without uv/pyyaml
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_CONFIG = REPO_ROOT / "config" / "agents" / "routing-config.yaml"

# Provider-token -> CLI-token. The single source of normalization. Carries the
# full provider token-space (not just openai-codex) so a forbid authored in
# provider tokens (e.g. `anthropic`) can't silently fail open (review r3-F3).
TOKEN_TO_CLI = {
    "openai-codex": "codex",
    "anthropic": "claude",
    "copilot": "gemini",
}

EXIT_UNKNOWN_CONTEXT = 3


class UnknownContextError(ValueError):
    """Raised when an explicit context is not present in execution_contexts."""


def cli(token: str) -> str:
    """Normalize a provider token to its CLI token."""
    return TOKEN_TO_CLI.get(token, token)


_CACHE: dict[str, dict] = {}


def load_routing_config(path: Path | str | None = None) -> dict:
    p = Path(path) if path is not None else ROUTING_CONFIG
    key = str(p)
    if key not in _CACHE:
        with open(p) as fh:
            _CACHE[key] = yaml.safe_load(fh) or {}
    return _CACHE[key]


def _contexts(cfg: dict | None) -> dict:
    cfg = cfg if cfg is not None else load_routing_config()
    return cfg.get("execution_contexts", {}) or {}


def resolve_context(name: str, cfg: dict | None = None) -> dict | None:
    """Return the execution_contexts entry for `name`, or None if absent."""
    return _contexts(cfg).get(name)


def forbidden_providers(name: str, cfg: dict | None = None) -> set[str]:
    """CLI-normalized set of providers forbidden for `name` (empty if none)."""
    ctx = resolve_context(name, cfg)
    if not ctx:
        return set()
    return {cli(t) for t in (ctx.get("forbid") or [])}


def is_cost_ceiling(name: str, cfg: dict | None = None) -> bool:
    ctx = resolve_context(name, cfg)
    return bool(ctx and ctx.get("cost_ceiling"))


def context_chain(name: str, cfg: dict | None = None) -> list[str]:
    """CLI-normalized [primary, *fallbacks] for `name`, with forbidden removed."""
    ctx = resolve_context(name, cfg)
    if ctx is None:
        raise UnknownContextError(name)
    forbid = forbidden_providers(name, cfg)
    chain: list[str] = []
    for tok in [ctx.get("primary"), *(ctx.get("fallbacks") or [])]:
        if not tok:
            continue
        c = cli(tok)
        if c not in forbid and c not in chain:
            chain.append(c)
    return chain


def filter_candidates(candidates: list[str], context: str | None, cfg: dict | None = None,
                      fallback: bool = True) -> list[str]:
    """Drop forbidden providers from `candidates` for `context` (order-preserving).

    - context=None: pass through unchanged (interactive path).
    - explicit unknown context: raise UnknownContextError (fail closed, r2-C2).
    - everything forbidden + fallback=True: fall back to the context chain
      (route_by_tier always wants *some* provider to route to).
    - everything forbidden + fallback=False: return [] (provider_filter reports
      genuine availability and must not re-add unavailable providers).
    """
    if not context:
        return list(candidates)
    if resolve_context(context, cfg) is None:
        raise UnknownContextError(context)
    forbid = forbidden_providers(context, cfg)
    kept = [c for c in candidates if c and cli(c) not in forbid]
    if not kept and fallback:
        kept = context_chain(context, cfg)
    return kept


def _parse_csv(value: str) -> list[str]:
    # `--filter ""` must yield [] (not [""]) — r1-F7.
    return [tok for tok in value.split(",") if tok.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--context", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--filter", dest="filter_csv", metavar="c1,c2,c3")
    mode.add_argument("--chain", action="store_true")
    mode.add_argument("--forbidden", action="store_true")
    mode.add_argument("--json", dest="json_mode", action="store_true")
    parser.add_argument("--no-fallback", dest="fallback", action="store_false", default=True,
                        help="With --filter: return [] when all forbidden (no context-chain fallback).")
    args = parser.parse_args(argv)

    try:
        # Uniform fail-closed: an explicit unknown context errors in EVERY mode
        # (review r3-F1), not just --filter/--chain/--json.
        if resolve_context(args.context) is None:
            raise UnknownContextError(args.context)
        if args.filter_csv is not None:
            out = filter_candidates(_parse_csv(args.filter_csv), args.context, fallback=args.fallback)
            print("\n".join(out))
        elif args.chain:
            print("\n".join(context_chain(args.context)))
        elif args.forbidden:
            print("\n".join(sorted(forbidden_providers(args.context))))
        elif args.json_mode:
            if resolve_context(args.context) is None:
                raise UnknownContextError(args.context)
            ctx = resolve_context(args.context)
            print(json.dumps({
                "context": args.context,
                "primary_cli": cli(ctx.get("primary")) if ctx.get("primary") else None,
                "fallbacks_cli": [cli(t) for t in (ctx.get("fallbacks") or [])],
                "forbid_cli": sorted(forbidden_providers(args.context)),
                "cost_ceiling": is_cost_ceiling(args.context),
            }))
    except UnknownContextError as exc:
        print(f"routing_resolver: unknown context '{exc}' — failing closed (exit {EXIT_UNKNOWN_CONTEXT})", file=sys.stderr)
        return EXIT_UNKNOWN_CONTEXT
    return 0


if __name__ == "__main__":
    sys.exit(main())
