#!/usr/bin/env python3
# ABOUTME: WRK-328 — Build agent-readable index of all specs across workspace
# ABOUTME: Walks specs/ in workspace-hub and all submodule specs/ dirs.
# ABOUTME: Extracts title, description, tags, wrk_refs, category, repo, mtime per file.
# ABOUTME: Writes structured output to specs/index.yaml.

import os
import re
import sys
import datetime
import yaml

HUB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILE = os.path.join(HUB_ROOT, "specs", "index.yaml")

# Submodule repos to scan (only those present as real checkouts, not empty stubs)
SUBMODULE_REPOS = [
    "digitalmodel",
    "worldenergydata",
    "assetutilities",
    "assethold",
    "doris",
    "OGManufacturing",
    "saipem",
    "rock-oil-field",
    "acma-projects",
    "aceengineer-admin",
    "aceengineer-website",
    "achantas-data",
    "frontierdeepwater",
    "hobbies",
    "pdf-large-reader",
    "pyproject-starter",
    "sd-work",
    "seanation",
    "teamresumes",
]

# Category inferred from top-level path segment under specs/
CATEGORY_MAP = {
    "modules": "modules",
    "wrk": "wrk",
    "repos": "repos",
    "data-sources": "data-sources",
    "archive": "archive",
    "templates": "templates",
}


def _rel(path):
    """Return path relative to HUB_ROOT with forward slashes."""
    return os.path.relpath(path, HUB_ROOT).replace(os.sep, "/")


def _parse_frontmatter(text):
    """Return (frontmatter_dict, body_text) from a markdown string."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm_str = text[3:end].strip()
            body = text[end + 4:].lstrip()
            try:
                fm = yaml.safe_load(fm_str) or {}
                if isinstance(fm, dict):
                    return fm, body
            except yaml.YAMLError:
                pass
    return {}, text


def _extract_title_md(text):
    """Return first # heading from markdown text, stripped of markup.

    Skips headings that are purely decorative (===, ---, or blank after #).
    """
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            candidate = line[2:].strip()
            # Skip decorator-only headings
            if re.match(r"^[=\-_#\s]*$", candidate) or not candidate:
                continue
            return candidate
    return ""


def _extract_description_md(body):
    """Return first non-empty prose paragraph from body (max 200 chars)."""
    paragraph_lines = []
    in_para = False
    for line in body.splitlines():
        stripped = line.strip()
        # Skip blockquotes, headings, horizontal rules, list items
        if (
            stripped.startswith(">")
            or stripped.startswith("#")
            or re.match(r"^[-_\*]{3,}$", stripped)   # --- / *** / ___
            or re.match(r"^[-\*\+] |^\d+\.", stripped)  # list items
        ):
            if in_para:
                break
            continue
        if stripped == "":
            if in_para:
                break
            continue
        in_para = True
        paragraph_lines.append(stripped)
        if len(" ".join(paragraph_lines)) > 200:
            break
    desc = " ".join(paragraph_lines).strip()
    if len(desc) > 200:
        desc = desc[:197] + "..."
    return desc


def _infer_tags_from_path(rel_path, frontmatter):
    """Infer tags from path segments and frontmatter keys."""
    tags = set()

    # Frontmatter-sourced tags
    for key in ("tags", "keywords"):
        val = frontmatter.get(key)
        if isinstance(val, list):
            for t in val:
                if isinstance(t, str):
                    tags.add(t.lower().replace(" ", "-"))
        elif isinstance(val, str):
            for t in re.split(r"[,\s]+", val):
                t = t.strip().lower().replace(" ", "-")
                if t:
                    tags.add(t)

    # Infer from path segments (skip generic ones)
    skip = {"specs", "modules", "wrk", "repos", "data-sources", "archive",
            "templates", "sub-specs", ""}
    parts = rel_path.replace("\\", "/").split("/")
    for part in parts:
        part_clean = os.path.splitext(part)[0].lower()
        if part_clean not in skip and len(part_clean) > 2:
            # WRK id pattern
            if re.match(r"^wrk-\d+$", part_clean):
                tags.add(part_clean)
            elif not re.match(r"^\d{4}-\d{2}-\d{2}.*", part_clean):
                tags.add(part_clean)

    return sorted(tags)


def _extract_wrk_refs(rel_path, frontmatter, title, description, raw_content=""):
    """Extract all WRK-NNN references from path, frontmatter, title, description, and content.

    Returns a sorted, deduplicated list of uppercase WRK-NNN strings.
    """
    wrk_pattern = re.compile(r"\bWRK-(\d+)\b", re.IGNORECASE)
    found = set()

    # From path segments (e.g. specs/wrk/WRK-185/plan.md)
    for m in wrk_pattern.finditer(rel_path):
        found.add(f"WRK-{int(m.group(1))}")

    # From frontmatter scalar values
    for key in ("related", "wrk_refs", "id", "wrk"):
        val = frontmatter.get(key)
        if isinstance(val, str):
            for m in wrk_pattern.finditer(val):
                found.add(f"WRK-{int(m.group(1))}")
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    for m in wrk_pattern.finditer(item):
                        found.add(f"WRK-{int(m.group(1))}")

    # From title and description
    for text in (title, description):
        for m in wrk_pattern.finditer(str(text)):
            found.add(f"WRK-{int(m.group(1))}")

    # From raw content (first 4000 chars to avoid large file cost)
    for m in wrk_pattern.finditer(raw_content[:4000]):
        found.add(f"WRK-{int(m.group(1))}")

    return sorted(found, key=lambda x: int(x.split("-")[1]))


def _infer_category(rel_path, specs_root_rel):
    """Infer category from the first sub-segment of the specs dir."""
    # rel_path is relative to HUB_ROOT e.g. specs/modules/foo.md
    # specs_root_rel is e.g. "specs" or "digitalmodel/specs"
    after_specs = rel_path[len(specs_root_rel):].lstrip("/")
    first_seg = after_specs.split("/")[0] if "/" in after_specs else ""
    first_seg_noext = os.path.splitext(first_seg)[0]
    return CATEGORY_MAP.get(first_seg_noext, "other")


def _extract_yaml_title_desc(content):
    """For YAML spec files, extract a title and description."""
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError:
        return "", ""

    if not isinstance(data, dict):
        return "", ""

    title = (
        data.get("title")
        or data.get("name")
        or data.get("repo")
        or ""
    )
    desc = (
        data.get("description")
        or data.get("summary")
        or ""
    )
    # If it's a data-sources YAML with a 'standards' list, describe that
    if "standards" in data and isinstance(data["standards"], list):
        count = len(data["standards"])
        repo = data.get("repo", "")
        if not title:
            title = f"{repo} standards data-source index"
        if not desc:
            desc = f"Data-source index with {count} standard entries for {repo}"
    return str(title)[:120], str(desc)[:200] if desc else ""


def _target_repo_from_rel(rel_path, specs_root_rel, repo_name):
    """For workspace-hub specs/repos/<subrepo>/... paths, return the subrepo name.

    For all other paths, return repo_name unchanged.
    """
    after_specs = rel_path[len(specs_root_rel):].lstrip("/")
    parts = after_specs.split("/")
    if parts[0] == "repos" and len(parts) >= 2:
        return parts[1]
    return repo_name


def process_file(fpath, specs_root, repo_name):
    """Return a spec record dict for a single file, or None to skip."""
    rel = _rel(fpath)
    specs_root_rel = _rel(specs_root)

    # Skip README files (not specs themselves)
    basename = os.path.basename(fpath)
    if basename.upper() == "README.MD":
        return None

    # Skip the index itself to avoid self-reference
    if rel == "specs/index.yaml":
        return None

    ext = os.path.splitext(basename)[1].lower()

    try:
        mtime = os.path.getmtime(fpath)
        mtime_str = datetime.datetime.fromtimestamp(
            mtime, tz=datetime.timezone.utc
        ).strftime("%Y-%m-%d")
    except OSError:
        mtime_str = ""

    title = ""
    description = ""
    frontmatter = {}
    raw = ""

    if ext == ".md":
        try:
            with open(fpath, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError:
            return None

        frontmatter, body = _parse_frontmatter(raw)

        # Title: prefer frontmatter, then first heading
        title = (
            frontmatter.get("title")
            or _extract_title_md(raw)
            or os.path.splitext(basename)[0].replace("-", " ").replace("_", " ").title()
        )
        # Description: prefer frontmatter, then first paragraph
        description = (
            frontmatter.get("description")
            or _extract_description_md(body)
        )

    elif ext in (".yaml", ".yml"):
        try:
            with open(fpath, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError:
            return None

        title, description = _extract_yaml_title_desc(raw)
        if not title:
            title = os.path.splitext(basename)[0].replace("-", " ").replace("_", " ").title()

    else:
        return None

    title = str(title).strip()[:120]
    description = str(description).strip()[:200]

    category = _infer_category(rel, specs_root_rel)
    target_repo = _target_repo_from_rel(rel, specs_root_rel, repo_name)
    tags = _infer_tags_from_path(rel, frontmatter)
    wrk_refs = _extract_wrk_refs(rel, frontmatter, title, description, raw)

    return {
        "path": rel,
        "title": title,
        "description": description,
        "category": category,
        "repo": target_repo,
        "tags": tags,
        "wrk_refs": wrk_refs,
        "mtime": mtime_str,
    }


def walk_specs_dir(specs_dir, repo_name, records):
    """Walk a specs directory and append records."""
    if not os.path.isdir(specs_dir):
        return
    for dirpath, dirnames, filenames in os.walk(specs_dir):
        # Skip hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in sorted(filenames):
            if not fname.lower().endswith((".md", ".yaml", ".yml")):
                continue
            fpath = os.path.join(dirpath, fname)
            rec = process_file(fpath, specs_dir, repo_name)
            if rec is not None:
                records.append(rec)


def build_index():
    records = []

    # 1. workspace-hub specs/
    hub_specs = os.path.join(HUB_ROOT, "specs")
    walk_specs_dir(hub_specs, "workspace-hub", records)

    # 2. Each submodule's specs/ dir
    for repo in SUBMODULE_REPOS:
        sub_specs = os.path.join(HUB_ROOT, repo, "specs")
        if os.path.isdir(sub_specs):
            walk_specs_dir(sub_specs, repo, records)

    # Build summary counts by category
    by_category = {}
    for rec in records:
        cat = rec["category"]
        by_category[cat] = by_category.get(cat, 0) + 1

    by_repo = {}
    for rec in records:
        r = rec["repo"]
        by_repo[r] = by_repo.get(r, 0) + 1

    # Count specs per WRK reference (multi-valued — a spec can ref multiple WRKs)
    by_wrk = {}
    for rec in records:
        for wrk in rec.get("wrk_refs") or []:
            by_wrk[wrk] = by_wrk.get(wrk, 0) + 1

    index = {
        "generated": datetime.date.today().isoformat(),
        "total_specs": len(records),
        "by_category": dict(sorted(by_category.items())),
        "by_repo": dict(sorted(by_repo.items())),
        "by_wrk": dict(sorted(by_wrk.items(), key=lambda kv: int(kv[0].split("-")[1]))),
        "specs": records,
    }
    return index


def main():
    print("Building specs index...")
    index = build_index()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Custom YAML dump: write scalars cleanly, preserve order
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        yaml.dump(
            index,
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

    n = index["total_specs"]
    print(f"WRK-328 complete: {n} specs indexed, index written to specs/index.yaml")
    print(f"By category: {index['by_category']}")
    print(f"By repo: {index['by_repo']}")


if __name__ == "__main__":
    main()
