from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prompt import NODE9_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.validator import validate_node9


def node9_learning_pattern_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node9: 학습 패턴 분석 (행동경제학 기반)
    """
    llm = get_solar_chat()
    # N9의 새 구조는 출력이 길어서 max_tokens를 충분히 설정
    llm_with_config = llm.bind(max_tokens=4096)

    n9_input = state.get("n9_input")
    if not isinstance(n9_input, dict):
        n9_input = {}

    # 투자 이유 추출 (fallback에서도 사용)
    investment_reason = (
        n9_input.get("investment_reason")
        or state.get("layer3_decision_basis")
        or ""
    )

    payload = {
        "investment_reason": investment_reason,
        "loss_cause_summary": n9_input.get("loss_cause_summary", ""),
        "loss_cause_details": n9_input.get("loss_cause_details", []),
        "objective_signals": n9_input.get("objective_signals", {}),
        "uncertainty_level": n9_input.get("uncertainty_level", "high"),
    }

    messages = [
        SystemMessage(content=NODE9_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "아래 입력을 바탕으로 학습 패턴 분석을 작성해 주세요.\n"
                "출력은 JSON만 반환하세요.\n"
                f"{payload}"
            )
        ),
    ]

    try:
        response = llm_with_config.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)

        parsed = parse_json(raw)
        if not isinstance(parsed, dict):
            return _fallback(investment_reason)

        if not validate_node9(parsed):
            return _fallback(investment_reason)

        return parsed
    except Exception:
        # LLM 호출 실패 시에도 fallback 반환
        return _fallback(investment_reason)


def _fallback(investment_reason: str = "") -> Dict[str, Any]:
    """
    LLM 호출 실패 시 기본 분석 결과 반환
    investment_reason 키워드 기반으로 기본적인 성향 분석 제공
    """
    # 키워드 기반 기본 분석
    reason_lower = investment_reason.lower() if investment_reason else ""

    # 기본값 (친근한 별명 스타일)
    character_type = "직감파 트레이더"
    character_desc = "분석보다는 직감을 믿는 스타일이에요. 체계적인 분석 습관을 기르면 더 좋은 결과를 얻을 수 있어요!"
    primary_bias = "confirmation_bias"
    primary_bias_name = "확증 편향"
    primary_bias_english = "Confirmation Bias"
    primary_bias_desc = "자신이 믿고 싶은 정보만 선택적으로 수용하는 경향"
    primary_bias_impact = "객관적 분석 없이 감정적으로 투자 결정을 내릴 수 있습니다"

    # 키워드 매칭으로 성향 추론 (친근한 별명 스타일)
    if any(kw in reason_lower for kw in ["친구", "추천", "주변", "커뮤니티", "카페", "유튜브", "다들"]):
        character_type = "트렌드 서퍼"
        character_desc = "주변의 분위기와 트렌드에 민감하게 반응하는 스타일이에요. 나만의 분석 기준을 세우면 더 현명한 투자가 가능해요!"
        primary_bias = "herding_effect"
        primary_bias_name = "군중 심리"
        primary_bias_english = "Herding Effect"
        primary_bias_desc = "다수의 행동을 따라하려는 경향"
        primary_bias_impact = "군중의 판단이 틀릴 때 함께 손실을 볼 수 있습니다"
    elif any(kw in reason_lower for kw in ["오를", "상승", "급등", "기회", "놓치", "지금"]):
        character_type = "기회의 사냥꾼"
        character_desc = "상승 기회를 놓치지 않으려는 열정적인 투자자예요. 하지만 급등 추격은 고점 매수 위험이 있으니 한 템포 쉬어가는 것도 좋아요!"
        primary_bias = "fomo"
        primary_bias_name = "FOMO"
        primary_bias_english = "Fear Of Missing Out"
        primary_bias_desc = "기회를 놓칠까 봐 조급해하는 경향"
        primary_bias_impact = "충분한 분석 없이 급하게 매수하여 고점에 물릴 수 있습니다"
    elif any(kw in reason_lower for kw in ["저점", "싸", "저렴", "할인", "바닥", "전고점"]):
        character_type = "바겐 헌터"
        character_desc = "가격이 저렴할 때를 노리는 알뜰한 투자자예요. '싼 데는 이유가 있다'는 점도 체크해보면 더 좋아요!"
        primary_bias = "anchoring_effect"
        primary_bias_name = "앵커링 효과"
        primary_bias_english = "Anchoring Effect"
        primary_bias_desc = "과거 가격에 판단이 고정되는 경향"
        primary_bias_impact = "전고점 대비 가격에만 집착하여 하락 추세를 간과할 수 있습니다"
    elif any(kw in reason_lower for kw in ["뉴스", "기사", "소식", "발표", "실적"]):
        character_type = "뉴스 헌터"
        character_desc = "뉴스와 정보에 민감한 정보통이에요. 정보가 이미 가격에 반영됐는지 체크하는 습관을 들이면 더 좋아요!"
        primary_bias = "availability_heuristic"
        primary_bias_name = "가용성 휴리스틱"
        primary_bias_english = "Availability Heuristic"
        primary_bias_desc = "최근 접한 정보에 과도한 가중치를 두는 경향"
        primary_bias_impact = "단기 뉴스에 과민 반응하여 장기적 관점을 놓칠 수 있습니다"

    return {
        "learning_pattern_analysis": {
            "investor_character": {
                "type": character_type,
                "description": character_desc,
                "behavioral_bias": primary_bias,
            },
            "profile_metrics": {
                "information_sensitivity": {
                    "score": 55,
                    "label": "정보 민감도",
                    "bias_detected": None,
                },
                "analysis_depth": {
                    "score": 45,
                    "label": "분석 깊이",
                    "bias_detected": "확증 편향(Confirmation Bias)" if primary_bias == "confirmation_bias" else None,
                },
                "risk_management": {
                    "score": 50,
                    "label": "리스크 관리",
                    "bias_detected": None,
                },
                "decisiveness": {
                    "score": 55,
                    "label": "결단력",
                    "bias_detected": None,
                },
                "emotional_control": {
                    "score": 45,
                    "label": "감정 통제",
                    "bias_detected": "군중 심리(Herding Effect)" if primary_bias == "herding_effect" else None,
                },
                "learning_adaptability": {
                    "score": 55,
                    "label": "학습 적응력",
                    "bias_detected": None,
                },
            },
            "cognitive_analysis": {
                "primary_bias": {
                    "name": primary_bias_name,
                    "english": primary_bias_english,
                    "description": primary_bias_desc,
                    "impact": primary_bias_impact,
                },
                "secondary_biases": [],
            },
            "decision_problems": [
                {
                    "problem_type": "분석 부족",
                    "psychological_trigger": "시간 압박 또는 정보 부족",
                    "situation": "투자 결정을 빠르게 내려야 할 때",
                    "thought_pattern": "자세한 분석 없이 감으로 결정",
                    "consequence": "예상치 못한 리스크에 노출될 수 있음",
                    "frequency": "medium",
                }
            ],
            "uncertainty_level": "high",
        }
    }
