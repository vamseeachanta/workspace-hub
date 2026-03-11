# WRK-1120 Plan: Atomic ID Reservation in next-id.sh

## Approach
Use bash `set -C` (noclobber) to atomically create `pending/WRK-NNN.md` sentinel
before returning the ID. Retry up to 5 times on collision.

## Steps
1. After computing NEXT_ID, set `set -C` (noclobber on).
2. Attempt: `echo "" > "${QUEUE_DIR}/pending/WRK-${NEXT_ID}.md"` — fails if exists.
3. On success: `set +C`, print ID, exit 0.
4. On EEXIST (collision): increment NEXT_ID, retry.
5. After 5 failures: `set +C`, exit 1 with message.

## Test
`scripts/work-queue/tests/test-next-id-collision.sh`:
- Spawn two concurrent `next-id.sh` calls via `&`
- Assert IDs are different
- Assert both sentinel files exist
- Clean up sentinels

## Files Changed
- `scripts/work-queue/next-id.sh` (implementation)
- `scripts/work-queue/tests/test-next-id-collision.sh` (new test)
