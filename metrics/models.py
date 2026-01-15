"""
Metrics Data Models

METRIC_GUIDE_V2.md 기반 3-Tier 평가 체계 데이터 모델 정의
"""

from typing import TypedDict, Dict, Any, List, Optional
from enum import Enum


class MetricTier(str, Enum):
    """평가 지표 계층"""
    IMPACT = "impact"       # Tier 1: Business Impact
    TRUST = "trust"         # Tier 2: Reliability & Trust
    STABILITY = "stability" # Tier 3: System Stability


class MetricResult(TypedDict):
    """개별 메트릭 측정 결과"""
    metric_name: str        # 메트릭 이름 (예: "E2E Latency")
    tier: str               # 소속 Tier ("impact", "trust", "stability")
    value: float            # 측정값
    target: float           # 목표치
    passed: bool            # 목표 달성 여부
    timestamp: str          # 측정 시간 (ISO format)
    request_id: str         # 요청 ID
    metadata: Dict[str, Any]  # 추가 메타데이터


class EvaluationReport(TypedDict):
    """전체 평가 리포트"""
    request_id: str                    # 요청 ID
    timestamp: str                     # 평가 시간
    metrics: List[MetricResult]        # 개별 메트릭 결과 리스트
    summary: Dict[str, float]          # Tier별 통과율 요약


class GoldenTestInput(TypedDict):
    """Golden Dataset 테스트 케이스 입력 (프론트엔드 형식 반영)"""
    layer1_stock: str                  # 종목명
    layer2_buy_date: str               # 거래시작일 (YYYY-MM-DD)
    layer2_sell_date: str              # 거래종료일 (YYYY-MM-DD)
    position_status: str               # 보유/매도 상태 ('holding' | 'sold')
    layer3_decision_basis: str         # 투자 결정 근거 (쉼표로 구분)
    patterns: List[str]                # 매매패턴 배열


class GoldenTestCase(TypedDict):
    """Golden Dataset 테스트 케이스"""
    id: str                            # 테스트 케이스 ID (예: "TC001")
    scenario: str                      # 시나리오 유형
    description: str                   # 시나리오 설명
    input: GoldenTestInput             # 입력 데이터 (프론트엔드 형식)
    user_belief: str                   # 사용자 믿음 (layer3_decision_basis와 별도)
    ground_truth: Dict[str, Any]       # 정답 데이터
    user_belief_correct: bool          # 사용자 믿음의 정확성
    expected_blind_spot_score: float   # 예상 Blind Spot 점수


class GoldenDataset(TypedDict):
    """Golden Dataset 전체 구조"""
    version: str
    generated_at: str
    description: str
    input_format: Dict[str, str]       # 입력 필드 설명
    decision_options: List[str]        # 투자 결정 근거 옵션
    trade_patterns: List[str]          # 매매패턴 옵션
    test_cases: List[GoldenTestCase]


# 프론트엔드 상수 (constants.tsx와 동기화)
DECISION_OPTIONS = [
    "유튜브/인플루언서 추천",
    "뉴스/미디어 보도",
    "커뮤니티(종토방, 레딧 등)",
    "지인/전문가 추천",
    "차트 기술적 지표 분석",
    "기업 재무제표 분석",
    "단순 직감/감",
    "FOMO (남들 다 사길래)",
    "공시/공식 발표"
]

TRADE_PATTERNS = [
    "분할 매수 (Scaling In)",
    "분할 매도 (Scaling Out)",
    "물타기 (단가 낮추기)",
    "불타기 (단가 올리기)",
    "손절매 (Stop Loss)",
    "장기 보유 (Buy & Hold)",
    "단기 스캘핑 (Scalping)"
]


# 메트릭별 목표치 상수
METRIC_TARGETS = {
    # Tier 1: Impact
    "blind_spot_detection_rate": 0.40,      # > 40%
    "time_to_insight_efficiency": 99.0,      # > 99%
    "actionability_score": 4.2,              # > 4.2 (5점 만점)

    # Tier 2: Trust
    "zero_anachronism_rate": 100.0,          # 100%
    "signal_to_noise_ratio": 70.0,           # > 70%
    "fact_consistency_score": 95.0,          # > 95%

    # Tier 3: Stability
    "e2e_latency": 15.0,                     # < 15초
    "json_stability_rate": 99.0,             # > 99%
}

# 인간 기준선 상수
HUMAN_BASELINE = {
    "avg_analysis_time_seconds": 30 * 60,    # 30분
}
