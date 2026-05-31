"""GitHub I/O helpers for the #2817 plan-approval gate."""

from __future__ import annotations

import re

from label_authority import gh_json, parse_iso


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def fetch_actor_type(login: str | None) -> str | None:
    if not login:
        return None
    data = gh_json("api", f"users/{login}") or {}
    return data.get("type")


def fetch_commit_pushed_at(repo: str, sha: str):
    owner, name = repo.split("/", 1)
    query = """
    query($owner:String!, $name:String!, $oid:GitObjectID!) {
      repository(owner:$owner, name:$name) {
        object(oid:$oid) { ... on Commit { pushedDate } }
      }
    }
    """
    data = gh_json("api", "graphql", "-f", f"owner={owner}", "-f", f"name={name}",
                   "-f", f"oid={sha}", "-f", f"query={query}") or {}
    commit = (((data.get("data") or {}).get("repository") or {}).get("object")) or {}
    return parse_iso(commit.get("pushedDate"))


def fetch_plan_revision_anchor(repo: str, sha: str, plan_path: str, fallback_time):
    if not re.fullmatch(r"[0-9a-fA-F]{40}", sha or ""):
        return None, False
    commit = gh_json("api", f"repos/{repo}/commits/{sha}") or {}
    files = {_normalize_path((item or {}).get("filename", "")) for item in commit.get("files", [])}
    if _normalize_path(plan_path) not in files:
        return None, False
    pushed_at = fetch_commit_pushed_at(repo, sha)
    if pushed_at is None:
        return None, False
    anchors = [ts for ts in [pushed_at, fallback_time] if ts is not None]
    return max(anchors), True


def revision_reaches_head(repo: str, revision_sha: str, head_sha: str | None) -> bool:
    if not head_sha or not re.fullmatch(r"[0-9a-fA-F]{40}", revision_sha or ""):
        return False
    if revision_sha.lower() == head_sha.lower():
        return True
    data = gh_json("api", f"repos/{repo}/compare/{revision_sha}...{head_sha}") or {}
    return data.get("status") in {"ahead", "identical"}


def fetch_file_blob(repo: str, ref: str, path: str) -> str | None:
    data = gh_json("api", f"repos/{repo}/contents/{path}?ref={ref}") or {}
    if isinstance(data, list):
        return None
    return data.get("sha")


def plan_blob_matches_revision(repo: str, revision_sha: str, head_sha: str | None, plan_path: str) -> bool:
    if not head_sha:
        return False
    revision_blob = fetch_file_blob(repo, revision_sha, plan_path)
    head_blob = fetch_file_blob(repo, head_sha, plan_path)
    return bool(revision_blob and head_blob and revision_blob == head_blob)


def load_issue_binding_sources(repo: str, issue: int) -> list[dict]:
    owner, name = repo.split("/", 1)
    query = """
    query($owner:String!, $name:String!, $number:Int!) {
      repository(owner:$owner, name:$name) {
        issue(number:$number) {
          author { login }
          body
          createdAt
          lastEditedAt
        }
        pullRequest(number:$number) {
          author { login }
          body
          createdAt
          lastEditedAt
        }
      }
    }
    """
    sources = []
    data = gh_json("api", "graphql", "-f", f"owner={owner}", "-f", f"name={name}",
                   "-F", f"number={issue}", "-f", f"query={query}") or {}
    repo_data = ((data.get("data") or {}).get("repository")) or {}
    # GitHub issues and PRs share one number namespace; this supports a linked
    # planning PR body, not the current implementation PR body.
    issue_data = repo_data.get("issue") or repo_data.get("pullRequest") or {}
    if issue_data.get("body"):
        sources.append({
            "author": issue_data.get("author") or {},
            "body": issue_data.get("body") or "",
            "createdAt": issue_data.get("createdAt"),
            "updatedAt": issue_data.get("lastEditedAt") or issue_data.get("createdAt"),
        })
    comments = gh_json("api", f"repos/{repo}/issues/{issue}/comments", "--paginate") or []
    for comment in comments:
        sources.append({
            "author": comment.get("user") or {},
            "body": comment.get("body") or "",
            "createdAt": comment.get("created_at"),
            "updatedAt": comment.get("updated_at"),
        })
    return sources


def load_current_issue_labels(repo: str, issue: int) -> set[str]:
    data = gh_json("api", f"repos/{repo}/issues/{issue}") or {}
    return {
        label.get("name")
        for label in data.get("labels", [])
        if isinstance(label, dict) and label.get("name")
    }
