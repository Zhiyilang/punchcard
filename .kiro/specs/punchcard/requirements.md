# Requirements — PUNCHCARD

## Goal
Force an AI agent to act ONLY by submitting 80-column punched cards, so its
actions become diffable, gateable, and auditable after the fact.

## Functional requirements
1. Encode a structured action (type, sequence, target, verb, value) into exactly
   one 80-character card with a checksum over columns 1-76.
2. Validate a single card: structural columns, regex-checked fields, checksum.
3. Validate a deck: strict sequence numbering, at-most-one trailing ABORT,
   at-least-one LEDGER, continuation consistency.
4. Render a card using faithful IBM 029 Hollerith zone+digit encoding (12x80).
5. Tally a "Hollerith census": count characters per column range (ASCII histogram).
6. Provide two applications on the same core: an expense/invoice **audit** and an
   incident-runbook **ops** simulator.
7. A deterministic eval suite printing `RESULT: N passed, 0 failed`.

## Non-functional requirements
- Python 3.9+ standard library only. Zero third-party dependencies.
- No network, no subprocess, no `eval`/`exec`/`open` in reader/columns.
- Importable and side-effect free at import time.
- `python eval.py` finishes in under 10 seconds, deterministically.

## Out of scope
- Real filesystem mutation (ops only simulates).
- Any ML / LLM integration (the point is to constrain one).
- Payment, networking, or persistence beyond an optional append-only tray.
