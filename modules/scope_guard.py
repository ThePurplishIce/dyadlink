from __future__ import annotations

import re
import unicodedata


_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
_TECHNICAL = re.compile(
    r"```|<\s*/?\s*(?:code|script)\b|#include|console\s*\.\s*log|"
    r"\b(?:python|javascript|typescript|java|c\+\+|c#|sql|html|css|bash|"
    r"code|coding|programming|debug(?:ging)?|compiler|compile|algorithm)\b|"
    r"\b(?:write|create|build|generate|develop|debug)\s+(?:a\s+)?"
    r"(?:computer\s+)?(?:program|script)\b|"
    r"\b(?:def|class|import|from|print|function|const|let|var)\s+[A-Za-z_$]|"
    r"代碼|代码|編程|编程|寫碼|写码",
    re.IGNORECASE,
)
_TECHNICAL_COMPACT_WORDS = (
    "python",
    "javascript",
    "typescript",
    "programming",
    "coding",
    "debug",
    "compiler",
    "compile",
    "code",
)
_MATH_COMPACT_WORDS = (
    "solve",
    "calculate",
    "equation",
    "homework",
    "mathematics",
    "worksheet",
    "integral",
    "derivative",
)
_MATH_OR_EXERCISE = re.compile(
    r"\b(?:solve|calculate|equation|homework|math|mathematics|proof|prove|"
    r"derive|integral|derivative|algebra|geometry|worksheet|problem\s+set)\b|"
    r"解題|解题|做題|做题|解方程|數學|数学|求答案",
    re.IGNORECASE,
)
_AMBIGUOUS_TASK_TERMS = re.compile(
    r"程式|程序|題目|题目|作業|作业|計算|计算|證明|证明|推導|推导|求解|解方程"
)
_TASK_INTENT = re.compile(
    r"幫我|帮我|幫忙|帮忙|請|请|給我|给我|教我|寫個|写个|寫一|写一|"
    r"做一|算一|解一|弄一|"
    r"\b(?:write|solve|finish|complete|explain|draft|compose|code|program|"
    r"debug|calculate|compute|prove|derive)\b",
    re.IGNORECASE,
)
_QUESTION_LIKE = re.compile(
    r"[?？]\s*$|"
    r"(?:是不是|好不好|對嗎|对吗|行嗎|行吗|可以嗎|可以吗|為什麼|为什么|"
    r"什麼呢|什么呢)[。？！…~\s]*$",
    re.IGNORECASE,
)
_REQUEST_START = re.compile(
    r"^\s*(?:請|请|幫我|帮我|給我|给我|幫忙|帮忙|教我|告訴我|告诉我|"
    r"問一下|问一下|我想知道|我想問|我想问|我想請問|我想请问|我想了解|"
    r"(?:tell\s+me|show\s+me|give\s+me|help\s+me|please|"
    r"what|why|who|whom|whose|when|where|which|"
    r"can\s+you|could\s+you|would\s+you|will\s+you|may\s+i|"
    r"i\s+(?:want|wanna|would\s+like)\s+to\s+know)\b)",
    re.IGNORECASE,
)
_OUTPUT_DISALLOWED = re.compile(
    r"```|<\s*/?\s*(?:code|script)\b|#include|console\s*\.\s*log|"
    r"\b(?:python|javascript|typescript|java|c\+\+|c#|sql|html|css|bash|"
    r"programming|coding|compiler|compile|debug(?:ging)?|algorithm)\b|"
    r"\b(?:write|create|build|generate|develop|debug)\s+(?:a\s+)?"
    r"(?:computer\s+)?(?:program|script)\b|"
    r"\b(?:def|class|import|from|print|function|const|let|var)\s+[A-Za-z_$]|"
    r"代碼|代码|編程|编程|寫碼|写码|"
    r"解題|解题|做題|做题|解方程|數學|数学|求答案|"
    r"\b(?:solve|calculate|equation|homework|mathematics|worksheet|"
    r"integral|derivative|algebra|geometry)\b|"
    r"\b(?:prompt\s+injection|system\s+prompt|developer\s+mode)\b",
    re.IGNORECASE,
)
_BYPASS = re.compile(
    r"\b(?:ignore|disregard|override|bypass|jailbreak)\b.{0,60}"
    r"\b(?:instructions?|rules?|restrictions?)\b|"
    r"\b(?:prompt\s+injection|system\s+prompt|developer\s+mode)\b|"
    r"(?:忽略|無視|无视|繞過|绕过|解除).{0,16}(?:規則|规则|指示|指令|限制)",
    re.IGNORECASE,
)
_TASK_REQUEST = re.compile(
    r"\b(?:translate|write\s+an?\s+(?:essay|article|report)|draft|compose|"
    r"look\s+up|search\s+for|what\s+is|who\s+is|when\s+was|tell\s+me\s+about)\b|"
    r"翻譯|翻译|寫一篇|写一篇|幫我寫|帮我写|查一下|搜尋|搜索|"
    r"請問什麼是|请问什么是",
    re.IGNORECASE,
)
_PERSONAL_LIFE = re.compile(
    r"\b(?:i|we)\s+(?:feel|felt|am|was|went|forgot|forget|remember|called|"
    r"visited|worked|slept|ate|have|had|miss|worry|worried|need|enjoy|noticed|"
    r"saw|helped|talked|live|moved|retired)\b|"
    r"\bmy\s+(?:family|wife|husband|grandma|grandmother|grandpa|grandfather|"
    r"mother|father|son|daughter|friend|colleague|job|work|home|keys|day|"
    r"routine|health|memory|medication|appointment|life|dog|cat)\b|"
    r"\b(?:today|yesterday|recently|daily|life|family|wife|husband|grandma|"
    r"grandmother|grandpa|grandfather|mother|father|son|"
    r"daughter|friend|colleague|work|retir\w*|sleep\w*|eat|forgot|forget|"
    r"remember|memory|mood|worried|afraid|lonely|sad|happy|routine|reminder|keys|"
    r"medication|shopping|care|home|walk|neighbor)\b|"
    r"今天|昨天|最近|剛才|刚才|剛剛|刚刚|日常|生活|家人|"
    r"妻子|丈夫|老婆|老公|奶奶|爺爺|爷爷|外婆|外公|媽媽|妈妈|爸爸|"
    r"孩子|兒子|儿子|女兒|女儿|朋友|同事|工作|上班|退休|睡|吃飯|吃饭|"
    r"出門|出门|鑰匙|钥匙|忘記|忘记|忘了|記得|记得|心情|擔心|担心|"
    r"(?:我|我們|我们)(?:今天|昨天|最近|剛才|刚才|剛剛|刚刚|忘記|忘记|"
    r"忘了|記得|记得|覺得|觉得|感到|叫|跟|和|去|做|遇到|吃|睡|上班|"
    r"工作|擔心|担心|難過|难过|想聊)|"
    r"害怕|孤單|孤单|難過|难过|開心|开心|記憶|记忆|安排|提醒|買菜|买菜|藥|药|"
    r"照顧|照顾|家裡|家里|回家|散步|鄰居|邻居|"
    r"返工|放工|收工|返學|返学|放學|放学|買餸|买餸|飲茶|饮茶|茶樓|茶楼|"
    r"街市|覆診|覆诊|藥房|药房|診所|诊所|搭車|搭车|地鐵|地铁|巴士|"
    r"落雨|天氣|天气|沖涼|冲凉|瞓覺|瞓觉|起身|行街|煮飯|煮饭|煲湯|煲汤|"
    r"電話|电话|手機|手机|電視|电视|晨運|晨运|公園|公园|街市場",
    re.IGNORECASE,
)
_LIFE_HELP_REQUEST = re.compile(
    r"\b(?:how\s+(?:can|do|should)\s+i|what\s+should\s+i\s+do|help\s+me|"
    r"what\s+(?:is|['’]s)\s+(?:a|the)\s+(?:good|best|helpful)\s+way)\b|"
    r"我該怎麼|我该怎么|怎麼才能|怎么才能|如何記得|如何记得|如何安排|"
    r"怎樣安排|怎样安排|有什麼方法|有什么方法|有沒有辦法|有没有办法",
    re.IGNORECASE,
)
_SHORT_REPLY = re.compile(
    r"^(?:yes|no|not really|i don't know|i do not know|not sure|sometimes|"
    r"occasionally|rarely|often|okay|ok|thanks|none|hard to say|it's hard to say|"
    r"i can't remember|i do not recall|不知道|唔知|唔係|係|是|不是|有|沒有|"
    r"没有|我不知道|我不確定|我不确定|不確定|不确定|偶爾|偶尔|有時|有时|好|謝謝|谢谢|不好說|不好说|"
    r"很難說|很难说|說不上來|说不上来|不太記得|不太记得)[.!?。！ ]*$",
    re.IGNORECASE,
)
_GREETING = re.compile(r"^(?:hello|hi|hey|你好|您好|嗨|哈囉|哈啰)[.!?。！ ]*$", re.I)


def _normalized(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return _ZERO_WIDTH.sub("", normalized).strip()


def _has_disallowed_markers(text: str) -> bool:
    normalized = _normalized(text)
    compact = re.sub(r"[^a-z+#]", "", normalized.lower())
    compact_han = re.sub(r"\s+", "", normalized)
    return bool(
        _TECHNICAL.search(normalized)
        or any(word in compact for word in _TECHNICAL_COMPACT_WORDS)
        or re.search(r"代碼|代码|編程|编程|寫碼|写码", compact_han)
        or _MATH_OR_EXERCISE.search(normalized)
        or any(word in compact for word in _MATH_COMPACT_WORDS)
        or _MATH_OR_EXERCISE.search(compact_han)
        or (
            _AMBIGUOUS_TASK_TERMS.search(normalized)
            and _TASK_INTENT.search(normalized)
        )
        or _BYPASS.search(normalized)
        or (
            any(word in compact for word in ("ignore", "disregard", "override", "bypass"))
            and any(word in compact for word in ("instruction", "rule", "restriction"))
        )
        or (
            any(word in compact_han for word in ("忽略", "無視", "无视", "繞過", "绕过"))
            and any(word in compact_han for word in ("規則", "规则", "指示", "指令", "限制"))
        )
    )


def contains_disallowed_content(text: str) -> bool:
    """Catch code, math, and prompt-bypass content in model output."""
    normalized = _normalized(text)
    return bool(
        _OUTPUT_DISALLOWED.search(normalized) or _BYPASS.search(normalized)
    )


def is_out_of_scope_request(text: str, has_life_context: bool = False) -> bool:
    """Allow everyday-life reflections; refuse detectable off-topic task requests."""
    normalized = _normalized(text)
    if not normalized:
        return False
    if _has_disallowed_markers(normalized):
        return True

    has_personal_context = bool(_PERSONAL_LIFE.search(normalized))
    if _TASK_REQUEST.search(normalized):
        return not (
            has_personal_context and _LIFE_HELP_REQUEST.search(normalized)
        )
    if has_personal_context:
        return False
    if _GREETING.fullmatch(normalized):
        return False
    if has_life_context and _SHORT_REPLY.fullmatch(normalized):
        return False
    return bool(
        _QUESTION_LIKE.search(normalized)
        or _REQUEST_START.search(normalized)
    )
