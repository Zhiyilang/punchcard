# Tech Context — PUNCHCARD

## Stack
- Python 3.9+ standard library only. No third-party packages.
- No network, no subprocess, no `eval`/`exec`/`open` in `reader.py`/`columns.py`.

## Determinism rules
- `python eval.py` must be deterministic and finish in < 10s.
- Checksum = `sum(ord(c) for c in card[0:76]) % 256`, 2 uppercase hex chars.
- All modules importable with no side effects.

## Quality gate
- Every commit must keep `python eval.py` green (`RESULT: 23 passed, 0 failed`).
- The `eval-on-write` hook enforces this locally after each file change.
