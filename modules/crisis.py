"""Highest-priority safety rule: detect suicidal/self-harm intent."""

from __future__ import annotations

import re
import unicodedata

_CRISIS = re.compile(
    r"不想活|唔想活|活著沒意思|活著冇意思|做人冇意思|做人沒意思|"
    r"想死|尋死|了結|自殺|自杀|輕生|轻生|自殘|自残|傷害自己|伤害自己|"
    r"結束生命|结束生命|唔想再捱|不想再捱|"
    r"\b(?:suicide|suicidal|kill myself|end my life|end it all|"
    r"self[- ]?harm|hurt myself|don't want to live|"
    r"want to die|better off dead|no reason to live)\b",
    re.IGNORECASE,
)


def detects_crisis(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text or "").strip()
    return bool(_CRISIS.search(normalized))
