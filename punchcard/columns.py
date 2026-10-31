"""Column map + single-card validation for 80-column punched cards.

Hard constraint: this module contains NO eval / exec / __import__ / open.
It only validates structure and returns a parsed dict. It never executes
anything the agent wrote.
"""
import re

CARD_LEN = 80

CARD_TYPES = ("ACTION", "ASSERT", "LEDGER", "ABORT")

# verb -> value regex (per the spec; value fields are space-padded to 20)
VERB_PATTERNS = {
    "SET_FIELD": r"[A-Za-z0-9 ./_-]{1,20}",
    "MOVE_FILE": r"[A-Za-z0-9 ./_-]{1,20}",
    "SEND_MSG": r"[A-Za-z0-9 ./_-]{1,20}",
    "RUN_STEP": r"[A-Za-z0-9 ./_-]{1,20}",
    "EQUALS": r"[A-Za-z0-9 .:%_-]{1,20}",
    "NOT_EXCEEDS": r"[A-Za-z0-9 .:%_-]{1,20}",
    "CONTAINS": r"[A-Za-z0-9 .:%_-]{1,20}",
    "MATCHES": r"[A-Za-z0-9 .:%_-]{1,20}",
    "COMMIT": r"[0-9a-f]{8}",
    "ROLLBACK": r"[0-9a-f]{8}",
    "WITH_REASON": r"[A-Za-z0-9 ]{1,20}",
}

# card type -> allowed verbs
TYPE_VERBS = {
    "ACTION": {"SET_FIELD", "MOVE_FILE", "SEND_MSG", "RUN_STEP"},
    "ASSERT": {"EQUALS", "NOT_EXCEEDS", "CONTAINS", "MATCHES"},
    "LEDGER": {"COMMIT", "ROLLBACK"},
    "ABORT": {"WITH_REASON"},
}

# 0-indexed column slices
TYPE = slice(0, 6)
SEP1 = 6
SEQ = slice(7, 13)
SEP2 = 13
TARGET = slice(14, 34)
SEP3 = 34
VERB = slice(35, 55)
SEP4 = 55
VALUE = slice(56, 76)
SEP5 = 76
CHECKSUM = slice(77, 79)
CONT = 79

_TARGET_RE = re.compile(r"^[a-z0-9_.-]+$")
_VERB_RE = re.compile(r"^[A-Z][A-Z_]*$")


class CardError(ValueError):
    """Raised on any card-level or deck-level violation."""


def compute_checksum(card):
    """2-char uppercase hex of sum(ord) over the first 76 columns."""
    return "%02X" % (sum(ord(c) for c in card[0:76]) % 256)


def validate(card):
    """Validate one 80-char card. Raise CardError on any violation.
    Returns a dict of parsed fields (no execution, no side effects)."""
    if not isinstance(card, str):
        raise CardError("card must be a string")
    if len(card) != CARD_LEN:
        raise CardError("card length %d != %d" % (len(card), CARD_LEN))
    for sep in (SEP1, SEP2, SEP3, SEP4, SEP5):
        if card[sep] != " ":
            raise CardError("column %d must be a space separator" % (sep + 1))
    ctype = card[TYPE].strip()
    if ctype not in CARD_TYPES:
        raise CardError("unknown card type %r" % ctype)
    seq_s = card[SEQ]
    if not seq_s.isdigit() or len(seq_s) != 6:
        raise CardError("sequence must be 6 digits")
    target = card[TARGET].strip()
    if not _TARGET_RE.match(target):
        raise CardError("invalid target %r" % target)
    verb = card[VERB].strip()
    if not _VERB_RE.match(verb):
        raise CardError("invalid verb %r" % verb)
    if verb not in TYPE_VERBS.get(ctype, set()):
        raise CardError("verb %r not allowed for type %s" % (verb, ctype))
    value = card[VALUE].strip()
    pat = VERB_PATTERNS[verb]
    if not re.match("^" + pat + "$", value):
        raise CardError("value %r violates %s for verb %s" % (value, pat, verb))
    if card[CHECKSUM] != compute_checksum(card):
        raise CardError("checksum mismatch")
    cont = card[CONT]
    if cont not in ("C", " "):
        raise CardError("continuation must be 'C' or space")
    return {
        "type": ctype,
        "seq": int(seq_s),
        "target": target,
        "verb": verb,
        "value": value,
        "continuation": cont,
    }
