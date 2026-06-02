from src.deckhand.ratelimit import decide


def policy(rate_limits=None, scope_rate_limits=None):
    scope = {
        "sensitivity": "private",
        "repositories": ["owner/acma"],
        "operators": ["tg-100"],
    }
    if scope_rate_limits is not None:
        scope["rate_limits"] = scope_rate_limits
    return {
        "policy": {
            "rate_limits": rate_limits
            or {
                "per_operator_writes_per_hour": 2,
                "per_scope_writes_per_hour": 3,
                "duplicate_request_window_seconds": 10,
            }
        },
        "scopes": {"scopes": {"acma": scope}},
    }


def test_n_plus_one_operator_write_denied(tmp_path):
    store = tmp_path / "store"
    config = policy(rate_limits={"per_operator_writes_per_hour": 2})

    assert decide("tg-100", "acma", "write", "one", policy=config, store_dir=store, clock="2026-06-01T12:00:00Z")[0]
    assert decide("tg-100", "acma", "write", "two", policy=config, store_dir=store, clock="2026-06-01T12:10:00Z")[0]
    allowed, reason = decide(
        "tg-100",
        "acma",
        "write",
        "three",
        policy=config,
        store_dir=store,
        clock="2026-06-01T12:20:00Z",
    )

    assert allowed is False
    assert reason == "rate limit exceeded: operator writes per hour"


def test_per_scope_cap_denied_with_scope_override(tmp_path):
    store = tmp_path / "store"
    config = policy(
        rate_limits={"per_operator_writes_per_hour": 10, "per_scope_writes_per_hour": 10},
        scope_rate_limits={"per_scope_writes_per_hour": 1},
    )

    assert decide("tg-100", "acma", "write", "one", policy=config, store_dir=store, clock="2026-06-01T12:00:00Z")[0]
    allowed, reason = decide(
        "tg-200",
        "acma",
        "write",
        "two",
        policy=config,
        store_dir=store,
        clock="2026-06-01T12:01:00Z",
    )

    assert allowed is False
    assert reason == "rate limit exceeded: scope writes per hour"


def test_duplicate_within_window_denied(tmp_path):
    store = tmp_path / "store"
    config = policy(rate_limits={"duplicate_request_window_seconds": 10})

    assert decide("tg-100", "acma", "write", "same", policy=config, store_dir=store, clock="2026-06-01T12:00:00Z")[0]
    allowed, reason = decide(
        "tg-100",
        "acma",
        "write",
        "same",
        policy=config,
        store_dir=store,
        clock="2026-06-01T12:00:09Z",
    )

    assert allowed is False
    assert reason == "duplicate request suppressed"


def test_window_expiry_allows_again(tmp_path):
    store = tmp_path / "store"
    config = policy(rate_limits={"per_operator_writes_per_hour": 1, "duplicate_request_window_seconds": 10})

    assert decide("tg-100", "acma", "write", "same", policy=config, store_dir=store, clock="2026-06-01T12:00:00Z")[0]
    allowed, reason = decide(
        "tg-100",
        "acma",
        "write",
        "same",
        policy=config,
        store_dir=store,
        clock="2026-06-01T13:00:01Z",
    )

    assert allowed is True
    assert reason == "rate limit ok"


def test_unwritable_store_dir_denies_fail_closed(tmp_path):
    store_file = tmp_path / "not-a-directory"
    store_file.write_text("occupied", encoding="utf-8")

    allowed, reason = decide(
        "tg-100",
        "acma",
        "write",
        "one",
        policy=policy(),
        store_dir=store_file,
        clock="2026-06-01T12:00:00Z",
    )

    assert allowed is False
    assert reason == "rate-limit store error"
