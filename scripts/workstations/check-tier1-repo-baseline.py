#!/usr/bin/env python3
"""Read-only ace-linux-1 tier-1 repo placement checker for #2766."""

from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

SOURCE = "scripts/workstations/check-tier1-repo-baseline.py"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    raise ValueError("expected list")


def _policy(baseline: dict[str, Any], key: str, default: str) -> str:
    return str((baseline.get("placement_rules") or {}).get(key, default))


def _emit(items: list[dict[str, str]], severity: str, code: str, message: str, repo: str | None = None) -> None:
    item = {"code": code, "message": message}
    if repo is not None:
        item["repo"] = repo
    items.append(item)


def _apply_policy(blockers: list[dict[str, str]], warnings: list[dict[str, str]], severity: str, code: str, message: str, repo: str | None = None) -> None:
    target = blockers if severity == "error" else warnings
    _emit(target, severity, code, message, repo)


def _is_git_metadata(path: Path) -> bool:
    return (path / ".git").is_dir() or (path / ".git").is_file()


def _inventory_sibling_git_repos(repo_root: Path) -> set[str]:
    if not repo_root.exists():
        return set()
    return {child.name for child in repo_root.iterdir() if child.is_dir() and _is_git_metadata(child)}


def _nested_git_children(workspace_root: Path) -> list[str]:
    if not workspace_root.exists() or not workspace_root.is_dir():
        return []
    return sorted(child.name for child in workspace_root.iterdir() if child.is_dir() and _is_git_metadata(child))


def classification_overlaps(baseline: dict[str, Any]) -> dict[str, list[str]]:
    buckets: dict[str, set[str]] = {
        "required": set(_as_list(baseline.get("required"))),
        "optional": set(_as_list(baseline.get("optional"))),
        "reference_only": set(_as_list(baseline.get("reference_only"))),
        "not_planned": set(_as_list(baseline.get("not_planned"))),
        "non_tier1_machine_access_current": set(_as_list(baseline.get("non_tier1_machine_access_current"))),
        "historically_moved_not_currently_present": set((baseline.get("historically_moved_not_currently_present") or {}).keys()),
    }
    repo_to_buckets: dict[str, list[str]] = {}
    for bucket, repos in buckets.items():
        for repo in repos:
            repo_to_buckets.setdefault(repo, []).append(bucket)
    return {repo: names for repo, names in repo_to_buckets.items() if len(names) > 1}


def minimal_registry_for_tests(*, repo_root: Path, workspace_root: Path) -> dict[str, Any]:
    required = ["workspace-hub", "digitalmodel", "assetutilities", "worldenergydata", "llm-wiki", "assethold"]
    optional = ["aceengineer-website", "aceengineer-strategy"]
    non_tier1 = [
        "aceengineer-admin",
        "achantas-data",
        "achantas-media",
        "CAD-DEVELOPMENTS",
        "hobbies",
        "kaggle-rogii-2026",
        "llm-wiki-acma",
        "sabithaandkrishnaestates",
        "teamresumes",
    ]
    historical_names = ["acma-projects", "client_projects", "doris", "frontierdeepwater", "OGManufacturing", "rock-oil-field", "saipem", "sd-work", "seanation"]
    historical = {}
    for name in historical_names:
        historical[name] = {
            "source_issue": 2766,
            "source_comment": 4497956095,
            "prior_claim": "sibling=git" if name != "OGManufacturing" else "sibling=git and registry-runtime-access",
            "latest_probe": "absent",
            "warning": "historical_state_changed_since_prior_comment",
        }
    historical["OGManufacturing"]["runtime_access_change"] = "remove_from_data_access_profile"
    return {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "workspace_root": str(workspace_root),
                "tier1_repo_root": str(repo_root),
                "repo_layout": "sibling",
                "repos": required + optional + non_tier1,
                "telegram_hermes": {"data_access_profile": {"repos": required}},
                "tier1_baseline": {
                    "version": 1,
                    "source_issues": {"tier1_decision": 2770, "relocation_reconciliation": 2766},
                    "repo_root": str(repo_root),
                    "workspace_root": str(workspace_root),
                    "layout": "sibling",
                    "required": required,
                    "optional": optional,
                    "reference_only": [],
                    "not_planned": [],
                    "non_tier1_machine_access_current": non_tier1,
                    "historically_moved_not_currently_present": historical,
                    "infrastructure_dirs": ["agent-worktrees"],
                    "placement_rules": {
                        "root_git_self_allowed": True,
                        "direct_nested_git_policy": "error",
                        "required_absence_policy": "error",
                        "optional_absence_policy": "warning",
                        "non_tier1_absence_policy": "warning",
                        "historical_absence_policy": "warning",
                        "historical_state_changed_since_prior_comment_policy": "warning",
                        "unknown_sibling_git_policy": "warning",
                        "dirty_policy": {"required": "warning", "optional": "warning", "non_tier1_machine_access_current": "warning"},
                        "ahead_policy": {"required": "warning", "optional": "warning", "non_tier1_machine_access_current": "warning"},
                        "behind_policy": {"required": "warning", "optional": "warning", "non_tier1_machine_access_current": "warning"},
                    },
                },
            }
        }
    }


def _load_registry(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("machines"), dict):
        raise ValueError("registry must contain machines mapping")
    return data


def _validate_registry_contract(machine: dict[str, Any], baseline: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if baseline.get("version") != 1:
        _emit(blockers, "error", "invalid_schema", "tier1_baseline.version must be 1")
    if str(machine.get("tier1_repo_root")) != str(baseline.get("repo_root")):
        _emit(blockers, "error", "repo_root_mismatch", "machines.dev-primary.tier1_repo_root must match tier1_baseline.repo_root")
    if str(machine.get("workspace_root")) != str(baseline.get("workspace_root")):
        _emit(blockers, "error", "workspace_root_mismatch", "machines.dev-primary.workspace_root must match tier1_baseline.workspace_root")
    if str(machine.get("repo_layout")) != str(baseline.get("layout")):
        _emit(blockers, "error", "repo_layout_mismatch", "machines.dev-primary.repo_layout must match tier1_baseline.layout")
    if classification_overlaps(baseline):
        _emit(blockers, "error", "classification_overlap", f"classification buckets overlap: {classification_overlaps(baseline)}")
    expected_repos = _as_list(baseline.get("required")) + _as_list(baseline.get("optional")) + _as_list(baseline.get("non_tier1_machine_access_current"))
    if _as_list(machine.get("repos")) != expected_repos:
        _emit(blockers, "error", "registry_repos_mismatch", "machines.dev-primary.repos must equal required + optional + non_tier1_machine_access_current")
    data_access_repos = _as_list(((machine.get("telegram_hermes") or {}).get("data_access_profile") or {}).get("repos"))
    if data_access_repos != _as_list(baseline.get("required")):
        _emit(blockers, "error", "data_access_mismatch", "data_access_profile.repos must equal exactly the required tier-1 set")
    return blockers, warnings



def _git_run(repo_path: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run git probes without optional index locks or network/mutation subcommands."""
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(["git", "--no-optional-locks", "-C", str(repo_path), *args], check=False, capture_output=True, text=True, env=env)


def _collect_git_state(repo_root: Path, repos: list[str]) -> dict[str, dict[str, Any]]:
    """Collect read-only dirty/ahead/behind state for existing repo checkouts."""
    states: dict[str, dict[str, Any]] = {}
    for repo in repos:
        repo_path = repo_root / repo
        if not repo_path.exists() or not _is_git_metadata(repo_path):
            continue
        status = _git_run(repo_path, ["status", "--porcelain=v1"])
        state: dict[str, Any] = {
            "dirty": bool(status.stdout.strip()) if status.returncode == 0 else False,
            "ahead": 0,
            "behind": 0,
        }
        if status.returncode != 0:
            state["probe_error"] = f"git status failed: {status.stderr.strip() or status.stdout.strip() or status.returncode}"
            states[repo] = state
            continue
        upstream = _git_run(repo_path, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
        if upstream.returncode == 0:
            state["upstream"] = upstream.stdout.strip()
            counts = _git_run(repo_path, ["rev-list", "--left-right", "--count", "@{upstream}...HEAD"])
            if counts.returncode == 0:
                try:
                    behind, ahead = (counts.stdout.strip().split() + ["0", "0"])[:2]
                    state["behind"] = int(behind)
                    state["ahead"] = int(ahead)
                except ValueError:
                    state["probe_error"] = f"git rev-list produced invalid counts: {counts.stdout.strip()}"
            else:
                state["probe_error"] = f"git rev-list failed: {counts.stderr.strip() or counts.stdout.strip() or counts.returncode}"
        else:
            state["upstream"] = None
        states[repo] = state
    return states


def _data_access_state(machine: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    configured = _as_list(((machine.get("telegram_hermes") or {}).get("data_access_profile") or {}).get("repos"))
    required = _as_list(baseline.get("required"))
    return {
        "configured_repos": configured,
        "required_repos": required,
        "matches_required": configured == required,
        "extra_repos": sorted(set(configured) - set(required)),
        "missing_required_repos": [repo for repo in required if repo not in set(configured)],
    }

def _classification_for(repo: str, baseline: dict[str, Any]) -> str | None:
    for bucket in ["required", "optional", "non_tier1_machine_access_current"]:
        if repo in set(_as_list(baseline.get(bucket))):
            return bucket
    return None


def check_machine(data: dict[str, Any], machine_id: str, *, repo_root: Path | None = None, git_state: dict[str, dict[str, Any]] | None = None, now: str | None = None) -> dict[str, Any]:
    machines = data.get("machines") or {}
    if machine_id != "dev-primary":
        raise ValueError("#2766 checker scope is dev-primary/ace-linux-1 only")
    machine = machines[machine_id]
    if machine.get("hostname") != "ace-linux-1":
        raise ValueError("machines.dev-primary.hostname must be ace-linux-1")
    baseline = machine.get("tier1_baseline") or {}
    root = Path(repo_root or machine.get("tier1_repo_root") or baseline.get("repo_root") or Path(machine.get("workspace_root", ".")).parent)
    workspace_root = Path(str(machine.get("workspace_root") or baseline.get("workspace_root") or root / "workspace-hub"))
    timestamp = now or str(((machine.get("telegram_hermes") or {}).get("readiness_now")) or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    blockers, warnings = _validate_registry_contract(machine, baseline)
    inventory = _inventory_sibling_git_repos(root)

    for repo in _as_list(baseline.get("required")):
        if repo not in inventory:
            _apply_policy(blockers, warnings, _policy(baseline, "required_absence_policy", "error"), "required_missing", f"required repo missing: {repo}", repo)
    for repo in _as_list(baseline.get("optional")):
        if repo not in inventory:
            _apply_policy(blockers, warnings, _policy(baseline, "optional_absence_policy", "warning"), "optional_missing", f"optional repo missing: {repo}", repo)
    for repo in _as_list(baseline.get("non_tier1_machine_access_current")):
        if repo not in inventory:
            _apply_policy(blockers, warnings, _policy(baseline, "non_tier1_absence_policy", "warning"), "non_tier1_missing", f"current non-tier-1 repo missing: {repo}", repo)

    historical = baseline.get("historically_moved_not_currently_present") or {}
    for repo, entry in historical.items():
        if not isinstance(entry, dict):
            continue
        if repo in inventory:
            _apply_policy(
                blockers,
                warnings,
                _policy(baseline, "historical_state_changed_since_prior_comment_policy", "warning"),
                "historical_repo_present",
                f"historical repo is present despite historical absent classification: {repo}",
                repo,
            )
        elif entry.get("warning") == "historical_state_changed_since_prior_comment":
            _apply_policy(
                blockers,
                warnings,
                _policy(baseline, "historical_state_changed_since_prior_comment_policy", "warning"),
                "historical_state_changed",
                f"historical state changed since prior comment: {repo} prior_claim={entry.get('prior_claim')} latest_probe={entry.get('latest_probe')}",
                repo,
            )

    known = (
        set(_as_list(baseline.get("required")))
        | set(_as_list(baseline.get("optional")))
        | set(_as_list(baseline.get("non_tier1_machine_access_current")))
        | set(historical.keys())
    )
    infra_dirs = set(_as_list(baseline.get("infrastructure_dirs")))
    for repo in sorted(inventory - known):
        _apply_policy(blockers, warnings, _policy(baseline, "unknown_sibling_git_policy", "warning"), "unknown_sibling_git_repo", f"unknown sibling git repo: {repo}", repo)
    for infra in sorted(infra_dirs):
        infra_path = root / infra
        if infra_path.exists() and _is_git_metadata(infra_path):
            _apply_policy(blockers, warnings, _policy(baseline, "unknown_sibling_git_policy", "warning"), "unknown_sibling_git_repo", f"infrastructure dir contains git metadata: {infra}", infra)

    for child in _nested_git_children(workspace_root):
        _apply_policy(blockers, warnings, _policy(baseline, "direct_nested_git_policy", "error"), "direct_nested_git_repo", f"direct nested git repo under workspace-hub: {child}", child)

    tracked_repos = _as_list(baseline.get("required")) + _as_list(baseline.get("optional")) + _as_list(baseline.get("non_tier1_machine_access_current"))
    git_state = git_state if git_state is not None else _collect_git_state(root, tracked_repos)
    dirty_policy = (baseline.get("placement_rules") or {}).get("dirty_policy") or {}
    ahead_policy = (baseline.get("placement_rules") or {}).get("ahead_policy") or {}
    behind_policy = (baseline.get("placement_rules") or {}).get("behind_policy") or {}
    upstream_policy = {"required": "error", "optional": "warning", "non_tier1_machine_access_current": "warning"}
    upstream_policy.update((baseline.get("placement_rules") or {}).get("upstream_policy") or {})
    for repo, state in git_state.items():
        bucket = _classification_for(repo, baseline)
        if not bucket:
            continue
        if state.get("probe_error"):
            _emit(blockers, "error", "git_probe_failed", f"{repo} git probe failed: {state.get('probe_error')}", repo)
            continue
        if "upstream" in state and not state.get("upstream"):
            _apply_policy(blockers, warnings, str(upstream_policy.get(bucket, "warning")), "git_upstream_missing", f"{repo} has no configured upstream/tracking branch", repo)
        if state.get("dirty"):
            _apply_policy(blockers, warnings, str(dirty_policy.get(bucket, "warning")), "git_dirty", f"{repo} dirty", repo)
        if int(state.get("ahead") or 0):
            _apply_policy(blockers, warnings, str(ahead_policy.get(bucket, "warning")), "git_ahead", f"{repo} ahead by {int(state.get('ahead') or 0)} commit(s)", repo)
        if int(state.get("behind") or 0):
            _apply_policy(blockers, warnings, str(behind_policy.get(bucket, "warning")), "git_behind", f"{repo} behind by {int(state.get('behind') or 0)} commit(s)", repo)

    data_access = _data_access_state(machine, baseline)

    return {
        "machine_id": machine_id,
        "machine": machine.get("hostname"),
        "source": SOURCE,
        "inventory_timestamp_utc": timestamp,
        "repo_root": str(root),
        "workspace_root": str(workspace_root),
        "dispatchable": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "git_state": git_state,
        "data_access": data_access,
        "inventory": {"sibling_git_repos": sorted(inventory), "nested_git_repos_under_workspace_root": _nested_git_children(workspace_root)},
        "baseline": baseline,
    }


def render_html(report: dict[str, Any]) -> str:
    baseline = report.get("baseline") or {}
    def rows(names: list[str]) -> str:
        inv = set((report.get("inventory") or {}).get("sibling_git_repos") or [])
        return "\n".join(f"<tr><td>{html.escape(name)}</td><td>{'present' if name in inv else 'missing'}</td></tr>" for name in names)
    hist = baseline.get("historically_moved_not_currently_present") or {}
    hist_rows = "\n".join(
        f"<tr><td>{html.escape(str(name))}</td><td>{html.escape(str(item.get('source_issue')))}</td><td>{html.escape(str(item.get('source_comment')))}</td><td>{html.escape(str(item.get('warning')))}</td></tr>"
        for name, item in hist.items() if isinstance(item, dict)
    )
    placement_json = html.escape(json.dumps({k: report[k] for k in ["dispatchable", "blockers", "warnings", "inventory_timestamp_utc", "source", "git_state", "data_access"]}, indent=2, sort_keys=True))
    return f"""<!doctype html>
<html><head><meta charset=\"utf-8\"><title>ace-linux-1 tier-1 checkout normalization</title></head>
<body>
<section id=\"summary\" data-machine=\"ace-linux-1\"><h1>ace-linux-1 tier-1 checkout normalization</h1><p>Dispatchable: {report.get('dispatchable')}</p></section>
<section id=\"required-tier1\"><h2>Required tier-1</h2><table>{rows(_as_list(baseline.get('required')))}</table></section>
<section id=\"optional-tier1\"><h2>Optional tier-1</h2><table>{rows(_as_list(baseline.get('optional')))}</table></section>
<section id=\"current-non-tier1-machine-access\"><h2>Current non-tier-1 machine access</h2><table>{rows(_as_list(baseline.get('non_tier1_machine_access_current')))}</table></section>
<section id=\"historical-reconciliation\"><h2>Historical reconciliation</h2><table>{hist_rows}</table></section>
<section id=\"nested-git-check\"><h2>Nested git check</h2><pre>{html.escape(json.dumps((report.get('inventory') or {}).get('nested_git_repos_under_workspace_root', []), indent=2))}</pre></section>
<section id=\"readiness-projection\"><h2>Readiness projection</h2><pre>{placement_json}</pre></section>
<section id=\"runbook-rollback-policy\"><h2>Runbook / rollback policy</h2><ol><li>No clone, pull, fetch, push, move, delete, or sync is authorized by this checker.</li><li>Future repo movement requires preflight evidence and separate approval.</li><li>Dirty or unique checkouts must be preserved before any future mutation.</li></ol></section>
</body></html>
"""


def render_markdown(report: dict[str, Any]) -> str:
    """Render a compact operator-readable checker report."""
    blockers = report.get("blockers") or []
    warnings = report.get("warnings") or []
    lines = [
        "# ace-linux-1 tier-1 checkout normalization",
        "",
        f"- Source: `{report.get('source')}`",
        f"- Generated: `{report.get('inventory_timestamp_utc')}`",
        f"- Dispatchable: `{report.get('dispatchable')}`",
        "",
        "## Blockers",
    ]
    if blockers:
        lines.extend(f"- `{item.get('code')}` {item.get('message')}" for item in blockers)
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Warnings")
    if warnings:
        lines.extend(f"- `{item.get('code')}` {item.get('message')}" for item in warnings)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check ace-linux-1 tier-1 repo placement baseline")
    parser.add_argument("--registry", default="config/workstations/registry.yaml")
    parser.add_argument("--machine", default="dev-primary")
    parser.add_argument("--repo-root")
    parser.add_argument("--now")
    parser.add_argument("--format", choices=["json", "markdown", "html"], default="json")
    args = parser.parse_args(argv)
    data = _load_registry(args.registry)
    report = check_machine(data, args.machine, repo_root=Path(args.repo_root) if args.repo_root else None, now=args.now)
    if args.format == "html":
        rendered = render_html(report)
    elif args.format == "markdown":
        rendered = render_markdown(report)
    else:
        rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    return 1 if report["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
