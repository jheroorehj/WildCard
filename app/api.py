from __future__ import annotations

import asyncio
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

    merged: Dict[str, Any] = {"request_id": str(uuid4()), **n3_result}
    for result in results:
        merged.update(result)

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
