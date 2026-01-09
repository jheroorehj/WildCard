import re
from typing import List

_ADVICE_PATTERNS: List[str] = [
    r"해야\s*합니다",
    r"하세요",
    r"추천(합니다|드립|해)",
    r"다음(에는|엔)",
    r"매수(하세요|하라|를\s*추천)",
    r"매도(하세요|하라|를\s*추천)",
    r"전략적으로",
]


def contains_advice(text: str) -> bool:
    """
    Node3 출력에 '조언/추천'이 섞였는지 탐지
    """
    if not text:
        return False

    for pattern in _ADVICE_PATTERNS:
        if re.search(pattern, text):
            return True

    return False
