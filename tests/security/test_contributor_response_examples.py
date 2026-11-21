"""Hand-counted synthetic expectations for the contributor response example.

Basis: the literal decision table and verification notes in
docs/security/contributor-response-examples.md, scoped to issue #3637.
"""

from pathlib import Path
import re
import subprocess
import sys


# Two parent levels above this file's directory: security -> tests -> root.
DOCUMENT = Path(__file__).resolve().parents[2] / "docs/security/contributor-response-examples.md"
SIGNALS = ("ordinary_contribution", "unsolicited_paid_help", "requests_private_material")

# Independent enumeration: private requests occupy four rows, no signal adds
# one escalation, paid help without private material occupies two rows, and
# the remaining ordinary contribution occupies one review row.
EXPECTED_ROWS = (
    (False, False, False, "private_escalation"),
    (False, False, True, "private_escalation"),
    (False, True, False, "decline"),
    (False, True, True, "private_escalation"),
    (True, False, False, "review"),
    (True, False, True, "private_escalation"),
    (True, True, False, "decline"),
    (True, True, True, "private_escalation"),
)


def documented_source():
    blocks = re.findall(r"^```python\n(?P<source>.*?)^```$", DOCUMENT.read_text(), re.M | re.S)
    source, = blocks  # Exactly one runnable example is part of the contract.
    return source


def run_example(tmp_path, probe="", *, main=False):
    """Run without site packages, guarding file, OS, socket and process access."""
    source = documented_source()
    wrapper = f"""
import sys

def reject_side_effects(event, arguments):
    if event == "open" or event.startswith(("os.", "socket.", "subprocess.")):
        raise RuntimeError("documented example attempted a side effect")

sys.addaudithook(reject_side_effects)
namespace = {{"__name__": {('__main__' if main else 'example_test')!r}}}
exec(compile({source!r}, "<documented-example>", "exec"), namespace)
exec(compile({probe!r}, "<synthetic-probe>", "exec"), namespace)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-B", "-c", wrapper],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    # Subprocess convention: zero is successful completion (verification notes).
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []
    return result.stdout


def test_documented_example_runs_offline(tmp_path):
    # Hand calculation from the three literal demonstration events, in order.
    assert run_example(tmp_path, main=True) == "review\ndecline\nprivate_escalation\n"


def test_literal_decision_table_matches_recommendations(tmp_path):
    rows = []
    for line in DOCUMENT.read_text().splitlines():
        if line.startswith("| False |") or line.startswith("| True |"):
            # Discard the empty cells outside the table's bounding pipes.
            ordinary, paid, private, category = (cell.strip() for cell in line.split("|")[1:-1])
            assert all(value in ("True", "False") for value in (ordinary, paid, private))
            rows.append((ordinary == "True", paid == "True", private == "True", category))
    assert tuple(rows) == EXPECTED_ROWS
    events = [dict(zip(SIGNALS, (ordinary, paid, private)))
              for ordinary, paid, private, category in rows]
    probe = f"for event in {events!r}:\n    print(recommend(event))\n"
    assert run_example(tmp_path, probe).splitlines() == [
        category for ordinary, paid, private, category in EXPECTED_ROWS
    ]


def test_private_material_is_never_in_public_response(tmp_path):
    # A synthetic marker stands for withheld content; it is not private data.
    events = [dict(zip(SIGNALS, (ordinary, paid, True)),
                   details="SYNTHETIC_WITHHELD_CONTENT")
              for ordinary in (False, True) for paid in (False, True)]
    probe = f"for event in {events!r}:\n    print(recommend(event))\n"
    output = run_example(tmp_path, probe)
    assert output.splitlines() == [
        "private_escalation", "private_escalation",
        "private_escalation", "private_escalation",
    ]
    assert "SYNTHETIC_WITHHELD_CONTENT" not in output


def test_incomplete_or_malformed_signals_escalate_without_echo(tmp_path):
    # Independent cases: absent event, empty event, missing flag, string flag,
    # list event and null flag. Each lacks the exact boolean input contract.
    events = [
        None,
        {},
        {"ordinary_contribution": True, "unsolicited_paid_help": False},
        dict(zip(SIGNALS, (True, False, "False"))),
        ["SYNTHETIC_UNCLASSIFIED_INPUT"],
        dict(zip(SIGNALS, (True, False, None))),
    ]
    probe = f"for event in {events!r}:\n    print(recommend(event))\n"
    expected = [
        "private_escalation", "private_escalation", "private_escalation",
        "private_escalation", "private_escalation", "private_escalation",
    ]
    output = run_example(tmp_path, probe)
    assert output.splitlines() == expected
    assert "SYNTHETIC_UNCLASSIFIED_INPUT" not in output
