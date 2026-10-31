"""The puncher: encode a structured action into one 80-char card."""
import re
from . import columns as C


def _pad(s, n):
    s = str(s).strip()
    if len(s) > n:
        raise C.CardError("field %r too long (>%d)" % (s, n))
    return s + " " * (n - len(s))


def encode(type_, seq, target, verb, value, continuation=" "):
    """Build a valid 80-column card string. Raise CardError on bad input."""
    if type_ not in C.CARD_TYPES:
        raise C.CardError("bad card type %r" % type_)
    if verb not in C.TYPE_VERBS.get(type_, set()):
        raise C.CardError("verb %r not allowed for %s" % (verb, type_))
    seq_i = int(seq)
    seq_s = "%06d" % seq_i
    if len(seq_s) != 6:
        raise C.CardError("seq out of range")
    target_s = _pad(target, 20)
    if not C._TARGET_RE.match(target.strip()):
        raise C.CardError("bad target %r" % target)
    verb_s = _pad(verb, 20)
    if not C._VERB_RE.match(verb.strip()):
        raise C.CardError("bad verb %r" % verb)
    value_s = _pad(value, 20)
    pat = C.VERB_PATTERNS[verb]
    if not re.match("^" + pat + "$", value.strip()):
        raise C.CardError("value %r violates %s" % (value, pat))
    cont = "C" if continuation == "C" else " "
    body = (
        type_.ljust(6) + " "
        + seq_s + " "
        + target_s + " "
        + verb_s + " "
        + value_s + " "
    )
    cs = C.compute_checksum(body)
    return body + cs + cont
