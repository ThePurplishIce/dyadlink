from __future__ import annotations

import re


_DISTRESS = re.compile(
    r"去世|過世|过世|走了|離開了|离开了|往生|逝世|"
    r"孤單|孤单|寂寞|害怕|恐懼|恐惧|難過|难过|傷心|伤心|"
    r"哭|流淚|流泪|眼淚|眼泪|焦慮|焦虑|擔心得|担心得|絕望|绝望|"
    r"唔開心|唔开心|好掛|掛住|挂住|冇晒|好驚|驚到|"
    r"\b(?:died|passed\s+away|lost\s+my|grief|grieving|lonely|lonesome|"
    r"afraid|scared|frightened|sad|sadness|cry|crying|tears|anxious|"
    r"anxiety|worried\s+sick|miss\s+(?:my|him|her|them)|heartbroken)\b",
    re.IGNORECASE,
)

EMPATHY_INSTRUCTION = (
    "使用者剛分享了沉重或悲傷的經歷。請先以溫柔、簡短的陪伴語氣回應："
    "這一輪不要追問日常活動細節、不要提出新問題，"
    "只需真誠安慰與陪伴（一兩句話），讓使用者決定要不要繼續說。"
)


def is_emotionally_distressed(text: str) -> bool:
    return bool(_DISTRESS.search(text))
