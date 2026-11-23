from scripts.ecosystem_sync.models import Signal


def test_signal_dedupe_key_release():
    s = Signal(
        repo="digitalmodel",
        kind="release",
        title="[sync] digitalmodel released v2.1.3",
        body="body here",
        dedupe_key="release:digitalmodel:v2.1.3",
        payload={"tag": "v2.1.3"},
    )
    assert s.dedupe_key == "release:digitalmodel:v2.1.3"
    assert s.kind == "release"


def test_signal_requires_all_fields():
    import pytest
    with pytest.raises(TypeError):
        Signal(repo="x")  # missing required fields
