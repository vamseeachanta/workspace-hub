# WRK-1120 Plan (Route A — Claude)

## Approach
Add atomic ID reservation to `next-id.sh` using bash `noclobber` (`set -C`).

## Steps
1. After computing NEXT_ID, enter retry loop (max 5 attempts).
2. `set -C; echo "" > pending/WRK-${NEXT_ID}.md` — fails if file exists (EEXIST).
3. On success: `set +C`, print ID, exit 0.
4. On failure: increment NEXT_ID, retry.
5. After 5 failures: exit 1 with clear error.

## Test
`scripts/work-queue/tests/test-next-id-collision.sh` — two concurrent calls → different IDs.
