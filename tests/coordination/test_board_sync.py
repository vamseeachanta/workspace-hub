import json
import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "coordination" / "board_sync.py"


def _write_fake_gh(tmp_path, responses):
    log = tmp_path / "gh-log.jsonl"
    fake = tmp_path / "gh"
    fake.write_text(
        f"""#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

responses = {json.dumps(responses)}
log = Path({str(log)!r})
args = sys.argv[1:]
with log.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(args) + "\\n")

key = " ".join(args)
for candidate in (key, " ".join(args[:5]), " ".join(args[:3]), "default"):
    if candidate in responses and isinstance(responses[candidate], dict) and "__rc__" in responses[candidate]:
        sys.stderr.write(responses[candidate].get("stderr", ""))
        raise SystemExit(int(responses[candidate]["__rc__"]))
if args[:2] == ["issue", "comment"]:
    print("https://github.com/vamseeachanta/workspace-hub/issues/4001#issuecomment-1")
elif args[:2] == ["issue", "edit"]:
    print("")
elif args[:2] == ["issue", "close"]:
    print("")
else:
    for candidate in (key, " ".join(args[:5]), " ".join(args[:3]), "default"):
        if candidate in responses:
            print(json.dumps(responses[candidate]))
            break
    else:
        print("[]")
""",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake, log


def _run(tmp_path, args, responses, *, check=True):
    fake, log = _write_fake_gh(tmp_path, responses)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}{os.pathsep}{env['PATH']}"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )
    calls = []
    if log.exists():
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    return result, calls


def test_export_writes_board_model_files(tmp_path):
    responses = {
        "label list --repo vamseeachanta/workspace-hub --search decision: --limit 1000 --json name": [
            {"name": "decision:ecosystem"}
        ],
        "label list --repo vamseeachanta/workspace-hub --search lane: --limit 1000 --json name": [
            {"name": "lane:codex"}
        ],
        "issue list --repo vamseeachanta/workspace-hub --state open --limit 1000 --label decision:ecosystem --json number,title,body,labels,url,state": [
            {
                "number": 4001,
                "title": "Rewire L4: owner board generated from decision:* issues",
                "body": "Parent RFC: #3997. Epic: #3993. Tier B.\\n\\n**Done when:** board regenerates.",
                "url": "https://github.com/vamseeachanta/workspace-hub/issues/4001",
                "state": "OPEN",
                "labels": [
                    {"name": "decision:ecosystem"},
                    {"name": "dispatch:ready"},
                    {"name": "lane:codex"},
                ],
            }
        ],
        "pr list --repo vamseeachanta/workspace-hub --state open --limit 1000 --label decision:ecosystem --json number,title,body,labels,url,state": [
            {
                "number": 12,
                "title": "Draft decision PR",
                "body": "Tier C.",
                "url": "https://github.com/vamseeachanta/workspace-hub/pull/12",
                "state": "OPEN",
                "labels": [{"name": "decision:ecosystem"}],
            }
        ],
        "issue list --repo vamseeachanta/workspace-hub --state open --limit 1000 --label lane:codex --json number,title,body,labels,url,state": [],
        "pr list --repo vamseeachanta/workspace-hub --state open --limit 1000 --label lane:codex --json number,title,body,labels,url,state": [],
    }
    out_dir = tmp_path / "board"

    _run(tmp_path, ["export", "--repo", "vamseeachanta/workspace-hub", "--out-dir", str(out_dir)], responses)

    for name in ("cards.json", "decisions.json", "goals.json", "sessions.json", "subgoals.json"):
        assert (out_dir / name).exists()
    cards = json.loads((out_dir / "cards.json").read_text(encoding="utf-8"))
    assert [card["id"] for card in cards] == [
        "workspace-hub-issue-4001",
        "workspace-hub-pr-12",
    ]
    assert cards[0]["section"] == "decision:ecosystem"
    assert cards[0]["configs"]["kind"] == "issue"
    assert cards[0]["recommended"] == "approve"
    assert cards[0]["goal"] == "workspace-hub-3997"
    assert cards[0]["owner_answer"] is None
    assert cards[0]["answered_at"] is None
    decisions = json.loads((out_dir / "decisions.json").read_text(encoding="utf-8"))
    assert decisions[0]["repo"] == "vamseeachanta/workspace-hub"
    assert decisions[0]["issue"] == 4001


def test_import_dry_run_does_not_write(tmp_path):
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps(
            [
                {
                    "id": "D01",
                    "repo": "vamseeachanta/workspace-hub",
                    "issue": 4001,
                    "choice": "approve",
                    "note": "ship it",
                }
            ]
        ),
        encoding="utf-8",
    )

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions)], {})

    assert "DRY-RUN" in result.stdout
    assert not any(call[:2] == ["issue", "comment"] for call in calls)
    assert not any(call[:2] == ["issue", "edit"] for call in calls)


def test_import_apply_comments_and_flips_labels(tmp_path):
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps(
            {
                "decisions": [
                    {
                        "card_id": "workspace-hub-issue-4001",
                        "repo": "vamseeachanta/workspace-hub",
                        "issue": 4001,
                        "answer": "approve",
                        "note": "owner note",
                        "label": "dispatch:ready",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    responses = {
        "issue view 4001": {
            "labels": [{"name": "decision:ecosystem"}, {"name": "dispatch:blocked"}],
            "comments": [],
        }
    }

    _, calls = _run(tmp_path, ["import", "--decisions", str(decisions), "--apply"], responses)

    assert ["issue", "comment", "4001", "--repo", "vamseeachanta/workspace-hub", "--body", "Owner decision workspace-hub-issue-4001: approve (+ owner note)"] in calls
    assert [
        "issue",
        "edit",
        "4001",
        "--repo",
        "vamseeachanta/workspace-hub",
        "--add-label",
        "dispatch:ready",
        "--remove-label",
        "decision:ecosystem",
        "--remove-label",
        "dispatch:blocked",
    ] in calls
    assert calls.index([
        "issue",
        "edit",
        "4001",
        "--repo",
        "vamseeachanta/workspace-hub",
        "--add-label",
        "dispatch:ready",
        "--remove-label",
        "decision:ecosystem",
        "--remove-label",
        "dispatch:blocked",
    ]) < calls.index(["issue", "comment", "4001", "--repo", "vamseeachanta/workspace-hub", "--body", "Owner decision workspace-hub-issue-4001: approve (+ owner note)"])


def test_import_exported_decision_round_trips_and_defer_stays_blocked(tmp_path):
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps(
            [
                {
                    "card_id": "workspace-hub-issue-4001",
                    "repo": "vamseeachanta/workspace-hub",
                    "issue": 4001,
                    "answer": "defer",
                    "written_back": False,
                    "comment_url": None,
                }
            ]
        ),
        encoding="utf-8",
    )
    responses = {
        "issue view 4001 --repo vamseeachanta/workspace-hub --json labels,comments": {
            "labels": [{"name": "decision:ecosystem"}, {"name": "dispatch:ready"}],
            "comments": [],
        }
    }

    _, calls = _run(tmp_path, ["import", "--decisions", str(decisions), "--apply"], responses)

    assert [
        "issue",
        "edit",
        "4001",
        "--repo",
        "vamseeachanta/workspace-hub",
        "--add-label",
        "dispatch:blocked",
        "--remove-label",
        "decision:ecosystem",
        "--remove-label",
        "dispatch:ready",
    ] in calls


def test_import_apply_is_idempotent_by_decision_id(tmp_path):
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps(
            [
                {
                    "id": "D02",
                    "repo": "vamseeachanta/workspace-hub",
                    "issue": 4001,
                    "choice": "defer",
                }
            ]
        ),
        encoding="utf-8",
    )
    responses = {
        "issue view 4001": {
            "labels": [{"name": "decision:ecosystem"}],
            "comments": [{"body": "Owner decision D02: defer"}],
        }
    }

    _, calls = _run(tmp_path, ["import", "--decisions", str(decisions), "--apply"], responses)

    assert any(call[:3] == ["issue", "view", "4001"] for call in calls)
    assert not any(call[:2] == ["issue", "comment"] for call in calls)
    assert not any(call[:2] == ["issue", "edit"] for call in calls)
