"""Faithful IBM 029 zone+digit Hollerith encoding and card rendering.

Rows top-to-bottom: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9  (12 rows total).
  - digit 0-9      -> punch the matching digit row
  - A-I            -> zone 12 + digit 1-9
  - J-R            -> zone 11 + digit 1-9
  - S-Z            -> zone 0  + digit 2-9
  - any other char -> column rendered empty, flagged '?'
"""


ROWS = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


def _rows_for_char(ch):
    if ch.isdigit():
        return [ROWS[2 + int(ch)]]
    if "A" <= ch <= "I":
        d = ord(ch) - ord("A") + 1
        return ["12", ROWS[2 + d]]
    if "J" <= ch <= "R":
        d = ord(ch) - ord("J") + 1
        return ["11", ROWS[2 + d]]
    if "S" <= ch <= "Z":
        d = ord(ch) - ord("S") + 2
        return ["0", ROWS[2 + d]]
    return []


def render(card):
    """Render an 80-char card as (list_of_12_strings, flagged_columns).
    punch = '#', blank = '.', unknown column marked '?' in the top row."""
    grid = [["." for _ in range(80)] for _ in range(12)]
    flagged = []
    for col, ch in enumerate(card):
        rows = _rows_for_char(ch)
        if not rows:
            grid[0][col] = "?"
            flagged.append(col)
            continue
        for r in rows:
            grid[ROWS.index(r)][col] = "#"
    return ["".join(row) for row in grid], flagged
