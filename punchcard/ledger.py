"""Append-only card tray: raw 80-col lines + a JSONL audit sidecar.

Designed so a reviewer can replay every card in order. No eval/exec.
"""
import json


class Tray:
    def __init__(self):
        self.cards = []   # raw 80-col strings, in order
        self.audit = []   # list of {"n", "card", "meta"}

    def add(self, raw, meta=None):
        self.cards.append(raw)
        self.audit.append({"n": len(self.cards), "card": raw, "meta": meta or {}})

    def to_jsonl(self):
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in self.audit)

    def load_jsonl(self, text):
        self.audit = [json.loads(line) for line in text.splitlines() if line.strip()]
        self.cards = [r["card"] for r in self.audit]
        return self
