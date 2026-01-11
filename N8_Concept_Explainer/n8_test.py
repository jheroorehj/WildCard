"""
N8 Concept Explainer 테스트
"""

from n8 import node8_concept_explainer


def test_term_explanation():
    """용어 설명 모드 테스트"""
    print("=" * 50)
    print("테스트 1: 용어 설명 모드")
    print("=" * 50)
    
    state = {
        "mode": "term",
        "term": "볼린저 밴드",
        "context": "주가 분석 중 볼린저 밴드라는 용어를 접했습니다."
    }
    
    result = node8_concept_explainer(state)
    print("\n입력:")
    print(f"  - 용어: {state['term']}")
    print(f"  - 맥락: {state['context']}")
    
    print("\n출력:")
    explanation = result.get("n8_concept_explanation", {})
    if explanation.get("mode") == "term":
        term_exp = explanation.get("term_explanation", {})
        print(f"  - 용어: {term_exp.get('term')}")
        print(f"  - 한줄 요약: {term_exp.get('short_summary')}")
        print(f"  - 상세 설명: {term_exp.get('detailed_explanation')[:100]}...")
        print(f"  - 예시: {term_exp.get('simple_example')}")
        print(f"  - 불확실성: {term_exp.get('uncertainty_level')}")
    else:
        print("  - 에러 발생")
        print(f"  - 메시지: {explanation}")


def test_learning_guide():
    """학습 가이드 모드 테스트"""
    print("\n" + "=" * 50)
    print("테스트 2: 학습 가이드 모드")
    print("=" * 50)
    
    state = {
        "mode": "learning",
        "investment_pattern": "유튜브 추천 영상을 보고 충동적으로 매수했습니다.",
        "loss_causes": [
            {"type": "information_bias", "description": "검증되지 않은 정보 신뢰"},
            {"type": "emotional_trading", "description": "충동적 의사결정"}
        ],
        "context": "손실 후 어떤 부분을 공부해야 할지 모르겠습니다."
    }
    
    result = node8_concept_explainer(state)
    print("\n입력:")
    print(f"  - 투자 패턴: {state['investment_pattern']}")
    print(f"  - 손실 원인: {len(state['loss_causes'])}개")
    
    print("\n출력:")
    explanation = result.get("n8_concept_explanation", {})
    if explanation.get("mode") == "learning":
        guide = explanation.get("learning_guide", {})
        print(f"  - 부족한 부분 요약: {guide.get('weakness_summary')}")
        print(f"  - 학습 방법 요약: {guide.get('learning_path_summary')}")
        print(f"  - 추천 주제: {guide.get('recommended_topics')}")
        print(f"  - 난이도: {guide.get('estimated_difficulty')}")
        print(f"  - 불확실성: {guide.get('uncertainty_level')}")
    else:
        print("  - 에러 발생")
        print(f"  - 메시지: {explanation}")


def test_fallback():
    """Fallback 테스트"""
    print("\n" + "=" * 50)
    print("테스트 3: Fallback (용어 없음)")
    print("=" * 50)
    
    state = {
        "mode": "term",
        # term 누락
        "context": "테스트"
    }
    
    result = node8_concept_explainer(state)
    print("\n입력:")
    print(f"  - 용어: (없음)")
    
    print("\n출력:")
    explanation = result.get("n8_concept_explanation", {})
    term_exp = explanation.get("term_explanation", {})
    print(f"  - 한줄 요약: {term_exp.get('short_summary')}")
    print(f"  - 불확실성: {term_exp.get('uncertainty_level')}")


if __name__ == "__main__":
    print("\n🧪 N8 Concept Explainer 테스트 시작\n")
    
    try:
        test_term_explanation()
        test_learning_guide()
        test_fallback()
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
