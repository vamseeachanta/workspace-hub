"""Offline registry consistency and configured-model comparison; no API probes."""

import argparse
import json
import math
import os
import tomllib
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

# Maintainer policy, not a provider guarantee: see docs/operations/model-drift.md.
DEFAULT_MAX_AGE_DAYS = 14


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys rather than silently losing evidence."""


def unique_mapping(loader, node):
    pairs = loader.construct_pairs(node, deep=True)
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate mapping key")
        result[key] = value
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def deprecated_ids(value):
    found = set()
    if isinstance(value, dict):
        if value.get("deprecated") is True and isinstance(value.get("model_id"), str):
            found.add(value["model_id"])
        for child in value.values():
            found.update(deprecated_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(deprecated_ids(child))
    return found


def references(value, model):
    if isinstance(value, dict):
        return model in value or any(references(v, model) for v in value.values())
    if isinstance(value, list):
        return any(references(v, model) for v in value)
    return value == model


def consistency(registry):
    latest = registry.get("latest_models")
    windows = registry.get("context_windows_k", {})
    if not isinstance(latest, dict) or not latest or not isinstance(windows, dict):
        return [("FAIL", "registry: latest_models and context_windows_k must be maps")]
    aliases = registry.get("model_aliases", {})
    rows = []
    if not isinstance(aliases, dict):
        rows.append(("FAIL", "model_aliases: mapping required"))
        aliases = {}
    invalid_aliases = set()
    for model, keys in aliases.items():
        if (not isinstance(keys, list) or
                any(not isinstance(key, str) or not key.strip() for key in keys) or
                len(set(keys)) != len(keys)):
            invalid_aliases.add(model)
            rows.append(("FAIL", f"model_aliases/{model}: unique non-empty string list required"))
        elif set(keys) != {key for key, value in latest.items() if value == model}:
            invalid_aliases.add(model)
            rows.append(("FAIL", f"model_aliases/{model}: exact binding membership required"))
    invalid_windows = set()
    for model, capacity in windows.items():
        if (type(capacity) not in (int, float) or capacity <= 0 or
                (isinstance(capacity, float) and not math.isfinite(capacity))):
            invalid_windows.add(model)
            rows.append(("FAIL", f"context_windows_k/{model}: positive finite number required"))
    counts = Counter(v for v in latest.values() if isinstance(v, str))
    deprecated = deprecated_ids(registry)
    for key, model in latest.items():
        if not isinstance(model, str) or not model.strip():
            rows.append(("FAIL", f"{key}: non-empty string id required"))
        elif model not in windows:
            rows.append(("FAIL", f"{key}: context window missing for {model}"))
        elif model in invalid_windows:
            rows.append(("FAIL", f"{key}: invalid context window for {model}"))
        elif model in deprecated:
            rows.append(("FAIL", f"{key}: deprecated id {model}"))
        elif model in invalid_aliases:
            rows.append(("FAIL", f"{key}: invalid model_aliases for {model}"))
        elif counts[model] > 1 and model not in aliases:
            rows.append(("FAIL", f"{key}: shared id {model} requires documented model_aliases"))
        else:
            rows.append(("PASS", f"{key}: registry consistent"))
    active = {k: v for k, v in registry.items() if k != "audit"}
    for model in sorted(deprecated):
        if references(active, model):
            rows.append(("FAIL", f"audit: deprecated id {model} referenced outside audit"))
    return rows


def freshness(registry, today, max_age):
    try:
        updated = date.fromisoformat(str(registry["last_updated"]))
    except (KeyError, ValueError, TypeError):
        return "NOT_EVALUATED", "freshness: missing or malformed last_updated"
    age = (today - updated).days
    if age < 0:
        return "WARN", "freshness: last_updated is in the future"
    return ("WARN" if age > max_age else "PASS"), f"freshness: age_days={age} bound_days={max_age}"


def read_live(paths, kind):
    """Read model strings or Hermes YAML model.default; project wins when set."""
    value = None
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        except OSError:
            raise ValueError("unreadable configuration") from None
        except UnicodeError:
            raise ValueError("malformed configuration encoding") from None
        try:
            data = (json.loads(text) if kind == "json" else
                    tomllib.loads(text) if kind == "toml" else yaml.load(text, Loader=UniqueLoader))
        except (ValueError, yaml.YAMLError):
            raise ValueError("malformed configuration") from None
        if not isinstance(data, dict):
            raise TypeError("malformed configuration mapping")
        if "model" in data:
            model = data["model"]
            if kind == "yaml" and isinstance(model, dict):
                if "default" not in model:
                    continue
                model = model["default"]
            if not isinstance(model, str) or not model.strip():
                raise ValueError("invalid model value")
            value = model
    return value


def evaluate(registry, user, project, today, max_age):
    if not isinstance(registry, dict):
        return [("FAIL", "registry: mapping required")]
    rows = consistency(registry)
    rows.append(freshness(registry, today, max_age))
    latest = registry.get("latest_models", {})
    if not isinstance(latest, dict):
        return rows
    known = {v for v in latest.values() if isinstance(v, str)}
    compared = missing = 0
    bindings = {
        "openai_primary": [("codex", "toml", ".codex/config.toml"),
                           ("hermes", "yaml", ".hermes/config.yaml")],
        "claude_primary": [("claude", "json", ".claude/settings.json")],
    }
    for key in latest:
        if key not in bindings:
            rows.append(("NOT_EVALUATED", f"{key}/live: no documented configuration binding"))
            missing += 1
        for provider, kind, relative in bindings.get(key, []):
            label = f"{key}/{provider}"
            try:
                live = read_live([user / relative, project / relative], kind)
            except (ValueError, TypeError) as exc:
                rows.append(("FAIL", f"{label}: {exc}"))
                missing += 1
                continue
            if live is None:
                rows.append(("NOT_EVALUATED", f"{label}: no readable configuration"))
                missing += 1
                continue
            compared += 1
            detail = f"{label}: live={live} registry={latest[key]}"
            if live not in known:
                rows.append(("FAIL", f"{detail}; unknown id {live}"))
            else:
                rows.append(("PASS" if live == latest[key] else "FAIL", detail))
    rows.append(("INFO", f"live: compared={compared} not_evaluated={missing}"))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--user-root", type=Path, default=Path.home())
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument("--max-age-days", type=int,
                        default=os.environ.get("MODEL_REGISTRY_MAX_AGE_DAYS", DEFAULT_MAX_AGE_DAYS))
    args = parser.parse_args()
    if args.max_age_days <= 0:
        parser.error("max-age-days must be positive")
    try:
        registry = yaml.load(args.registry.read_text(encoding="utf-8"), Loader=UniqueLoader)
        rows = evaluate(registry, args.user_root, args.project_root, args.today, args.max_age_days)
    except OSError:
        rows = [("NOT_EVALUATED", "registry: unreadable file")]
    except (ValueError, yaml.YAMLError):
        rows = [("FAIL", "registry: malformed YAML")]
    for status, detail in rows:
        print(f"{status}\t{detail}")
    return int(any(status == "FAIL" for status, _ in rows))


if __name__ == "__main__":
    raise SystemExit(main())
