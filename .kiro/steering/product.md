# Product Context — PUNCHCARD

## What this is
PUNCHCARD is a resurrection of the 1890 Hollerith / IBM 80-column punched card,
repurposed to solve a 2026 problem: LLM agent output is free-form text that
cannot be diffed, gated, or audited after the fact. By forcing every agent action
through a fixed 80-column layout, actions become machine-checkable and replayable.

## Audience
- Hackathon judges (Kiroween 2026, Resurrection category)
- Security / agent-platform engineers who need an auditable action medium

## Constraints
- Must run with `git clone && python eval.py` — zero dependencies, zero network.
- The reader must never execute agent output.

## Non-goals
- Not an LLM wrapper. Not a payment system. Not a real execution engine (ops only
  simulates; audit only checks).
