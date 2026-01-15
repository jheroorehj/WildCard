from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from N9_Fallback_Handler.n9 import node9_fallback_handler
from workflow.graph import build_graph
from app.service.embedding_service import EmbeddingService
from core.db import get_chroma_collection, get_supabase_client
from core.llm import get_solar_chat
from langchain_core.messages import HumanMessage, SystemMessage
from utils.json_parser import parse_json
from app.quiz_prompt import QUIZ_SYSTEM_PROMPT


class AnalyzeRequest(BaseModel):
    layer1_stock: str
    layer2_buy_date: str
    layer2_sell_date: str
    layer3_decision_basis: str
    position_status: str | None = None
    user_message: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    history: List[ChatMessage] = []
    message: str


class QuizRequest(BaseModel):
    learning_pattern_analysis: Dict[str, Any]


app = FastAPI(title="WildCard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_embedding_service: EmbeddingService | None = None
_graph = build_graph()


def _get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def _safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _save_to_supabase(request_id: str, state: Dict[str, Any], results: Dict[str, Any]) -> None:
    try:
        db = get_supabase_client()
        request_payload = {
            "id": request_id,
            "layer1_stock": state.get("layer1_stock"),
            "layer2_buy_date": state.get("layer2_buy_date"),
            "layer2_sell_date": state.get("layer2_sell_date"),
            "layer3_decision_basis": state.get("layer3_decision_basis"),
            "user_message": state.get("user_message"),
            "raw_input": state,
        }
        db.table("analysis_requests").insert(request_payload).execute()

        result_rows = []
        for node_key in ("n6", "n7", "n8", "n9", "n10"):
            node_result = results.get(node_key)
            if node_result is None:
                continue
            result_rows.append(
                {"request_id": request_id, "node": node_key, "result": node_result}
            )
        if result_rows:
            db.table("analysis_results").insert(result_rows).execute()
    except Exception as exc:
        print(f"[WARNING] Supabase save failed: {exc}")


def _save_to_chroma(request_id: str, state: Dict[str, Any], results: Dict[str, Any]) -> None:
    try:
        embeddings = _get_embedding_service()
        llm_collection = get_chroma_collection("llm_outputs")
        learning_collection = get_chroma_collection("learning_data")

        llm_docs = []
        llm_ids = []
        llm_meta = []
        for node_key in ("n6", "n7", "n8", "n9", "n10"):
            node_result = results.get(node_key)
            if node_result is None:
                continue
            llm_docs.append(_safe_json(node_result))
            llm_ids.append(f"{request_id}:{node_key}")
            llm_meta.append({"request_id": request_id, "node": node_key})
        if llm_docs:
            llm_embeddings = embeddings.create_embeddings(llm_docs)
            llm_collection.add(
                ids=llm_ids, documents=llm_docs, embeddings=llm_embeddings, metadatas=llm_meta
            )

        learning_docs = []
        learning_meta = []
        learning_id = f"{request_id}:learning"
        basis = state.get("layer3_decision_basis")
        user_message = state.get("user_message")
        if basis:
            learning_docs.append(str(basis))
            learning_meta.append({"request_id": request_id, "source": "decision_basis"})
        if user_message and user_message != basis:
            learning_docs.append(str(user_message))
            learning_meta.append({"request_id": request_id, "source": "user_message"})
        if learning_docs:
            learning_embeddings = embeddings.create_embeddings(learning_docs)
            learning_collection.add(
                ids=[f"{learning_id}:{i}" for i in range(len(learning_docs))],
                documents=learning_docs,
                embeddings=learning_embeddings,
                metadatas=learning_meta,
            )
    except Exception as exc:
        print(f"[WARNING] Chroma save failed: {exc}")


@app.get("/v1/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


async def _run_node(name: str, fn: Any, state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return await asyncio.to_thread(fn, dict(state))
    except Exception as exc:
        return {f"{name}_error": str(exc)}


@app.post("/v1/analyze")
async def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    if hasattr(req, "model_dump"):
        state: Dict[str, Any] = req.model_dump()
    else:
        state = req.dict()
    if not state.get("user_message"):
        state["user_message"] = state.get("layer3_decision_basis", "")
    if state.get("position_status") == "holding" and not state.get("layer2_sell_date"):
        state["layer2_sell_date"] = datetime.utcnow().date().isoformat()

    result = await asyncio.to_thread(_graph.invoke, state)

    request_id = str(uuid4())
    merged: Dict[str, Any] = {"request_id": request_id, **result}

    n8_result = {
        "n8_loss_cause_analysis": result.get("n8_loss_cause_analysis"),
        "n8_market_context_analysis": result.get("n8_market_context_analysis"),
        "n9_input": result.get("n9_input"),
    }

    node_results: Dict[str, Any] = {
        "n6": result.get("n6_stock_analysis"),
        "n7": result.get("n7_news_analysis"),
        "n8": n8_result,
        "n9": result.get("learning_pattern_analysis"),
        "n10": result.get("n10_loss_review_report"),
    }

    await asyncio.to_thread(_save_to_supabase, request_id, state, node_results)
    await asyncio.to_thread(_save_to_chroma, request_id, state, node_results)

    return merged


@app.post("/v1/chat")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    context = "\n".join([f"{m.role}: {m.content}" for m in req.history][-10:])
    state = {"user_message": req.message, "context": context}
    result = node9_fallback_handler(state)
    message = ""
    if isinstance(result, dict):
        analysis = result.get("learning_pattern_analysis", {})
        if isinstance(analysis, dict):
            message = analysis.get("pattern_summary", "")
    return {"message": message, "raw": result}


@app.post("/v1/quiz")
async def quiz(req: QuizRequest) -> Dict[str, Any]:
    payload = {
        "learning_pattern_analysis": req.learning_pattern_analysis,
    }
    llm = get_solar_chat()
    messages = [
        SystemMessage(content=QUIZ_SYSTEM_PROMPT),
        HumanMessage(content=f"입력을 기반으로 JSON만 출력하세요.\n{payload}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:
        return _fallback_quiz(f"LLM 호출 실패: {exc}")

    parsed = parse_json(raw)
    if not isinstance(parsed, dict):
        return _fallback_quiz("JSON 파싱 실패")

    if not _is_valid_quiz(parsed):
        return _fallback_quiz("출력 스키마 검증 실패")

    return parsed


def _fallback_quiz(reason: str) -> Dict[str, Any]:
    return {
        "quiz_set": {
            "quiz_purpose": f"학습 점검 (오류: {reason})",
            "quizzes": [
                {
                    "quiz_id": "Q1",
                    "quiz_type": "multiple_choice",
                    "question": "가장 중요한 손실 원인은 무엇이었나요?",
                    "options": [{"text": "정보 검증 부족"}, {"text": "과도한 자신감"}, {"text": "추세 오판"}, {"text": "손절 규칙 부재"}],
                    "has_fixed_answer": True,
                    "correct_answer_index": 0,
                },
                {
                    "quiz_id": "Q2",
                    "quiz_type": "multiple_choice",
                    "question": "시장 상황에서 가장 영향이 컸던 요소는 무엇이었나요?",
                    "options": [{"text": "금리 변화"}, {"text": "뉴스 충격"}, {"text": "수급 변화"}, {"text": "변동성 급등"}],
                    "has_fixed_answer": True,
                    "correct_answer_index": 0,
                },
                {
                    "quiz_id": "Q3",
                    "quiz_type": "reflection",
                    "question": "다음 거래에서 우선 보완할 행동은 무엇인가요?",
                    "options": [
                        {"text": "진입/청산 기준 정리", "solution": "사전에 체크리스트를 만들고 진입·청산 기준을 문서화하세요."},
                        {"text": "리스크 한도 설정", "solution": "포지션별 최대 손실 범위를 정하고 즉시 적용하세요."},
                        {"text": "외부 신호 확인", "solution": "뉴스/거시 지표로 자신의 판단을 교차 검증하세요."},
                        {"text": "기록과 복기 강화", "solution": "매매 후 기록을 남기고 반복 패턴을 찾아보세요."},
                    ],
                    "has_fixed_answer": False,
                    "solution_required": True,
                },
            ],
        }
    }


def _is_valid_quiz(data: Dict[str, Any]) -> bool:
    quiz_set = data.get("quiz_set")
    if not isinstance(quiz_set, dict):
        return False
    quizzes = quiz_set.get("quizzes")
    if not isinstance(quizzes, list) or len(quizzes) != 3:
        return False
    for quiz in quizzes:
        if not isinstance(quiz, dict):
            return False
        if not isinstance(quiz.get("quiz_id"), str):
            return False
        if quiz.get("quiz_type") not in ("multiple_choice", "reflection"):
            return False
        if not isinstance(quiz.get("question"), str):
            return False
        options = quiz.get("options")
        if not isinstance(options, list) or len(options) != 4:
            return False
        for option in options:
            if not isinstance(option, dict):
                return False
            if not isinstance(option.get("text"), str):
                return False
            if quiz.get("quiz_type") == "reflection":
                if not isinstance(option.get("solution"), str):
                    return False
        if not isinstance(quiz.get("has_fixed_answer"), bool):
            return False
    return True
