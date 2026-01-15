"""
Golden Dataset 배치 처리 스크립트

golden_dataset.json의 모든 테스트 케이스를 분석하고 
결과를 metrics/results/ 에 저장합니다.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 프로젝트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from metrics.golden_generator import load_golden_dataset
from metrics.evaluator import BatchEvaluator, MetricsEvaluator
from metrics.storage import save_metrics_json, append_metrics_csv
from core.llm import get_solar_chat


async def create_mock_analysis(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    프론트엔드 입력을 워크플로우 상태로 변환
    (실제 분석 함수 호출 또는 목업 데이터)
    """
    # TODO: 실제 워크플로우 사용
    # from workflow.graph import build_graph
    # graph = build_graph()
    # return await asyncio.to_thread(graph.invoke, state)
    
    # 임시 목업 데이터
    return {
        "request_id": f"batch_{input_data['layer1_stock']}_{datetime.now().isoformat()}",
        "layer1_stock": input_data["layer1_stock"],
        "layer2_buy_date": input_data["layer2_buy_date"],
        "layer2_sell_date": input_data["layer2_sell_date"],
        "position_status": input_data.get("position_status", "sold"),
        "layer3_decision_basis": input_data["layer3_decision_basis"],
        "n8_loss_cause_analysis": {
            "root_causes": [
                {
                    "title": "Market Condition",
                    "description": "글로벌 시장 변동성 증가",
                    "confidence": 0.85
                }
            ]
        },
        "n7_news_analysis": {
            "news_context": {
                "ticker": input_data["layer1_stock"],
                "period": {
                    "buy_date": input_data["layer2_buy_date"],
                    "sell_date": input_data["layer2_sell_date"]
                },
                "key_headlines": [
                    {
                        "title": "Sample News",
                        "content": "분석 대상 뉴스",
                        "date": input_data["layer2_buy_date"]
                    }
                ]
            }
        },
        "learning_pattern_analysis": {
            "learning_recommendation": {
                "focus_area": "시장 분석",
                "learning_steps": ["Step 1", "Step 2"],
                "recommended_topics": ["Market Analysis", "Risk Management"]
            }
        }
    }


async def process_single_case(
    case: Dict[str, Any],
    evaluator: MetricsEvaluator,
    case_number: int,
    total_cases: int
) -> Dict[str, Any]:
    """
    단일 테스트 케이스 처리
    """
    print(f"\n[{case_number}/{total_cases}] {case['id']} - {case['scenario']} 처리 중...")
    
    try:
        # 분석 실행
        start_time = datetime.now()
        analysis_result = await create_mock_analysis(case["input"])
        end_time = datetime.now()
        
        # 메트릭 평가
        report = await evaluator.evaluate_all(
            request_id=case["id"],
            start_time=start_time,
            end_time=end_time,
            validation_results=[True, True, True],  # 성공 가정
            news_data={
                "ticker": case["input"]["layer1_stock"],
                "buy_date": case["input"]["layer2_buy_date"],
                "sell_date": case["input"]["layer2_sell_date"],
                "items": [],
                "dates": []
            },
            analysis_result=analysis_result,
            golden_truth=case,
            save_results=True  # 자동 저장
        )
        
        print(f"✓ {case['id']} 완료")
        return {
            "status": "success",
            "case_id": case["id"],
            "scenario": case["scenario"],
            "metrics_summary": report.get("summary", {})
        }
        
    except Exception as e:
        print(f"✗ {case['id']} 실패: {str(e)}")
        return {
            "status": "failed",
            "case_id": case["id"],
            "scenario": case["scenario"],
            "error": str(e)
        }


async def run_batch_processing(use_llm: bool = False):
    """
    Golden Dataset 전체 배치 처리
    
    Args:
        use_llm: LLM 기반 평가 포함 여부
    """
    print("=" * 60)
    print("🚀 Golden Dataset 배치 처리 시작")
    print("=" * 60)
    
    # 1. Golden Dataset 로드
    print("\n📂 Golden Dataset 로드 중...")
    golden_dataset = load_golden_dataset()
    
    if not golden_dataset or not golden_dataset.get("test_cases"):
        print("❌ Golden Dataset을 찾을 수 없습니다.")
        return
    
    test_cases = golden_dataset["test_cases"]
    print(f"✓ {len(test_cases)}개의 테스트 케이스 로드됨")
    
    # 2. LLM 초기화 (필요 시)
    llm = None
    if use_llm:
        print("\n🤖 LLM 초기화 중...")
        try:
            llm = await get_solar_chat()
            print("✓ LLM 초기화 완료")
        except Exception as e:
            print(f"⚠️ LLM 초기화 실패: {e}")
            print("   기본 메트릭만 평가합니다.")
    
    # 3. 평가기 생성
    evaluator = MetricsEvaluator(llm=llm)
    
    # 4. 배치 처리 시작
    print(f"\n📊 배치 처리 시작 ({len(test_cases)}개 케이스)...")
    print("-" * 60)
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, case in enumerate(test_cases, 1):
        result = await process_single_case(case, evaluator, i, len(test_cases))
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
        else:
            failed_count += 1
    
    # 5. 결과 요약
    print("\n" + "=" * 60)
    print("📈 배치 처리 완료")
    print("=" * 60)
    print(f"✓ 성공: {success_count}/{len(test_cases)}")
    print(f"✗ 실패: {failed_count}/{len(test_cases)}")
    print(f"\n💾 결과는 metrics/results/ 에 저장되었습니다")
    
    # 6. 상세 결과 요약
    print("\n" + "=" * 60)
    print("📋 개별 결과 요약")
    print("=" * 60)
    
    for result in results:
        status_icon = "✓" if result["status"] == "success" else "✗"
        scenario = result.get("scenario", "unknown")
        print(f"{status_icon} {result['case_id']} ({scenario})")
        
        if result["status"] == "success":
            summary = result.get("metrics_summary", {})
            if summary:
                print(f"   Impact: {summary.get('impact', 'N/A')}%")
                print(f"   Trust: {summary.get('trust', 'N/A')}%")
                print(f"   Stability: {summary.get('stability', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # 7. 최종 통계
    print("\n" + "=" * 60)
    print("📊 최종 통계")
    print("=" * 60)
    
    overall_results = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(test_cases),
        "successful": success_count,
        "failed": failed_count,
        "success_rate": round((success_count / len(test_cases) * 100) if test_cases else 0, 1),
        "individual_results": results,
        "results_location": str(Path(__file__).parent / "results")
    }
    
    print(f"처리 시간: {datetime.now().isoformat()}")
    print(f"성공률: {overall_results['success_rate']}%")
    print(f"저장 위치: {overall_results['results_location']}")
    
    return overall_results


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Golden Dataset 배치 처리")
    parser.add_argument(
        "--llm",
        action="store_true",
        help="LLM 기반 평가 포함 (느리지만 정확함)"
    )
    
    args = parser.parse_args()
    
    # 비동기 실행
    asyncio.run(run_batch_processing(use_llm=args.llm))


if __name__ == "__main__":
    main()
