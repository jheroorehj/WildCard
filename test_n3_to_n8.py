"""
N3 → N8 통합 테스트
시나리오: 2025-11-03 테슬라 매수 → 2025-11-25 매도 (지인 추천)
"""

from N3_Loss_Analyzer.n3 import node3_loss_analyzer
from N8_Concept_Explainer.n8 import node8_concept_explainer
import json


def test_n3_to_n8_flow():
    """N3 → N8 플로우 테스트"""
    print("=" * 70)
    print("📊 N3 → N8 통합 테스트")
    print("시나리오: 테슬라 투자 (지인 추천)")
    print("=" * 70)
    
    # Step 1: N3 가이드라인 생성
    print("\n[Step 1] N3: 손실 분석 가이드라인 생성")
    print("-" * 70)
    
    n3_state = {
        "layer1_stock": "TSLA",
        "layer2_buy_date": "2025-11-03",
        "layer2_sell_date": "2025-11-25",
        "layer3_decision_basis": "지인이 테슬라가 오를 거라고 추천해서 매수했습니다."
    }
    
    print(f"입력:")
    print(f"  - 종목: {n3_state['layer1_stock']}")
    print(f"  - 매수일: {n3_state['layer2_buy_date']}")
    print(f"  - 매도일: {n3_state['layer2_sell_date']}")
    print(f"  - 의사결정: {n3_state['layer3_decision_basis']}")
    
    n3_result = node3_loss_analyzer(n3_state)
    n3_guideline = n3_result.get("n3_loss_diagnosis", {})
    
    print(f"\n출력:")
    if "n8_loss_cause_guideline" in n3_guideline:
        n8_guideline = n3_guideline["n8_loss_cause_guideline"]
        print(f"  ✓ N8 가이드라인 생성됨")
        print(f"    - 목적: {n8_guideline.get('objective', 'N/A')}")
        print(f"    - 손실 원인 개수: {n8_guideline.get('loss_cause_count', 0)}개")
        print(f"    - 손실 원인 유형: {n8_guideline.get('loss_cause_types', [])}")
    else:
        print(f"  ✗ N8 가이드라인 생성 실패")
        print(f"  Fallback 결과: {json.dumps(n3_guideline, indent=2, ensure_ascii=False)}")
    
    # Step 2: N8 용어 설명 - "정보 검증" 용어 설명
    print("\n\n[Step 2] N8: 용어 설명 모드 (정보 검증)")
    print("-" * 70)
    
    n8_term_state = {
        "mode": "term",
        "term": "정보 검증",
        "context": "지인 추천으로 투자했는데, 정보 검증이 뭔지 모르겠어요."
    }
    
    print(f"입력:")
    print(f"  - 모드: {n8_term_state['mode']}")
    print(f"  - 용어: {n8_term_state['term']}")
    print(f"  - 맥락: {n8_term_state['context']}")
    
    n8_term_result = node8_concept_explainer(n8_term_state)
    n8_term_exp = n8_term_result.get("n8_concept_explanation", {})
    
    print(f"\n출력:")
    if n8_term_exp.get("mode") == "term":
        term_data = n8_term_exp.get("term_explanation", {})
        print(f"  ✓ 용어 설명 생성됨")
        print(f"    - 용어: {term_data.get('term')}")
        print(f"    - 한줄 요약: {term_data.get('short_summary')}")
        print(f"    - 상세 설명: {term_data.get('detailed_explanation', '')[:100]}...")
        print(f"    - 예시: {term_data.get('simple_example')}")
        print(f"    - 불확실성: {term_data.get('uncertainty_level')}")
    else:
        print(f"  ✗ 용어 설명 생성 실패")
        print(f"  에러: {n8_term_exp.get('error_message', 'Unknown')}")
    
    # Step 3: N8 학습 가이드 - 투자 패턴 분석
    print("\n\n[Step 3] N8: 학습 가이드 모드 (투자 패턴 분석)")
    print("-" * 70)
    
    n8_learning_state = {
        "mode": "learning",
        "investment_pattern": n3_state["layer3_decision_basis"],
        "loss_causes": [
            {
                "type": "information_bias",
                "description": "검증되지 않은 지인 추천 정보를 맹신"
            },
            {
                "type": "emotional_trading",
                "description": "FOMO(놓칠까봐 두려움)로 인한 충동 매수"
            }
        ],
        "context": "앞으로 어떻게 투자해야 할지 모르겠습니다. 무엇을 공부해야 하나요?"
    }
    
    print(f"입력:")
    print(f"  - 모드: {n8_learning_state['mode']}")
    print(f"  - 투자 패턴: {n8_learning_state['investment_pattern']}")
    print(f"  - 손실 원인: {len(n8_learning_state['loss_causes'])}개")
    for i, cause in enumerate(n8_learning_state['loss_causes'], 1):
        print(f"    {i}. {cause['type']}: {cause['description']}")
    
    n8_learning_result = node8_concept_explainer(n8_learning_state)
    n8_learning_guide = n8_learning_result.get("n8_concept_explanation", {})
    
    print(f"\n출력:")
    if n8_learning_guide.get("mode") == "learning":
        guide_data = n8_learning_guide.get("learning_guide", {})
        print(f"  ✓ 학습 가이드 생성됨")
        print(f"    - 부족한 부분 요약: {guide_data.get('weakness_summary')}")
        print(f"    - 학습 방법 요약: {guide_data.get('learning_path_summary')}")
        print(f"    - 추천 주제: {guide_data.get('recommended_topics')}")
        print(f"    - 난이도: {guide_data.get('estimated_difficulty')}")
        print(f"    - 불확실성: {guide_data.get('uncertainty_level')}")
        
        print(f"\n    [상세 학습 경로]")
        learning_path = guide_data.get('learning_path_detailed', {})
        for step, desc in learning_path.items():
            print(f"      {step}: {desc}")
    else:
        print(f"  ✗ 학습 가이드 생성 실패")
        print(f"  에러: {n8_learning_guide.get('error_message', 'Unknown')}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("📝 테스트 요약")
    print("=" * 70)
    print(f"N3 가이드라인: {'✓ 성공' if 'n8_loss_cause_guideline' in n3_guideline else '✗ 실패'}")
    print(f"N8 용어 설명: {'✓ 성공' if n8_term_exp.get('mode') == 'term' else '✗ 실패'}")
    print(f"N8 학습 가이드: {'✓ 성공' if n8_learning_guide.get('mode') == 'learning' else '✗ 실패'}")
    print("=" * 70)
    
    # 전체 결과 저장
    full_result = {
        "scenario": {
            "stock": "TSLA",
            "buy_date": "2025-11-03",
            "sell_date": "2025-11-25",
            "decision_basis": "지인 추천"
        },
        "n3_guideline": n3_guideline,
        "n8_term_explanation": n8_term_exp,
        "n8_learning_guide": n8_learning_guide
    }
    
    with open("test_n3_to_n8_result.json", "w", encoding="utf-8") as f:
        json.dump(full_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n전체 결과가 test_n3_to_n8_result.json에 저장되었습니다.")


if __name__ == "__main__":
    try:
        test_n3_to_n8_flow()
        print("\n✅ 테스트 완료")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
