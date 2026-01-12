# -*- coding: utf-8 -*-
from typing import Any, Dict, List
import json

from langchain_core.messages import HumanMessage, SystemMessage
from core.llm import get_solar_chat, get_upstage_embeddings
from .prompt import NODE7_SYSTEM_PROMPT
from utils.json_parser import parse_json
from utils.safety import contains_advice
from utils.validator import validate_node7
from .search_tool import search_news_with_serper

# Repository imports - optional (will be used when available)
try:
    from repository.rdb_repo import RDBRepository
    from repository.vector.vector_repo import ChromaDBRepository
    HAS_REPOSITORY = True
except ImportError:
    HAS_REPOSITORY = False
    print("[WARNING] Repository modules not found. Database features will be disabled.")


def node7_news_summarizer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N7 에이전트: 뉴스 및 시황 분석 노드
    1. N3 분석 결과에서 검색 키워드 추출
    2. Serper API로 뉴스 검색
    3. 검색 결과를 ChromaDB에 저장 (RAG 대비)
    4. LLM을 사용하여 팩트 체크 및 시황 요약 수행
    5. 분석 결과를 Supabase에 저장
    """

    ticker = state.get("layer1_stock", "Unknown")
    buy_date = state.get("layer2_buy_date", "Unknown")
    user_reason = state.get("layer3_decision_basis", "판단 근거 없음")

    n3_analysis = state.get("n3_loss_analysis", {})
    loss_factors = n3_analysis.get("loss_factors", [])

    search_query = f"{ticker} 악재"
    for factor in loss_factors:
        if factor.get("type") == "information_bias":
            missing_check_hint = factor.get("evidence", {}).get("missing_check", "")
            if missing_check_hint:
                search_query = f"{ticker} {missing_check_hint}"
            break

    print(f"[*] N7 searching for: {search_query} around {buy_date}")

    news_results = search_news_with_serper(search_query, date_range=buy_date, num_results=3)

    # ChromaDB 저장 (선택적)
    if HAS_REPOSITORY:
        try:
            v_repo = ChromaDBRepository(collection_name="news_context")
            docs = [f"[{n['source']}] {n['title']}: {n['snippet']}" for n in news_results]
            metadatas = [{"url": n["link"], "date": n["date"]} for n in news_results]

            print(f"[DEBUG] Docs to embed: {len(docs)}")

            # Upstage Embedding 적용
            embedding_model = get_upstage_embeddings()
            embeddings = embedding_model.embed_documents(docs)

            print(f"[DEBUG] Generated embeddings: {len(embeddings)}")

            v_repo.add_documents(
                documents=docs,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            print(f"[*] Saved {len(docs)} news items to ChromaDB.")
        except Exception as e:
            print(f"[WARNING] Failed to save news to VectorDB: {e}")
    else:
        print("[INFO] Skipping ChromaDB storage (repository module not available)")


    llm = get_solar_chat()
    news_text = "\n".join([f"- {n['title']} ({n['source']}, {n['date']})" for n in news_results[:3]])

    prompt = f"""
당신은 전문 투자 뉴스 분석가입니다.
사용자의 매수 판단 근거와 당시 실제 뉴스 데이터를 비교하여 '팩트 체크' 리포트를 작성하세요.

[종목]: {ticker}
[매수일]: {buy_date}
[사용자의 믿음]: {user_reason}

[당시 주요 뉴스]:
{news_text}

[작성 규칙]:
1. 시장의 공포/탐욕 지수(0~100)를 추정하여 포함하세요.
2. 사용자가 놓친 핵심 사실(Fact Check)을 날카롭게 지적하세요.
3. 투자 조언은 하지 말고, '사실의 괴리'에만 집중하세요.
4. 반드시 아래 JSON 형식으로만 출력하세요.

{{
  "summary": "전체 시황 요약",
  "market_sentiment": {{
    "index": 45,
    "label": "neutral",
    "description": "당시 시장 분위기 설명"
  }},
  "fact_check": {{
    "user_belief": "{user_reason}",
    "actual_fact": "실제 뉴스 기반 사실",
    "verdict": "정보 일치/불일치/편향 여부"
  }}
}}
""".strip()

    try:
        response = llm.invoke(prompt)
        content = response.content.replace("```json", "").replace("```", "").strip()
        analysis_json = json.loads(content)
    except Exception as e:
        print(f"[ERROR] LLM analysis failed: {e}")
        analysis_json = {
            "summary": "분석 실패",
            "market_sentiment": {"index": 50, "label": "unknown", "description": ""},
            "fact_check": {"user_belief": user_reason, "actual_fact": "분석 오류", "verdict": "unknown"},
        }

    output_data = {
        "ticker": ticker,
        "period": {"buy_date": buy_date, "sell_date": state.get("layer2_sell_date")},
        "summary": analysis_json.get("summary"),
        "market_sentiment": analysis_json.get("market_sentiment"),
        "key_headlines": news_results[:3],
        "fact_check": analysis_json.get("fact_check"),
        "uncertainty_level": "low",
    }

    # Supabase 저장 (선택적)
    if HAS_REPOSITORY:
        try:
            case_id = state.get("case_id")
            if case_id:
                r_repo = RDBRepository()
                r_repo.save_market_context(case_id, output_data)
                print(f"[*] N7 results saved to Supabase for case: {case_id}")
        except Exception as e:
            print(f"[WARNING] Failed to save N7 results to Supabase: {e}")
    else:
        print("[INFO] Skipping Supabase storage (repository module not available)")

    return {"n7_news_analysis": {"news_context": output_data}}
