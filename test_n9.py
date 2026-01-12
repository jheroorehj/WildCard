"""
N9 Fallback Handler 테스트

Node9는 Node5에서 general_chat으로 분류된 메시지를 처리하는 폴백 핸들러입니다.
투자 조언 없이 친절한 일반 대화를 제공합니다.
"""

import json
from N9_Fallback_Handler.n9 import node9_fallback_handler


def test_n9_general_chat():
    """일반 대화 테스트"""
    print("\n" + "="*80)
    print("TEST 1: 일반 대화 (인사)")
    print("="*80)

    state = {
        "user_message": "안녕하세요! 오늘 날씨 좋네요.",
        "context": "사용자가 인사를 하고 있음"
    }

    result = node9_fallback_handler(state)

    print("\n[입력]")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print("\n[출력]")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 검증
    assert "fallback_response" in result, "fallback_response 키가 없습니다"
    assert "message" in result["fallback_response"], "message 키가 없습니다"
    assert "intent_hint" in result["fallback_response"], "intent_hint 키가 없습니다"
    assert result["fallback_response"]["intent_hint"] in ["general_chat", "investing_help", "unknown"], \
        f"허용되지 않은 intent_hint: {result['fallback_response']['intent_hint']}"

    print("\n✓ 스키마 검증 통과")


def test_n9_investing_question():
    """투자 관련 질문 (조언 없이 안내)"""
    print("\n" + "="*80)
    print("TEST 2: 투자 관련 질문 (조언 없이 정보 제공)")
    print("="*80)

    state = {
        "user_message": "주식 투자를 시작하려면 어떻게 해야 하나요?",
        "context": "투자 초보자가 일반적인 질문을 하고 있음"
    }

    result = node9_fallback_handler(state)

    print("\n[입력]")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print("\n[출력]")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 검증: 투자 조언이 포함되지 않았는지 확인
    message = result["fallback_response"]["message"]

    # 금지된 조언 패턴 검사
    forbidden_patterns = ["사세요", "파세요", "추천", "매수", "매도", "목표가"]
    for pattern in forbidden_patterns:
        assert pattern not in message, f"투자 조언 포함 감지: {pattern}"

    print("\n✓ 스키마 검증 통과")
    print("✓ 투자 조언 없음 확인")


def test_n9_unclear_intent():
    """의도가 불분명한 메시지"""
    print("\n" + "="*80)
    print("TEST 3: 의도가 불분명한 메시지")
    print("="*80)

    state = {
        "user_message": "음... 그게...",
        "context": "사용자의 의도가 불명확함"
    }

    result = node9_fallback_handler(state)

    print("\n[입력]")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print("\n[출력]")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 검증
    assert "fallback_response" in result
    assert isinstance(result["fallback_response"]["message"], str)
    assert len(result["fallback_response"]["message"]) > 0, "응답 메시지가 비어있습니다"

    print("\n✓ 스키마 검증 통과")


def test_n9_contextual_response():
    """컨텍스트를 활용한 응답"""
    print("\n" + "="*80)
    print("TEST 4: 컨텍스트를 활용한 응답")
    print("="*80)

    state = {
        "user_message": "더 알려주세요",
        "context": "이전에 손실 분석에 대해 대화했음. 사용자가 추가 정보를 요청하고 있음."
    }

    result = node9_fallback_handler(state)

    print("\n[입력]")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print("\n[출력]")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 검증
    assert "fallback_response" in result
    assert result["fallback_response"]["intent_hint"] in ["general_chat", "investing_help", "unknown"]

    print("\n✓ 스키마 검증 통과")


def test_n9_empty_context():
    """컨텍스트가 없는 경우"""
    print("\n" + "="*80)
    print("TEST 5: 컨텍스트 없음")
    print("="*80)

    state = {
        "user_message": "테슬라가 뭐예요?",
        "context": ""
    }

    result = node9_fallback_handler(state)

    print("\n[입력]")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print("\n[출력]")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 검증
    assert "fallback_response" in result
    assert isinstance(result["fallback_response"]["message"], str)

    print("\n✓ 스키마 검증 통과")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*80)
    print("N9 FALLBACK HANDLER 테스트 시작")
    print("="*80)

    tests = [
        ("일반 대화 테스트", test_n9_general_chat),
        ("투자 질문 테스트", test_n9_investing_question),
        ("불분명한 의도 테스트", test_n9_unclear_intent),
        ("컨텍스트 활용 테스트", test_n9_contextual_response),
        ("빈 컨텍스트 테스트", test_n9_empty_context),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n✓ {test_name} 성공")
        except AssertionError as e:
            failed += 1
            print(f"\n✗ {test_name} 실패: {e}")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name} 에러: {e}")

    print("\n" + "="*80)
    print("테스트 결과 요약")
    print("="*80)
    print(f"통과: {passed}/{len(tests)}")
    print(f"실패: {failed}/{len(tests)}")
    print(f"성공률: {passed/len(tests)*100:.1f}%")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_all_tests()
