# Structure — PUNCHCARD

## Module layout
```
punchcard/
  __init__.py     package marker
  columns.py      column constants + single-card validation (no eval/import/open)
  encoder.py      the puncher: action -> 80-char card
  reader.py       deck parsing + deck-level rules (no eval/import/open)
  hollerith.py    IBM 029 zone+digit encoding + 12x80 render
  ledger.py       append-only tray + JSONL sidecar
  tally.py        per-range character census + histogram
  apps.py         run_audit / run_ops (consume only parsed dicts)
  cli.py          argparse entrypoint
eval.py           deterministic assertion suite
examples/         sample decks (one card per line)
```

## Naming conventions
- Card fields are UPPERCASE constants; modules are lowercase.
- Validators raise `columns.CardError` on any violation.
- Public functions are verbs: `validate`, `encode`, `read_deck`, `render`,
  `census`, `run_audit`, `run_ops`.
