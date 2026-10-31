"""Hollerith census: count characters in a column range across a deck."""
from collections import Counter


def census(deck_cards, col_start, col_end):
    """Count character occurrences over columns [col_start, col_end) (0-indexed)."""
    c = Counter()
    for card in deck_cards:
        for ch in card[col_start:col_end]:
            c[ch] += 1
    return c


def histogram(counter, top=20):
    if not counter:
        return "(empty)"
    mx = max(counter.values())
    lines = []
    for ch, n in counter.most_common(top):
        bar = "#" * max(1, int(round(n / mx * 40)))
        disp = ch if ch != " " else "·"
        lines.append("%3s %5d %s" % (disp, n, bar))
    return "\n".join(lines)
