#!/usr/bin/env python3
"""A tracked queue file must not carry raw GitHub issue titles.

## The gap

`dispatch.py` materialises `.claude/dispatch/<machine>.yaml` and **commits it**.
`workspace-hub` is a PUBLIC repo. The card carried `title` verbatim from the
routed issue, and the routed set spans workspace-hub, digitalmodel and deckhand
— repos whose issue titles include client identifiers.

CI's Client-PII Gate blocks on exactly this (PR #3765): ten-plus hits in
`dev-primary.yaml`, two in `multi.yaml`. The values are withheld from the log by
design, which is itself the point — the leak is real but unquotable, so the fix
cannot be "redact the ones we can see". The generator must stop emitting the
field at all.

`scripts/legal/legal-sanity-scan.sh` passing locally proves nothing here: it
runs without the private redaction map, which is a CI secret. A local pass is
the absence of a signal, not a clean result.

## What must NOT change

`route.py` keeps fetching titles. They feed `--detail` console output and
`--json`, which are ephemeral and local — never tracked. #3763/#3767 had just
repaired that fetch after every card shipped with an empty title; narrowing the
fetch to "fix" the leak would re-break it. The boundary is **serialisation**,
not retrieval.

## Why the field is OMITTED, not blanked

#3763's failure mode was 1341/1341 cards with `title: ""`. If redaction shipped
as a blank or a placeholder string, a redacted queue and a broken pipeline would
be byte-identical on disk. So the card carries no title-shaped field at all, and
the payload declares the omission once (`title_policy`) so a reader can tell
"deliberately absent" from "generator dropped it".

The card stays identifiable without it: `gh`, `repo`, `url`, `domain`,
`provider`, `dispatch_status`, `wip_eligible`, `routed_by`. A draining session
fetches the title from GitHub at drain time, where it is ephemeral.

## What is asserted

The PROPERTY — no substring of a routed title survives into the serialised
YAML — not merely that a key named `title` is gone. A rename to `summary`, a
nested `meta:` blob, or a truncated prefix would all pass a key-absence check
and still leak.

Three things the first cut of this file got wrong, and what replaced them:

1. The window scan had a silent length floor: `range(len(t) - 12 + 1)` yields
   NOTHING for a title under 12 characters, so `title: ZZQ-7` passed vacuously
   — and client identifiers are typically SHORT codes. The needle set now
   always includes the whole title, whatever its length, plus every token.
2. Nothing looked at the artifacts we actually ship. Freshly-generated payloads
   were clean while the tracked bytes on `main` still carried titles, and the
   suite was green throughout. `test_no_tracked_queue_file_...` reads the
   tracked files themselves, enumerated by `git ls-files`.
3. `title_policy` could lie: a hand-edited or half-regenerated file could
   declare the omission AND carry the field. The declaration now binds the
   cards in the same payload, generated and shipped alike.

Every `assert not leaked` is satisfied perfectly by a scanner that finds
nothing, so `test_the_scanner_itself_has_teeth` runs the same scanner over a
deliberately leaking payload and requires a hit.

Hermetic apart from `git ls-files` (index read, no network): injected
proposals, injected clock, no gh.

Run: uv run --with pyyaml pytest tests/dispatch/test_queue_omits_issue_titles.py
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCH_PY = REPO_ROOT / "scripts" / "dispatch" / "dispatch.py"
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _load():
    # dispatch.py does `import route` as a SIBLING module, so its directory has
    # to be importable. Prepending rather than appending: a stray `route.py`
    # elsewhere on sys.path would otherwise shadow the one under test.
    pkg_dir = str(DISPATCH_PY.parent)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    spec = importlib.util.spec_from_file_location("dispatch_notitle", DISPATCH_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_notitle"] = mod
    spec.loader.exec_module(mod)
    return mod


D = _load()

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

# Long enough that a 12-character window is unambiguous, and shaped like a real
# issue title so a truncating leak (`title[:60]`, `title[:20]`) still trips the
# window scan below. Deliberately synthetic — no real identifier goes in a test.
SENTINEL_TITLE = "Refit programme for ZZQX-9 marine terminal berth 4"

# The shape that matters most and used to be invisible. A client identifier in
# a real issue title is usually a short code, not a sentence — and the old
# 12-character window scan returned an empty needle list for anything this
# size, so the assertion passed without examining a single byte.
SHORT_SENTINEL = "ZZQ-7"

WINDOW = 12

# Runs shorter than this are dropped from the TOKEN needles as noise. It is not
# a length floor on the scan: `_needles` always includes the whole title, so a
# 2-character title is still checked in full.
MIN_TOKEN = 3

TITLE_SHAPES = [
    SENTINEL_TITLE,
    SHORT_SENTINEL,                              # 5 chars — under the old floor
    "ZZQ7",                                      # 4 chars, no punctuation at all
    "x" * 300,                                   # longer than route.py's [:60]
    "Ünïcøde tïtle wíth ZZQX-9 accénts",         # non-ASCII must not slip through
    "title: with: colons: and #hash",            # YAML-punctuating title
]


def _norm(text: str) -> str:
    """NFKC on both sides of every comparison.

    `yaml.safe_dump` defaults to `allow_unicode=False`, so an accented title
    reaches disk as `\\xE9` escapes rather than as the characters that were
    routed; and a leak rewritten through a compatibility form (fullwidth,
    ligature, non-breaking space) is byte-different from the title but reads
    identically to a human — and to anyone grepping the public repo. Folding
    both haystack and needle means an encoding cannot launder the identifier.
    """
    return unicodedata.normalize("NFKC", text)


def _windows(text: str, size: int = WINDOW) -> list[str]:
    """Every contiguous slice of `text` — and the WHOLE string when it is
    shorter than `size`, so the needle set is never empty.

    The previous form was `[text[i:i+size] for i in range(len(text)-size+1)]`,
    which returns `[]` for anything under 12 characters. Every caller then
    asserted `not any(w in text for w in [])` — true by construction. The guard
    was strongest on prose and absent on short codes, which is precisely
    backwards: a leaked `ZZQ-7` is the disclosure, a leaked English sentence
    usually is not.
    """
    if len(text) <= size:
        return [text]
    return [text[i:i + size] for i in range(len(text) - size + 1)]


_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    """Word-ish runs of at least MIN_TOKEN characters.

    Catches a leak that REFORMATS the title on the way out — lowercased,
    slugified, punctuation-stripped — where no verbatim window survives but
    every identifying word does.
    """
    return [t for t in _TOKEN_RE.findall(text) if len(t) >= MIN_TOKEN]


def _needles(title: str) -> list[str]:
    """The whole title, each token, each window — deduped, order preserved.

    The whole title first and unconditionally: that is the needle with no
    length precondition attached to it, and the one the old scan lacked.
    """
    out, seen = [], set()
    for n in [title, *_tokens(title), *_windows(title)]:
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _proposal(**kw):
    base = {
        "key": "gh:owner/name#4242",
        "repo": "owner/name",
        "domain": "subsea",
        "provider": "codex",
        "title": SENTINEL_TITLE,
        "url": "https://github.com/owner/name/issues/4242",
        "machine": "dev-primary",
        "slot": "active-eligible",
        "routed_by": "rule",
    }
    base.update(kw)
    return base


def _dump(payload) -> str:
    """Serialise exactly as `cmd_build` does, so the assertion covers the bytes
    that actually reach the tracked file rather than an in-memory dict."""
    return yaml.safe_dump(payload, sort_keys=False, width=100)


def _values(obj):
    """Every scalar in a nested structure — keys are ignored on purpose.

    A leak that renames the field, nests it, or stuffs it into a list is still a
    leak. Only the VALUES matter.
    """
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _values(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _values(v)
    else:
        yield obj


def _haystacks(text: str) -> list[str]:
    """Every form the same bytes can be read back as, all NFKC-folded.

    Two forms, because one is not enough. The raw text is what lands in the
    repo and what a grep sees. The round-tripped VALUES undo `safe_dump`'s
    escaping, so an accented title that shipped as `t\\xEFtle` is compared as
    `title` — a scan of the raw text alone would call that clean.
    """
    forms = [text]
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError:                # a corrupt file is scanned raw only
        loaded = None
    if loaded is not None:
        forms.append("\n".join(str(v) for v in _values(loaded) if v is not None))
    return [_norm(f) for f in forms]


_NOISE: list[str] | None = None


def _structural_noise() -> list[str]:
    """The same payload built from a proposal with an EMPTY title — the floor.

    `title_policy` puts the literal word "title" into every queue file, so a
    token-level scan flags it forever unless something subtracts it. An
    allowlist would be that something, and would also be a hole: whoever adds
    the next field gets to name what the scanner ignores. This control instead
    asks the generator what it emits when there is no title to leak. Anything
    present under those conditions carries zero information about the routed
    title, by construction, and no hand-maintained list can drift.

    (Corollary: a title that is *entirely* structural noise — literally
    `"ready"` — is unscannable. It is also unidentifying, so nothing is lost.)
    """
    global _NOISE
    if _NOISE is None:
        cards = D.build_queues([_proposal(title="")])["dev-primary"]
        _NOISE = _haystacks(_dump(D.queue_payload("dev-primary", cards, now=lambda: NOW)))
    return _NOISE


def _leaked(title: str, text: str) -> list[str]:
    """Needles from `title` that survive into `text` and are not structural."""
    hays = _haystacks(text)
    noise = _structural_noise()
    hits = []
    for needle in _needles(title):
        n = _norm(needle)
        if any(n in h for h in hays) and not any(n in c for c in noise):
            hits.append(needle)
    return hits


# --------------------------------------------------------------------------
# what counts as a title-shaped field — a shape, never the string "title"
# --------------------------------------------------------------------------


def _card_schema() -> set[str]:
    """The generator's own card keys, asked of the generator.

    Never a hand-written list: the whole failure mode is a field the reader did
    not think to name. Anything on a card that `build_queues` does not emit is
    unaccounted-for, whether it is called `title`, `summary`, `meta` or `note`.
    """
    return set(D.build_queues([_proposal()])["dev-primary"][0])


def _title_shaped(card: dict, allowed: set[str]) -> list[str]:
    """Fields on `card` that could be carrying an issue title.

    Two independent properties, neither of them a key name:

    * a key the generator does not emit — catches the rename;
    * a value containing whitespace — catches the leak that reuses an
      ALLOWED key. Every legitimate card value is a slug, a `owner/repo#N`
      reference, a URL or a bool; an issue title is prose. Prose in a queue
      card is the tell regardless of what the key is called.
    """
    findings = [f"non-schema field {k!r}" for k in sorted(set(card) - allowed)]
    findings += [f"{k!r} carries prose: {v[:40]!r}"
                 for k, v in sorted(card.items())
                 if isinstance(v, str) and any(ch.isspace() for ch in v)]
    return findings


# --------------------------------------------------------------------------
# the property: no routed title reaches the tracked bytes
# --------------------------------------------------------------------------


def test_no_fragment_of_a_routed_title_reaches_the_serialised_queue():
    """The whole property, on the serialised form.

    Not `"title" not in card`: a rename to `summary`, a nested `meta:` blob, or
    a truncated prefix would all satisfy a key-absence check and still publish
    the identifier to a public repo.
    """
    payload = D.queue_payload(
        "dev-primary", D.build_queues([_proposal()])["dev-primary"], now=lambda: NOW)
    text = _dump(payload)
    leaked = _leaked(SENTINEL_TITLE, text)
    assert not leaked, (
        f"routed issue title reached the tracked YAML via {leaked[:3]!r}\n{text}")


def test_no_card_value_equals_the_title_under_any_key():
    """Same property at the object level, so the failure names the offending value."""
    cards = D.build_queues([_proposal()])["dev-primary"]
    for v in _values(cards):
        if not isinstance(v, str):
            continue
        leaked = _leaked(SENTINEL_TITLE, v)
        assert not leaked, f"a card value carries the routed title: {v!r} via {leaked[:3]!r}"


@pytest.mark.parametrize("title", TITLE_SHAPES)
def test_the_property_holds_for_any_title_shape(title):
    """Including the shapes the old scan could not see.

    `SHORT_SENTINEL` and `"ZZQ7"` are here specifically: under the previous
    12-character window floor both produced an empty needle list, so this test
    reported a pass on a payload it never examined.
    """
    cards = D.build_queues([_proposal(title=title)])["dev-primary"]
    text = _dump(D.queue_payload("dev-primary", cards, now=lambda: NOW))
    leaked = _leaked(title, text)
    assert not leaked, f"title shape {title[:30]!r} leaked into the queue file via {leaked[:3]!r}"


@pytest.mark.parametrize("title", TITLE_SHAPES)
def test_the_scanner_itself_has_teeth(title):
    """Guards the guard — the one assertion in this file that is not `not ...`.

    Every other check here is `assert not leaked`, which a scanner returning
    nothing satisfies perfectly; that is exactly how the length floor survived
    review. This runs the same scanner over a payload that deliberately carries
    the title under a RENAMED key and requires a hit, for every shape including
    the short codes. Re-introduce a minimum length, narrow the needle set, or
    over-subtract the noise floor, and this goes red instead of quiet.
    """
    cards = [dict(c, summary=title)
             for c in D.build_queues([_proposal(title=title)])["dev-primary"]]
    text = _dump(D.queue_payload("dev-primary", cards, now=lambda: NOW))
    assert _leaked(title, text), (
        f"the scanner reported CLEAN on a payload that carries {title[:30]!r} "
        f"verbatim under `summary` — every other assertion in this file is "
        f"therefore vacuous for this shape")


def test_the_whole_write_path_is_clean(tmp_path, monkeypatch):
    """End-to-end through `cmd_build(write=True)` onto disk.

    The unit assertions above cover the two functions; this covers the command
    that actually produces the tracked file, so a leak reintroduced between them
    (a post-processing step, a second serialiser) is still caught.
    """
    out = tmp_path / "dispatch"
    monkeypatch.setattr(D, "ROOT", tmp_path)
    monkeypatch.setattr(D, "DISPATCH_DIR", out)
    monkeypatch.setattr(D.route, "propose", lambda args: [_proposal()])

    D.cmd_build(write=True)

    written = out / "dev-primary.yaml"
    assert written.is_file(), "cmd_build wrote no queue file"
    text = written.read_bytes().decode("utf-8")
    leaked = _leaked(SENTINEL_TITLE, text)
    assert not leaked, f"routed title reached the file on disk via {leaked[:3]!r}\n{text}"


# --------------------------------------------------------------------------
# the artifacts we actually ship
# --------------------------------------------------------------------------


def _tracked_queue_files() -> list[Path]:
    """`git ls-files`, not `Path.glob`.

    The glob answers "what is on this disk", which is the wrong question twice
    over. Only tracked bytes reach the public repo, so an untracked local file
    is out of scope (this checkout has one right now — `cfd-dedicated.yaml`);
    and a glob scanning it would report a sweep over files nobody ships while a
    tracked file could be missing from the working tree entirely.

    `-z` + NUL split rather than line iteration: a newline in a pathname would
    otherwise split one path into two nonexistent ones.
    """
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", ".claude/dispatch/*.yaml"],
        capture_output=True, check=True, timeout=120)
    return [REPO_ROOT / n.decode("utf-8") for n in out.stdout.split(b"\0") if n]


def test_no_tracked_queue_file_ships_a_title_shaped_field():
    """The committed artifacts, read as bytes.

    Everything above tests a payload built in this process. That is necessary
    and was not sufficient: while `dispatch.py` was being fixed, freshly
    generated payloads were clean and the tracked files on `main` still carried
    titles — a green suite over a leaking repo. Regenerating the queues is a
    separate act from fixing the generator, and only this test notices when the
    second has happened and the first has not.

    Bytes, not `read_text()`: the published artifact is a byte sequence, and
    decoding it with the ambient locale is a way to not see what is in it.
    """
    files = _tracked_queue_files()
    assert files, "git ls-files found no tracked queue files — this scan would be vacuous"
    allowed = _card_schema()
    offenders = []
    for path in files:
        raw = path.read_bytes()
        try:
            data = yaml.safe_load(_norm(raw.decode("utf-8"))) or {}
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            offenders.append(f"{path.name}: unreadable, cannot be scanned ({exc})")
            continue
        for i, card in enumerate(data.get("cards") or []):
            offenders += [f"{path.name} card[{i}]: {f}" for f in _title_shaped(card, allowed)]
    assert not offenders, (
        "tracked queue files carry title-shaped data:\n  " + "\n  ".join(offenders))


# --------------------------------------------------------------------------
# absence must be DELIBERATE, not indistinguishable from breakage
# --------------------------------------------------------------------------


def test_no_card_carries_a_title_shaped_field():
    """A blank or placeholder title is the shape a *failed* fetch produces.

    #3763 shipped 1341/1341 cards with `title: ""`. Emitting `""` or a
    `"<redacted>"` stand-in would make an intentionally-redacted queue
    indistinguishable from that outage, so the field is gone entirely.
    """
    allowed = _card_schema()
    for card in D.build_queues([_proposal()])["dev-primary"]:
        assert not _title_shaped(card, allowed), (
            f"card carries a title-shaped field: {_title_shaped(card, allowed)}")


def test_the_payload_declares_that_titles_are_omitted():
    """The counterpart to the test above.

    With no per-card field, a reader cannot otherwise tell "redacted by policy"
    from "the generator forgot" — which is precisely the ambiguity #3763 turned
    into a silent 1341-card outage. One payload-level declaration resolves it
    without repeating a placeholder 1341 times in a tracked file.

    Asserted on a payload that actually carries cards: an empty one declares a
    policy about nothing.
    """
    cards = D.build_queues([_proposal()])["dev-primary"]
    assert cards, "the fixture produced no cards — the declaration below is about nothing"
    payload = D.queue_payload("dev-primary", cards, now=lambda: NOW)
    policy = payload.get("title_policy")
    assert policy, "the queue payload does not declare its title policy"
    assert "omit" in str(policy).lower(), (
        f"title_policy must state that titles are omitted, got {policy!r}")


def _policy_is_honoured(payload: dict, allowed: set[str]) -> list[str]:
    """A declared `title_policy` must bind the cards in the SAME payload.

    A file that declares the omission and carries the field is worse than one
    that declares nothing: it tells a reader — and a reviewer skimming for the
    key — that it has already been checked. Half-regeneration and hand-editing
    both produce exactly that state.
    """
    if not (payload or {}).get("title_policy"):
        return []
    return [f"card[{i}]: {f}"
            for i, card in enumerate(payload.get("cards") or [])
            for f in _title_shaped(card, allowed)]


def test_a_declared_policy_binds_the_cards_of_a_generated_payload():
    cards = D.build_queues([_proposal()])["dev-primary"]
    payload = D.queue_payload("dev-primary", cards, now=lambda: NOW)
    assert payload.get("title_policy"), "no policy declared — this check would be vacuous"
    assert not _policy_is_honoured(payload, _card_schema()), (
        "the generated payload declares titles omitted and emits them anyway")


def test_a_declared_policy_binds_the_cards_of_every_shipped_file():
    """Same rule on disk, where hand-edits and partial regenerations land."""
    files = _tracked_queue_files()
    assert files, "git ls-files found no tracked queue files — this scan would be vacuous"
    allowed = _card_schema()
    declaring, offenders = [], []
    for path in files:
        try:
            data = yaml.safe_load(_norm(path.read_bytes().decode("utf-8"))) or {}
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            offenders.append(f"{path.name}: unreadable, cannot be scanned ({exc})")
            continue
        if not isinstance(data, dict):
            continue
        if data.get("cards") is not None:
            # A queue file that carries cards must say what it did with the
            # titles; silence is the pre-fix shape and must not read as clean.
            assert data.get("title_policy"), (
                f"{path.name} ships cards without declaring a title policy")
        if data.get("title_policy"):
            declaring.append(path.name)
        offenders += [f"{path.name} {o}" for o in _policy_is_honoured(data, allowed)]
    assert declaring, "no shipped file declares a title policy — this check would be vacuous"
    assert not offenders, (
        "shipped files declare titles omitted and carry them anyway:\n  "
        + "\n  ".join(offenders))


# --------------------------------------------------------------------------
# the card stays identifiable, and route.py keeps fetching
# --------------------------------------------------------------------------


def test_the_card_is_still_identifiable_without_a_title():
    """Dropping the title must not cost the fields a drain actually routes on."""
    card = D.build_queues([_proposal()])["dev-primary"][0]
    assert card["gh"] == "owner/name#4242"
    assert card["repo"] == "owner/name"
    assert card["url"] == "https://github.com/owner/name/issues/4242"
    assert card["domain"] == "subsea"
    assert card["provider"] == "codex"
    assert card["dispatch_status"] == "ready"
    assert card["wip_eligible"] is True
    assert card["routed_by"] == "rule"


def test_build_queues_does_not_mutate_the_proposal():
    """`--detail` and `--json` read the same proposal objects.

    Redacting by `del p["title"]` in place would strip the console output too —
    a silent re-break of #3763 that no queue-file assertion would catch.
    """
    p = _proposal()
    D.build_queues([p])
    assert p["title"] == SENTINEL_TITLE, (
        "build_queues mutated its input; the ephemeral surfaces lose their titles")


def test_route_still_carries_the_title_into_its_proposals():
    """The fix belongs at serialisation, not retrieval.

    Guards against a future "simplification" that removes the title from
    `route.py` because nothing tracked consumes it — which would re-break the
    `--detail`/`--json` surfaces #3767 had just repaired.
    """
    spec = importlib.util.spec_from_file_location("route_notitle", ROUTE_PY)
    R = importlib.util.module_from_spec(spec)
    sys.modules["route_notitle"] = R
    spec.loader.exec_module(R)
    card = R.issue_to_card({"number": 1, "state": "OPEN", "title": SENTINEL_TITLE,
                            "labels": [{"name": "domain:subsea"}]}, "owner/name")
    assert card["title"] == SENTINEL_TITLE, (
        "route.py stopped carrying titles; --detail and --json go blank again")
