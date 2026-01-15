# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import sys

from langsmith import Client
from langsmith.evaluation import evaluate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from N7_News_Summarizer.n7 import node7_news_summarizer
from N7_News_Summarizer.metrics import evaluate_n7_metrics
from core.llm import get_solar_chat


def predict(inputs: Dict[str, Any]) -> Dict[str, Any]:
    state = {
        "layer1_stock": inputs.get("layer1_stock", ""),
        "layer2_buy_date": inputs.get("layer2_buy_date", ""),
        "layer2_sell_date": inputs.get("layer2_sell_date", ""),
        "layer3_decision_basis": inputs.get("layer3_decision_basis", ""),
        "request_id": inputs.get("request_id", ""),
    }
    return node7_news_summarizer(state)


def n7_metrics_evaluator(run: Any, example: Any) -> Dict[str, Any]:
    output = run.outputs or {}
    analysis = output.get("n7_news_analysis", {})
    news_context = analysis.get("news_context", {}) if isinstance(analysis, dict) else {}

    analysis_json = {
        "summary": news_context.get("summary"),
        "news_summaries": news_context.get("news_summaries"),
        "fact_check": news_context.get("fact_check"),
    }
    news_results = news_context.get("key_headlines", []) or []

    llm = get_solar_chat()
    report = evaluate_n7_metrics(
        llm=llm,
        ticker=(example.inputs or {}).get("layer1_stock", ""),
        user_reason=(example.inputs or {}).get("layer3_decision_basis", ""),
        news_results=news_results,
        analysis_json=analysis_json,
        buy_date=(example.inputs or {}).get("layer2_buy_date"),
        sell_date=(example.inputs or {}).get("layer2_sell_date"),
    )
    summary = report.get("summary", {})
    return {
        "key": "n7_metrics",
        "score": summary.get("score", 0),
        "comment": f"passed {summary.get('passed')}/{summary.get('total')}",
    }


def main() -> None:
    client = Client()
    dataset_name = "n7-eval-dataset"

    evaluate(
        predict,
        data=dataset_name,
        evaluators=[n7_metrics_evaluator],
        experiment_prefix="n7-eval",
        client=client,
    )


if __name__ == "__main__":
    main()
