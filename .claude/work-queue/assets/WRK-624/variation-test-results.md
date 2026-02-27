# Variation Test Results: WRK-624

## Test 1: Missing status
- **Input**: WRK-X with no status field.
- **Expected**: `validate-queue-state.sh` fails; `migrate-queue.py` adds status based on folder.
- **Result**: PASS

## Test 2: Mismatched folder
- **Input**: WRK-Y in `pending/` with `status: done`.
- **Expected**: `validate-queue-state.sh` fails; `migrate-queue.py` moves to `done/` (or updates status).
- **Result**: PASS

## Test 3: Legacy status
- **Input**: `status: complete`.
- **Expected**: `migrate-queue.py` converts to `done`.
- **Result**: PASS
