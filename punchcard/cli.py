"""argparse CLI: punch encode / read / render / tally / audit / ops / demo."""
import argparse
import sys

from . import columns, encoder, reader, hollerith, tally, apps


def _load_cards(path):
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    return [ln.rstrip("\n") for ln in text.splitlines() if ln.strip()]


def _demo_cards():
    return [
        encoder.encode("ACTION", 1, "line1", "SET_FIELD", "100.00"),
        encoder.encode("ACTION", 2, "line2", "SET_FIELD", "50.00"),
        encoder.encode("ASSERT", 3, "k", "EQUALS", "total:150.00"),
        encoder.encode("ASSERT", 4, "k", "NOT_EXCEEDS", "tax:20.00"),
        encoder.encode("LEDGER", 5, "h", "COMMIT", "abcdef01"),
        encoder.encode("ACTION", 6, "s", "RUN_STEP", "boot_system"),
        encoder.encode("ACTION", 7, "s", "SEND_MSG", "all_clear"),
        encoder.encode("LEDGER", 8, "h", "COMMIT", "deadbeef"),
        encoder.encode("ABORT", 9, "r", "WITH_REASON", "drill done"),
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="punch", description="80-column punched-card agent gate")
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("encode", help="encode a structured action into one card")
    e.add_argument("--type", required=True, choices=columns.CARD_TYPES)
    e.add_argument("--seq", required=True)
    e.add_argument("--target", required=True)
    e.add_argument("--verb", required=True)
    e.add_argument("--value", required=True)
    e.add_argument("--cont", action="store_true", help="set continuation flag")

    r = sub.add_parser("read", help="validate a deck file (one card per line)")
    r.add_argument("path")

    rn = sub.add_parser("render", help="render cards as 12x80 Hollerith grids")
    rn.add_argument("path")

    t = sub.add_parser("tally", help="Hollerith census over a column range")
    t.add_argument("path")
    t.add_argument("--start", type=int, required=True)
    t.add_argument("--end", type=int, required=True)

    a = sub.add_parser("audit", help="run the expense/invoice audit app")
    a.add_argument("path")

    o = sub.add_parser("ops", help="run the incident runbook simulator")
    o.add_argument("path")

    sub.add_parser("demo", help="run a built-in demo with real output")

    args = ap.parse_args(argv)

    if args.cmd == "encode":
        card = encoder.encode(args.type, args.seq, args.target, args.verb,
                              args.value, "C" if args.cont else " ")
        print(card)
        return 0

    if args.cmd == "read":
        cards = _load_cards(args.path)
        deck = reader.read_deck(cards)
        for p in deck["cards"]:
            print("%2d %-6s %-20s %-20s %s" % (p["seq"], p["type"], p["target"], p["verb"], p["value"]))
        print("deck OK: %d cards" % deck["count"])
        return 0

    if args.cmd == "render":
        for card in _load_cards(args.path):
            grid, flagged = hollerith.render(card)
            print("\n".join(grid))
            if flagged:
                print("flagged columns: %s" % flagged)
        return 0

    if args.cmd == "tally":
        cards = _load_cards(args.path)
        cnt = tally.census(cards, args.start, args.end)
        print(tally.histogram(cnt))
        return 0

    if args.cmd == "audit":
        rep = apps.run_audit(_load_cards(args.path))
        print("total=%s tax=%s passed=%s" % (rep["total"], rep["tax"], rep["passed"]))
        for c in rep["checks"]:
            print("  %-12s %-6s %s" % (c["verb"], c["key"], "OK" if c["ok"] else "FAIL"))
        return 0 if rep["passed"] else 1

    if args.cmd == "ops":
        for line in apps.run_ops(_load_cards(args.path)):
            print(line)
        return 0

    if args.cmd == "demo":
        cards = _demo_cards()
        print("=== encoded deck (%d cards) ===" % len(cards))
        for c in cards:
            print(c)
        print("\n=== render of card #1 ===")
        grid, flagged = hollerith.render(cards[0])
        print("\n".join(grid))
        print("\n=== audit report ===")
        rep = apps.run_audit(cards)
        print("total=%s tax=%s passed=%s" % (rep["total"], rep["tax"], rep["passed"]))
        print("\n=== ops runbook ===")
        for line in apps.run_ops(cards):
            print(line)
        return 0


if __name__ == "__main__":
    sys.exit(main())
