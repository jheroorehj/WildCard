from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from utils.json_parser import parse_json
from utils.validator import validate_action_missions

from .prompt import NODE10_REPORT_PROMPT





def node10_learning_tutor(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node10: N8/N9 결과를 기반으로 투자 학습 튜터 출력을 생성합니다.
    action_missions도 이 노드에서 생성됩니다.
    """
    # N9에서 받은 learning_pattern_analysis 포함
    learning_pattern = state.get("learning_pattern_analysis", {})

    payload = {
        "n8_loss_cause_analysis": state.get("n8_loss_cause_analysis"),
        "n8_market_context_analysis": state.get("n8_market_context_analysis"),
        "n9_input": state.get("n9_input"),
        "learning_pattern_analysis": learning_pattern,
    }

    llm = get_solar_chat()
    # action_missions 포함으로 출력이 길어짐
    llm_with_config = llm.bind(max_tokens=4096)

    messages = [
        SystemMessage(content=NODE10_REPORT_PROMPT),
        HumanMessage(content=f"Write the report using this input:\n{payload}"),
    ]

    try:
        response = llm_with_config.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:
        return {"n10_loss_review_report": _fallback(f"LLM 호출 실패: {exc}", learning_pattern)}



    parsed = parse_json(raw)

    if not isinstance(parsed, dict):
        return {"n10_loss_review_report": _fallback("JSON 파싱 실패", learning_pattern)}

    return {"n10_loss_review_report": _normalize(parsed, learning_pattern)}


def _normalize(data: Dict[str, Any], learning_pattern: Dict[str, Any] = None) -> Dict[str, Any]:
    tutor = data.get("learning_tutor")
    if isinstance(tutor, dict):
        return {"learning_tutor": _normalize_learning_tutor(tutor, learning_pattern)}

    if _looks_like_tutor(data):
        return {"learning_tutor": _normalize_learning_tutor(data, learning_pattern)}

    return {"learning_tutor": _normalize_learning_tutor({}, learning_pattern)}




def _coerce_list(value: Any) -> List[str]:

    if isinstance(value, list):

        return [str(item) for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():

        return [value]

    return []





def _normalize_learning_tutor(value: Any, learning_pattern: Dict[str, Any] = None) -> Dict[str, Any]:
    if not isinstance(value, dict):
        value = {}
    custom_path = value.get("custom_learning_path")
    if not isinstance(custom_path, dict):
        custom_path = {}
    advisor = value.get("investment_advisor")
    if not isinstance(advisor, dict):
        advisor = {}

    # action_missions 처리
    missions = value.get("action_missions", [])
    if not validate_action_missions(missions):
        # LLM이 생성하지 못한 경우 N9의 편향 기반으로 기본 미션 생성
        missions = _generate_fallback_missions(learning_pattern)

    return {
        "custom_learning_path": {
            "path_summary": str(custom_path.get("path_summary", "")),
            "learning_materials": _coerce_list(custom_path.get("learning_materials")),
            "practice_steps": _coerce_list(custom_path.get("practice_steps")),
            "recommended_topics": _coerce_list(custom_path.get("recommended_topics")),
        },
        "investment_advisor": {
            "advisor_message": str(advisor.get("advisor_message", "")),
            "recommended_questions": _coerce_list(advisor.get("recommended_questions")),
        },
        "action_missions": missions,
        "uncertainty_level": value.get("uncertainty_level", "high"),
    }


def _fallback(reason: str, learning_pattern: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "learning_tutor": {
            "custom_learning_path": {
                "path_summary": "학습 경로를 생성하지 못했습니다.",
                "learning_materials": [],
                "practice_steps": [],
                "recommended_topics": [],
            },
            "investment_advisor": {
                "advisor_message": f"튜터 메시지를 생성하지 못했습니다. ({reason})",
                "recommended_questions": [],
            },
            "action_missions": _generate_fallback_missions(learning_pattern),
            "uncertainty_level": "high",
        }
    }


def _generate_fallback_missions(learning_pattern: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    N9의 learning_pattern_analysis 기반으로 기본 미션 생성
    """
    if not learning_pattern:
        learning_pattern = {}

    # N9의 인지 편향 정보 추출
    cognitive = learning_pattern.get("cognitive_analysis", {})
    primary_bias = cognitive.get("primary_bias", {})
    bias_name = primary_bias.get("name", "확증 편향")
    bias_code = learning_pattern.get("investor_character", {}).get("behavioral_bias", "confirmation_bias")

    # 편향별 맞춤 미션 매핑
    mission_templates = {
        "confirmation_bias": {
            "title": "반대 의견 3개 찾기",
            "description": "매수하려는 종목에 대해 부정적인 의견이나 리스크 요인을 3가지 이상 찾아 기록하세요. 긍정적 뉴스만 찾는 습관을 바꿔봅니다.",
            "behavioral_target": "확증 편향 완화",
        },
        "herding_effect": {
            "title": "나만의 투자 논리 정리하기",
            "description": "'왜 이 종목인가?'에 대해 다른 사람의 의견을 배제하고 자신만의 분석을 3줄 이상 작성하세요.",
            "behavioral_target": "군중 심리 완화",
        },
        "fomo": {
            "title": "24시간 대기 룰 적용하기",
            "description": "급등 종목 발견 시 바로 매수하지 말고 24시간 후에 다시 판단해보세요. 그 사이 조사할 내용을 리스트업합니다.",
            "behavioral_target": "FOMO 완화",
        },
        "loss_aversion": {
            "title": "손절 기준 미리 정하기",
            "description": "매수 전에 '이 가격까지 떨어지면 손절한다'는 기준을 정해 메모하세요. 투자 전 손절 계획이 리스크 관리의 첫걸음입니다.",
            "behavioral_target": "손실 회피 완화",
        },
        "anchoring_effect": {
            "title": "현재 기업가치 분석하기",
            "description": "전고점 가격이 아닌 현재 기업의 펀더멘털(실적, 성장성, 경쟁력)을 기준으로 적정 가격을 다시 평가해보세요.",
            "behavioral_target": "앵커링 효과 완화",
        },
        "overconfidence": {
            "title": "과거 투자 복기하기",
            "description": "최근 3개의 투자 결정을 되돌아보고, 각각에서 예상과 다른 결과가 있었다면 그 원인을 분석해보세요.",
            "behavioral_target": "자기과신 완화",
        },
    }

    # 해당 편향에 맞는 미션 선택 (기본값: 확증 편향)
    template = mission_templates.get(bias_code, mission_templates["confirmation_bias"])

    return [
        {
            "mission_id": "M001",
            "priority": 1,
            "title": template["title"],
            "description": template["description"],
            "behavioral_target": template["behavioral_target"],
            "expected_outcome": "투자 의사결정 품질 향상",
            "difficulty": "medium",
            "estimated_impact": "high",
        }
    ]


def _looks_like_tutor(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if "custom_learning_path" in value:
        return True
    if "investment_advisor" in value:
        return True
    return False
