"""列名・チャンネル名の正規化と、見つからない名前の候補探し"""

from __future__ import annotations

import difflib
import unicodedata
from typing import Hashable, Iterable, List, Tuple


def normalize(text: object, *, casefold: bool = True) -> str:
    """表記の揺れを吸収した比較用の文字列（NFKC で全角・半角をそろえ、大文字小文字と空白の違いを無視する）

    Args:
        text: 元の文字列
        casefold: 大文字小文字の違いを無視するか（単位は mN と MN が別物なので False にする）

    Examples:
        >>> normalize("ＳＧ１　荷重（kN）")
        'sg1 荷重(kn)'
        >>> normalize("µε", casefold=False) == normalize("με", casefold=False)   # マイクロ記号とギリシャ文字
        True
    """
    text = unicodedata.normalize("NFKC", str(text))
    return " ".join((text.casefold() if casefold else text).split())


Candidate = Tuple[str, str, Hashable]
"""(比較する名前, 表示する文字列, 対象の識別子)。同じ対象を複数の名前（列名と ch など）で探すときは識別子をそろえる"""


def suggest(key: str, candidates: Iterable[Candidate], n: int = 3) -> List[str]:
    """key に近い候補の表示文字列（正規化して一致・類似・部分一致の順、最大 n 件）

    同じ識別子の候補は、最も順位の高いものだけを残します。

    Args:
        key: 見つからなかった名前
        candidates: (比較する名前, 表示する文字列, 対象の識別子) の並び
        n: 候補の最大数
    """
    target = normalize(key)
    if not target:
        return []
    items = [(normalize(name), display, ident) for name, display, ident in candidates]
    keys = list(dict.fromkeys(name for name, _, _ in items if name))
    ranked = [name for name in keys if name == target]
    ranked += difflib.get_close_matches(target, keys, n=len(keys), cutoff=0.6)
    # 候補が key に含まれる向きは、1文字の候補（チャンネル番号など）がほぼ何にでも当たるため2文字以上に限る
    ranked += [name for name in keys if target in name or (len(name) >= 2 and name in target)]

    result: List[str] = []
    seen: set = set()
    for name in dict.fromkeys(ranked):
        for normalized, display, ident in items:
            if normalized == name and ident not in seen:
                seen.add(ident)
                result.append(display)
    return result[:n]


def missing_message(label: str, key: str, candidates: Iterable[Candidate]) -> str:
    """「{label} '{key}' が存在しません」に、近い候補があれば添えたメッセージ"""
    hits = suggest(key, candidates)
    hint = f"（候補: {', '.join(hits)}）" if hits else ""
    return f"{label} '{key}' が存在しません{hint}"
