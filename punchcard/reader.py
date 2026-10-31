"""Deck reader: parse + validate a deck. No eval / exec / import / open.

The reader only slices fixed column ranges and checks deck-level rules.
It never executes, imports, or interprets agent output as code.
"""
from . import columns as C


def read_deck(cards):
    """cards: iterable of 80-char strings. Returns {'cards': [...], 'count': N}.
    Raises C.CardError on any card-level or deck-level violation."""
    parsed = [C.validate(raw) for raw in cards]
    if not parsed:
        raise C.CardError("empty deck")
    if parsed[0]["seq"] != 1:
        raise C.CardError("sequence must start at 1")
    for i in range(1, len(parsed)):
        if parsed[i]["seq"] != parsed[i - 1]["seq"] + 1:
            raise C.CardError("sequence gap at card %d" % (i + 1))
    aborts = [p for p in parsed if p["type"] == "ABORT"]
    if len(aborts) > 1:
        raise C.CardError("at most one ABORT card allowed")
    if aborts and aborts[0] is not parsed[-1]:
        raise C.CardError("ABORT must be the last card")
    if not any(p["type"] == "LEDGER" for p in parsed):
        raise C.CardError("deck must contain at least one LEDGER card")
    for i, p in enumerate(parsed):
        if p["continuation"] == "C" and i == len(parsed) - 1:
            raise C.CardError("continuation 'C' on final card with no follower")
    return {"cards": parsed, "count": len(parsed)}
