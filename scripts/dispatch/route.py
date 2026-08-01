#!/usr/bin/env python3
"""route.py — propose machine/provider assignment for open kanban cards.

Reads the kanban board YAMLs (each card already carries its domain via the
board it lives in) plus routing-rules.yaml, then proposes a (domain, machine,
provider) assignment per open GitHub-issue card using first-match capability
rules. WIP caps and the shared codex+hermes budget pool are enforced as
backpressure: cards beyond a cap stay queued, never auto-spawned.

SAFETY: default mode is dry-run (prints the plan only). `--apply` writes the
GitHub labels (machine:/ai:/domain:/dispatch:ready) via `gh` — Phase B only.
This script NEVER spawns a worker; execution is pull-based (see dispatch.py).

Usage:
  route.py                 dry-run, full proposal table
  route.py --repo R        limit to one repo (e.g. vamseeachanta/digitalmodel)
  route.py --json          machine-readable proposal
  route.py --apply         write GH labels (requires gh; Phase B)
"""
from __future__ import annotations
import argparse, fnmatch, json, math, os, subprocess, sys, time
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: `uv run` in workspace-hub, or `pip install pyyaml`")


def repo_root() -> Path:
    """Git top-level; no hardcoded absolute paths (check-no-abs-paths.sh)."""
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if out.returncode == 0:
        return Path(out.stdout.strip())
    # fallback: walk up looking for the kanban dir
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / ".claude/memory/kanban").is_dir():
            return parent
    sys.exit("cannot locate repo root (no git, no .claude/memory/kanban)")


ROOT = repo_root()
KANBAN = ROOT / ".claude/memory/kanban"


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_rules() -> dict:
    return load_yaml(KANBAN / "routing-rules.yaml")


def iter_cards():
    """Yield (board_meta, card) for every github_issue card across all boards."""
    for bf in sorted((KANBAN / "boards").glob("*.yaml")):
        data = load_yaml(bf)
        board = data.get("board", {})
        for card in (data.get("cards") or []):
            if card.get("source") == "github_issue":
                yield board, card


def existing_label_value(labels: list[str], prefix: str) -> str | None:
    """Lenient read: FIRST matching label wins.

    Retained for multi-valued axes, where taking one representative value is
    correct. For a single-valued axis use `axis_value()` — this function's
    first-wins behaviour makes the result depend on GitHub's API ordering, which
    is the defect `label_axes` exists to close.
    """
    for lab in labels or []:
        if lab.startswith(prefix):
            return lab.split(":", 1)[1]
    return None


# ---------------------------------------------------------------------------
# Label axis cardinality — fail closed on a scalar axis carrying two values.
#
# See the `label_axes:` block in routing-rules.yaml for the measurement and the
# argument. In short: a label SET can express states the domain forbids, and
# resolving those by API order is silent non-determinism.
# ---------------------------------------------------------------------------


class AmbiguousAxis(ValueError):
    """A single-valued axis carries more than one label.

    Carries the axis and the sorted values so the message is stable regardless
    of the order GitHub returned them — an error that varies with label order is
    as unhelpful as the bug it replaces.
    """

    def __init__(self, prefix: str, values) -> None:
        self.prefix = prefix
        self.values = sorted(values)
        super().__init__(
            f"{prefix} is single-valued but carries {len(self.values)} labels: "
            f"{', '.join(self.values)} — routing would depend on API label order"
        )


def load_axis_cardinality(cfg: dict) -> tuple[set[str], set[str]]:
    """Return (single_axes, multi_axes) declared in routing-rules.yaml."""
    axes = (cfg or {}).get("label_axes") or {}
    return set(axes.get("single") or {}), set(axes.get("multi") or {})


def axis_value(labels, prefix: str, single_axes) -> str | None:
    """Read one axis, failing closed when a declared scalar carries 2+ values.

    Undeclared axes are NOT enforced — a new axis must not break routing the day
    it is invented — but they are surfaced by `undeclared_axes()` so the
    fail-open cannot become a silent hole.
    """
    values = [lab.split(":", 1)[1] for lab in (labels or []) if lab.startswith(prefix)]
    if not values:
        return None
    if prefix in (single_axes or frozenset()) and len(values) > 1:
        raise AmbiguousAxis(prefix, values)
    return values[0]


def undeclared_axes(labels, single_axes, multi_axes) -> list[str]:
    """Axes present on an issue that no one has classified.

    The compensating control for `axis_value`'s fail-open: an unclassified axis
    is reported rather than assumed benign.
    """
    known = set(single_axes or ()) | set(multi_axes or ())
    seen = {lab.split(":", 1)[0] + ":" for lab in (labels or []) if ":" in lab}
    return sorted(seen - known)


def assert_write_preserves_cardinality(merged_labels, single_axes) -> None:
    """Refuse a write that would leave a scalar axis holding two values.

    The write-side counterpart to `axis_value()`. A read guard without a write
    guard is half a control: the resolver would refuse an issue the writer had
    just created.

    Checked on the MERGED set (existing + additions) rather than on the
    additions alone — a single new `machine:` label is only a violation in the
    context of a `machine:` label already there, which is exactly the case a
    "did we add two?" check would miss.
    """
    for prefix in sorted(single_axes or ()):
        values = [lab.split(":", 1)[1] for lab in merged_labels if lab.startswith(prefix)]
        if len(values) > 1:
            raise AmbiguousAxis(prefix, values)


def classify_card_axes(card: dict, single_axes) -> dict:
    """Decide whether one card is safe to route.

    Fail-closed here means "do not route THIS card", never "abort the run" — one
    contradictory issue must not take down a 1,700-issue pass, or the pressure
    is to disable the check outright.
    """
    labels = card.get("labels") or []
    for prefix in sorted(single_axes or ()):
        try:
            axis_value(labels, prefix, single_axes)
        except AmbiguousAxis as exc:
            return {"routable": False, "reason": str(exc), "axis": prefix}
    return {"routable": True, "reason": None, "axis": None}


# ---------------------------------------------------------------------------
# Assignment coverage (deckhand#584) — READ-ONLY reporting.
#
# Four buckets, because "has a label" is not "is routable":
#   missing    no label on the axis
#   ambiguous  MULTIPLE labels on one axis. existing_label_value() returns the
#              FIRST match, so routing depends on API label order. This presents
#              as healthy and is arguably worse than missing.
#   terminal   deliberately not scheduled — a valid end state, not a finding
#   skipped    in flight (skip_if_labeled) — not an assignment failure
#   routable   exactly one label, and it resolves
#
# NOTE the `model:` inversion: per #584 decision 1, ABSENCE of a model: label is
# MEANINGFUL ("executor chooses") and must never be counted as a gap. That is the
# opposite of machine:/lane:. `model:` is therefore not an axis here at all.
# ---------------------------------------------------------------------------

COVERAGE_BUCKETS = ("missing", "ambiguous", "terminal", "skipped", "routable")


def classify_axis(labels, prefix, terminal, skip) -> str:
    """Bucket one issue on one label axis. Pure: never mutates `labels`."""
    labs = list(labels or [])

    # Terminal beats everything: deliberately unscheduled is an answer, not a gap.
    if any(t in labs for t in terminal):
        return "terminal"
    # In-flight work is not an assignment failure.
    if any(s in labs for s in skip):
        return "skipped"

    on_axis = [lab for lab in labs if lab.startswith(prefix)]
    if not on_axis:
        return "missing"
    if len(on_axis) > 1:
        return "ambiguous"
    return "routable"


def coverage_report(issues, axes, terminal, skip) -> dict:
    """Read-only coverage over an issue list. No gh, no writes, no network.

    `issues` are dicts with `number` and `labels`. Returns per-axis bucket counts
    plus the issue numbers behind each finding — a count alone is not reviewable.
    """
    report = {"axes": {}, "total": len(issues), "missing_all_axes": []}

    for axis in axes:
        counts = {b: 0 for b in COVERAGE_BUCKETS}
        counts["missing_issues"] = []
        counts["ambiguous_issues"] = []
        for iss in issues:
            bucket = classify_axis(iss.get("labels"), axis, terminal, skip)
            counts[bucket] += 1
            if bucket == "missing":
                counts["missing_issues"].append(iss["number"])
            elif bucket == "ambiguous":
                counts["ambiguous_issues"].append(iss["number"])
        report["axes"][axis] = counts

    for iss in issues:
        if all(
            classify_axis(iss.get("labels"), axis, terminal, skip) == "missing" for axis in axes
        ):
            report["missing_all_axes"].append(iss["number"])

    return report


def _domain_matches(pattern: str, domain) -> bool:
    """Match a rule's `domain:` pattern against a card's domain.

    Backward-compatible: a plain string matches exactly (existing rules like
    `domain: solver` keep their exact semantics). A pattern containing a glob
    metacharacter (`* ? [`) matches via `fnmatch`, so ONE rule `domain: hydro*`
    covers the parent domain `hydro` AND all its split subdomains
    (`hydro-diffraction`, `hydro-mooring`, ...) — this is what keeps licensed-
    Windows routing attached across the workspace-hub#2878 subdomain splits.
    A card with no domain (None) never matches a domain rule.
    """
    if domain is None:
        return False
    if any(ch in pattern for ch in "*?["):
        return fnmatch.fnmatchcase(domain, pattern)
    return pattern == domain


def _family_matches(base: str, domain) -> bool:
    """Match a taxonomy FAMILY: the parent domain `base` OR a subdomain `base-*`.

    Precise where a bare glob over-reaches: the `hydro` family matches `hydro`
    and `hydro-diffraction` but NOT `hydrocarbon`/`hydrostatic`; `solver` matches
    `solver`/`solver-orcaflex` but NOT `solverless`. This is the intended
    "parent rule covers its splits" semantics for the #2878 reorg.
    """
    if domain is None:
        return False
    return domain == base or domain.startswith(base + "-")


def _as_domains(domain) -> list[str]:
    """Normalise a card's domain(s) to a list.

    A kanban BOARD gave each card exactly one domain — the board it lived in. A
    live GitHub issue carries however many `domain:` labels it has, and 74 open
    issues legitimately carry more than one (`domain:` is declared multi-valued).

    Taking "the first domain: label" would resolve routing by GitHub's API
    ordering — the exact defect removed from status:, lane: and machine: today.
    So every domain is considered and rules stay first-match-wins.
    """
    if domain is None:
        return []
    if isinstance(domain, str):
        return [domain]
    return [d for d in domain if d]


def issue_to_card(issue: dict, repo: str) -> dict:
    """Live GitHub issue -> the card shape propose() consumes.

    Replaces the kanban board mirror as the routing input (workspace-hub#3736):
    the mirror had no GitHub->board refresh path, so it drifted monotonically and
    held labels that had been deleted.
    """
    labels = [l["name"] if isinstance(l, dict) else l for l in issue.get("labels") or []]
    number = issue.get("number")
    prio = 0
    for lab in labels:
        if lab.startswith("priority:"):
            prio = {"high": 3, "medium": 2, "low": 1}.get(lab.split(":", 1)[1].lower(), 1)
    return {
        "idempotency_key": f"gh:{repo}#{number}",
        "repo": repo,
        # gh returns OPEN/CLOSED; `routable_states` is declared lowercase, and a
        # case mismatch would filter out every card and report an empty backlog
        # rather than an error.
        "gh_state": str(issue.get("state") or "open").lower(),
        "gh_labels": labels,
        "domains": [l.split(":", 1)[1] for l in labels if l.startswith("domain:")],
        "title": issue.get("title") or "",
        "priority": prio,
        "source_url": f"https://github.com/{repo}/issues/{number}",
    }


def match_rule(rules: list[dict], *, repo, domain, gh_labels) -> dict:
    """First-match-wins. Empty match {} is the catch-all.

    Domain matchers (most specific first): `domain` (exact, or fnmatch glob if it
    carries `* ? [`) and `domain_family` (precise parent-or-`parent-`child).
    """
    labelset = set(gh_labels or [])
    for rule in rules:
        m = rule.get("match", {})
        if "repo" in m and m["repo"] != repo:
            continue
        # ANY-OF over the card's domains. Order-independent by construction, so
        # two issues with the same domains in different label order route
        # identically; rule precedence stays first-match-wins.
        doms = _as_domains(domain)
        if "domain" in m and not any(_domain_matches(m["domain"], d) for d in doms):
            continue
        if "domain_family" in m and not any(_family_matches(m["domain_family"], d) for d in doms):
            continue
        if "gh_label" in m and m["gh_label"] not in labelset:
            continue
        return rule
    return {"assign": {}, "reason": "no rule matched"}


# lane: vocabulary is fixed to the two auto-routable workhorse providers;
# unknown lane values (e.g. a future lane:gemini) must never route (#3029).
LANE_PROVIDERS = {"codex", "claude"}


def resolve_provider(labels: list[str], assign: dict, defaults: dict,
                     single_axes=None) -> tuple[str | None, bool, str]:
    """Resolve (provider, provider_explicit, source) for one card.

    source is one of "ai" | "rule" | "lane" | "default" — the quota gate
    (#3030) suspends only the lane-derived codex choice.

    Precedence: ai: (human/dispatch override) > rule provider > lane:
    (plan-time preference) > defaults.provider.

    lane: labels are plan-time, agent-or-human-set during the human-gated
    planning stage (compute-lane rule, .claude/memory/agents.md) — weaker than
    the human-set ai: override and than specific routing rules (e.g.
    needs:cross-review -> codex), stronger only than the catch-all default.
    A lane-derived provider never sets provider_explicit, so labels_for()
    never materializes an ai: label from a lane — lane stays re-classifiable
    at planning time (#3029 adversarial review r2).
    """
    # `single_axes` defaults to no enforcement for back-compat with the six
    # existing call sites and their tests. propose() passes the loaded set, and
    # test_propose_passes_the_loaded_axes_not_the_lenient_default asserts it —
    # a lenient default is exactly how an enforced guard quietly becomes
    # optional, so the wiring is pinned rather than trusted.
    existing_ai = axis_value(labels, "ai:", single_axes)
    lane = axis_value(labels, "lane:", single_axes)
    accepted_lane = lane if lane in LANE_PROVIDERS else None
    if existing_ai:
        provider, source = existing_ai, "ai"
    elif assign.get("provider"):
        provider, source = assign["provider"], "rule"
    elif accepted_lane:
        provider, source = accepted_lane, "lane"
    else:
        provider, source = defaults.get("provider"), "default"
    # provider is "explicit" only if a human or a rule chose it (not lane/default)
    provider_explicit = source in ("ai", "rule")
    return provider, provider_explicit, source


QUOTA_SCRIPT = ROOT / "scripts/ai/assessment/query-codex-usage.sh"
QUOTA_GATE_PCT = 10  # suspend lane:codex strictly below this weekly remaining %


def codex_weekly_remaining(override=None):
    """Codex weekly remaining % for the dispatch quota gate (#3030), or None.

    None means "unknown" and the gate FAILS OPEN — this gate is an
    optimization on top of lane routing (#3029); an unreachable quota source
    must never strand heavy work. The statusline keeps the human informed.

    Window-validity guard: a snapshot may drive demotion only when it provably
    belongs to the current weekly window — source == "app-server-live", or a
    fallback source with resets_at_epoch in the future. A fallback snapshot
    from before the weekly reset would freeze pre-reset numbers (codex #3030
    plan review MAJOR-1); within a current window, fallback staleness can only
    understate usage, which errs toward fail-open.

    `override` carries the --codex-remaining CLI value (loud operator escape
    hatch). Deliberately NO environment-variable override: cron environments
    inherit env silently (#3030 plan review MAJOR-2).
    """
    if override is not None:
        print(f"\033[1;33m[quota-override] --codex-remaining={override} — "
              f"live codex quota NOT consulted\033[0m", file=sys.stderr)
        return float(override)
    try:
        timeout = float(os.environ.get("DISPATCH_QUOTA_TIMEOUT", "10"))
        res = subprocess.run([str(QUOTA_SCRIPT), "--json"],
                             capture_output=True, text=True, timeout=timeout)
        if res.returncode != 0:
            raise ValueError(f"quota script exit {res.returncode}")
        data = json.loads(res.stdout)
        remaining = float(data.get("pct_remaining"))
        # malformed numerics (NaN/inf/out-of-range) must never demote
        if not (math.isfinite(remaining) and 0 <= remaining <= 100):
            raise ValueError(f"pct_remaining out of range: {remaining}")
        src = data.get("source")
        if src != "app-server-live":
            reset = data.get("resets_at_epoch")
            if not reset or float(reset) <= time.time():
                print(f"[quota-gate] stale codex quota snapshot "
                      f"(source={src}, resets_at_epoch={reset}) — fail open",
                      file=sys.stderr)
                return None
        return remaining
    except Exception as exc:  # timeout, missing script, bad JSON — fail open
        print(f"[quota-gate] codex quota unavailable ({exc}) — fail open",
              file=sys.stderr)
        return None


#: Carries the SPEND decision, separately from the provider choice (deckhand#584
#: R9). Without it, an `ai:` label chose the provider AND silently opted out of
#: the budget guard — one label making two decisions, the second invisible at
#: the point of labelling.
QUOTA_OVERRIDE_LABEL = "quota:override"


def quota_demotion(provider, source, remaining_pct, defaults, labels=None):
    """Return (provider, demoted). Suspends a codex choice from ANY source when
    weekly remaining is strictly below QUOTA_GATE_PCT.

    R9 (deckhand#584, owner 2026-07-30): `ai:` and rule-sourced codex are no
    longer exempt. The provider choice and the budget bypass are different
    decisions — "codex does this work better" is about a task, "spend into a
    suspended pool" is about the month — so they now need different labels.
    Rule-sourced is demotable too, decided rather than inherited: a capability
    rule is MACHINE-decided and has even less claim on a budget guard than a
    human's deliberate `ai:`.

    `QUOTA_OVERRIDE_LABEL` is the only bypass, and it is a spend decision only —
    it never chooses a provider.

    `None` remaining FAILS OPEN: the gate is an optimisation on top of routing
    (#3030) and an unreachable quota source must not strand heavy work. That is
    deliberately the opposite of the write gate's fail-closed posture — the cost
    of a wrong answer differs in each direction.

    A demoted card keeps provider_explicit=False at the call site, so
    labels_for() writes no ai: label — demotion leaves no sticky residue. An
    EXISTING `ai:` label is not removed: it records the operator's intent, while
    the gate governs this run's execution.
    """
    if provider != "codex":
        return provider, False
    if QUOTA_OVERRIDE_LABEL in (labels or []):
        return provider, False
    if remaining_pct is not None and remaining_pct < QUOTA_GATE_PCT:
        return defaults.get("provider"), True
    return provider, False


#: Back-compat alias — the old name said "lane" and the restriction is gone.
lane_quota_demotion = quota_demotion


def propose(args) -> list[dict]:
    cfg = load_rules()
    rules = cfg.get("rules", [])
    defaults = cfg.get("defaults", {})
    aliases = cfg.get("machine_aliases", {})  # label-in-the-wild -> canonical
    skip_labels = set(defaults.get("skip_if_labeled", []))
    routable_states = set(defaults.get("routable_states", ["open"]))
    single_axes, multi_axes = load_axis_cardinality(cfg)
    blocked: list[dict] = []   # cards refused for a contradictory scalar axis

    proposals = []
    _QUOTA_UNSET = object()
    quota_remaining = _QUOTA_UNSET

    # LIVE GITHUB, not the kanban board mirror (workspace-hub#3736, owner
    # decision 2026-07-31 "retire the mirror as a routing input").
    #
    # `propose()` used to iterate .claude/memory/kanban/boards/*.yaml, so the
    # routing ENGINE never read GitHub while every checker did. The mirror held
    # 6 machine:/lane: labels deleted the same day, and there was no
    # GitHub -> board refresh path to lapse: load.py runs boards -> Hermes and
    # nothing runs the reverse, so the gap only grew.
    repos = [args.repo] if getattr(args, "repo", None) else list(DEFAULT_COVERAGE_REPOS)
    cards = []
    for r in repos:
        for issue in fetch_issues_for_coverage(r):
            cards.append((r, issue_to_card(issue, r)))

    for repo, card in cards:
        if card.get("gh_state") not in routable_states:
            continue
        labels = card.get("gh_labels") or []
        if skip_labels & set(labels):
            continue

        # Fail closed on a contradictory card BEFORE routing it. Excluding one
        # card is the failure mode; aborting the run is not — a single bad issue
        # must not take down a 1,700-issue pass, or the pressure is to disable
        # the check outright.
        axis_check = classify_card_axes({"labels": labels}, single_axes)
        if not axis_check["routable"]:
            blocked.append({
                "repo": repo, "number": card.get("number"),
                "reason": axis_check["reason"], "axis": axis_check["axis"],
            })
            continue

        # EVERY domain the issue carries, not the one board it happened to sit
        # on. match_rule is any-of over these, so label order cannot change the
        # answer.
        domain = card.get("domains") or []
        rule = match_rule(rules, repo=repo, domain=domain, gh_labels=labels)
        assign = rule.get("assign", {})

        # human-set labels on the issue always override the rule
        existing_machine = axis_value(labels, "machine:", single_axes)
        machine = existing_machine or assign.get("machine") or defaults.get("machine")
        machine = aliases.get(machine, machine)  # fold a hostname straggler -> its role
        provider, provider_explicit, provider_source = resolve_provider(
            labels, assign, defaults, single_axes=single_axes)
        quota_demoted = False
        # R9: NO source restriction here. This call site previously carried its
        # own `provider_source == "lane"` guard, so relaxing only the function
        # would have left the exemption fully intact — the fix would look done
        # and do nothing.
        if provider == "codex":
            if quota_remaining is _QUOTA_UNSET:  # one quota read per run
                quota_remaining = codex_weekly_remaining(
                    override=getattr(args, "codex_remaining", None))
            provider, quota_demoted = quota_demotion(
                provider, provider_source, quota_remaining, defaults, labels=labels)
        routed_by = "manual" if existing_machine else "rule"

        proposals.append({
            "key": card.get("idempotency_key"),
            "repo": repo,
            "number": card.get("idempotency_key", "").rsplit("#", 1)[-1],
            # Display/serialisation form. `domain` is now a LIST internally (an
            # issue can carry several), but consumers — print_detail, --json,
            # dispatch.py's queue files — expect a scalar. Joining keeps every
            # domain visible instead of silently dropping all but one, which is
            # what picking `domain[0]` would have done.
            "domain": ",".join(domain) if domain else None,
            "domains": list(domain),
            "title": (card.get("title") or "")[:60],
            "machine": machine,
            "has_machine_label": bool(existing_machine),
            "provider": provider,
            "provider_explicit": provider_explicit,
            "quota_demoted": quota_demoted,
            "priority": card.get("priority", 0),  # higher = more urgent (SCHEMA)
            "routed_by": routed_by,
            "reason": rule.get("reason", ""),
            "url": card.get("source_url"),
        })
    report_blocked(blocked)
    # WIP slots must go to the MOST URGENT cards, not whichever were globbed first.
    proposals.sort(key=lambda p: (-int(p.get("priority") or 0), p["repo"], _num(p["number"])))
    return apply_wip(proposals, cfg)


def _num(s):
    """Numeric issue number for stable sort; non-numeric sorts last."""
    try:
        return (0, int(s))
    except (TypeError, ValueError):
        return (1, 0)


def apply_wip(proposals: list[dict], cfg: dict) -> list[dict]:
    """Mark cards beyond a WIP cap as queued. Fail-CLOSED: machines/providers
    with no explicit cap fall back to a default cap (never unbounded — that is
    the runaway-worker failure mode this guards). Providers with
    auto_routable=false are never auto-eligible (manual ai: only).
    Proposals are expected pre-sorted by priority so winners are the urgent N."""
    caps = cfg.get("wip_caps", {})
    per_machine = caps.get("per_machine", {})
    per_provider = caps.get("per_provider", {})
    m_default = per_machine.get("default", 1)        # fail-closed default
    p_default = per_provider.get("default", 999)     # provider default (machine is the real gate)
    providers = cfg.get("providers", {})
    pools = cfg.get("budget_pools", {})
    prov_pool = {}
    for pool, meta in pools.items():
        for member in meta.get("members", []):
            prov_pool[member] = pool
    pool_cap = {p: meta.get("max_concurrent", 999) for p, meta in pools.items()}

    m_count = defaultdict(int)
    p_count = defaultdict(int)
    pool_count = defaultdict(int)
    for p in proposals:
        m, prov = p["machine"], p["provider"]
        over = False
        reason = None

        # (1) UNKNOWN PROVIDER -> refuse. This used to read
        #     `providers.get(prov, {}).get("auto_routable", True)`, so an
        #     unrecognised value inherited True and sailed past every scarce cap
        #     — fail-OPEN, one line below a docstring promising fail-CLOSED.
        #     A typo (`ai:agi`) or a label left over from a retired provider must
        #     not become a workhorse: nothing in the roster has vouched for its
        #     quota or capacity. (deckhand#584 slice 4; found by Codex design
        #     review before this slice was built on top of it.)
        if prov not in providers:
            over = True
            reason = f"unknown provider {prov!r} — not in the providers roster"
        # (2) NOT AUTO-SELECTABLE != NOT USABLE. `auto_routable: false` exists to
        #     say "defaults, rules and lanes may not pick this; a human may".
        #     The old code queued such a provider unconditionally, so the manual
        #     escape hatch its own config comment documented did not work.
        #     An explicit `ai:` choice (provider_explicit) now passes; the budget
        #     pool below still applies, so the override moves the SELECTION, not
        #     the CAP.
        elif providers.get(prov, {}).get("auto_routable", True) is False:
            if not p.get("provider_explicit"):
                over = True
                reason = f"provider {prov!r} is manual-only (needs an explicit ai: label)"
        mcap = per_machine.get(m, m_default)         # default applies to home-win/macbook/multi/etc.
        if m_count[m] >= mcap:
            over = True
            reason = reason or f"machine {m!r} at WIP cap {mcap}"
        if prov in prov_pool:
            pcap = pool_cap.get(prov_pool[prov], 999)
            if pool_count[prov_pool[prov]] >= pcap:
                over = True
                reason = reason or f"budget pool {prov_pool[prov]!r} at cap {pcap}"
        elif p_count[prov] >= per_provider.get(prov, p_default):
            over = True
            reason = reason or f"provider {prov!r} at WIP cap"
        p["slot"] = "queued" if over else "active-eligible"
        # A queued card without a stated reason is indistinguishable from one
        # nobody got to. Every refusal names itself.
        if over:
            p["wip_reason"] = reason
        if not over:
            m_count[m] += 1
            p_count[prov] += 1
            if prov in prov_pool:
                pool_count[prov_pool[prov]] += 1
    return proposals


def report_blocked(blocked: list[dict]) -> None:
    """A refused card must be VISIBLE.

    An issue silently dropped from routing is the same defect class as one
    silently mis-routed — it simply fails to appear, which reads as "nothing to
    do" rather than "I refused to guess". stderr so it survives `--json`.
    """
    if not blocked:
        return
    print(
        f"\n\033[1;31mREFUSED {len(blocked)} card(s) — contradictory single-valued axis\033[0m",
        file=sys.stderr,
    )
    for b in blocked:
        print(f"  {b['repo']}#{b['number']}: {b['reason']}", file=sys.stderr)
    print(
        "  Fix: remove the extra label so the axis carries exactly one value.",
        file=sys.stderr,
    )


def print_detail(proposals: list[dict]):
    by_machine = defaultdict(list)
    for p in proposals:
        by_machine[p["machine"]].append(p)
    for machine in sorted(by_machine):
        cards = by_machine[machine]
        print(f"\n\033[1m{machine}\033[0m  ({len(cards)} cards)")
        for p in cards:
            slot = "▶" if p["slot"] == "active-eligible" else "\033[2m·\033[0m"
            prov = p["provider"] + ("(Q)" if p.get("quota_demoted") else "")
            tag = "\033[35m" if p["routed_by"] == "manual" else ""
            print(f"  {slot} [{prov:<6}] {p['domain'] or '–':<14} "
                  f"{tag}{p['key']}\033[0m  {p['title']}")


def print_summary(proposals: list[dict]):
    total = len(proposals)
    # machine x provider matrix
    matrix = defaultdict(lambda: defaultdict(int))
    active = defaultdict(int)
    for p in proposals:
        matrix[p["machine"]][p["provider"]] += 1
        if p["slot"] == "active-eligible":
            active[p["machine"]] += 1
    provs = sorted({p["provider"] for p in proposals})
    print("\n\033[1mAssignment summary (machine × provider)\033[0m")
    header = f"  {'machine':<14}" + "".join(f"{pr:>9}" for pr in provs) + f"{'total':>8}{'active*':>9}"
    print(header)
    print("  " + "─" * (len(header) - 2))
    for m in sorted(matrix):
        row = f"  {m:<14}"
        mt = 0
        for pr in provs:
            c = matrix[m][pr]; mt += c
            row += f"{c or '·':>9}"
        row += f"{mt:>8}{active[m]:>9}"
        print(row)
    # domain coverage
    dom_counts = defaultdict(int)
    for p in proposals:
        dom_counts[p["domain"] or "(no domain)"] += 1
    no_dom = dom_counts.get("(no domain)", 0)
    manual = sum(1 for p in proposals if p["routed_by"] == "manual")
    demoted = sum(1 for p in proposals if p.get("quota_demoted"))
    print(f"\n  total open cards routed: \033[1m{total}\033[0m   "
          f"with domain: {total - no_dom}   no domain: {no_dom}   "
          f"manual-override: {manual}"
          + (f"   \033[1;33mquota-demoted: {demoted}\033[0m" if demoted else ""))
    print(f"  *active = concurrent slots allowed now per WIP caps; "
          f"the rest sit dispatch:ready in queue.")
    print("\n\033[2mDRY-RUN — no labels written. `--detail` for per-card, "
          f"`--apply` to preview writes; `--apply --yes` with {APPLY_FLAG}=1 to "
          "actually write.\033[0m")


# ---------------------------------------------------------------------------
# Phase B: apply labels to live GitHub issues (idempotent, live-verified, batched)
# ---------------------------------------------------------------------------
# Conventions adopted from the pre-existing in-the-wild label scheme so new
# labels are visually consistent (machine:/domain: already established).
LABEL_CONVENTION = {
    "domain":   ("c5def5", "Domain: {v}"),       # matches workspace-hub's 162 labels
    "machine":  ("e4e669", "Assigned to {v}"),   # matches existing machine: labels
    "ai":       ("0e8a16", "AI provider: {v}"),
    "dispatch": ("fbca04", "Dispatch: {v}"),
}


def gh(args: list[str], **kw):
    return subprocess.run(["gh", *args], capture_output=True, text=True, **kw)


def existing_labels(repo: str) -> set[str]:
    out = gh(["label", "list", "--repo", repo, "--limit", "500", "--json", "name"])
    if out.returncode != 0:
        return set()
    return {l["name"] for l in json.loads(out.stdout)}


def ensure_labels(repo: str, names: set[str], dry: bool):
    """Create ONLY missing labels (never overwrite an existing definition's
    color/description — those may follow an established convention)."""
    have = set() if dry else existing_labels(repo)
    for name in sorted(names):
        ns, _, val = name.partition(":")
        color, desc_t = LABEL_CONVENTION.get(ns, ("ededed", "{v}"))
        desc = desc_t.format(v=val)
        if name in have:
            print(f"    label: {name}  (exists — left as-is)")
            continue
        if dry:
            print(f"    label: {name}  (would create #{color})")
            continue
        gh(["label", "create", name, "--repo", repo, "--color", color,
            "--description", desc])  # no --force: create-only


def fetch_open_issues(repo: str):
    """ONE GraphQL call: map {number -> set(label names)} for all OPEN issues.
    Replaces per-issue lookups (which exhausted the 5000-pt GraphQL budget on
    big repos). Returns None on API failure (e.g. rate limit) so the caller can
    abort cleanly instead of miscounting failures as drift."""
    LIMIT = 100000  # effectively unbounded; truncation here silently drops issues
    out = gh(["issue", "list", "--repo", repo, "--state", "open",
              "--limit", str(LIMIT), "--json", "number,labels"])
    if out.returncode != 0:
        return None
    try:
        items = json.loads(out.stdout)
    except Exception:
        return None
    if len(items) >= LIMIT:
        # would silently truncate -> false drift-skips that never self-heal; abort
        return None
    return {str(it["number"]): {l["name"] for l in it["labels"]} for it in items}


def repo_has_domain_authority(repo: str) -> bool:
    """True if the repo owns an authoritative fine-grained domain: taxonomy
    (a domain-map-<name>.yaml exists). For those repos we NEVER write coarse
    board-domain labels — doing so would create a mixed fine/coarse taxonomy.
    The map governs board-grouping instead. (e.g. workspace-hub: 162 labels)"""
    base = repo.split("/")[-1]
    return (KANBAN / f"domain-map-{base}.yaml").exists()


def labels_for(p: dict, existing: set[str], skip_domain: bool = False) -> list[str]:
    """Labels to ADD for one proposal, given the issue's current labels.
    - dispatch:ready always
    - domain: only if issue has none AND repo lacks its own authoritative taxonomy
    - machine: only if none set (respect manual assignment)
    - ai: only when a rule/human chose a non-default provider"""
    out = []
    # dispatch:ready only if the issue has NO dispatch: state yet — re-adding it
    # would bounce a consumer-advanced (active/done) issue back to ready (P1).
    if not any(n.startswith("dispatch:") for n in existing):
        out.append("dispatch:ready")
    has_domain = any(n.startswith("domain:") for n in existing)
    if p["domain"] and not has_domain and not skip_domain:
        out.append(f"domain:{p['domain']}")
    if not any(n.startswith("machine:") for n in existing):
        out.append(f"machine:{p['machine']}")
    if p["provider_explicit"] and not any(n.startswith("ai:") for n in existing):
        out.append(f"ai:{p['provider']}")
    # don't re-add labels already present
    return [l for l in out if l not in existing]


# ---------------------------------------------------------------------------
# Write gate (deckhand#584 slice 2).
#
# route.py used to PRINT "`--apply` for Phase B (disabled)" while --apply/--yes
# were real flags reaching a live `gh issue edit --add-label`. The "disabled"
# lived only in a help string.
#
# The original justification named a specific defect: routing-rules claimed a
# solver capability for a host that could not obtain the licence (deckhand#579),
# so an accidental mass-apply would have dispatched 177 issues into guaranteed
# failure. **That defect is FIXED** — the rules now target a host carrying a
# dated `licence_verified` attestation, enforced by
# tests/dispatch/test_routing_rules_capability_truth.py.
#
# The gate stays, because its reason was never that one defect. A mass label
# write is high-blast-radius whether or not today's map is correct, and the map
# is a human-maintained file that can go wrong again. Removing a control once
# its triggering incident is closed is how the next incident gets discovered in
# production.
#
# The gate is an ENVIRONMENT flag, deliberately not a config value: config is
# committed and diffable, so a flag flipped in a PR could be merged without
# anyone registering that it armed a mass-write path. An env var has to be set
# by the person running the command, at the moment they run it.
# ---------------------------------------------------------------------------

APPLY_FLAG = "DISPATCH_APPLY_ENABLED"
#: Only these open the gate. Anything else — including "0", "false", "off" and
#: the empty string — fails closed. A naive truthiness check would treat "0" and
#: "false" as permission, which is worse than no gate because it reads protected.
_AFFIRMATIVE = {"1", "true", "yes", "on"}


def assert_write_allowed() -> None:
    """Exit unless the operator explicitly armed writes for this invocation."""
    value = (os.environ.get(APPLY_FLAG) or "").strip().lower()
    if value not in _AFFIRMATIVE:
        sys.exit(
            f"REFUSED: label writes are gated. Set {APPLY_FLAG}=1 to arm this "
            f"invocation.\n"
            f"  Before arming, confirm the capability map is correct. Licensed "
            f"routing is now guarded by a dated `licence_verified` attestation "
            f"(deckhand#579) — but the map is hand-maintained, and a mass-apply "
            f"writes labels across hundreds of issues.\n"
            f"  Run `--coverage` first to see what is actually assigned."
        )


def cmd_apply(proposals: list[dict], repo: str, do_write: bool, batch: int, pace: float):
    import time

    # Gate BEFORE any fetch, label-ensure, or write. Dry-run (--apply without
    # --yes) is a preview and stays ungated: gating it too would push people to
    # set the flag habitually, which defeats the gate.
    if do_write:
        assert_write_allowed()
    # `ai:` is included here but NOT in the routing-rules `single` list: it is a
    # dispatch-time override read by resolve_provider, and two of them would be
    # the same contradiction. Declared at the write boundary because that is the
    # only place this process creates one.
    write_single_axes = set(load_axis_cardinality(load_rules())[0]) | {"ai:"}
    proposals = [p for p in proposals if p["repo"] == repo]
    if not proposals:
        sys.exit(f"no open cards for {repo}")
    skip_domain = repo_has_domain_authority(repo)
    # universe of labels that could be added (empty-existing = max set) to ensure defs
    used = set()
    for p in proposals:
        used.update(labels_for(p, set(), skip_domain))
    print(f"\n\033[1m{'APPLY' if do_write else 'APPLY (dry-run)'} -> {repo}\033[0m  "
          f"({len(proposals)} cards)" + ("  [domain: skipped — repo has own taxonomy]" if skip_domain else ""))
    print("  label namespaces to ensure:")
    ensure_labels(repo, used, dry=not do_write)

    # one pre-fetch of live open issues (None => API/rate-limit failure)
    live = None if not do_write else fetch_open_issues(repo)
    if do_write and live is None:
        sys.exit("ERR: could not fetch live issues (rate limit?). "
                 "Check `gh api rate_limit`; re-run after reset (idempotent).")

    written = noop = err = drifted = 0
    for i, p in enumerate(proposals, 1):
        if not do_write:
            labs = labels_for(p, set(), skip_domain)  # optimistic preview
            print(f"    #{p['number']:<6} += {','.join(labs)}")
            continue
        existing = live.get(p["number"])
        if existing is None:
            drifted += 1  # genuinely not open (closed since snapshot) — not an API error
            continue
        labs = labels_for(p, existing, skip_domain)
        if not labs:
            noop += 1  # already fully labeled
            continue
        # Fail closed at the mutation boundary. A wrongly-written label is
        # expensive to undo across hundreds of issues (#582's 676-issue
        # migration is the local proof of how far one travels), so the check
        # goes BEFORE `gh`, not in a report afterwards.
        assert_write_preserves_cardinality(set(existing) | set(labs), write_single_axes)
        r = gh(["issue", "edit", p["number"], "--repo", repo, "--add-label", ",".join(labs)])
        if r.returncode == 0:
            written += 1
        else:
            err += 1
            print(f"    #{p['number']:<6} \033[31mERR\033[0m {r.stderr.strip()[:60]}")
            if "rate limit" in r.stderr.lower():
                print("    \033[31mrate limit hit — stopping; re-run after reset "
                      "(idempotent).\033[0m")
                break
        if i % batch == 0:
            time.sleep(pace)
    if do_write:
        print(f"\n  \033[32mwritten={written}\033[0m  already-labeled={noop}  "
              f"errors={err}  drift-skipped={drifted}")
    else:
        print("\n  \033[2mdry-run — re-run with --apply --yes to write "
              "(domain: shown optimistically; skipped live where one exists).\033[0m")


def cmd_coverage(args) -> None:
    """READ-ONLY coverage report (deckhand#584). Reaches no write path."""
    cfg = load_rules()
    defaults = cfg.get("defaults", {}) or {}
    skip = list(defaults.get("skip_if_labeled", []) or [])
    # Deliberately-unscheduled markers. These must ALSO be honoured by the
    # routing engine, not merely named here — see #584: a marker that the
    # report calls terminal while the engine routes it is a dead control.
    terminal = list(defaults.get("terminal_if_labeled", []) or
                    ["machine:unassigned", "status:icebox"])
    axes = ("machine:", "lane:")

    repos = [args.repo] if args.repo else DEFAULT_COVERAGE_REPOS
    overall = {}
    for repo in repos:
        issues = fetch_issues_for_coverage(repo)
        overall[repo] = coverage_report(issues, axes, terminal, skip)

    if args.json:
        print(json.dumps(overall, indent=2))
        return

    for repo, rep_ in overall.items():
        print(f"\n\033[1m{repo}\033[0m  open={rep_['total']}")
        for axis, c in rep_["axes"].items():
            print(f"  {axis:<10} missing={c['missing']:<5} ambiguous={c['ambiguous']:<4} "
                  f"terminal={c['terminal']:<4} skipped={c['skipped']:<4} routable={c['routable']}")
        if rep_["missing_all_axes"]:
            n_all = len(rep_["missing_all_axes"])
            print(f"  \033[1;33mno axis at all: {n_all}\033[0m "
                  f"(e.g. {rep_['missing_all_axes'][:8]})")
    print("\n\033[2mREAD-ONLY — no labels written. `model:` absence is NOT a gap "
          "(#584: it means the executor chooses).\033[0m")


DEFAULT_COVERAGE_REPOS = (
    "vamseeachanta/workspace-hub",
    "vamseeachanta/digitalmodel",
    "vamseeachanta/deckhand",
)


def fetch_issues_for_coverage(repo: str) -> list[dict]:
    """Open issues with labels as a LIST, via gh. READ-ONLY: `issue list` only.

    Deliberately named apart from `fetch_open_issues()` (line ~687), which
    returns a `{number -> set(labels)}` MAPPING for the write path.

    They previously shared a name. Python keeps the last definition, so this one
    shadowed the mapping version and `cmd_apply`'s `live.get(number)` raised
    `AttributeError: 'list' object has no attribute 'get'` — the write path was
    broken on main from the moment the coverage reporter landed (#3713).

    It went unnoticed because the only caller is `--apply --yes`, which is gated
    behind `DISPATCH_APPLY_ENABLED`: a path nobody had armed since. Two functions
    with one name and different return types is a collision no test asserts
    against, which is why the shapes are now in the names.
    """
    r = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "open",
         "--limit", "2000", "--json", "number,labels"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return []
    return [{"number": i["number"], "labels": [lab["name"] for lab in i.get("labels", [])]}
            for i in json.loads(r.stdout or "[]")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--coverage", action="store_true",
                    help="READ-ONLY assignment-coverage report (deckhand#584); "
                         "never writes. Buckets: missing/ambiguous/terminal/skipped/routable")
    ap.add_argument("--detail", action="store_true", help="per-card listing")
    ap.add_argument("--apply", action="store_true", help="write GH labels (Phase B)")
    ap.add_argument("--yes", action="store_true",
                    help=f"actually write (else apply dry-run); requires {APPLY_FLAG}=1")
    ap.add_argument("--batch", type=int, default=50, help="pace every N writes")
    ap.add_argument("--pace", type=float, default=2.0, help="seconds to sleep per batch")
    ap.add_argument("--codex-remaining", type=float, default=None,
                    dest="codex_remaining",
                    help="override live codex weekly remaining %% for the lane "
                         "quota gate (loud operator escape hatch, #3030)")
    args = ap.parse_args()

    if args.coverage:
        # Returns BEFORE propose(): the reporter must not touch the routing
        # engine's proposal path at all, so it cannot reach a write.
        cmd_coverage(args)
        return

    proposals = propose(args)
    if args.json:
        print(json.dumps(proposals, indent=2))
        return
    if args.apply:
        # guardrail: --apply is per-repo so rollout stays incremental (canary first)
        if not args.repo:
            sys.exit("--apply requires --repo <owner/name> (incremental rollout; "
                     "no all-repos bulk apply).")
        cmd_apply(proposals, args.repo, do_write=args.yes,
                  batch=args.batch, pace=args.pace)
        return
    if args.detail or args.repo:
        print_detail(proposals)
    print_summary(proposals)


if __name__ == "__main__":
    main()
