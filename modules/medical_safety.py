from __future__ import annotations

import re
import unicodedata


_DOSAGE_REQUEST = re.compile(
    r"\b(?:dose|dosage|mg|mcg|milligrams?|micrograms?|ml|milliliters?|"
    r"how many pills?|how much medicine|medication dose)\b|"
    r"藥物劑量|藥量|劑量|剂量|吃幾顆|吃几颗|服用多少|幾毫克|几毫克",
    re.IGNORECASE,
)
_MEDICATION_ADJUSTMENT = re.compile(
    r"\b(?:adjust|change|increase|decrease|reduce|raise|stop|start|skip)\b"
    r".{0,60}\b(?:medication|medicine|drug|prescription|pill|dose)\b|"
    r"\b(?:medication|medicine|drug|prescription|pill|dose)\b.{0,60}"
    r"\b(?:adjust|change|increase|decrease|reduce|raise|stop|start|skip)\b|"
    r"調整.{0,12}(?:藥|藥物|藥量|劑量)|調藥|加藥|減藥|停藥|改藥|"
    r"调整.{0,12}(?:药|药物|药量|剂量)|调药|加药|减药|停药|改药",
    re.IGNORECASE,
)
_MEDICATION_ADVICE_REQUEST = re.compile(
    r"\b(?:what|which)\s+(?:medicine|medication|drug|pill)\b|"
    r"\bwhat\s+should\s+i\s+take\b|"
    r"吃什麼藥|吃什么药|該吃什麼|该吃什么|要不要吃藥|要不要吃药",
    re.IGNORECASE,
)
_DIAGNOSIS_REQUEST = re.compile(
    r"\b(?:diagnos(?:e|is)|what disease|what condition|what illness|"
    r"do i have|am i suffering from|what's wrong with me)\b|"
    r"診斷|诊断|這是什麼病|这是什么病|我得了什麼病|我得了什么病|"
    r"是否患有|是不是.*(?:病|失智)|"
    r"係咪.*(?:病|失智)",
    re.IGNORECASE,
)
_TREATMENT_PLAN = re.compile(
    r"\b(?:treatment plan|treatment options|how do i treat|what treatment|"
    r"treat this|cure this|therapy plan)\b|"
    r"治療方案|治療計畫|治療計劃|治療建議|如何治療|治疗方案|治疗计划|治疗建议|如何治疗",
    re.IGNORECASE,
)


def requires_medical_disclaimer(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text).strip()
    return bool(
        _DOSAGE_REQUEST.search(normalized)
        or _MEDICATION_ADJUSTMENT.search(normalized)
        or _MEDICATION_ADVICE_REQUEST.search(normalized)
        or _DIAGNOSIS_REQUEST.search(normalized)
        or _TREATMENT_PLAN.search(normalized)
    )
