#!/usr/bin/env python3
"""weekly_skills_audit.py — Deterministic weekly skills housekeeping audit.

Scans .claude/skills/ for duplicate frontmatter names, leaf-directory
collisions, and v2 housekeeping signals for content quality, grouping drift,
size, and future usage adapters. Findings are classified per the policy
contract at config/skills/weekly-audit-policy.yaml and emitted as stable local
JSON + Markdown artifacts under logs/maintenance/skills-curation/.

This is a read-only audit: it never modifies the skills directory and never
posts to GitHub automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
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

        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        parts = Path(rel_path).parts
        top_level = parts[0] if parts else ""
        category = fm.get("category") if isinstance(fm, dict) else None

        inventory.append({
            "canonical_name": canonical_name,
            "leaf": leaf,
            "path": rel_path,
            "top_level": top_level,
            "category": category.strip() if isinstance(category, str) else None,
            "line_count": len(text.splitlines()),
            "source_id": "local-skill-filesystem",
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
# V2 deterministic housekeeping signal families (#2486)
# ---------------------------------------------------------------------------

def _v2_cfg(policy: dict) -> dict:
    return policy.get("v2", {}) if isinstance(policy.get("v2"), dict) else {}


def _stable_key(*parts: object, length: int = 24) -> str:
    payload = "|".join(str(p) for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _finding_defaults(policy: dict, family: str, rule_id: str) -> dict:
    cfg = _v2_cfg(policy).get("rules", {})
    return cfg.get(f"{family}.{rule_id}", {}) if isinstance(cfg, dict) else {}


def _mk_v2_finding(
    policy: dict,
    *,
    family: str,
    rule_id: str,
    canonical_names: list[str],
    paths: list[str],
    summary: str,
    recommended_action: str,
    informational_only: bool = False,
    alias_family_id: str | None = None,
    threshold_id: str | None = None,
    key_parts: list[object] | None = None,
) -> dict:
    defaults = _finding_defaults(policy, family, rule_id)
    headline = bool(defaults.get("headline", True)) and not informational_only
    key_payload = key_parts or [family, rule_id, *sorted(canonical_names), *sorted(paths)]
    finding = {
        "finding_key": _stable_key(*key_payload),
        "family": family,
        "rule_id": rule_id,
        "classification": rule_id,
        "severity": defaults.get("severity", "medium"),
        "confidence": defaults.get("confidence", "high"),
        "headline": headline,
        "canonical_names": sorted(canonical_names),
        "paths": sorted(paths),
        "summary": summary,
        "recommended_action": defaults.get("recommended_action", recommended_action),
        "escalation_state": defaults.get("escalation_state", "candidate" if headline else "no-escalation"),
        "is_new": True,
        "is_changed": False,
        "informational_only": informational_only,
    }
    if alias_family_id:
        finding["alias_family_id"] = alias_family_id
    if threshold_id:
        finding["threshold_id"] = threshold_id
    return finding


def _alias_families(policy: dict) -> list[dict]:
    families = _v2_cfg(policy).get("category_alias_families", [])
    return families if isinstance(families, list) else []


def _normalize_category_token(value: str) -> str:
    return value.strip().strip("/").replace("_", "-")


def _detect_content_quality_findings(inventory: list[dict], policy: dict) -> list[dict]:
    findings: list[dict] = []
    for item in inventory:
        fm = item.get("frontmatter") or {}
        if not item.get("frontmatter_valid"):
            findings.append(_mk_v2_finding(
                policy,
                family="content-quality",
                rule_id="malformed-frontmatter",
                canonical_names=[item["canonical_name"]],
                paths=[item["path"]],
                summary=f"Malformed or missing frontmatter in {item['path']}",
                recommended_action="Repair YAML frontmatter before relying on this skill for automated routing.",
                informational_only=item.get("informational_only", False),
                key_parts=["content-quality", "malformed-frontmatter", item["canonical_name"], item["path"]],
            ))
            continue
        if not isinstance(fm.get("category"), str) or not fm.get("category", "").strip():
            findings.append(_mk_v2_finding(
                policy,
                family="content-quality",
                rule_id="missing-category",
                canonical_names=[item["canonical_name"]],
                paths=[item["path"]],
                summary=f"Skill {item['canonical_name']} is missing category frontmatter",
                recommended_action="Add category frontmatter aligned with the skill path taxonomy.",
                informational_only=item.get("informational_only", False),
                key_parts=["content-quality", "missing-category", item["canonical_name"], item["path"]],
            ))
    return _sort_findings(findings)


def _category_matches_path(category: str, top_level: str) -> bool:
    if not category or not top_level:
        return False
    normalized_category = _normalize_category_token(category.split("/")[0])
    normalized_top = _normalize_category_token(top_level)
    return normalized_category == normalized_top


def _detect_grouping_findings(inventory: list[dict], policy: dict) -> list[dict]:
    findings: list[dict] = []
    seen: set[str] = set()
    for item in inventory:
        category = item.get("category")
        if not isinstance(category, str) or not category.strip():
            continue
        if not _category_matches_path(category, item.get("top_level", "")):
            key = _stable_key("grouping", "category-path-mismatch", item["canonical_name"], item["path"])
            if key not in seen:
                seen.add(key)
                findings.append(_mk_v2_finding(
                    policy,
                    family="grouping",
                    rule_id="category-path-mismatch",
                    canonical_names=[item["canonical_name"]],
                    paths=[item["path"]],
                    summary=f"Category '{category}' does not match path prefix '{item.get('top_level', '')}' for {item['canonical_name']}",
                    recommended_action="Align category frontmatter and directory taxonomy or declare an explicit alias family.",
                    informational_only=item.get("informational_only", False),
                    key_parts=["grouping", "category-path-mismatch", item["canonical_name"], item["path"]],
                ))

    for family in _alias_families(policy):
        family_id = family.get("id")
        aliases = family.get("aliases", [])
        if not family_id or not isinstance(aliases, list):
            continue
        alias_tokens = {_normalize_category_token(str(a)) for a in aliases}
        offenders = [
            item for item in inventory
            if _normalize_category_token(str(item.get("top_level", ""))) in alias_tokens
            or _normalize_category_token(str(item.get("category", ""))) in alias_tokens
        ]
        used_raw: set[str] = set()
        for item in offenders:
            top_level_raw = str(item.get("top_level", ""))
            category_raw = str(item.get("category", ""))
            if top_level_raw and _normalize_category_token(top_level_raw) in alias_tokens:
                used_raw.add(top_level_raw)
            if category_raw and _normalize_category_token(category_raw) in alias_tokens:
                used_raw.add(category_raw)
        normalized_used = {_normalize_category_token(v) for v in used_raw if v}
        # A single canonical spelling is healthy. Emit alias drift only when raw
        # values that actually belong to the alias family use mixed spellings
        # (e.g. underscore and hyphen/slash variants).
        if len(offenders) < 1 or len(used_raw) <= 1 or len(normalized_used) < 1:
            continue
        offender_paths = sorted(item["path"] for item in offenders)
        path_hash = _stable_key(*offender_paths, length=16)
        findings.append(_mk_v2_finding(
            policy,
            family="grouping",
            rule_id="category-alias-drift",
            canonical_names=sorted({item["canonical_name"] for item in offenders}),
            paths=offender_paths[:20],
            summary=f"Category alias family '{family_id}' appears in {len(offenders)} skill paths/frontmatter values",
            recommended_action="Normalize the alias family through a bounded cleanup issue after review.",
            alias_family_id=str(family_id),
            key_parts=["grouping", "category-alias-drift", family_id, path_hash],
        ))
    return _sort_findings(findings)


def _detect_size_findings(inventory: list[dict], policy: dict) -> list[dict]:
    cfg = _v2_cfg(policy).get("size", {})
    threshold = int(cfg.get("oversized_active_skill_lines", 500))
    findings: list[dict] = []
    for item in inventory:
        if int(item.get("line_count", 0)) <= threshold:
            continue
        findings.append(_mk_v2_finding(
            policy,
            family="size",
            rule_id="oversized-skill",
            canonical_names=[item["canonical_name"]],
            paths=[item["path"]],
            summary=f"Skill {item['canonical_name']} has {item.get('line_count', 0)} lines, above threshold {threshold}",
            recommended_action="Review for split, wrapper, or reference-file extraction opportunity.",
            informational_only=item.get("informational_only", False),
            threshold_id=f"oversized-active-skill-lines-{threshold}",
            key_parts=["size", f"oversized-active-skill-lines-{threshold}", item["canonical_name"], item["path"]],
        ))
    return _sort_findings(findings)


def _archive_alias_tokens(policy: dict) -> set[str]:
    """Return path-segment spellings that mean intentionally archived skills."""
    aliases = {"_archive"}
    for family in _alias_families(policy):
        if family.get("id") != "archive":
            continue
        aliases.add(str(family.get("canonical", "")))
        aliases.update(str(a) for a in family.get("aliases", []) if a)
    return {a.strip() for a in aliases if a and a.strip()}


def _is_active_skill_path(rel_path: str, policy: dict) -> bool:
    parts = Path(rel_path).parts
    archive_aliases = _archive_alias_tokens(policy)
    return not any(part in archive_aliases for part in parts)


def _git_repo_root(path: Path) -> Path | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    root = proc.stdout.strip()
    return Path(root) if root else None


def _git_bool(repo_root: Path, key: str) -> bool | None:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "config", "--bool", key],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    value = proc.stdout.strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return None


def detect_git_inventory_trust(skills_dir: Path) -> dict:
    """Classify whether git tracked-skill inventory is authoritative for skills_dir."""
    repo_root = _git_repo_root(skills_dir)
    filesystem_count = sum(1 for _ in skills_dir.glob("**/SKILL.md")) if skills_dir.exists() else 0
    evidence: dict = {"filesystem_skill_count": filesystem_count}
    if repo_root is None:
        return {"trusted": False, "reason": "skills_dir is not inside a git worktree", "evidence": evidence}

    try:
        rel_skills_dir = skills_dir.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return {"trusted": False, "reason": "skills_dir is outside git repository root", "evidence": evidence | {"repo_root": str(repo_root)}}

    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z", "--", str(rel_skills_dir)],
            check=False,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"trusted": False, "reason": f"git ls-files failed: {exc}", "evidence": evidence | {"repo_root": str(repo_root)}}

    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace") if isinstance(proc.stderr, bytes) else str(proc.stderr)
        return {"trusted": False, "reason": "git ls-files returned non-zero", "evidence": evidence | {"returncode": proc.returncode, "stderr": stderr.strip()}}

    tracked_paths = [p.decode("utf-8", errors="replace") for p in proc.stdout.split(b"\0") if p]
    tracked_skill_paths = [p for p in tracked_paths if p.endswith("/SKILL.md")]
    evidence.update({
        "repo_root": str(repo_root),
        "skills_dir": str(rel_skills_dir),
        "tracked_skill_count": len(tracked_skill_paths),
    })

    sparse_enabled = _git_bool(repo_root, "core.sparseCheckout")
    evidence["core.sparseCheckout"] = sparse_enabled
    if sparse_enabled:
        sparse_proc = subprocess.run(
            ["git", "-C", str(repo_root), "sparse-checkout", "list"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        sparse_patterns = [line.strip() for line in sparse_proc.stdout.splitlines() if line.strip()]
        evidence["sparse_checkout_patterns"] = sparse_patterns
        rel_text = str(rel_skills_dir).rstrip("/")
        covered = any(pattern.rstrip("/") in {rel_text, ".claude", ".claude/skills"} or rel_text.startswith(pattern.rstrip("/") + "/") for pattern in sparse_patterns)
        if not covered:
            return {"trusted": False, "reason": "sparse checkout does not cover skills_dir", "evidence": evidence}

    if filesystem_count > 0 and len(tracked_skill_paths) == 0:
        return {"trusted": False, "reason": "git ls-files returned zero while filesystem has skills", "evidence": evidence}

    return {"trusted": True, "reason": "git ls-files inventory is authoritative for skills_dir", "evidence": evidence}


def _tracked_skill_paths(skills_dir: Path, trust: dict) -> set[str]:
    if not trust.get("trusted"):
        return set()
    repo_root = Path(str(trust.get("evidence", {}).get("repo_root", "")))
    rel_skills_dir = Path(str(trust.get("evidence", {}).get("skills_dir", "")))
    if not repo_root or not rel_skills_dir:
        return set()
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z", "--", str(rel_skills_dir)],
        check=False,
        capture_output=True,
        timeout=15,
    )
    if proc.returncode != 0:
        return set()
    rel_prefix = str(rel_skills_dir).rstrip("/") + "/"
    tracked: set[str] = set()
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        path = raw.decode("utf-8", errors="replace")
        if not path.endswith("/SKILL.md") or not path.startswith(rel_prefix):
            continue
        tracked.add(path[len(rel_prefix):])
    return tracked


def _path_object(path: str, *, informational: bool = False) -> dict:
    return {"path": path, "informational": informational}


def _all_filesystem_skill_paths(skills_dir: Path) -> set[str]:
    if not skills_dir.exists():
        return set()
    return {str(path.relative_to(skills_dir)) for path in skills_dir.glob("**/SKILL.md")}


def _is_informational_path(rel_path: str) -> bool:
    return any(part in INFORMATIONAL_DIRS for part in Path(rel_path).parts)


def _provider_skill_mirrors(skills_dir: Path) -> dict:
    workspace = skills_dir.parent.parent if skills_dir.name == "skills" else skills_dir.parent
    mirrors: dict[str, str] = {}
    for provider in ("codex", "gemini"):
        path = workspace / f".{provider}" / "skills"
        key = f"{provider}_skills_link"
        if path.is_symlink():
            try:
                mirrors[key] = os.readlink(path)
            except OSError as exc:
                mirrors[key] = f"error:{exc}"
        elif path.exists():
            mirrors[key] = "directory"
        else:
            mirrors[key] = "missing"
    return mirrors


def _repo_relative_skill_path(rel_path: str, trust: dict) -> str:
    evidence = trust.get("evidence", {}) if isinstance(trust.get("evidence"), dict) else {}
    rel_skills_dir = str(evidence.get("skills_dir", "")).strip("/")
    return f"{rel_skills_dir}/{rel_path}" if rel_skills_dir else rel_path


def build_inventory_summary(skills_dir: Path, policy: dict, tracked_skill_paths: set[str], trust: dict) -> dict:
    filesystem_paths = _all_filesystem_skill_paths(skills_dir)
    archive_aliases = _archive_alias_tokens(policy)
    tracked_active = {p for p in tracked_skill_paths if _is_active_skill_path(p, policy)}
    filesystem_active = {p for p in filesystem_paths if _is_active_skill_path(p, policy)}
    filesystem_only = filesystem_paths - tracked_skill_paths
    filesystem_only_active = sorted(filesystem_active - tracked_active)
    missing_tracked_active = sorted(tracked_active - filesystem_active)
    filesystem_only_archived = sorted(p for p in filesystem_only if not _is_active_skill_path(p, policy))
    if not trust.get("trusted"):
        filesystem_only = set()
        filesystem_only_active = []
        missing_tracked_active = []
        filesystem_only_archived = []
    warnings = []
    if not trust.get("trusted"):
        warnings.append(f"Git inventory not trusted: {trust.get('reason', 'unknown')}")
    return {
        "counts": {
            "tracked_total": len(tracked_skill_paths),
            "tracked_active": len(tracked_active),
            "filesystem_total": len(filesystem_paths),
            "filesystem_active": len(filesystem_active),
            "filesystem_only_total": len(filesystem_only),
            "filesystem_only_active": len(filesystem_only_active),
            "missing_tracked_total": len(tracked_skill_paths - filesystem_paths),
            "missing_tracked_active": len(missing_tracked_active),
            "filesystem_only_archived_total": len(filesystem_only_archived),
        },
        "paths": {
            "filesystem_only_active": [_path_object(_repo_relative_skill_path(p, trust), informational=_is_informational_path(p)) for p in filesystem_only_active],
            "missing_tracked_active": [_path_object(_repo_relative_skill_path(p, trust), informational=_is_informational_path(p)) for p in missing_tracked_active],
            "filesystem_only_archived": [_path_object(_repo_relative_skill_path(p, trust), informational=True) for p in filesystem_only_archived],
        },
        "mirrors": _provider_skill_mirrors(skills_dir),
        "archive_aliases": sorted(archive_aliases),
        "warnings": warnings,
    }


def _detect_filesystem_inventory_findings(
    inventory: list[dict],
    policy: dict,
    *,
    skills_dir: Path,
    tracked_skill_paths: set[str],
    trust: dict,
) -> list[dict]:
    """Find active SKILL.md files that exist only on disk or only in git."""
    if not trust.get("trusted"):
        return []
    fs_active = {item["path"]: item for item in inventory if _is_active_skill_path(str(item["path"]), policy)}
    tracked_active = {path for path in tracked_skill_paths if _is_active_skill_path(path, policy)}
    findings: list[dict] = []

    filesystem_only = sorted(set(fs_active) - tracked_active)
    if filesystem_only:
        display_paths = [_repo_relative_skill_path(path, trust) for path in filesystem_only]
        names = [fs_active[path]["canonical_name"] for path in filesystem_only]
        findings.append(_mk_v2_finding(
            policy,
            family="filesystem-inventory",
            rule_id="filesystem-only-active",
            canonical_names=names,
            paths=display_paths,
            summary=f"{len(filesystem_only)} active skill file(s) exist on disk but are not tracked by git",
            recommended_action="Disposition as promote_after_review, archive_intentionally, ignore_with_rationale, or delete_after_backup before local filesystem state is lost.",
            key_parts=["filesystem-inventory.filesystem-only-active", *display_paths],
        ))

    missing_tracked = sorted(tracked_active - set(fs_active))
    if missing_tracked:
        display_paths = [_repo_relative_skill_path(path, trust) for path in missing_tracked]
        findings.append(_mk_v2_finding(
            policy,
            family="filesystem-inventory",
            rule_id="missing-tracked-active",
            canonical_names=[Path(path).parent.name for path in missing_tracked],
            paths=display_paths,
            summary=f"{len(missing_tracked)} active skill file(s) are tracked by git but missing from the filesystem",
            recommended_action="Restore the missing tracked skill file(s) or intentionally remove them in a separate reviewed cleanup.",
            key_parts=["filesystem-inventory.missing-tracked-active", *display_paths],
        ))

    return _sort_findings(findings)


def _skill_counts(inventory: list[dict], errors: list[str], skills_dir: Path) -> dict:
    excluded = 0
    for excluded_dir in EXCLUDED_DIRS:
        excluded += sum(1 for _ in (skills_dir / excluded_dir).glob("**/SKILL.md")) if (skills_dir / excluded_dir).exists() else 0
    return {
        "active": sum(1 for item in inventory if not item.get("informational_only")),
        "informational": sum(1 for item in inventory if item.get("informational_only")),
        "excluded": excluded,
        "malformed": len(errors),
        "total_scanned": len(inventory),
    }


def _category_summary(inventory: list[dict]) -> dict:
    by_path = Counter(item.get("top_level", "") or "<root>" for item in inventory)
    by_frontmatter = Counter(str(item.get("category") or "<missing>") for item in inventory)
    return {
        "by_path_prefix": dict(sorted(by_path.items())),
        "by_frontmatter_category": dict(sorted(by_frontmatter.items())),
    }


def _load_baseline_with_compatibility(
    artifact_dir: Path,
    policy_version: str,
    audit_scope: str,
    *,
    accept_append_only_v1: bool = False,
) -> tuple[dict | None, dict]:
    if not artifact_dir.exists():
        return None, {"state": "absent", "reason": "no prior artifact directory"}
    json_files = sorted(artifact_dir.glob("*.json"), reverse=True)
    saw_any = False
    previous_policy_candidate: tuple[dict, Path] | None = None
    for jf in json_files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        saw_any = True
        if data.get("audit_scope") != audit_scope:
            continue
        prior_policy_version = str(data.get("policy_version", ""))
        if prior_policy_version == policy_version:
            return data, {"state": "compatible", "reason": "matching policy_version and audit_scope", "artifact": str(jf)}
        if (
            accept_append_only_v1
            and previous_policy_candidate is None
            and prior_policy_version.startswith("weekly-skills-audit-v1")
        ):
            previous_policy_candidate = (data, jf)
    if previous_policy_candidate is not None:
        data, jf = previous_policy_candidate
        return data, {
            "state": "compatible-previous-policy",
            "reason": "append-only v2 reader accepted prior v1 artifact with matching audit_scope",
            "artifact": str(jf),
            "previous_policy_version": data.get("policy_version"),
        }
    if saw_any:
        return None, {"state": "ignored", "reason": "no prior artifact matched current policy_version and audit_scope"}
    return None, {"state": "absent", "reason": "no readable prior artifacts"}


def _write_github_payload(result: dict, payload_path: Path) -> None:
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    counts = result.get("summary_counts", {})
    payload_path.write_text(
        "# Weekly skills housekeeping update\n\n"
        f"Generated: {result.get('generated_at')}\n\n"
        f"Findings: {counts.get('total', 0)} active, {counts.get('suppressed', 0)} suppressed, {counts.get('errors', 0)} errors.\n\n"
        "This is a local payload only; posting to GitHub is intentionally outside the scheduled audit path.\n",
        encoding="utf-8",
    )

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


def _baseline_finding_sources(baseline: dict) -> list[dict]:
    """Return all known finding arrays from a prior artifact.

    V2 appends family-specific arrays, while v1 artifacts only had findings and
    suppressed_findings. Unknown keys are intentionally ignored by readers, but
    all known v2 arrays must participate in carry-forward/changed detection.
    """
    sources: list[dict] = []
    for key in (
        "findings",
        "suppressed_findings",
        "content_quality_findings",
        "grouping_findings",
        "size_findings",
        "filesystem_inventory_findings",
        "usage_findings",
    ):
        values = baseline.get(key, [])
        if isinstance(values, list):
            sources.extend(f for f in values if isinstance(f, dict) and "finding_key" in f)
    return sources


def _apply_baseline(findings: list[dict], baseline: dict | None) -> None:
    """Mark is_new/is_changed based on prior baseline."""
    if baseline is None:
        return  # All findings stay is_new=True

    prior_sources = _baseline_finding_sources(baseline)
    prior_keys = {f["finding_key"] for f in prior_sources}
    prior_map = {f["finding_key"]: f for f in prior_sources}

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


def _all_active_findings(result: dict) -> list[dict]:
    findings: list[dict] = []
    for key in ("findings", "content_quality_findings", "grouping_findings", "size_findings", "filesystem_inventory_findings", "usage_findings"):
        values = result.get(key, [])
        if isinstance(values, list):
            findings.extend(f for f in values if isinstance(f, dict))
    return _sort_findings(findings)


def _headline_findings(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f.get("headline", True)]


def _markdown_actionable_findings(findings: list[dict]) -> list[dict]:
    """Findings that deserve full detail in family sections.

    Stable low/medium-confidence carry-forward items are summarized later in the
    compact carry-forward section to avoid weekly report noise. High-confidence
    carry-forward remains visible as unresolved risk.
    """
    return [
        f for f in findings
        if f.get("is_new") or f.get("is_changed") or f.get("confidence") == "high"
    ]


def _append_finding_section(lines: list[str], title: str, findings: list[dict], empty: str) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if findings:
        for f in _sort_findings(findings):
            lines.append(f"- **[{f.get('classification', f.get('rule_id', 'unknown'))}]** {f.get('summary', '')}  ")
            lines.append(f"  Key: `{f.get('finding_key', '')}` | Severity: {f.get('severity', 'unknown')} | Confidence: {f.get('confidence', 'unknown')}")
            if f.get("paths"):
                lines.append(f"  Paths: {', '.join(f.get('paths', []))}")
            if f.get("recommended_action"):
                lines.append(f"  Action: {f.get('recommended_action')}")
            lines.append("")
    else:
        lines.append(empty)
        lines.append("")


def _append_inventory_summary_section(lines: list[str], result: dict) -> None:
    summary = result.get("inventory_summary", {}) if isinstance(result.get("inventory_summary"), dict) else {}
    counts = summary.get("counts", {}) if isinstance(summary.get("counts"), dict) else {}
    paths = summary.get("paths", {}) if isinstance(summary.get("paths"), dict) else {}
    warnings = summary.get("warnings", []) if isinstance(summary.get("warnings"), list) else []
    lines.append("## Filesystem-only skill files")
    lines.append("")
    lines.append(
        "Inventory counts: "
        f"tracked_active={counts.get('tracked_active', 0)}, "
        f"filesystem_active={counts.get('filesystem_active', 0)}, "
        f"filesystem_only_active={counts.get('filesystem_only_active', 0)}, "
        f"missing_tracked_active={counts.get('missing_tracked_active', 0)}, "
        f"filesystem_only_archived={counts.get('filesystem_only_archived_total', 0)}"
    )
    lines.append("")
    if warnings:
        for warning in warnings:
            lines.append(f"- WARNING: {warning}")
        lines.append("")
    filesystem_only_active = paths.get("filesystem_only_active", []) if isinstance(paths.get("filesystem_only_active"), list) else []
    if filesystem_only_active:
        for item in filesystem_only_active:
            suffix = " (informational)" if item.get("informational") else ""
            lines.append(f"- `{item.get('path', '')}`{suffix}")
        lines.append("")
    else:
        lines.append("No filesystem-only active skill files.")
        lines.append("")


def _write_markdown_artifact(result: dict, md_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)

    all_findings = _all_active_findings(result)
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
    new = [f for f in all_findings if f.get("is_new")]
    _append_finding_section(lines, "New Findings", new, "No new findings.")

    # Section 2: Changed Findings
    changed = [f for f in all_findings if f.get("is_changed")]
    _append_finding_section(lines, "Changed Findings", changed, "No changed findings.")

    # Section 3: Filesystem-only inventory section
    _append_inventory_summary_section(lines, result)

    # Section 4: Stable v2 family sections
    _append_finding_section(lines, "Content Quality Findings", _markdown_actionable_findings(result.get("content_quality_findings", [])), "No content quality findings.")
    _append_finding_section(lines, "Grouping / Taxonomy Drift Findings", _markdown_actionable_findings(result.get("grouping_findings", [])), "No grouping or taxonomy drift findings.")
    _append_finding_section(lines, "Oversized / Maintainability Findings", _markdown_actionable_findings(result.get("size_findings", [])), "No oversized or maintainability findings.")
    _append_finding_section(lines, "Filesystem-Only Active Skill Loss-Risk Inventory", _markdown_actionable_findings(result.get("filesystem_inventory_findings", [])), "No filesystem-only active skill loss-risk findings.")
    _append_finding_section(lines, "Usage / Staleness Findings", _markdown_actionable_findings(result.get("usage_findings", [])), "No usage or staleness findings.")
    _append_finding_section(lines, "Follow-up Candidates", result.get("follow_up_candidates", []), "No follow-up candidates.")

    # Section 4: Unresolved High-Confidence Findings
    unresolved = [
        f for f in all_findings
        if f.get("confidence") == "high" and not f.get("is_new")
    ]
    _append_finding_section(lines, "Unresolved High-Confidence Findings", unresolved, "No unresolved high-confidence findings.")

    # Section 5: Suppressed / Carry-Forward Findings
    lines.append("## Suppressed / Carry-Forward Findings")
    lines.append("")
    carry_forward = [
        f for f in all_findings
        if not f.get("is_new") and not f.get("is_changed") and f.get("confidence") != "high"
    ]
    suppressed = result.get("suppressed_findings", [])
    combined_carry_forward = carry_forward + suppressed
    if combined_carry_forward:
        for f in _sort_findings(combined_carry_forward):
            reason = f.get("waiver_reason", "carry-forward")
            lines.append(f"- `{f['finding_key']}` — {f['summary']} (reason: {reason})")
            lines.append("")
    else:
        lines.append("No suppressed findings.")
        lines.append("")

    # Section 6: Operational Errors
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
    render_github_payload: bool = False,
) -> dict:
    """Execute the full audit pipeline. Returns the result dict."""
    if run_date is None:
        run_date = date.today()

    policy = _load_policy(policy_path)
    policy_version = f"{policy.get('policy_id', 'unknown')}-v{policy.get('version', '?')}"

    scan_started = time.monotonic()
    # Build inventory
    inventory = build_inventory(skills_dir)
    inventory_seconds = time.monotonic() - scan_started
    git_inventory_trust = detect_git_inventory_trust(skills_dir)
    tracked_skill_paths = _tracked_skill_paths(skills_dir, git_inventory_trust)
    inventory_summary = build_inventory_summary(skills_dir, policy, tracked_skill_paths, git_inventory_trust)

    # Detect errors (malformed frontmatter)
    errors: list[str] = []
    for item in inventory:
        if not item["frontmatter_valid"]:
            errors.append(f"Malformed or missing frontmatter: {item['path']}")

    # Detect findings
    detection_started = time.monotonic()
    findings = _detect_findings(inventory, policy)
    content_quality_findings = _detect_content_quality_findings(inventory, policy)
    grouping_findings = _detect_grouping_findings(inventory, policy)
    size_findings = _detect_size_findings(inventory, policy)
    filesystem_inventory_findings = _detect_filesystem_inventory_findings(
        inventory,
        policy,
        skills_dir=skills_dir,
        tracked_skill_paths=tracked_skill_paths,
        trust=git_inventory_trust,
    )
    usage_findings: list[dict] = []
    detection_seconds = time.monotonic() - detection_started

    audit_scope = _derive_audit_scope(skills_dir)

    # Baseline comparison
    artifact_dir = output_dir / "logs" / "maintenance" / "skills-curation"
    baseline = _load_baseline(artifact_dir, policy_version, audit_scope)
    baseline_v2, baseline_compatibility = _load_baseline_with_compatibility(
        artifact_dir,
        policy_version,
        audit_scope,
        accept_append_only_v1=bool(_v2_cfg(policy).get("schema_contract", {}).get("append_only_v1")),
    )
    baseline = baseline_v2 or baseline
    baseline_artifact = None
    if baseline:
        baseline_artifact = baseline.get("generated_at", "unknown")
        _apply_baseline(findings, baseline)
        _apply_baseline(content_quality_findings, baseline)
        _apply_baseline(grouping_findings, baseline)
        _apply_baseline(size_findings, baseline)
        _apply_baseline(filesystem_inventory_findings, baseline)

    # Move _core/_internal findings out of the active ranked findings set first.
    active_findings, informational_findings = _split_informational_findings(findings)

    # Waiver handling
    waivers = _load_waivers(waiver_path)
    active_findings, suppressed_findings = _apply_waivers(active_findings, waivers)
    content_quality_findings, suppressed_content_quality = _apply_waivers(content_quality_findings, waivers)
    grouping_findings, suppressed_grouping = _apply_waivers(grouping_findings, waivers)
    size_findings, suppressed_size = _apply_waivers(size_findings, waivers)
    filesystem_inventory_findings, suppressed_filesystem_inventory = _apply_waivers(filesystem_inventory_findings, waivers)
    usage_findings, suppressed_usage = _apply_waivers(usage_findings, waivers)
    suppressed_findings.extend(informational_findings)
    suppressed_findings.extend(suppressed_content_quality)
    suppressed_findings.extend(suppressed_grouping)
    suppressed_findings.extend(suppressed_size)
    suppressed_findings.extend(suppressed_filesystem_inventory)
    suppressed_findings.extend(suppressed_usage)

    # Sort findings per ranking policy
    active_findings = _sort_findings(active_findings)
    content_quality_findings = _sort_findings(content_quality_findings)
    grouping_findings = _sort_findings(grouping_findings)
    size_findings = _sort_findings(size_findings)
    filesystem_inventory_findings = _sort_findings(filesystem_inventory_findings)
    usage_findings = _sort_findings(usage_findings)
    suppressed_findings = _sort_findings(suppressed_findings)

    active_all_findings = _sort_findings(active_findings + content_quality_findings + grouping_findings + size_findings + filesystem_inventory_findings + usage_findings)
    headline_all_findings = _headline_findings(active_all_findings)
    carry_forward_findings = [
        f for f in active_all_findings
        if not f.get("is_new") and not f.get("is_changed") and f.get("confidence") != "high"
    ]
    follow_up_candidates = [
        f for f in headline_all_findings
        if f.get("escalation_state") == "candidate"
    ]

    # Build result
    result = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy_version,
        "audit_scope": audit_scope,
        "baseline_artifact": baseline_artifact,
        "baseline_compatibility": baseline_compatibility,
        "scan_durations": {
            "inventory_seconds": round(inventory_seconds, 6),
            "detection_seconds": round(detection_seconds, 6),
        },
        "skill_counts": _skill_counts(inventory, errors, skills_dir),
        "inventory_summary": inventory_summary,
        "git_inventory_trust": git_inventory_trust,
        "tracked_skill_count": len(tracked_skill_paths),
        "category_summary": _category_summary(inventory),
        "summary_counts": {
            "total": len(headline_all_findings),
            "legacy_total": len(active_findings),
            "content_quality_total": len(content_quality_findings),
            "grouping_total": len(grouping_findings),
            "size_total": len(size_findings),
            "filesystem_inventory_total": len(filesystem_inventory_findings),
            "usage_total": len(usage_findings),
            "new": sum(1 for f in headline_all_findings if f.get("is_new")),
            "changed": sum(1 for f in headline_all_findings if f.get("is_changed")),
            "suppressed": len(suppressed_findings) + len(carry_forward_findings),
            "errors": len(errors),
        },
        "findings": active_findings,
        "suppressed_findings": suppressed_findings,
        "content_quality_findings": content_quality_findings,
        "grouping_findings": grouping_findings,
        "size_findings": size_findings,
        "filesystem_inventory_findings": filesystem_inventory_findings,
        "usage_findings": usage_findings,
        "follow_up_candidates": follow_up_candidates,
        "errors": errors,
    }

    # Write artifacts
    date_str = run_date.isoformat()
    if render_github_payload:
        payload_path = artifact_dir / "github-update-payload.md"
        _write_github_payload(result, payload_path)
        result["github_update_payload_path"] = str(payload_path)
    _write_json_artifact(result, artifact_dir / f"{date_str}.json")
    _write_markdown_artifact(result, artifact_dir / f"{date_str}.md")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic weekly skills housekeeping audit",
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
    parser.add_argument(
        "--render-github-payload",
        action="store_true",
        help="Render a local Markdown payload for manual GitHub posting; never posts automatically.",
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
        render_github_payload=args.render_github_payload,
    )

    total = result["summary_counts"]["total"]
    errors = result["summary_counts"]["errors"]
    print(f"Audit complete: {total} findings, {errors} errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
