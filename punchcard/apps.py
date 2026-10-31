"""Two applications built on the same punched-card core.

Neither app imports, evals, or executes agent output. They only read the
structured fields that the reader already parsed.
"""
from .reader import read_deck


def run_audit(cards):
    """Expense/invoice audit.

    Card semantics:
      ACTION SET_FIELD <target> <value>  -> store field (target lowercased)
      ASSERT <VERB> <key>:<expected>     -> check a computed/field value
      LEDGER COMMIT <hash>               -> required by deck rules

    Computed values:
      total = sum of fields whose target starts with 'line'
      tax   = round(total * 0.13, 2)
    """
    deck = read_deck(cards)
    fields = {}
    assertions = []
    for p in deck["cards"]:
        if p["type"] == "ACTION" and p["verb"] == "SET_FIELD":
            fields[p["target"]] = p["value"]
        elif p["type"] == "ASSERT":
            assertions.append(p)
    line_items = [float(v) for k, v in fields.items() if k.startswith("line")]
    total = round(sum(line_items), 2)
    tax = round(total * 0.13, 2)
    report = {"fields": fields, "total": total, "tax": tax, "checks": []}
    for a in assertions:
        key, expected = a["value"].split(":")
        expected = float(expected)
        if key == "tax":
            actual = tax
        elif key == "total":
            actual = total
        else:
            actual = float(fields.get(key, "nan"))
        if a["verb"] == "EQUALS":
            ok = abs(actual - expected) < 0.01
        elif a["verb"] == "NOT_EXCEEDS":
            ok = actual <= expected
        elif a["verb"] == "CONTAINS":
            ok = str(expected) in str(actual)
        elif a["verb"] == "MATCHES":
            ok = str(actual) == str(expected)
        else:
            ok = False
        report["checks"].append({"verb": a["verb"], "key": key, "ok": ok})
    report["passed"] = all(c["ok"] for c in report["checks"])
    return report


def run_ops(cards):
    """Incident runbook simulator. Prints planned actions; halts on ABORT.

    No filesystem / subprocess / network access. Returns emitted lines.
    """
    deck = read_deck(cards)
    out = []
    for p in deck["cards"]:
        if p["type"] == "ACTION":
            out.append("WOULD %s -> %s (target=%s)" % (p["verb"], p["value"], p["target"]))
        elif p["type"] == "ABORT":
            out.append("ABORT: %s" % p["value"])
            break
    return out
