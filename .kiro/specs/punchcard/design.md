# Design — PUNCHCARD

## Why punched cards?
An 80-column card is a *fixed-width, non-ambiguous* medium. A free-form LLM
output is the opposite. By forcing every agent action through fixed column
ranges, anything outside those ranges has no slot to occupy. The reader does not
need a blacklist of "dangerous strings" — dangerous strings are simply
unparseable by construction.

## Module layout
- `columns.py` — column constants + single-card validation. No eval/import/open.
- `encoder.py` — the "puncher": structured action -> 80-char card.
- `reader.py` — deck parsing + deck-level rules. No eval/import/open.
- `hollerith.py` — IBM 029 zone+digit encoding + 12x80 render.
- `ledger.py` — append-only tray (raw lines + JSONL sidecar).
- `tally.py` — per-range character census + histogram.
- `apps.py` — `audit` (expense checks) and `ops` (runbook simulator).
- `cli.py` — argparse entrypoint.

## Encoding decisions
- Checksum = `sum(ord(c) for c in card[0:76]) % 256`, printed as 2 uppercase hex.
  Covers everything except the final separator, checksum, and continuation flag.
- Values are space-padded to 20 columns; validators strip before regex match, so
  padding never affects validity.
- Verbs are scoped per card type (e.g. COMMIT/ROLLBACK only on LEDGER).

## Safety boundary
The reader is the load-bearing invariant: it only slices fixed ranges and never
executes. `apps.py` consumes only the already-parsed dict. No agent-controlled
string is ever passed to eval/exec/subprocess.
