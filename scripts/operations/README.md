# Operations Scripts

> Infrastructure, compliance, monitoring, and system maintenance.

Contains audit tools, compliance checking, connection management,
system monitoring, and maintenance utilities.

## Failure alert journals

`update_alerts.py` supplies a local pending/acknowledged view for notification
JSONL, as scoped in issue #1679. `scripts/notify.sh` already writes events;
this consumer does not change that producer. No desktop, email, webhook,
provider, startup or scheduler integration is installed. Active delivery and
automatic startup display remain open.

Both journal paths must be explicit and distinct. The notification journal must
exist. A missing acknowledgement journal means no acknowledgements; only `ack`
creates it, and its parent directory must already exist. Run from the repository
root, replacing the relative example paths with authorized local journals:

```sh
python scripts/operations/update_alerts.py \
  --notifications notifications.jsonl --acknowledgements acknowledgements.jsonl pending
python scripts/operations/update_alerts.py \
  --notifications notifications.jsonl --acknowledgements acknowledgements.jsonl \
  ack sha256:ALERT_DIGEST --at 2026-01-02T00:00:00Z
```

The timestamp above is a fixed synthetic example. Omitting `--at` records the
current UTC time. The ID must be copied from the pending view. Only a known
failure can be acknowledged. Replaying an acknowledgement does not append
another row. The source notification journal is never opened for writing, and
existing acknowledgement bytes are preserved, including a missing final newline.
Callers must serialize writers and keep paths stable while commands run; no
shared lock, file-rotation coordination or transactional snapshot is supplied.

Each notification is a JSON object with a nonempty string `job`, `status` equal
to `pass` or `fail`, and `ts` in UTC `YYYY-MM-DDTHH:MM:SSZ` form. Optional `source`,
`tool`, `failure`, `rollback` and `details` fields must be strings when supplied.
Other JSON fields are retained. All supplied fields are returned unchanged in
`pending[].event`; missing rollback or failure detail is not invented. This
accepts the existing notification writer's fields. Successful events are excluded
and do not clear earlier failures.

Identity is `sha256:` followed by the SHA-256 digest of UTF-8 JSON with sorted
object keys, compact separators and unescaped Unicode, without a trailing newline.
The entire object participates. Reordered keys and repeated ingestion have the
same identity; any changed field, including the timestamp, creates another
identity. Identical records cannot be distinguished as separate occurrences.
The pending view keeps first-seen order. Duplicate keys, non-finite numbers,
invalid UTF-8, blank rows and invalid record shapes are malformed.

For an independent synthetic identity example, `sha256sum` applied to exactly
these compact bytes (without a trailing newline) yields
`f7a68d7feab5d1e22ad5f28b5fcc396df4b04f5048ace6afa08e434a92e65696`:

```json
{"details":"maintainer attention required","failure":"synthetic update rejected","job":"update-check","rollback":"previous configuration restored","source":"maintenance","status":"fail","tool":"configured-tool","ts":"2026-01-01T00:00:00Z"}
```

Acknowledgements are JSONL objects containing exactly `id` and `acknowledged_at`,
with the latter in the same UTC timestamp form. Valid replayed rows are harmless;
unrelated valid IDs do not clear other alerts. Neither journal is deleted or
compacted. A local acknowledgement is a record of operator intent, not proof of
identity or permission.

`pending` emits a JSON object with `pending`, `diagnostics` and `diagnostic_count`.
Malformed rows remain explicit while valid rows remain visible. The local output
contract caps diagnostics at twenty entries to bound diagnostic output, counting
all malformed rows in `diagnostic_count`. Each diagnostic contains only the
journal role, line number (starting at one) and fixed reason; no raw record or
filesystem path is included. Alert details themselves are supplied content, so
only authorized journals should be displayed. `ack` refuses to append while
either journal contains malformed rows. It emits `acknowledged` and `appended`
on success. Records and acknowledgements are read afresh on each invocation.

The CLI exit contract uses zero for success, one for malformed records or a
journal/acknowledgement error, and two for invalid command arguments. I/O errors
use a fixed diagnostic without a path or exception payload. Supplied control
characters are JSON-escaped in output. The module uses only the Python standard
library; its tests use pytest with synthetic temporary journals and no network:

```sh
uv run --no-project --with pytest python -m pytest \
  tests/operations/test_update_alerts.py -q -rA -p no:cacheprovider
```
