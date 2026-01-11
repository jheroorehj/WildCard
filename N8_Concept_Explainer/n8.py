from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm import get_solar_chat
from .prompt import NODE8_TERM_EXPLANATION_PROMPT, NODE8_LEARNING_GUIDE_PROMPT
from .rag import search_term_in_knowledge_base
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node8


def node8_concept_explainer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node8: 용어/개념 설명 및 학습 가이드 제공
    
    두 가지 모드로 동작:
    1. term_explanation: 경제/주식 용어 설명 (요약 + 상세)
    2. learning_guide: 투자 패턴 분석 및 학습 경로 제시 (요약 + 상세)
    
    Args:
        state: 상태 딕셔너리
            - mode: "term" 또는 "learning" (기본값: "term")
            - term: 설명할 용어 (term 모드일 때)
            - context: 맥락 정보
            - investment_pattern: 투자 패턴 (learning 모드일 때)
            - loss_causes: 손실 원인 분석 결과 (learning 모드일 때, 선택)
    
    Returns:
        {
          "n8_concept_explanation": {
            "mode": "term" or "learning",
            "term_explanation": {...} or None,
            "learning_guide": {...} or None
          }
        }
    """
    mode = state.get("mode", "term")
    
    if mode == "term":
        return explain_term(state)
    elif mode == "learning":
        return provide_learning_guide(state)
    else:
        return {"n8_concept_explanation": fallback_result("알 수 없는 모드입니다.")}


def explain_term(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    용어 설명 모드
    
    경제/주식 용어를 한 줄 요약 + 상세 설명으로 제공
    """
    llm = get_solar_chat()
    
    term = state.get("term") or state.get("concept") or state.get("layer3_decision_basis")
    context = state.get("context", "")
    
    if not term:
        return {"n8_concept_explanation": fallback_result("설명할 용어가 제공되지 않았습니다.")}
    
    # RAG 검색 수행 (TODO: RAG 구현 후 활성화)
    rag_context = search_term_in_knowledge_base(term)
    # rag_context = ""  # 이제 실제 RAG 사용
    
    payload = {
        "term": term,
        "context": context,
        "rag_context": rag_context
    }
    
    messages = [
        SystemMessage(content=NODE8_TERM_EXPLANATION_PROMPT),
        HumanMessage(content=f"다음 용어를 설명해 주세요.\n{payload}")
    ]
    
    try:
        response = llm.invoke(messages)
        raw = response.content

        # DEBUG: LLM 원본 응답 출력
        print(f"[N8 DEBUG] Term: {term}")
        print(f"[N8 DEBUG] LLM Raw Response:\n{raw}\n")

        # 안전성 검사
        if contains_investment_advice(raw):
            print(f"[N8 DEBUG] Safety check failed: contains_advice")
            return {"n8_concept_explanation": fallback_result_term(term)}

        # JSON 파싱
        parsed = parse_json(raw)
        print(f"[N8 DEBUG] Parsed JSON: {parsed}\n")

        if not parsed:
            print(f"[N8 DEBUG] JSON parsing failed")
            return {"n8_concept_explanation": fallback_result_term(term)}
        
        # 스키마 검증 (term_explanation 형태로 변환)
        if "term_explanation" in parsed:
            validation_data = {
                "concept_explanation": {
                    "term": parsed["term_explanation"].get("term", str(term)),
                    "short_definition": parsed["term_explanation"].get("short_summary", ""),
                    "beginner_explanation": parsed["term_explanation"].get("detailed_explanation", ""),
                    "examples": [parsed["term_explanation"].get("simple_example", "")],
                    "related_terms": parsed["term_explanation"].get("related_terms", []),
                    "uncertainty_level": parsed["term_explanation"].get("uncertainty_level", "low")
                }
            }
            
            if not validate_node8(validation_data):
                print(f"[N8 DEBUG] Validation failed")
                return {"n8_concept_explanation": fallback_result_term(term)}

            print(f"[N8 DEBUG] Validation passed ✓")
            return {
                "n8_concept_explanation": {
                    "mode": "term",
                    "term_explanation": parsed["term_explanation"],
                    "learning_guide": None
                }
            }

        print(f"[N8 DEBUG] 'term_explanation' key not found in parsed JSON")
        return {"n8_concept_explanation": fallback_result_term(term)}
    
    except Exception as e:
        print(f"N8 용어 설명 중 오류: {e}")
        return {"n8_concept_explanation": fallback_result_term(term)}


def provide_learning_guide(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    학습 가이드 모드
    
    사용자의 투자 패턴을 분석하여 학습 경로 제시
    """
    llm = get_solar_chat()
    
    investment_pattern = state.get("investment_pattern") or state.get("layer3_decision_basis")
    loss_causes = state.get("loss_causes", [])
    context = state.get("context", "")
    
    if not investment_pattern:
        return {"n8_concept_explanation": fallback_result("투자 패턴 정보가 제공되지 않았습니다.")}
    
    payload = {
        "investment_pattern": investment_pattern,
        "loss_causes": loss_causes,
        "context": context
    }
    
    messages = [
        SystemMessage(content=NODE8_LEARNING_GUIDE_PROMPT),
        HumanMessage(content=f"다음 투자 패턴을 분석하여 학습 가이드를 제공해 주세요.\n{payload}")
    ]
    
    try:
        response = llm.invoke(messages)
        raw = response.content
        
        # 안전성 검사
        if contains_investment_advice(raw):
            return {"n8_concept_explanation": fallback_result_learning()}
        
        # JSON 파싱
        parsed = parse_json(raw)
        if not parsed:
            return {"n8_concept_explanation": fallback_result_learning()}
        
        # learning_guide가 있는지 확인
        if "learning_guide" in parsed:
            return {
                "n8_concept_explanation": {
                    "mode": "learning",
                    "term_explanation": None,
                    "learning_guide": parsed["learning_guide"]
                }
            }
        
        return {"n8_concept_explanation": fallback_result_learning()}
    
    except Exception as e:
        print(f"N8 학습 가이드 생성 중 오류: {e}")
        return {"n8_concept_explanation": fallback_result_learning()}


def fallback_result(error_message: str = "데이터를 확보하지 못했습니다.") -> Dict[str, Any]:
    """
    일반 에러 시 fallback
    """
    return {
        "mode": "error",
        "term_explanation": None,
        "learning_guide": None,
        "error_message": error_message,
        "uncertainty_level": "high"
    }


def fallback_result_term(term: Any) -> Dict[str, Any]:
    """
    용어 설명 실패 시 fallback
    """
    return {
        "mode": "term",
        "term_explanation": {
            "term": str(term),
            "short_summary": "용어 설명을 생성하지 못했습니다.",
            "detailed_explanation": "외부 지식 리소스가 연결되지 않았거나 용어 정보를 찾을 수 없습니다.",
            "simple_example": "예시를 제공할 수 없습니다.",
            "usage_context": "정보 부족",
            "related_terms": [],
            "uncertainty_level": "high"
        },
        "learning_guide": None
    }


def fallback_result_learning() -> Dict[str, Any]:
    """
    학습 가이드 생성 실패 시 fallback
    """
    return {
        "mode": "learning",
        "term_explanation": None,
        "learning_guide": {
            "weakness_summary": "투자 패턴을 분석하지 못했습니다.",
            "weakness_detailed": "충분한 정보가 제공되지 않았거나 분석에 실패했습니다. 더 구체적인 투자 내역을 제공해 주세요.",
            "learning_path_summary": "기본 투자 지식부터 시작하세요.",
            "learning_path_detailed": {
                "step1": "주식 투자 기초 개념 학습",
                "step2": "기술적 분석 기본 지표 이해",
                "step3": "리스크 관리 원칙 습득"
            },
            "recommended_topics": ["주식 기초", "기술적 분석", "리스크 관리"],
            "estimated_difficulty": "보통",
            "uncertainty_level": "high"
        }
    }


# RAG 연동 함수 (TODO: 실제 RAG 구현)
def search_term_in_knowledge_base(term: str) -> str:
    """
    RAG를 사용하여 지식 베이스에서 용어 검색
    
    Args:
        term: 검색할 용어
    
    Returns:
        검색된 컨텍스트 문자열
    
    TODO: LangChain RAG 구현
    - 벡터 DB 구축 (Chroma, FAISS 등)
    - 경제/주식 용어 문서 임베딩
    - 유사도 기반 검색
    """
    # 임시 구현 - 추후 실제 RAG로 교체
    return ""


def contains_investment_advice(text: str) -> bool:
    """
    N8 전용 안전성 검사
    
    용어 설명이나 교육적 내용은 허용하고,
    직접적인 매수/매도 조언만 차단
    """
    import re
    
    # 직접적인 행동 유도만 차단
    strict_advice_patterns = [
        r"(지금|당장|빨리)\s*(매수|매도|사세요|파세요)",
        r"(이|저)\s*종목(을|를)\s*(사|팔)",
        r"목표가\s*\d+원",
        r"반드시\s*(사|팔|투자)",
    ]
    
    for pattern in strict_advice_patterns:
        if re.search(pattern, text):
            return True
    
    return False
