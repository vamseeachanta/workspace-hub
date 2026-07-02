from __future__ import annotations


def canonicalize_path(path: str, alias_map: dict[str, str]) -> str:
    for alias, canonical in sorted(alias_map.items(), key=lambda item: len(item[0]), reverse=True):
        if path == alias:
            return canonical
        if path.startswith(alias + "/"):
            return canonical + path[len(alias) :]
    return path
