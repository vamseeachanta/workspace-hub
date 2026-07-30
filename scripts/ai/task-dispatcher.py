#!/usr/bin/env python3
"""Task Dispatcher — recommends agent + model based on task description and tier.

Reads routing-config.yaml and provider-capabilities.yaml to build a routing
table, then scores providers against the requested tier and task keywords.

Usage:
  uv run scripts/ai/task-dispatcher.py --task "analyze 500-page PDF" --tier complex
  uv run scripts/ai/task-dispatcher.py --task "fix typo in README" --tier simple
  uv run scripts/ai/task-dispatcher.py --task "design new auth architecture" --tier reasoning

Output: JSON with recommended_agent, model, provider, rationale, and alternatives.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency bootstrap — works with uv run (no project pyproject needed)
# ---------------------------------------------------------------------------
try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
# Honor ROUTING_CONFIG_PATH so this tool and the resolver read the SAME config
# when the override is set (#3209 review r3-F3).
ROUTING_CONFIG = Path(os.environ.get(
    "ROUTING_CONFIG_PATH", REPO_ROOT / "config" / "agents" / "routing-config.yaml"))
PROVIDER_CAPS   = REPO_ROOT / "config" / "agents" / "provider-capabilities.yaml"

# Single forbid-policy interpreter (#3205) — never re-implement forbid logic here.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import routing_resolver  # noqa: E402


# ---------------------------------------------------------------------------
# Keyword signals per agent/dimension
# ---------------------------------------------------------------------------
KEYWORD_SIGNALS: dict[str, list[str]] = {
    "hermes": [
        "pdf", "document", "report", "data", "csv", "analysis", "analyze",
        "spreadsheet", "batch", "overnight", "skill", "delegate", "delegation",
        "transform", "extract", "parse", "summarize", "synthesis", "cross-repo",
    ],
    "claude": [
        "architecture", "design", "refactor", "orchestrate", "integration",
        "multi-file", "complex", "sensitive", "compliance", "plan", "planning",
        "review", "trade-off", "tradeoff", "evaluate",
    ],
    "codex": [
        "implement", "implementation", "test", "tests", "refactor", "cleanup",
        "configuration", "config", "edit", "fix", "bug", "patch", "diff",
    ],
    "agy": [
        "large context", "million token", "research", "web", "external source",
        "long document", "overflow", "third lane", "supplementary",
    ],
}

KNOWN_AGENTS: list[str] = list(KEYWORD_SIGNALS.keys())  # hermes, claude, codex, agy


def tier_preference(tier: str) -> list[str]:
    """Cost-aligned agent preference for a tier, sourced from routing-config.yaml
    tiers.* (#3209). The tier chain (claude/codex/agy) leads; agents not in the
    chain (hermes) are appended so keyword/dimension signals can still surface them.
    """
    try:
        chain = routing_resolver.tier_chain(tier)
    except routing_resolver.UnknownTierError:
        chain = routing_resolver.tier_chain("STANDARD")
    return chain + [a for a in KNOWN_AGENTS if a not in chain]

# Hermes specialises in data/doc/batch work — boost it for COMPLEX data tasks
HERMES_BOOST_TIERS = {"complex", "reasoning"}


# ---------------------------------------------------------------------------
# Loader helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def best_model_for_agent(provider_caps: dict, agent: str, tier: str) -> tuple[str, str]:
    """Return (model_id, provider) for the given agent at the given tier."""
    providers = provider_caps.get("providers", {})
    cap = providers.get(agent, {})
    model_ids = cap.get("model_ids", {})

    # Map tier to model quality preference
    if tier in ("reasoning", "complex"):
        model = model_ids.get("primary") or model_ids.get("balanced") or "unknown"
    elif tier == "standard":
        model = model_ids.get("balanced") or model_ids.get("primary") or "unknown"
    else:
        model = model_ids.get("fast") or model_ids.get("balanced") or model_ids.get("primary") or "unknown"

    # Provider name — derive from display_name or fall back to agent key
    display = cap.get("display_name", agent)
    if "anthropic" in display.lower() or agent == "claude":
        provider = "anthropic"
    elif "openai" in display.lower() or agent == "codex":
        provider = "openai-codex"
    elif "google" in display.lower() or agent == "agy":
        provider = "copilot"   # Gemini surface via Copilot pool; TOKEN_TO_CLI resolves copilot -> agy (#3573)
    elif agent == "hermes":
        provider = "copilot"
    else:
        provider = agent

    return model, provider


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_agents(task: str, tier: str, routing_cfg: dict, provider_caps: dict) -> list[dict]:
    """Score each known agent and return sorted list of candidates."""
    task_lower = task.lower()
    tier_lower = tier.lower()

    tier_pref = tier_preference(tier_lower)
    known_agents = list(KEYWORD_SIGNALS.keys())

    scores: list[dict] = []
    for agent in known_agents:
        # Base score from tier preference (position-based, lower index = higher score)
        if agent in tier_pref:
            tier_score = (len(tier_pref) - tier_pref.index(agent)) / len(tier_pref)
        else:
            tier_score = 0.0

        # Keyword signal score
        keywords = KEYWORD_SIGNALS.get(agent, [])
        kw_matches = [kw for kw in keywords if kw in task_lower]
        kw_score = min(len(kw_matches) * 0.15, 0.60)  # cap at 0.60

        # Hermes boost for data-heavy complex/reasoning tiers
        boost = 0.0
        if agent == "hermes" and tier_lower in HERMES_BOOST_TIERS and kw_matches:
            boost = 0.20

        total = round(tier_score + kw_score + boost, 4)

        model, provider = best_model_for_agent(provider_caps, agent, tier_lower)

        scores.append({
            "agent": agent,
            "score": total,
            "tier_score": round(tier_score, 4),
            "kw_score": round(kw_score, 4),
            "boost": round(boost, 4),
            "kw_matches": kw_matches,
            "model": model,
            "provider": provider,
        })

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores


def build_rationale(best: dict, task: str, tier: str, routing_cfg: dict) -> str:
    tier_desc = ""
    for t, info in routing_cfg.get("tiers", {}).items():
        if t.lower() == tier.lower():
            tier_desc = info.get("description", "")
            break

    parts = [
        f"Tier {tier.upper()} routing ({tier_desc}).",
        f"Agent '{best['agent']}' selected with composite score {best['score']:.2f}.",
    ]
    if best["kw_matches"]:
        parts.append(f"Task keyword signals matched: {', '.join(best['kw_matches'])}.")
    if best["boost"] > 0:
        parts.append("Hermes data/document specialist boost applied.")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dispatch a task to the best-matched AI agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--task", required=True,
        help="Natural language description of the task to route.",
    )
    parser.add_argument(
        "--tier", required=True,
        choices=["simple", "standard", "complex", "reasoning"],
        help="Complexity tier for the task.",
    )
    parser.add_argument(
        "--context", default=None,
        help="Execution context for the cost ceiling (e.g. hermes_batch). "
             "When set, providers forbidden for that context are excluded. "
             "An unknown context fails closed (#3205).",
    )
    parser.add_argument(
        "--top", type=int, default=3,
        help="Number of alternatives to include in output (default: 3).",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true", default=True,
        help="Output as JSON (default: true).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    routing_cfg   = load_yaml(ROUTING_CONFIG)
    provider_caps = load_yaml(PROVIDER_CAPS)

    if not routing_cfg:
        print(json.dumps({"error": f"Could not load routing config from {ROUTING_CONFIG}"}))
        return 1

    scored = score_agents(args.task, args.tier, routing_cfg, provider_caps)

    # Cost-ceiling enforcement (#3205): drop forbidden agents for the context.
    forbidden: list[str] = []
    if args.context:
        try:
            forbid = routing_resolver.forbidden_providers(args.context)
        except routing_resolver.UnknownContextError:
            print(json.dumps({"error": f"unknown context '{args.context}' — failing closed"}))
            return routing_resolver.EXIT_UNKNOWN_CONTEXT
        if routing_resolver.resolve_context(args.context) is None:
            print(json.dumps({"error": f"unknown context '{args.context}' — failing closed"}))
            return routing_resolver.EXIT_UNKNOWN_CONTEXT
        forbidden = sorted(forbid)
        filtered = [s for s in scored if routing_resolver.cli(s["agent"]) not in forbid]
        if filtered:
            scored = filtered
        else:
            # Everything scored is forbidden — fall to the context chain.
            chain = routing_resolver.context_chain(args.context)
            scored = [s for s in score_agents(args.task, args.tier, routing_cfg, provider_caps)
                      if routing_resolver.cli(s["agent"]) in chain] or scored

    best   = scored[0]
    alts   = scored[1:args.top]

    result = {
        "task": args.task,
        "tier": args.tier.upper(),
        "context": args.context,
        "forbidden": forbidden,
        "recommended_agent": best["agent"],
        "model": best["model"],
        "provider": best["provider"],
        "confidence_score": best["score"],
        "rationale": build_rationale(best, args.task, args.tier, routing_cfg),
        "alternatives": [
            {
                "agent": a["agent"],
                "model": a["model"],
                "provider": a["provider"],
                "score": a["score"],
            }
            for a in alts
        ],
        "routing_source": str(ROUTING_CONFIG),
        "capabilities_source": str(PROVIDER_CAPS),
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
