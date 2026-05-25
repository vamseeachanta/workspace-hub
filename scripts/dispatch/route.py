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
import argparse, json, subprocess, sys
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
    for lab in labels or []:
        if lab.startswith(prefix):
            return lab.split(":", 1)[1]
    return None


def match_rule(rules: list[dict], *, repo, domain, gh_labels) -> dict:
    """First-match-wins. Empty match {} is the catch-all."""
    labelset = set(gh_labels or [])
    for rule in rules:
        m = rule.get("match", {})
        if "repo" in m and m["repo"] != repo:
            continue
        if "domain" in m and m["domain"] != domain:
            continue
        if "gh_label" in m and m["gh_label"] not in labelset:
            continue
        return rule
    return {"assign": {}, "reason": "no rule matched"}


def propose(args) -> list[dict]:
    cfg = load_rules()
    rules = cfg.get("rules", [])
    defaults = cfg.get("defaults", {})
    aliases = cfg.get("machine_aliases", {})  # label-in-the-wild -> canonical
    skip_labels = set(defaults.get("skip_if_labeled", []))
    routable_states = set(defaults.get("routable_states", ["open"]))

    proposals = []
    for board, card in iter_cards():
        repo = board.get("repo")
        if args.repo and repo != args.repo:
            continue
        if card.get("gh_state") not in routable_states:
            continue
        labels = card.get("gh_labels") or []
        if skip_labels & set(labels):
            continue

        domain = board.get("domain")  # card's domain = the board it lives in
        rule = match_rule(rules, repo=repo, domain=domain, gh_labels=labels)
        assign = rule.get("assign", {})

        # human-set labels on the issue always override the rule
        existing_machine = existing_label_value(labels, "machine:")
        existing_ai = existing_label_value(labels, "ai:")
        machine = existing_machine or assign.get("machine") or defaults.get("machine")
        machine = aliases.get(machine, machine)  # fold acma-ws014 -> licensed-win-2
        provider = existing_ai or assign.get("provider") or defaults.get("provider")
        # provider is "explicit" only if a human or a rule chose it (not the default)
        provider_explicit = bool(existing_ai or assign.get("provider"))
        routed_by = "manual" if existing_machine else "rule"

        proposals.append({
            "key": card.get("idempotency_key"),
            "repo": repo,
            "number": card.get("idempotency_key", "").rsplit("#", 1)[-1],
            "domain": domain,
            "title": (card.get("title") or "")[:60],
            "machine": machine,
            "has_machine_label": bool(existing_machine),
            "provider": provider,
            "provider_explicit": provider_explicit,
            "routed_by": routed_by,
            "reason": rule.get("reason", ""),
            "url": card.get("source_url"),
        })
    return apply_wip(proposals, cfg)


def apply_wip(proposals: list[dict], cfg: dict) -> list[dict]:
    """Mark cards beyond a WIP cap as queued (dispatch stays ready, not active)."""
    caps = cfg.get("wip_caps", {})
    per_machine = caps.get("per_machine", {})
    per_provider = caps.get("per_provider", {})
    pools = cfg.get("budget_pools", {})
    # map provider -> pool
    prov_pool = {}
    for pool, meta in pools.items():
        for member in meta.get("members", []):
            prov_pool[member] = pool
    pool_cap = {p: meta.get("max_concurrent", 999) for p, meta in pools.items()}

    m_count = defaultdict(int)
    p_count = defaultdict(int)
    pool_count = defaultdict(int)
    # priority: rule-routed engineering first is out of scope here; keep input order
    for p in proposals:
        m, prov = p["machine"], p["provider"]
        over = False
        if m in per_machine and m_count[m] >= per_machine[m]:
            over = True
        if prov in prov_pool:
            pool = prov_pool[prov]
            if pool_count[pool] >= pool_cap.get(pool, 999):
                over = True
        elif prov in per_provider and p_count[prov] >= per_provider[prov]:
            over = True
        p["slot"] = "queued" if over else "active-eligible"
        if not over:
            m_count[m] += 1
            p_count[prov] += 1
            if prov in prov_pool:
                pool_count[prov_pool[prov]] += 1
    return proposals


def print_detail(proposals: list[dict]):
    by_machine = defaultdict(list)
    for p in proposals:
        by_machine[p["machine"]].append(p)
    for machine in sorted(by_machine):
        cards = by_machine[machine]
        print(f"\n\033[1m{machine}\033[0m  ({len(cards)} cards)")
        for p in cards:
            slot = "▶" if p["slot"] == "active-eligible" else "\033[2m·\033[0m"
            prov = p["provider"]
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
    print(f"\n  total open cards routed: \033[1m{total}\033[0m   "
          f"with domain: {total - no_dom}   no domain: {no_dom}   "
          f"manual-override: {manual}")
    print(f"  *active = concurrent slots allowed now per WIP caps; "
          f"the rest sit dispatch:ready in queue.")
    print("\n\033[2mDRY-RUN — no labels written. `--detail` for per-card, "
          "`--apply` for Phase B (disabled).\033[0m")


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


def live_state(repo: str, number: str):
    """Return (is_open, existing_label_names) at write time. Guards both the
    3-day mirror staleness AND respects pre-existing domain: taxonomies."""
    out = gh(["issue", "view", number, "--repo", repo, "--json", "state,labels"])
    if out.returncode != 0:
        return False, set()
    try:
        d = json.loads(out.stdout)
        return d.get("state", "").lower() == "open", {l["name"] for l in d.get("labels", [])}
    except Exception:
        return False, set()


def labels_for(p: dict, existing: set[str]) -> list[str]:
    """Labels to ADD for one proposal, given the issue's current labels.
    - dispatch:ready always
    - domain: only if the issue has NO domain: label yet (respect fine taxonomies)
    - machine: only if none set (respect manual assignment)
    - ai: only when a rule/human chose a non-default provider"""
    out = ["dispatch:ready"]
    has_domain = any(n.startswith("domain:") for n in existing)
    if p["domain"] and not has_domain:
        out.append(f"domain:{p['domain']}")
    if not any(n.startswith("machine:") for n in existing):
        out.append(f"machine:{p['machine']}")
    if p["provider_explicit"] and not any(n.startswith("ai:") for n in existing):
        out.append(f"ai:{p['provider']}")
    # don't re-add labels already present
    return [l for l in out if l not in existing]


def cmd_apply(proposals: list[dict], repo: str, do_write: bool, batch: int, pace: float):
    import time
    proposals = [p for p in proposals if p["repo"] == repo]
    if not proposals:
        sys.exit(f"no open cards for {repo}")
    # universe of labels that could be added (empty-existing = max set) to ensure defs
    used = set()
    for p in proposals:
        used.update(labels_for(p, set()))
    print(f"\n\033[1m{'APPLY' if do_write else 'APPLY (dry-run)'} -> {repo}\033[0m  "
          f"({len(proposals)} cards)")
    print("  label namespaces to ensure:")
    ensure_labels(repo, used, dry=not do_write)

    written = noop = err = drifted = 0
    for i, p in enumerate(proposals, 1):
        if not do_write:
            labs = labels_for(p, set())  # optimistic preview (domain shown even if skipped live)
            print(f"    #{p['number']:<6} += {','.join(labs)}")
            continue
        is_open, existing = live_state(repo, p["number"])
        if not is_open:
            drifted += 1
            print(f"    #{p['number']:<6} \033[33mSKIP (not live-open)\033[0m")
            continue
        labs = labels_for(p, existing)
        if not labs:
            noop += 1  # already fully labeled
            continue
        r = gh(["issue", "edit", p["number"], "--repo", repo, "--add-label", ",".join(labs)])
        if r.returncode == 0:
            written += 1
        else:
            err += 1
            print(f"    #{p['number']:<6} \033[31mERR\033[0m {r.stderr.strip()[:60]}")
        if i % batch == 0:
            time.sleep(pace)
    if do_write:
        print(f"\n  \033[32mwritten={written}\033[0m  already-labeled={noop}  "
              f"errors={err}  drift-skipped={drifted}")
    else:
        print("\n  \033[2mdry-run — re-run with --apply --yes to write "
              "(domain: shown optimistically; skipped live where one exists).\033[0m")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--detail", action="store_true", help="per-card listing")
    ap.add_argument("--apply", action="store_true", help="write GH labels (Phase B)")
    ap.add_argument("--yes", action="store_true", help="actually write (else apply dry-run)")
    ap.add_argument("--batch", type=int, default=50, help="pace every N writes")
    ap.add_argument("--pace", type=float, default=2.0, help="seconds to sleep per batch")
    args = ap.parse_args()

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
