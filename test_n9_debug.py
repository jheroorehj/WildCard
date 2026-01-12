"""
N9 Fallback Handler 디버그 테스트

LLM의 실제 응답을 확인하기 위한 디버그 테스트
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from core.llm import get_solar_chat
from N9_Fallback_Handler.prompt import NODE9_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.validator import validate_node9


def test_n9_llm_response():
    """N9의 LLM 응답 확인"""
    print("\n" + "="*80)
    print("N9 LLM 응답 디버그 테스트")
    print("="*80)

    llm = get_solar_chat()

    test_cases = [
        {
            "name": "일반 대화",
            "state": {
                "user_message": "안녕하세요! 오늘 날씨 좋네요.",
                "context": "사용자가 인사를 하고 있음"
            }
        },
        {
            "name": "투자 질문",
            "state": {
                "user_message": "주식 투자를 시작하려면 어떻게 해야 하나요?",
                "context": "투자 초보자가 일반적인 질문을 하고 있음"
            }
        },
        {
            "name": "빈 컨텍스트",
            "state": {
                "user_message": "테슬라가 뭐예요?",
                "context": ""
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n{'='*80}")
        print(f"테스트: {test_case['name']}")
        print("="*80)

        state = test_case["state"]
        payload = {
            "user_message": state["user_message"],
            "context": state.get("context", ""),
        }

        messages = [
            SystemMessage(content=NODE9_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "아래 입력을 바탕으로 응답하세요.\n"
                    "출력은 반드시 JSON만 반환하세요.\n"
                    f"{payload}"
                )
            ),
        ]

        print("\n[입력 payload]")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        # LLM 호출
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)

        print("\n[LLM 원본 응답]")
        print(raw)
        print()

        # JSON 파싱 시도
        parsed = parse_json(raw)

        print("\n[파싱 결과]")
        if parsed:
            print(json.dumps(parsed, ensure_ascii=False, indent=2))

            # 검증 시도
            print("\n[검증 결과]")
            if isinstance(parsed, dict):
                is_valid = validate_node9(parsed)
                print(f"validate_node9: {is_valid}")

                if not is_valid:
                    print("\n검증 실패 이유 분석:")
                    if "fallback_response" not in parsed:
                        print("- 'fallback_response' 키가 없음")
                    else:
                        response_obj = parsed.get("fallback_response")
                        if not isinstance(response_obj, dict):
                            print(f"- 'fallback_response'가 dict가 아님: {type(response_obj)}")
                        else:
                            if "message" not in response_obj:
                                print("- 'message' 키가 없음")
                            elif not isinstance(response_obj.get("message"), str):
                                print(f"- 'message'가 str이 아님: {type(response_obj.get('message'))}")

                            if "intent_hint" not in response_obj:
                                print("- 'intent_hint' 키가 없음")
                            else:
                                intent = response_obj.get("intent_hint")
                                allowed = {"general_chat", "investing_help", "unknown"}
                                if intent not in allowed:
                                    print(f"- 'intent_hint'가 허용되지 않은 값: {intent}")
                                    print(f"  허용된 값: {allowed}")
            else:
                print(f"파싱 결과가 dict가 아님: {type(parsed)}")
        else:
            print("JSON 파싱 실패")

    print("\n" + "="*80)
    print("디버그 테스트 완료")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_n9_llm_response()
