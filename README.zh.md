# PUNCHCARD（打孔卡）

> 你的 agent 只能用 80 列说话。

PUNCHCARD 强制 AI agent 的每一个动作**只能**以 80 列打孔卡的形式提交。它是对
1890 年 Hollerith / IBM 029 打孔卡的*复活*，用来解决 2026 年的一个真问题：LLM
agent 的输出是自由文本，事后无法 diff、无法闸门、无法审计。

## 核心思想

打孔卡有**固定的 80 列布局**。agent 的动作被编码进一张卡；列区间之外的内容
**没有位置可放**——它不是"被某条规则拒绝"，而是*在语法上就根本无法解析*。

读取器（reader）绝不 eval / import / 解释。它只切固定的列区间。自由文本因此
没有任何执行路径。没有任何代码路径会去执行 agent 的输出。

## 卡片布局（严格 80 列，1-based）

```
 1-6   卡片类型    ACTION | ASSERT | LEDGER | ABORT  （大写，空格补齐）
 7     分隔符      空格
 8-13  序号        6 位零补齐整数
14     分隔符      空格
15-34  目标        20 列，^[a-z0-9_.-]+$（小写）
35     分隔符      空格
36-55  动词        20 列，^[A-Z][A-Z_]*$
56     分隔符      空格
57-76  值          20 列，按动词注册的正则
77     分隔符      空格
78-79  校验和      2 位大写十六进制 = 第 1-76 列 ord 之和 mod 256
80     续卡位      'C' 表示卡片续接，否则空格
```

动词按卡片类型划分：

| 类型   | 动词                                              | 值正则 |
|--------|---------------------------------------------------|--------|
| ACTION | SET_FIELD, MOVE_FILE, SEND_MSG, RUN_STEP          | `[A-Za-z0-9 ./_-]{1,20}` |
| ASSERT | EQUALS, NOT_EXCEEDS, CONTAINS, MATCHES            | `[A-Za-z0-9 .:%_-]{1,20}` |
| LEDGER | COMMIT, ROLLBACK                                  | `[0-9a-f]{8}` |
| ABORT  | WITH_REASON                                       | `[A-Za-z0-9 ]{1,20}` |

卡组级规则（`reader.read_deck` 强制执行）：

- 序号从 1 开始，每次严格 +1
- 至多一张 ABORT，且若存在必须是最后一张
- 卡组必须包含至少一张 LEDGER
- 续卡位为 `C` 的卡片后面必须还有卡片

## Hollerith 渲染（忠实复刻 IBM 029）

`punchcard.hollerith` 把一张卡渲染成 **12 行 × 80 列** 的 `#`/`.`，使用真实的
zone+digit 编码：

- 数字 `0-9` → 对应数字行打孔
- `A-I` → zone 12 + 数字 1-9
- `J-R` → zone 11 + 数字 1-9
- `S-Z` → zone 0 + 数字 2-9
- 其他字符 → 该列留空，标记为 `?`

## 同一个核心上的两个应用

1. **`punch audit`** — 费用/发票审计卡组：`ASSERT` 卡校验总额、税额与边界；
   `LEDGER` 提交；`punch tally` 打印分类普查。
2. **`punch ops`** — 事故演练手册：`ACTION` 卡驱动一个*模拟*执行器，只打印它
   将要做什么；`ABORT` 中止卡组。不触碰任何真实文件系统。

## 用法

```bash
python eval.py                 # 确定性测试套件 -> "RESULT: 23 passed, 0 failed"
python -m punchcard.cli demo  # 内置演示，真实输出

python -m punchcard.cli encode --type ACTION --seq 1 --target file1 \
    --verb SET_FIELD --value "hello_world"
python -m punchcard.cli read examples/audit.deck
python -m punchcard.cli render examples/audit.deck
python -m punchcard.cli audit examples/audit.deck
python -m punchcard.cli ops examples/ops.deck
```

## 硬性约束

- **仅标准库。** 无第三方包、无网络、无子进程。
- **`reader.py` 与 `columns.py` 中无 `eval`/`exec`/`open`。** 读取器只切列、只校验结构。
- `python eval.py` 确定性执行，10 秒内完成。
- 每个模块导入时无副作用。

## 基于 Kiro 构建

本项目通过 Kiro 的 spec 驱动工作流构建：

- `.kiro/specs/punchcard/requirements.md` — 项目必须做什么
- `.kiro/specs/punchcard/design.md` — 模块布局与编码决策
- `.kiro/specs/punchcard/tasks.md` — 实现任务清单
- `.kiro/steering/*` — 产品 / 技术 / 结构上下文
- `.kiro/hooks/eval-on-write.json` — 每次写文件后运行 `python eval.py`

## 许可证

MIT — 见 [LICENSE](LICENSE)。
