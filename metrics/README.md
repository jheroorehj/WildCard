# WildCard-W 메트릭 평가 시스템

## 개요

METRIC_GUIDE_V2.md 기반 3-Tier 정량적 평가 시스템입니다.

## 메트릭 구조

### Tier 1: Business Impact (핵심 가치)
| 메트릭 | 목표치 | 설명 |
|--------|--------|------|
| Blind Spot Detection Rate | > 40% | 사용자 맹점 교정 비율 |
| Time-to-Insight Efficiency | > 99% | 인간 대비 분석 시간 단축률 |
| Actionability Score | > 4.2 | 실행 가능한 지침 제공 정도 (1-5점) |

### Tier 2: Reliability & Trust (신뢰성)
| 메트릭 | 목표치 | 설명 |
|--------|--------|------|
| Zero-Anachronism Rate | 100% | 미래 정보 참조 오류 없음 |
| Signal-to-Noise Ratio | > 70% | 핵심 뉴스 비율 |
| Fact-Consistency Score | > 95% | 팩트 정합성 |

### Tier 3: System Stability (안정성)
| 메트릭 | 목표치 | 설명 |
|--------|--------|------|
| E2E Latency | < 15s | 전체 응답 시간 |
| JSON Stability Rate | > 99% | JSON 스키마 준수율 |

---

## 평가 실행 방법

### 방법 1: API를 통한 자동 평가

분석 API 호출 시 자동으로 기본 메트릭이 평가됩니다.

```bash
# 분석 요청 (기본 메트릭 자동 포함)
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "layer1_stock": "삼성전자",
    "layer2_buy_date": "2024-01-15",
    "layer2_sell_date": "2024-02-15",
    "position_status": "sold",
    "layer3_decision_basis": "뉴스/미디어 보도, 기업 재무제표 분석"
  }'
```

응답에 `metrics_summary` 필드가 포함됩니다:
```json
{
  "request_id": "uuid-1234",
  "metrics_summary": {
    "impact": 100.0,
    "trust": 100.0,
    "stability": 100.0,
    "overall": 100.0
  },
  ...
}
```

### 방법 2: LLM Judge 포함 전체 평가

LLM을 사용한 상세 평가가 필요한 경우:

```bash
curl -X POST http://localhost:8000/v1/metrics/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "layer1_stock": "삼성전자",
    "layer2_buy_date": "2024-01-15",
    "layer2_sell_date": "2024-02-15",
    "position_status": "sold",
    "layer3_decision_basis": "뉴스/미디어 보도, 기업 재무제표 분석"
  }'
```

### 방법 3: 메트릭 결과 조회

```bash
# 특정 요청 메트릭 조회
curl http://localhost:8000/v1/metrics/{request_id}

# 전체 메트릭 이력 조회
curl http://localhost:8000/v1/metrics?limit=100

# Tier별 통계 요약
curl http://localhost:8000/v1/metrics/summary
```

### 방법 4: Golden Dataset 배치 테스트 (Python)

```python
import asyncio
import json
from metrics.evaluator import BatchEvaluator
from metrics.golden_generator import load_golden_dataset
from core.llm import get_solar_chat
from workflow.graph import build_graph

async def run_batch_test():
    # Golden Dataset 로드
    dataset = load_golden_dataset()
    cases = dataset["test_cases"]

    # LLM 및 그래프 초기화
    llm = get_solar_chat()
    graph = build_graph()

    # 분석 함수 정의
    async def analyze(input_data):
        state = {
            "layer1_stock": input_data["layer1_stock"],
            "layer2_buy_date": input_data["layer2_buy_date"],
            "layer2_sell_date": input_data["layer2_sell_date"],
            "layer3_decision_basis": input_data["layer3_decision_basis"],
            "position_status": input_data.get("position_status", "sold"),
            "user_message": input_data["layer3_decision_basis"],
        }
        return await asyncio.to_thread(graph.invoke, state)

    # 배치 평가 실행
    evaluator = BatchEvaluator(llm=llm)
    results = await evaluator.evaluate_golden_dataset(cases, analyze)

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(run_batch_test())
```

---

## 입력 형식 (프론트엔드 동기화)

### API 요청 필드

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `layer1_stock` | string | ✓ | 종목명 (예: "삼성전자") |
| `layer2_buy_date` | string | ✓ | 거래시작일 (YYYY-MM-DD) |
| `layer2_sell_date` | string | ✓ | 거래종료일 (YYYY-MM-DD) |
| `position_status` | string | - | 보유/매도 상태 ("holding" \| "sold") |
| `layer3_decision_basis` | string | ✓ | 투자 결정 근거 (쉼표로 구분) |

### 투자 결정 근거 옵션 (중복 선택 가능)

- 유튜브/인플루언서 추천
- 뉴스/미디어 보도
- 커뮤니티(종토방, 레딧 등)
- 지인/전문가 추천
- 차트 기술적 지표 분석
- 기업 재무제표 분석
- 단순 직감/감
- FOMO (남들 다 사길래)
- 공시/공식 발표

### 매매패턴 옵션 (중복 선택 가능)

- 분할 매수 (Scaling In)
- 분할 매도 (Scaling Out)
- 물타기 (단가 낮추기)
- 불타기 (단가 올리기)
- 손절매 (Stop Loss)
- 장기 보유 (Buy & Hold)
- 단기 스캘핑 (Scalping)

---

## 결과 저장 위치

메트릭 결과는 `metrics/results/` 디렉토리에 저장됩니다:

```
metrics/results/
├── metrics_{request_id}_{timestamp}.json   # 개별 요청 결과
└── metrics_history.csv                     # 시계열 누적 데이터
```

### JSON 결과 예시

```json
{
  "request_id": "uuid-1234",
  "timestamp": "2025-01-15T10:30:00",
  "metrics": [
    {
      "metric_name": "E2E Latency",
      "tier": "stability",
      "value": 8.5,
      "target": 15,
      "passed": true,
      "metadata": {"unit": "seconds"}
    },
    {
      "metric_name": "Zero-Anachronism Rate",
      "tier": "trust",
      "value": 100,
      "target": 100,
      "passed": true,
      "metadata": {"total_news": 5, "valid_news": 5}
    }
  ],
  "summary": {
    "impact": 100.0,
    "trust": 100.0,
    "stability": 100.0,
    "overall": 100.0
  }
}
```

---

## Golden Dataset

`metrics/golden_dataset.json`에 14개의 테스트 케이스가 포함되어 있습니다.

### 시나리오 유형

| 시나리오 | 설명 | 케이스 수 |
|----------|------|----------|
| `hidden_truth` | 시장 탓이라 생각했지만 개별 악재가 원인 | 3개 |
| `time_traveler` | 매도 후 발표된 정보를 원인으로 착각 | 2개 |
| `confirmation_bias` | 일부 맞지만 더 큰 요인 존재 | 2개 |
| `external_shock` | 내부 문제라 생각했지만 외부 충격이 원인 | 2개 |
| `technical_miss` | 기술적 지표 무시 | 2개 |
| `herd_behavior` | 군중 심리에 휩쓸림 | 2개 |
| `risk_management_fail` | 손절 기준 없이 물타기 반복 | 1개 |

### 새 테스트 케이스 추가

```python
from metrics.golden_generator import add_manual_case

new_case = {
    "scenario": "hidden_truth",
    "description": "새로운 테스트 시나리오",
    "input": {
        "layer1_stock": "종목명",
        "layer2_buy_date": "2024-01-01",
        "layer2_sell_date": "2024-02-01",
        "position_status": "sold",
        "layer3_decision_basis": "뉴스/미디어 보도",
        "patterns": ["장기 보유 (Buy & Hold)"]
    },
    "user_belief": "사용자가 생각하는 손실 원인",
    "ground_truth": {
        "actual_cause": "실제 손실 원인",
        "category": "external",
        "subcategory": "market_condition",
        "key_evidence": "핵심 증거"
    },
    "user_belief_correct": False,
    "expected_blind_spot_score": 1.0
}

add_manual_case(new_case)
```

---

## 파일 구조

```
metrics/
├── __init__.py           # 모듈 초기화
├── models.py             # 데이터 모델 및 상수
├── storage.py            # 로컬 파일 저장
├── tier1_impact.py       # Tier 1 메트릭 함수
├── tier2_trust.py        # Tier 2 메트릭 함수
├── tier3_stability.py    # Tier 3 메트릭 함수
├── llm_judge.py          # LLM-as-a-Judge 프롬프트
├── golden_generator.py   # Golden Dataset 생성기
├── golden_dataset.json   # 테스트 데이터셋
├── evaluator.py          # 통합 평가 실행기
├── README.md             # 이 문서
└── results/              # 평가 결과 저장 디렉토리
```
