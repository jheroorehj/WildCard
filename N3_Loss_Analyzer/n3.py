from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_solar_chat
from .prommpt import NODE3_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.validator import validate_node3
from utils.safety import contains_advice


def node3_loss_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_solar_chat()

    payload = {
        "layer1_stock": state.get("layer1_stock"),
        "layer2_buy_date": state.get("layer2_buy_date"),
        "layer2_sell_date": state.get("layer2_sell_date"),
        "layer3_decision_basis": state.get("layer3_decision_basis"),
    }

    messages = [
        SystemMessage(content=NODE3_SYSTEM_PROMPT),
        HumanMessage(
            content=f"레이어 1~3 입력만으로 N6~N9 가이드라인을 만들어 주세요.\n{payload}"
        ),
    ]

    response = llm.invoke(messages)
    raw = response.content

    if contains_advice(raw):
        return {"n3_loss_diagnosis": fallback_result()}

    parsed = parse_json(raw)
    if not parsed:
        return {"n3_loss_diagnosis": fallback_result()}

    if not validate_node3(parsed):
        return {"n3_loss_diagnosis": fallback_result()}

    return {"n3_loss_diagnosis": parsed}


def fallback_result() -> Dict[str, Any]:
    return {
        "n6_tech_indicator_guideline": {
            "objective": "손실 구간의 기술적 지표 흐름을 요약하도록 안내합니다.",
            "required_inputs": ["layer1_stock", "layer2_buy_date", "layer2_sell_date"],
            "analysis_steps": [
                "손실 구간의 가격 흐름을 요약합니다.",
                "볼린저 밴드 기준 위치를 정성적으로 해석합니다.",
                "신호의 불확실성을 함께 명시합니다.",
            ],
            "output_requirements": [
                "볼린저 밴드만 사용",
                "수치가 없으면 정성 설명으로 대체",
            ],
        },
        "n7_news_market_guideline": {
            "objective": "손실 구간의 뉴스/시장 상황을 요약하도록 안내합니다.",
            "required_inputs": ["layer1_stock", "layer2_buy_date", "layer2_sell_date"],
            "analysis_steps": [
                "기간 내 주요 이벤트/이슈를 요약합니다.",
                "종목/섹터/시장에 미친 영향을 설명합니다.",
                "불확실성과 근거 부족을 분리해 적습니다.",
            ],
            "output_requirements": [
                "사실 중심 요약",
                "추측성 표현은 제한",
            ],
        },
        "n8_loss_cause_guideline": {
            "objective": "손실 원인 3가지를 서로 다른 관점으로 진단하도록 안내합니다.",
            "required_inputs": [
                "layer1_stock",
                "layer2_buy_date",
                "layer2_sell_date",
                "layer3_decision_basis",
            ],
            "analysis_steps": [
                "원인을 3개로 제한해 분리합니다.",
                "각 원인은 정의된 유형 내에서만 선택합니다.",
                "입력 근거에 기반해 간결히 설명합니다.",
            ],
            "output_requirements": [
                "각 원인의 유형(type) 포함",
                "서로 다른 유형 사용",
            ],
            "loss_cause_count": 3,
            "loss_cause_types": [
                "timing_error",
                "information_bias",
                "risk_management",
                "emotional_trading",
                "thesis_change_ignored",
            ],
        },
        "n9_mistake_pattern_guideline": {
            "objective": "실수 패턴 유형을 분류하도록 안내합니다.",
            "required_inputs": ["layer3_decision_basis"],
            "analysis_steps": [
                "의사결정 근거에서 반복 가능성을 찾습니다.",
                "실수 패턴을 간단한 유형으로 분류합니다.",
                "패턴과 손실 원인의 연결을 요약합니다.",
            ],
            "output_requirements": [
                "유형명은 짧게 작성",
                "판단 근거를 1문장으로 요약",
            ],
        },
        "global_constraints": [
            "직접적인 매수/매도 조언 금지",
            "가이드라인만 제공",
            "확신이 없으면 불확실성 명시",
        ],
        "uncertainty_level": "high",
    }
