from __future__ import annotations

import time
import uuid

import streamlit as st

from modules.consent import CONSENT_SESSION_KEY
from modules.deepseek_service import extract_observation, get_api_key
from modules.i18n import get_response_language


ECOG_DIMENSIONS = frozenset(
    {
        "memory",
        "planning",
        "financial",
        "shopping",
        "medication",
        "personal_care",
        "communication",
        "daily_activities",
        "none",
    }
)
RISK_FLAGS = frozenset({"normal", "mild", "concern"})

_SAFETY_KEYWORDS = (
    "煤气",
    "煤氣",
    "gas",
    "吃錯",
    "吃错",
    "服錯",
    "服错",
    "wrong medication",
    "wrong dose",
    "急症",
    "emergency",
    "跌倒",
    "fall",
    "迷路",
    "lost",
    "鎖門",
    "锁门",
    "忘記鎖",
    "忘记锁",
)
_MILD_KEYWORDS = (
    "忘",
    "記不",
    "记不",
    "鑰匙",
    "钥匙",
    "藥",
    "药",
    "medicine",
    "medication",
    "帳單",
    "账单",
    "bill",
    "appointment",
    "預約",
    "预约",
    "行程",
    "schedule",
)
_SHOPPING_KEYWORDS = (
    "買",
    "买",
    "購物",
    "购物",
    "超市",
    "結帳",
    "结账",
    "shop",
    "shopping",
    "checkout",
)
_FINANCIAL_KEYWORDS = (
    "錢",
    "钱",
    "帳單",
    "账单",
    "bill",
    "銀行",
    "银行",
    "bank",
    "money",
    "financial",
)
_MEDICATION_KEYWORDS = ("藥", "药", "medicine", "medication", "dose", "劑量", "剂量")
_PERSONAL_CARE_KEYWORDS = (
    "洗澡",
    "洗漱",
    "穿衣",
    "如廁",
    "如厕",
    "梳頭",
    "梳头",
    "personal care",
    "hygiene",
    "dressing",
    "toileting",
)
_PLANNING_KEYWORDS = (
    "安排",
    "約",
    "约",
    "預約",
    "预约",
    "行程",
    "schedule",
    "plan",
    "appointment",
)
_MEMORY_KEYWORDS = (
    "忘",
    "記得",
    "记得",
    "記不",
    "记不",
    "鑰匙",
    "钥匙",
    "名字",
    "日期",
    "remember",
    "forget",
    "forgot",
)
_COMMUNICATION_KEYWORDS = (
    "電話",
    "电话",
    "phone",
    "說話",
    "说话",
    "聽不懂",
    "听不懂",
    "understand",
    "communicate",
)


def _detect_dimension(text: str) -> str:
    lowered = text.casefold()
    if any(keyword in lowered for keyword in _SHOPPING_KEYWORDS):
        return "shopping"
    if any(keyword in lowered for keyword in _FINANCIAL_KEYWORDS):
        return "financial"
    if any(keyword in lowered for keyword in _MEDICATION_KEYWORDS):
        return "medication"
    if any(keyword in lowered for keyword in _PERSONAL_CARE_KEYWORDS):
        return "personal_care"
    if any(keyword in lowered for keyword in _PLANNING_KEYWORDS):
        return "planning"
    if any(keyword in lowered for keyword in _MEMORY_KEYWORDS):
        return "memory"
    if any(keyword in lowered for keyword in _COMMUNICATION_KEYWORDS):
        return "communication"
    return "daily_activities"


def _detect_risk_flag(text: str) -> str:
    lowered = text.casefold()
    if any(keyword in lowered for keyword in _SAFETY_KEYWORDS):
        return "concern"
    if any(keyword in lowered for keyword in _MILD_KEYWORDS):
        return "mild"
    return "normal"


def _fallback_extract(user_input: str) -> dict[str, object]:
    clean_input = user_input.strip()
    dimension = _detect_dimension(clean_input)
    return {
        "theme": dimension,
        "summary": clean_input[:160],
        "ecog_dimension": dimension,
        "risk_flag": _detect_risk_flag(clean_input),
    }


def _sanitize_extraction(
    payload: dict[str, object],
    user_input: str,
) -> dict[str, object]:
    theme = payload.get("theme")
    summary = payload.get("summary")
    dimension = payload.get("ecog_dimension")
    risk_flag = payload.get("risk_flag")
    clean_input = user_input.strip()

    return {
        "theme": str(theme).strip()[:60] if isinstance(theme, str) and theme.strip() else "daily",
        "summary": (
            str(summary).strip()[:240]
            if isinstance(summary, str) and summary.strip()
            else clean_input[:160]
        ),
        "ecog_dimension": dimension if dimension in ECOG_DIMENSIONS else "none",
        "risk_flag": risk_flag if risk_flag in RISK_FLAGS else "normal",
    }


def extract_memory_from_input(user_input: str) -> dict[str, object]:
    clean_input = user_input.strip()
    record: dict[str, object] = {
        "id": uuid.uuid4().hex[:12],
        "created_at": time.time(),
        "source_quote": clean_input[:300],
        "source": "local-fallback",
    }

    api_key = get_api_key()
    consent = bool(st.session_state.get(CONSENT_SESSION_KEY, False))
    if api_key and consent:
        try:
            payload = extract_observation(
                api_key,
                clean_input,
                response_language=get_response_language(),
            )
            record.update(_sanitize_extraction(payload, clean_input))
            record["source"] = "deepseek"
            return record
        except Exception:
            pass

    record.update(_fallback_extract(clean_input))
    return record
