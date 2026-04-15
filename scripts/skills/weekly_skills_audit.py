#!/usr/bin/env python3
"""weekly_skills_audit.py — Deterministic v1 weekly skills audit (#2281).

Scans .claude/skills/ for duplicate frontmatter names and leaf-directory
collisions, classifies findings per the policy contract at
config/skills/weekly-audit-policy.yaml, and emits stable JSON + Markdown
artifacts under logs/maintenance/skills-curation/.

This is a read-only audit: it never modifies the skills directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Inventory: discover and parse SKILL.md files
# ---------------------------------------------------------------------------

EXCLUDED_DIRS = {"_archive", "_diverged"}
INFORMATIONAL_DIRS = {"_core", "_internal"}


def _extract_frontmatter(skill_md: Path) -> dict | None:
    """Parse YAML frontmatter from a SKILL.md file. Returns None on failure."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    if not text.startswith("---"):
        return None

    end = text.find("\n---", 3)
    if end == -1:
        return None

    fm_text = text[4:end]
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None

    if not isinstance(fm, dict):
        return None

    return fm


def build_inventory(skills_dir: Path) -> list[dict]:
    """Walk skills_dir, returning a list of skill records.

    Each record: {canonical_name, leaf, path, informational_only, frontmatter}
    Excludes _archive and _diverged. Marks _core/_internal as informational_only.
    """
    inventory: list[dict] = []
    for root, dirs, files in os.walk(str(skills_dir)):
        root_path = Path(root)
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        if "SKILL.md" not in files:
            continue

        skill_md = root_path / "SKILL.md"
        rel_path = str(skill_md.relative_to(skills_dir))
        leaf = root_path.name.lower()

        # Determine if this is under an informational-only prefix
        try:
            parts = skill_md.relative_to(skills_dir).parts
        except ValueError:
            parts = ()
        informational = any(p in INFORMATIONAL_DIRS for p in parts)

        fm = _extract_frontmatter(skill_md)
        if fm and isinstance(fm.get("name"), str):
            canonical_name = fm["name"].strip().strip("'\"").lower()
        else:
            canonical_name = leaf

        inventory.append({
            "canonical_name": canonical_name,
            "leaf": leaf,
            "path": rel_path,
            "informational_only": informational,
            "frontmatter": fm,
            "frontmatter_valid": fm is not None,
        })

    return sorted(inventory, key=lambda s: s["path"])


# ---------------------------------------------------------------------------
# Classification: apply policy rules to produce findings
# ---------------------------------------------------------------------------

def _compute_finding_key(classification: str, names: list[str]) -> str:
    """Deterministic key: hash of classification + sorted canonical names."""
    payload = classification + "|" + "|".join(sorted(names))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _load_policy(policy_path: Path) -> dict:
    return yaml.safe_load(policy_path.read_text(encoding="utf-8"))


def _bucket_map(policy: dict) -> dict[str, dict]:
    return {b["id"]: b for b in policy["classification_buckets"]}


def _matches_rule(signals: set[str], rule: dict) -> bool:
    match_all = set(rule.get("match_all", []))
    match_any = set(rule.get("match_any", []))
    exclude_if_any = set(rule.get("exclude_if_any", []))
    if exclude_if_any & signals:
        return False
    if not match_all.issubset(signals):
        return False
    if match_any and not (match_any & signals):
        return False
    return True


def _classify(policy: dict, signals: set[str]) -> str:
    buckets = _bucket_map(policy)
    for bucket_id in policy["precedence_order"]:
        if _matches_rule(signals, buckets[bucket_id]["rule"]):
            return bucket_id
    return "needs-human-review"


def _escalation_state(policy: dict, classification: str) -> str:
    for rule in policy["escalation_model"]["rules"]:
        if classification in set(rule["when"]["classification_in"]):
            return rule["result"]
    return "no-escalation"


def _detect_findings(inventory: list[dict], policy: dict) -> list[dict]:
    """Detect duplicate names and leaf collisions, classify each."""
    buckets = _bucket_map(policy)

    # Group by canonical name
    name_groups: dict[str, list[dict]] = defaultdict(list)
    for item in inventory:
        name_groups[item["canonical_name"]].append(item)

    # Group by leaf directory name
    leaf_groups: dict[str, list[dict]] = defaultdict(list)
    for item in inventory:
        leaf_groups[item["leaf"]].append(item)

    findings: list[dict] = []
    seen_keys: set[str] = set()

    # Duplicate frontmatter names (same canonical_name, multiple paths)
    for name, items in sorted(name_groups.items()):
        if len(items) < 2:
            continue

        signals: set[str] = {"same_canonical_name", "same_primary_intent", "substantial_overlap"}
        # Check for wrapper signals
        has_wrapper = any(
            _is_wrapper(item) for item in items
        )
        has_explicit_target = any(
            item.get("frontmatter", {}).get("canonical_target") for item in items
            if item.get("frontmatter")
        )
        if has_wrapper:
            signals.add("wrapper_redirect")
        if has_explicit_target:
            signals.add("explicit_canonical_target")

        # Check if all are informational-only
        all_informational = all(item["informational_only"] for item in items)

        classification = _classify(policy, signals)
        bucket_def = buckets.get(classification, {})
        paths = [item["path"] for item in items]
        names = sorted({item["canonical_name"] for item in items})
        key = _compute_finding_key(classification, names)

        if key not in seen_keys:
            seen_keys.add(key)
            findings.append({
                "finding_key": key,
                "classification": classification,
                "severity": bucket_def.get("default_severity", "medium"),
                "confidence": bucket_def.get("default_confidence", "medium"),
                "canonical_names": names,
                "paths": paths,
                "summary": f"Duplicate canonical name '{name}' across {len(items)} skills",
                "recommended_action": bucket_def.get("recommended_action", "Review manually."),
                "escalation_state": _escalation_state(policy, classification),
                "is_new": True,
                "is_changed": False,
                "informational_only": all_informational,
            })

    # Leaf collisions (same leaf dir name, different canonical names)
    for leaf, items in sorted(leaf_groups.items()):
        if len(items) < 2:
            continue
        unique_names = {item["canonical_name"] for item in items}
        if len(unique_names) < 2:
            continue  # Same canonical name — already reported above

        signals: set[str]
        if all(name.endswith(f"-{leaf}") for name in unique_names):
            signals = {"same_primary_intent", "distinct_deliverable_surface"}
        else:
            signals = {"generic_leaf_only"}
        classification = _classify(policy, signals)
        bucket_def = buckets.get(classification, {})
        paths = [item["path"] for item in items]
        names = sorted(unique_names)
        key = _compute_finding_key(classification, names)
        all_informational = all(item["informational_only"] for item in items)

        if key not in seen_keys:
            seen_keys.add(key)
            findings.append({
                "finding_key": key,
                "classification": classification,
                "severity": bucket_def.get("default_severity", "medium"),
                "confidence": bucket_def.get("default_confidence", "medium"),
                "canonical_names": names,
                "paths": paths,
                "summary": f"Leaf collision on '{leaf}' with distinct names: {', '.join(names)}",
                "recommended_action": bucket_def.get("recommended_action", "Review manually."),
                "escalation_state": _escalation_state(policy, classification),
                "is_new": True,
                "is_changed": False,
                "informational_only": all_informational,
            })

    # Detect wrapper pairs (skills with canonical_target pointing to another skill)
    _detect_wrapper_pairs(inventory, policy, findings, seen_keys, buckets)

    return findings


def _is_wrapper(item: dict) -> bool:
    """Check if a skill declares itself as a wrapper/redirect."""
    fm = item.get("frontmatter") or {}
    skill_type = str(fm.get("type", "")).lower()
    return skill_type in ("wrapper", "redirect", "alias", "stub")


def _detect_wrapper_pairs(
    inventory: list[dict],
    policy: dict,
    findings: list[dict],
    seen_keys: set[str],
    buckets: dict[str, dict],
) -> None:
    """Find skills with canonical_target frontmatter pointing to another skill."""
    name_set = {item["canonical_name"] for item in inventory}

    for item in inventory:
        fm = item.get("frontmatter") or {}
        target = fm.get("canonical_target")
        if not target or not isinstance(target, str):
            continue
        target_lower = target.strip().lower()
        if target_lower not in name_set:
            continue

        signals = {"wrapper_redirect", "explicit_canonical_target"}
        classification = _classify(policy, signals)
        bucket_def = buckets.get(classification, {})
        names = sorted([item["canonical_name"], target_lower])
        paths = [item["path"]]
        key = _compute_finding_key(classification, names)

        if key not in seen_keys:
            seen_keys.add(key)
            findings.append({
                "finding_key": key,
                "classification": classification,
                "severity": bucket_def.get("default_severity", "low"),
                "confidence": bucket_def.get("default_confidence", "high"),
                "canonical_names": names,
                "paths": paths,
                "summary": f"Wrapper '{item['canonical_name']}' points to canonical '{target_lower}'",
                "recommended_action": bucket_def.get("recommended_action", "Keep canonical target authoritative."),
                "escalation_state": _escalation_state(policy, classification),
                "is_new": True,
                "is_changed": False,
                "informational_only": False,
            })


def _derive_audit_scope(skills_dir: Path) -> str:
    """Return a stable audit scope identifier across worktrees when possible."""
    resolved = skills_dir.resolve()
    parts = list(resolved.parts)
    if ".claude" in parts:
        idx = parts.index(".claude")
        return f"skills-dir:{Path(*parts[idx:])}"
    return f"skills-dir:{resolved}"


# ---------------------------------------------------------------------------
# Baseline comparison
# ---------------------------------------------------------------------------

def _load_baseline(artifact_dir: Path, policy_version: str, audit_scope: str) -> dict | None:
    """Load the most recent prior JSON artifact as baseline, if compatible."""
    if not artifact_dir.exists():
        return None

    json_files = sorted(artifact_dir.glob("*.json"), reverse=True)
    for jf in json_files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if (
            data.get("policy_version") == policy_version
            and data.get("audit_scope") == audit_scope
        ):
            return data
    return None


def _apply_baseline(findings: list[dict], baseline: dict | None) -> None:
    """Mark is_new/is_changed based on prior baseline."""
    if baseline is None:
        return  # All findings stay is_new=True

    prior_keys = {f["finding_key"] for f in baseline.get("findings", [])}
    prior_keys |= {f["finding_key"] for f in baseline.get("suppressed_findings", [])}
    prior_map = {}
    for f in baseline.get("findings", []) + baseline.get("suppressed_findings", []):
        prior_map[f["finding_key"]] = f

    for finding in findings:
        key = finding["finding_key"]
        if key in prior_keys:
            finding["is_new"] = False
            prior = prior_map.get(key, {})
            finding["is_changed"] = (
                finding.get("severity") != prior.get("severity")
                or finding.get("confidence") != prior.get("confidence")
                or finding.get("escalation_state") != prior.get("escalation_state")
                or finding.get("classification") != prior.get("classification")
                or finding.get("canonical_names") != prior.get("canonical_names")
                or finding.get("paths") != prior.get("paths")
            )
        else:
            finding["is_new"] = True
            finding["is_changed"] = False


def _split_informational_findings(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Move informational-only findings out of the main ranked findings list."""
    active: list[dict] = []
    informational: list[dict] = []
    for finding in findings:
        if finding.get("informational_only"):
            finding = dict(finding)
            finding["waiver_reason"] = "informational-only (_core/_internal de-emphasized in v1)"
            informational.append(finding)
        else:
            active.append(finding)
    return active, informational


# ---------------------------------------------------------------------------
# Waiver handling
# ---------------------------------------------------------------------------

def _load_waivers(waiver_path: Path | None) -> dict[str, dict]:
    """Load waiver registry keyed by finding_key. Expired waivers are ignored."""
    if waiver_path is None or not waiver_path.exists():
        return {}
    try:
        data = yaml.safe_load(waiver_path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    waivers = data.get("waivers", [])
    active_waivers: dict[str, dict] = {}
    today = date.today()
    for waiver in waivers:
        if not isinstance(waiver, dict) or "finding_key" not in waiver:
            continue
        expires = waiver.get("expires")
        if expires:
            try:
                expires_date = date.fromisoformat(str(expires))
            except ValueError:
                continue
            if expires_date < today:
                continue
        active_waivers[waiver["finding_key"]] = waiver
    return active_waivers


def _apply_waivers(
    findings: list[dict], waivers: dict[str, dict]
) -> tuple[list[dict], list[dict]]:
    """Split findings into active and suppressed based on waivers."""
    active: list[dict] = []
    suppressed: list[dict] = []
    for f in findings:
        if f["finding_key"] in waivers:
            waiver = waivers[f["finding_key"]]
            f["waiver_reason"] = waiver.get("reason", "waived")
            suppressed.append(f)
        else:
            active.append(f)
    return active, suppressed


# ---------------------------------------------------------------------------
# Ranking: sort findings per policy contract
# ---------------------------------------------------------------------------

_ESCALATION_RANK = {"candidate": 0, "no-escalation": 1}
_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


def _sort_findings(findings: list[dict]) -> list[dict]:
    def key_for(f: dict) -> tuple:
        return (
            _ESCALATION_RANK.get(f.get("escalation_state", "no-escalation"), 9),
            _SEVERITY_RANK.get(f.get("severity", "low"), 9),
            _CONFIDENCE_RANK.get(f.get("confidence", "low"), 9),
            0 if f.get("is_new") else 1,
            f.get("finding_key", ""),
        )
    return sorted(findings, key=key_for)


# ---------------------------------------------------------------------------
# Output: JSON + Markdown artifacts
# ---------------------------------------------------------------------------

def _write_json_artifact(result: dict, artifact_path: Path) -> None:
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(result, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def _write_markdown_artifact(result: dict, md_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# Weekly Skills Audit — {result['generated_at'][:10]}")
    lines.append("")
    lines.append(f"Policy version: `{result['policy_version']}`")
    lines.append(f"Scope: {result['audit_scope']}")
    lines.append(f"Baseline: {result['baseline_artifact'] or 'none (first run)'}")
    lines.append("")

    counts = result.get("summary_counts", {})
    lines.append(f"Total findings: {counts.get('total', 0)} | "
                 f"New: {counts.get('new', 0)} | "
                 f"Changed: {counts.get('changed', 0)} | "
                 f"Suppressed: {counts.get('suppressed', 0)} | "
                 f"Errors: {counts.get('errors', 0)}")
    lines.append("")

    # Section 1: New Findings
    lines.append("## New Findings")
    lines.append("")
    new = [f for f in result["findings"] if f.get("is_new")]
    if new:
        for f in new:
            lines.append(f"- **[{f['classification']}]** {f['summary']}  ")
            lines.append(f"  Key: `{f['finding_key']}` | Severity: {f['severity']} | Confidence: {f['confidence']}")
            lines.append(f"  Paths: {', '.join(f.get('paths', []))}")
            lines.append("")
    else:
        lines.append("No new findings.")
        lines.append("")

    # Section 2: Changed Findings
    lines.append("## Changed Findings")
    lines.append("")
    changed = [f for f in result["findings"] if f.get("is_changed")]
    if changed:
        for f in changed:
            lines.append(f"- **[{f['classification']}]** {f['summary']}  ")
            lines.append(f"  Key: `{f['finding_key']}` | Severity: {f['severity']}")
            lines.append("")
    else:
        lines.append("No changed findings.")
        lines.append("")

    # Section 3: Unresolved High-Confidence Findings
    lines.append("## Unresolved High-Confidence Findings")
    lines.append("")
    unresolved = [
        f for f in result["findings"]
        if f.get("confidence") == "high" and not f.get("is_new")
    ]
    if unresolved:
        for f in unresolved:
            lines.append(f"- **[{f['classification']}]** {f['summary']}  ")
            lines.append(f"  Key: `{f['finding_key']}`")
            lines.append("")
    else:
        lines.append("No unresolved high-confidence findings.")
        lines.append("")

    # Section 4: Suppressed / Carry-Forward Findings
    lines.append("## Suppressed / Carry-Forward Findings")
    lines.append("")
    carry_forward = [
        f for f in result["findings"]
        if not f.get("is_new") and not f.get("is_changed") and f.get("confidence") != "high"
    ]
    suppressed = result.get("suppressed_findings", [])
    combined_carry_forward = carry_forward + suppressed
    if combined_carry_forward:
        for f in combined_carry_forward:
            reason = f.get("waiver_reason", "carry-forward")
            lines.append(f"- `{f['finding_key']}` — {f['summary']} (reason: {reason})")
            lines.append("")
    else:
        lines.append("No suppressed findings.")
        lines.append("")

    # Section 5: Operational Errors
    lines.append("## Operational Errors")
    lines.append("")
    errors = result.get("errors", [])
    if errors:
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")
    else:
        lines.append("No operational errors.")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main audit entrypoint
# ---------------------------------------------------------------------------

def run_audit(
    *,
    skills_dir: Path,
    output_dir: Path,
    policy_path: Path,
    waiver_path: Path | None = None,
    run_date: date | None = None,
) -> dict:
    """Execute the full audit pipeline. Returns the result dict."""
    if run_date is None:
        run_date = date.today()

    policy = _load_policy(policy_path)
    policy_version = f"{policy.get('policy_id', 'unknown')}-v{policy.get('version', '?')}"

    # Build inventory
    inventory = build_inventory(skills_dir)

    # Detect errors (malformed frontmatter)
    errors: list[str] = []
    for item in inventory:
        if not item["frontmatter_valid"]:
            errors.append(f"Malformed or missing frontmatter: {item['path']}")

    # Detect findings
    findings = _detect_findings(inventory, policy)

    audit_scope = _derive_audit_scope(skills_dir)

    # Baseline comparison
    artifact_dir = output_dir / "logs" / "maintenance" / "skills-curation"
    baseline = _load_baseline(artifact_dir, policy_version, audit_scope)
    baseline_artifact = None
    if baseline:
        baseline_artifact = baseline.get("generated_at", "unknown")
        _apply_baseline(findings, baseline)

    # Move _core/_internal findings out of the active ranked findings set first.
    active_findings, informational_findings = _split_informational_findings(findings)

    # Waiver handling
    waivers = _load_waivers(waiver_path)
    active_findings, suppressed_findings = _apply_waivers(active_findings, waivers)
    suppressed_findings.extend(informational_findings)

    # Sort findings per ranking policy
    active_findings = _sort_findings(active_findings)
    suppressed_findings = _sort_findings(suppressed_findings)

    carry_forward_findings = [
        f for f in active_findings
        if not f.get("is_new") and not f.get("is_changed") and f.get("confidence") != "high"
    ]

    # Build result
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy_version,
        "audit_scope": audit_scope,
        "baseline_artifact": baseline_artifact,
        "summary_counts": {
            "total": len(active_findings),
            "new": sum(1 for f in active_findings if f.get("is_new")),
            "changed": sum(1 for f in active_findings if f.get("is_changed")),
            "suppressed": len(suppressed_findings) + len(carry_forward_findings),
            "errors": len(errors),
        },
        "findings": active_findings,
        "suppressed_findings": suppressed_findings,
        "errors": errors,
    }

    # Write artifacts
    date_str = run_date.isoformat()
    _write_json_artifact(result, artifact_dir / f"{date_str}.json")
    _write_markdown_artifact(result, artifact_dir / f"{date_str}.md")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic v1 weekly skills audit",
    )
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="Root of skills directory (default: $WORKSPACE_HUB/.claude/skills)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output root for artifacts (default: $SKILLS_AUDIT_OUTPUT_ROOT or $WORKSPACE_HUB)",
    )
    parser.add_argument(
        "--policy",
        default=None,
        help="Path to policy YAML (default: config/skills/weekly-audit-policy.yaml)",
    )
    parser.add_argument(
        "--waivers",
        default=None,
        help="Path to waiver registry YAML (default: config/skills/weekly-audit-waivers.yaml)",
    )
    args = parser.parse_args()

    script_repo_root = Path(__file__).resolve().parents[2]
    workspace = script_repo_root

    skills_dir = Path(args.skills_dir) if args.skills_dir else workspace / ".claude" / "skills"
    output_dir = (
        Path(args.output_dir) if args.output_dir
        else Path(os.environ.get("SKILLS_AUDIT_OUTPUT_ROOT", str(workspace)))
    )
    policy_path = (
        Path(args.policy) if args.policy
        else workspace / "config" / "skills" / "weekly-audit-policy.yaml"
    )
    waiver_path = (
        Path(args.waivers) if args.waivers
        else workspace / "config" / "skills" / "weekly-audit-waivers.yaml"
    )

    if not skills_dir.exists():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 1
    if not policy_path.exists():
        print(f"ERROR: policy file not found: {policy_path}", file=sys.stderr)
        return 1

    result = run_audit(
        skills_dir=skills_dir,
        output_dir=output_dir,
        policy_path=policy_path,
        waiver_path=waiver_path if waiver_path.exists() else None,
    )

    total = result["summary_counts"]["total"]
    errors = result["summary_counts"]["errors"]
    print(f"Audit complete: {total} findings, {errors} errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
