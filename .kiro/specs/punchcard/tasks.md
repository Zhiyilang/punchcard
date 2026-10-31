# Tasks — PUNCHCARD

- [x] Define 80-column layout constants in `columns.py`
- [x] Implement `validate()` with structural + regex + checksum checks
- [x] Implement `encoder.encode()` (the puncher)
- [x] Implement `reader.read_deck()` deck-level rules
- [x] Implement `hollerith.render()` faithful IBM 029 encoding (12x80)
- [x] Implement `ledger.Tray` append-only tray + JSONL sidecar
- [x] Implement `tally.census()` + `histogram()`
- [x] Implement `apps.run_audit()` expense/invoice checks
- [x] Implement `apps.run_ops()` incident runbook simulator
- [x] Implement `cli.main()` with encode/read/render/tally/audit/ops/demo
- [x] Write `eval.py` deterministic suite (23 assertions)
- [x] Add MIT LICENSE, README.md, README.zh.md
- [x] Add `.github/workflows/ci.yml` (Python 3.9 / 3.11 / 3.12)
- [x] Add `.kiro/` specs, steering, and eval-on-write hook
- [x] Add `examples/audit.deck` and `examples/ops.deck`
- [ ] (user) Register kiro.dev + Devpost, submit during the window
- [ ] (user) Record a <=3 minute demo video
- [ ] (user) Publish a blog post (Bonus Blog Prize) + `#Kiroween26` social post
