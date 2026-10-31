"""Deterministic assertion suite. Must print 'RESULT: N passed, 0 failed'."""
import sys

from punchcard import columns, encoder, reader, hollerith, tally, apps

passed = 0


def check(cond, msg):
    global passed
    if cond:
        passed += 1
    else:
        print("FAILED:", msg)
        sys.exit(1)


# 1. encode + validate roundtrip
c1 = encoder.encode("ACTION", 1, "file1", "SET_FIELD", "value_here")
check(len(c1) == 80, "encode length 80")
parsed = columns.validate(c1)
check(parsed["type"] == "ACTION" and parsed["seq"] == 1, "parse roundtrip type/seq")
check(parsed["target"] == "file1" and parsed["verb"] == "SET_FIELD", "parse fields")

# 2. checksum tamper detection
bad = c1[:77] + ("FF" if c1[77:79] != "FF" else "00") + c1[79]
try:
    columns.validate(bad)
    check(False, "checksum should reject tampering")
except columns.CardError:
    passed += 1

# 3. bad type / verb / target
for bad_args in [
    ("NOPE", 1, "x", "SET_FIELD", "v"),
    ("ACTION", 1, "x", "EQUALS", "v"),
    ("ACTION", 1, "Bad Target", "SET_FIELD", "v"),
]:
    try:
        encoder.encode(*bad_args)
        check(False, "should reject %r" % (bad_args,))
    except columns.CardError:
        passed += 1

# 4. deck rules
good = [encoder.encode("ACTION", i, "t", "SET_FIELD", "v") for i in (1, 2)]
good.append(encoder.encode("LEDGER", 3, "h", "COMMIT", "abcdef01"))
check(reader.read_deck(good)["count"] == 3, "valid deck count")

gap = list(good)
gap.insert(1, encoder.encode("ACTION", 5, "t", "SET_FIELD", "v"))
try:
    reader.read_deck(gap)
    check(False, "sequence gap should fail")
except columns.CardError:
    passed += 1

dbl = [encoder.encode("ACTION", 1, "t", "SET_FIELD", "v"),
       encoder.encode("ABORT", 2, "r", "WITH_REASON", "x"),
       encoder.encode("ABORT", 3, "r", "WITH_REASON", "y")]
try:
    reader.read_deck(dbl)
    check(False, "two aborts (not last) should fail")
except columns.CardError:
    passed += 1

abl = [encoder.encode("ABORT", 1, "r", "WITH_REASON", "x"),
       encoder.encode("LEDGER", 2, "h", "COMMIT", "abcdef01")]
try:
    reader.read_deck(abl)
    check(False, "abort not last should fail")
except columns.CardError:
    passed += 1

try:
    reader.read_deck([encoder.encode("ACTION", 1, "t", "SET_FIELD", "v")])
    check(False, "missing ledger should fail")
except columns.CardError:
    passed += 1

# 5. Hollerith render
grid, flagged = hollerith.render(c1)
check(len(grid) == 12 and all(len(r) == 80 for r in grid), "render 12x80")

grid_a, fl_a = hollerith.render("A" + " " * 79)
check(grid_a[0][0] == "#" and grid_a[3][0] == "#", "A punches zone12 + digit1")
check(0 not in fl_a, "A column not flagged")

grid_q, fl_q = hollerith.render("@" + " " * 79)
check(0 in fl_q, "unknown char column flagged")

# 6. tally census
tdeck = [encoder.encode("ACTION", 1, "aaaa", "SET_FIELD", "v"),
         encoder.encode("ACTION", 2, "aaaa", "SET_FIELD", "v")]
cnt = tally.census(tdeck, 14, 34)
check(cnt["a"] == 8, "census counts target 'a'")

# 7. audit app
audit_deck = [
    encoder.encode("ACTION", 1, "line1", "SET_FIELD", "100.00"),
    encoder.encode("ACTION", 2, "line2", "SET_FIELD", "50.00"),
    encoder.encode("ASSERT", 3, "k", "EQUALS", "total:150.00"),
    encoder.encode("ASSERT", 4, "k", "NOT_EXCEEDS", "tax:20.00"),
    encoder.encode("LEDGER", 5, "h", "COMMIT", "abcdef01"),
]
rep = apps.run_audit(audit_deck)
check(rep["total"] == 150.0 and rep["tax"] == 19.5, "audit totals")
check(rep["passed"] is True, "audit passes")

audit_bad = list(audit_deck)
audit_bad[2] = encoder.encode("ASSERT", 3, "k", "EQUALS", "total:999.00")
check(apps.run_audit(audit_bad)["passed"] is False, "audit detects failure")

# 8. ops app halts at abort
ops_deck = [
    encoder.encode("ACTION", 1, "s", "RUN_STEP", "boot"),
    encoder.encode("ACTION", 2, "s", "SEND_MSG", "ok"),
    encoder.encode("LEDGER", 3, "h", "COMMIT", "deadbeef"),
    encoder.encode("ABORT", 4, "r", "WITH_REASON", "done"),
]
out = apps.run_ops(ops_deck)
check(len(out) == 3 and out[-1].startswith("ABORT"), "ops halts at abort")

# 9. continuation rule
cont_deck = [encoder.encode("ACTION", 1, "t", "SET_FIELD", "v", continuation="C"),
             encoder.encode("LEDGER", 2, "h", "COMMIT", "abcdef01")]
check(reader.read_deck(cont_deck)["count"] == 2, "continuation followed ok")
try:
    reader.read_deck([encoder.encode("ACTION", 1, "t", "SET_FIELD", "v", continuation="C")])
    check(False, "continuation on last should fail")
except columns.CardError:
    passed += 1

print("RESULT: %d passed, 0 failed" % passed)
