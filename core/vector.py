"""自由文ニーズのベクトル検索層(pgvector の代替: 外部依存なしのローカル埋め込み).

文字n-gramのTFベクトル + コサイン類似。本番では pgvector + 実埋め込みに差し替え可能。
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+|[぀-ヿ一-鿿々〆ぁ-んァ-ヶ]")


def _tokens(text: str):
    chars = _TOKEN_RE.findall(text.lower())
    grams = list(chars)
    grams += ["".join(chars[i:i + 2]) for i in range(len(chars) - 1)]
    return grams


def embed(text: str) -> Dict[str, float]:
    tf = Counter(_tokens(text))
    norm = math.sqrt(sum(v * v for v in tf.values())) or 1.0
    return {k: v / norm for k, v in tf.items()}


def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())
