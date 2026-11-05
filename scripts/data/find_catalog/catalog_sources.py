"""Read owner metadata into a private discovery projection; never copy payloads."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath

import yaml

KINDS = {"energy_catalog", "atlas_manifests", "riser_manifest",
         "standards_registry", "wiki_pages", "ace_manifest"}
EXPOSURES = {"public", "internal", "restricted"}


def configured_path(value, parent):
    text = os.path.expandvars(str(value))
    if "$" in text or not text.strip():
        raise ValueError("source and database paths require resolved configuration")
    path = Path(text).expanduser()
    return (parent / path).absolute() if not path.is_absolute() else path


def load_config(path):
    path = Path(path).resolve()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("catalog config version must be 1")
    if not isinstance(data.get("sources"), list) or not data["sources"]:
        raise ValueError("sources must be a nonempty list")
    data["sources"] = [dict(source) for source in data["sources"]]
    data["database"] = configured_path(data["database"], path.parent)
    seen = set()
    for source in data["sources"]:
        for field in ("id", "kind", "path", "domain", "exposure"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError(f"source requires {field}")
        if source["id"] in seen:
            raise ValueError("duplicate source id")
        seen.add(source["id"])
        if source["kind"] not in KINDS:
            raise ValueError("unsupported source kind")
        if source["exposure"] not in EXPOSURES:
            raise ValueError("exposure must be public, internal or restricted")
        source["path"] = configured_path(source["path"], path.parent)
    return data


def is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def read_input(path, root):
    if is_link(path) or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("source symlink or path outside configured root")
    # Reject intermediate symlink directories, including ones that point inward.
    if any(is_link(p) for p in (path, *path.parents)):
        raise ValueError("source symlink requires a direct configured root")
    return path.read_bytes()


def document(raw, path):
    if path.suffix == ".json":
        return json.loads(raw)
    return yaml.safe_load(raw)


def text(value):
    return json.dumps(value, ensure_ascii=False, default=str) if isinstance(value, (dict, list)) else str(value or "")


def row(source, identity, locator, title, body="", *, domain=None, units=None,
        digest=None, provenance=None):
    return {"id": str(identity), "source": source["id"],
            "domain": domain or source["domain"], "exposure": source["exposure"],
            "locator": str(locator), "title": text(title), "body": text(body),
            "units": units, "digest": digest, "provenance": provenance or {},
            "readiness": "unverified"}


def energy_rows(source, data, locator):
    if not isinstance(data, dict) or not isinstance(data.get("modules"), dict):
        raise ValueError("energy catalog requires a modules mapping")
    modules = data["modules"]
    for module_id, module in modules.items():
        if not isinstance(module, dict) or not isinstance(module.get("datasets"), list):
            raise ValueError("energy catalog modules require a datasets list")
        for item in module["datasets"]:
            if (not isinstance(item, dict) or not isinstance(item.get("path"), str)
                    or not item["path"].strip()):
                raise ValueError("energy catalog datasets require a nonempty path string")
            path = item["path"]
            yield row(source, item.get("id", item.get("dataset_id", path)), path,
                      item.get("name", path), [item.get("description"), item.get("columns"), module_id],
                      domain=item.get("domain", module_id),
                      units=item.get("units", item.get("columns")), provenance={
                          "source_version": data.get("version"),
                          "catalog_generated_at": data.get("generated_at"),
                          "last_modified": item.get("last_modified"),
                          "last_refreshed": item.get("last_refreshed"),
                          "source_url": item.get("source_url"),
                      })


def atlas_rows(source, data, locator):
    yield row(source, data["atlas_id"], locator, data.get("basename", data["atlas_id"]),
              [data.get("response"), data.get("physics"), data.get("axes"), data.get("provenance")],
              units=data.get("units", data.get("axes")),
              digest=data.get("provenance", {}).get("content_fingerprint"),
              provenance=dict(data.get("provenance") or {}))


def riser_rows(source, data, locator):
    for key, item in data["tables"].items():
        yield row(source, item.get("id", key), item["file"], key.replace("_", " "),
                  [key, item.get("description"), item.get("columns")], units=item.get("units"),
                  digest=item.get("sha256"))


def standards_rows(source, data, locator):
    standards = data["standards"]
    items = standards.items() if isinstance(standards, dict) else enumerate(standards)
    for key, item in items:
        identity = item.get("id", item.get("code_id", item.get("standard_id")))
        if identity is None and isinstance(key, str):
            identity = key
        if identity is None:
            raise ValueError("standard missing owner-issued identity")
        yield row(source, identity, f"{locator}#{identity}", item.get("title", item.get("name", identity)),
                  [identity, item.get("family_key"), item.get("description"), item.get("tags"),
                   item.get("publishers", item.get("publisher"))],
                  domain=item.get("domain"), units=item.get("units"),
                  provenance={"revisions": item.get("revisions"), "pages": item.get("pages")})


def page_rows(source, raw, locator):
    content = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    metadata = {}
    warnings = []
    if content.startswith("---\n"):
        front, separator, body = content[4:].partition("\n---")
        if separator:
            try:
                parsed = yaml.safe_load(front)
                metadata = parsed if isinstance(parsed, dict) else {}
                content = body
            except yaml.YAMLError:
                warnings.append("invalid page frontmatter; metadata unverified")
    identity = metadata.get("id", metadata.get("doc_key", "sha256:" + hashlib.sha256(raw).hexdigest()))
    title = metadata.get("title") or next((line.lstrip("# ") for line in content.splitlines()
                                          if line.startswith("# ")), Path(locator).stem)
    result = row(source, identity, locator, title, content,
                 domain=metadata.get("domain", Path(locator).parts[0]), units=metadata.get("units"))
    result["warnings"] = warnings
    yield result


def archive_rows(source, raw, locator):
    lines = (line for line in io.StringIO(raw.decode("utf-8")) if not line.startswith("#"))
    for item in csv.DictReader(lines, delimiter="\t"):
        digest = item["sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("manifest payload digest must be SHA-256")
        locator_path = PurePosixPath(item["path"])
        windows_path = PureWindowsPath(item["path"])
        if (locator_path.is_absolute() or windows_path.drive or windows_path.root
                or ".." in locator_path.parts or ".." in windows_path.parts):
            raise ValueError("manifest path must be owner-relative")
        path = (Path(locator).parent / item["path"]).as_posix()
        yield row(source, item.get("id") or "sha256:" + digest, path,
                  Path(item["path"]).name, [item["path"], item.get("disposition")],
                  digest="sha256:" + digest,
                  provenance={"blob": item.get("blob"), "bytes": item.get("bytes")})


def input_paths(source):
    root = source["path"]
    if not root.exists():
        raise ValueError(f"source unavailable: {source['id']}")
    patterns = {"atlas_manifests": "*/*/manifest.yaml", "wiki_pages": "*/wiki/**/*.md",
                "ace_manifest": "*/MANIFEST.tsv"}
    if root.is_file():
        return root.parent, [root]
    if source["kind"] not in patterns:
        raise ValueError("source kind requires a metadata file")
    paths = sorted(root.glob(patterns[source["kind"]]))
    if not paths:
        raise ValueError(f"source has no metadata inputs: {source['id']}")
    return root, paths


def records(config):
    observed_at = datetime.now(UTC).isoformat()
    adapters = {"energy_catalog": energy_rows, "atlas_manifests": atlas_rows,
                "riser_manifest": riser_rows, "standards_registry": standards_rows}
    for source in config["sources"]:
        root, paths = input_paths(source)
        for path in paths:
            raw = read_input(path, root)
            digest = hashlib.sha256(raw).hexdigest()
            if source.get("sha256") and source["sha256"].removeprefix("sha256:") != digest:
                raise ValueError(f"import digest mismatch: {source['id']}")
            locator = path.relative_to(root).as_posix()
            kind = source["kind"]
            if kind == "wiki_pages":
                imported = page_rows(source, raw, locator)
            elif kind == "ace_manifest":
                imported = archive_rows(source, raw, locator)
            else:
                imported = adapters[kind](source, document(raw, path), locator)
            for result in imported:
                result["provenance"].update({"manifest": locator,
                    "observed_sha256": "sha256:" + digest, "observed_at": observed_at,
                    "source_revision": source.get("revision", "unknown"),
                    "owner": source.get("owner", source["id"]),
                    "source_catalog_id": source["id"]})
                yield result
