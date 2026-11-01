# PUNCHCARD

> Your agent may only speak in 80 columns.

PUNCHCARD forces an AI agent to act **only** by submitting 80-column punched
cards. It is a *Resurrection* of the 1890 Hollerith / IBM 029 punched card,
brought back to solve a 2026 problem: LLM agent output is free-form text that
cannot be diffed, gated, or audited after the fact.

## The core idea

A punched card has **fixed 80-column layout**. An agent's action is encoded into
one card; everything outside the column ranges **has no slot to occupy** — it is
not "rejected by a rule", it is *unparseable by construction*.

The reader never evaluates, imports, or interprets. It only slices fixed column
ranges. Free-form text therefore has no path to execution. No code path ever
runs agent output.

## Card layout (exactly 80 columns, 1-based)

```
 1-6   CARD TYPE     ACTION | ASSERT | LEDGER | ABORT   (uppercase, space-padded)
 7     separator     space
 8-13  SEQUENCE      6-digit zero-padded integer
14     separator     space
15-34  TARGET        20 cols, ^[a-z0-9_.-]+$  (lowercase)
35     separator     space
36-55  VERB          20 cols, ^[A-Z][A-Z_]*$
56     separator     space
57-76  VALUE         20 cols, pattern registered per verb
77     separator     space
78-79  CHECKSUM      2 uppercase hex = sum(ord) over columns 1-76 mod 256
80     CONTINUATION  'C' if the deck continues, else space
```

Verbs by type:

| Type   | Verbs                                             | Value pattern |
|--------|---------------------------------------------------|---------------|
| ACTION | SET_FIELD, MOVE_FILE, SEND_MSG, RUN_STEP          | `[A-Za-z0-9 ./_-]{1,20}` |
| ASSERT | EQUALS, NOT_EXCEEDS, CONTAINS, MATCHES            | `[A-Za-z0-9 .:%_-]{1,20}` |
| LEDGER | COMMIT, ROLLBACK                                  | `[0-9a-f]{8}` |
| ABORT  | WITH_REASON                                       | `[A-Za-z0-9 ]{1,20}` |

Deck-level rules (enforced by `reader.read_deck`):

- sequence numbers start at 1 and increase by exactly 1
- at most one ABORT card, and if present it must be the last card
- the deck must contain at least one LEDGER card
- a card with continuation `C` must be followed by another card

## Hollerith rendering (faithful IBM 029)

`punchcard.hollerith` renders a card as **12 rows × 80 columns** of `#`/`'.'`,
using the real zone+digit encoding:

- digit `0-9` → punch the matching digit row
- `A-I` → zone 12 + digit 1-9
- `J-R` → zone 11 + digit 1-9
- `S-Z` → zone 0 + digit 2-9
- any other character → column rendered empty, marked `?`

## Two applications on the same core

1. **`punch audit`** — an expense/invoice audit deck: `ASSERT` cards check
   totals, tax and bounds; `LEDGER` commits; `punch tally` prints a per-category
   census.
2. **`punch ops`** — an incident runbook: `ACTION` cards drive a *simulated*
   runner that only prints what it would do; `ABORT` halts the deck. Nothing
   touches the real filesystem.

## Usage

```bash
python eval.py                 # deterministic suite -> "RESULT: 23 passed, 0 failed"
python -m punchcard.cli demo  # built-in demo with real output

# encode an action
python -m punchcard.cli encode --type ACTION --seq 1 --target file1 \
    --verb SET_FIELD --value "hello_world"

# validate + inspect a deck (one card per line)
python -m punchcard.cli read examples/audit.deck
python -m punchcard.cli render examples/audit.deck
python -m punchcard.cli audit examples/audit.deck
python -m punchcard.cli ops examples/ops.deck
```

## Constraints (hard)

- **Standard library only.** No third-party packages, no network, no subprocess.
- **No `eval`/`exec`/`open` in `reader.py` or `columns.py`.** The reader only
  slices columns and validates structure.
- `python eval.py` is deterministic and finishes in well under 10 seconds.
- Every module is importable and side-effect free at import time.

## Built with Kiro

This project was built through Kiro's spec-driven workflow:

- `.kiro/specs/punchcard/requirements.md` — what the project must do
- `.kiro/specs/punchcard/design.md` — module layout and encoding decisions
- `.kiro/specs/punchcard/tasks.md` — implementation task list
- `.kiro/steering/*` — product / tech / structure context
- `.kiro/hooks/eval-on-write.json` — runs `python eval.py` after every file write

## License

MIT — see [LICENSE](LICENSE).

---

## 💝 赞助 / 打赏

如果这个项目对你有帮助，欢迎通过 **爱发电** 请我喝杯咖啡 ☕  
👉 https://afdian.com/a/Zhiyilang

> GitHub Sponsors 在中国大陆暂不支持个人账号，赞助统一走爱发电。

---
## 📚 我的实战课程
**《影刀RPA到AI Agent工程师：大专生的实战转型笔记》** —— 5 课可直接抄的作业（含可复制代码模板 + 真实接单复盘）。
在 **小报童 / 小红书** 搜索「支一郎」即可购买；完整大纲见 [GitHub Pages](https://Zhiyilang.github.io/#course)。
