from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from N3_Loss_Analyzer.n3 import node3_loss_analyzer
from N6_Stock_Analyst.n6 import node6_stock_analyst
from N7_News_Summarizer.n7 import node7_news_summarizer
from N8_Concept_Explainer.n8 import node8_concept_explainer
from N9_Fallback_Handler.n9 import node9_fallback_handler
from app.service.embedding_service import EmbeddingService
from core.db import get_chroma_collection, get_supabase_client


class AnalyzeRequest(BaseModel):
    layer1_stock: str
    layer2_buy_date: str
    layer2_sell_date: str
    layer3_decision_basis: str
    user_message: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    history: List[ChatMessage] = []
    message: str


app = FastAPI(title="WildCard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_embedding_service: EmbeddingService | None = None


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
        for node_key in ("n3", "n6", "n7", "n8", "n9"):
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
        for node_key in ("n3", "n6", "n7", "n8", "n9"):
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


async def _run_node(
    name: str, fn: Any, state: Dict[str, Any]
) -> Dict[str, Any]:
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

    n3_result = node3_loss_analyzer(state)
    state.update(n3_result)

    nodes: List[Tuple[str, Any]] = [
        ("n6", node6_stock_analyst),
        ("n7", node7_news_summarizer),
        ("n8", node8_concept_explainer),
        ("n9", node9_fallback_handler),
    ]

    results = await asyncio.gather(
        *[_run_node(name, fn, state) for name, fn in nodes]
    )

    request_id = str(uuid4())
    merged: Dict[str, Any] = {"request_id": request_id, **n3_result}
    for result in results:
        merged.update(result)

    node_results: Dict[str, Any] = {"n3": n3_result}
    for (name, _), result in zip(nodes, results):
        node_results[name] = result

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
        message = result.get("fallback_response", {}).get("message", "")
    return {"message": message, "raw": result}
