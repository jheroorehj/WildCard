from typing import Any, Dict, List



from langchain_core.messages import HumanMessage, SystemMessage



from core.llm import get_solar_chat

from utils.json_parser import parse_json



from .prompt import NODE10_REPORT_PROMPT





def node10_loss_review_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node10: N8/N9 결과를 기반으로 투자 학습 경로를 생성합니다.
    """
    payload = {
        "n8_loss_cause_analysis": state.get("n8_loss_cause_analysis"),
        "n8_market_context_analysis": state.get("n8_market_context_analysis"),
        "n9_input": state.get("n9_input"),
        "learning_pattern_analysis": state.get("learning_pattern_analysis"),
    }


    llm = get_solar_chat()

    messages = [

        SystemMessage(content=NODE10_REPORT_PROMPT),

        HumanMessage(content=f"Write the report using this input:\n{payload}"),

    ]



    try:

        response = llm.invoke(messages)

        raw = response.content if isinstance(response.content, str) else str(response.content)

    except Exception as exc:

        return {"n10_loss_review_report": _fallback(f"LLM 호출 실패: {exc}")}



    parsed = parse_json(raw)

    if not isinstance(parsed, dict):

        return {"n10_loss_review_report": _fallback("JSON 파싱 실패")}



    return {"n10_loss_review_report": _normalize(parsed)}


def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_title": str(data.get("report_title", "손실 복기 리포트")),
        "overall_summary": str(data.get("overall_summary", "요약을 생성하지 못했습니다.")),
        "node_summaries": _normalize_node_summaries(data.get("node_summaries")),
        "learning_materials": _normalize_learning_materials(data.get("learning_materials")),
        "uncertainty_level": data.get("uncertainty_level", "high"),
    }




def _coerce_list(value: Any) -> List[str]:

    if isinstance(value, list):

        return [str(item) for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():

        return [value]

    return []





def _normalize_node_summaries(value: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(value, dict):
        value = {}
    return {
        "n6": _normalize_node_block(value.get("n6")),
        "n7": _normalize_node_block(value.get("n7")),
        "n8": _normalize_node_block(value.get("n8")),
        "n9": _normalize_node_block(value.get("n9")),
    }


def _normalize_node_block(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        value = {}
    return {
        "summary": str(value.get("summary", "")),
        "details": _coerce_list(value.get("details")),
    }


def _normalize_learning_materials(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        value = {}
    return {
        "key_takeaways": _coerce_list(value.get("key_takeaways")),
        "recommended_topics": _coerce_list(value.get("recommended_topics")),
        "practice_steps": _coerce_list(value.get("practice_steps")),
    }


def _fallback(reason: str) -> Dict[str, Any]:
    return {
        "report_title": "손실 복기 리포트",
        "overall_summary": f"리포트를 생성하지 못했습니다. ({reason})",
        "node_summaries": _normalize_node_summaries({}),
        "learning_materials": _normalize_learning_materials({}),
        "uncertainty_level": "high",
    }
