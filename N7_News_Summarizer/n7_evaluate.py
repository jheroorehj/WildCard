# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict

from langsmith import Client
from langsmith.evaluation import evaluate

from core.llm import get_solar_chat
from N7_News_Summarizer.n7 import node7_news_summarizer
from N7_News_Summarizer.metrics import evaluate_n7_metrics


def _extract_inputs(example: Any) -> Dict[str, Any]:
    if hasattr(example, "inputs") and isinstance(example.inputs, dict):
        return example.inputs
    if isinstance(example, dict):
        return example.get("inputs", example)
    return {}


def _extract_outputs(run: Any) -> Dict[str, Any]:
    if hasattr(run, "outputs") and isinstance(run.outputs, dict):
        return run.outputs
    if isinstance(run, dict):
        return run.get("outputs", run)
    return {}


def predict(example: Any) -> Dict[str, Any]:
    inputs = _extract_inputs(example)
    state = {
        "layer1_stock": inputs.get("layer1_stock", ""),
        "layer2_buy_date": inputs.get("layer2_buy_date", ""),
        "layer2_sell_date": inputs.get("layer2_sell_date", ""),
        "layer3_decision_basis": inputs.get("layer3_decision_basis", ""),
        "position_status": inputs.get("position_status"),
        "user_message": inputs.get("user_message"),
    }
    return node7_news_summarizer(state)


def n7_metrics_evaluator(run: Any, example: Any) -> list[dict[str, Any]]:
    inputs = _extract_inputs(example)
    outputs = _extract_outputs(run)

    news_context = (
        outputs.get("n7_news_analysis", {}).get("news_context", {})
        if isinstance(outputs, dict)
        else {}
    )

    analysis_json = {
        "summary": news_context.get("summary"),
        "news_summaries": news_context.get("news_summaries"),
        "fact_check": news_context.get("fact_check"),
    }
    news_results = news_context.get("key_headlines", []) or []

    llm = get_solar_chat()
    metrics = evaluate_n7_metrics(
        llm=llm,
        ticker=inputs.get("layer1_stock", ""),
        user_reason=inputs.get("layer3_decision_basis", ""),
        news_results=news_results,
        analysis_json=analysis_json,
        buy_date=inputs.get("layer2_buy_date"),
        sell_date=inputs.get("layer2_sell_date"),
    )

    return [
        {"key": "n7_zero_anachronism", "score": metrics.get("n7_zero_anachronism", 0.0)},
        {"key": "n7_relevance_rate", "score": metrics.get("n7_relevance_rate", 0.0)},
        {"key": "n7_faithfulness", "score": metrics.get("n7_faithfulness", 0.0)},
        {"key": "n7_signal_to_noise", "score": metrics.get("n7_signal_to_noise", 0.0)},
        {"key": "n7_coverage", "score": metrics.get("n7_coverage", 0.0)},
    ]


def run_n7_evaluation(
    dataset_name: str,
    experiment_prefix: str = "n7-eval",
) -> Any:
    client = Client()
    return evaluate(
        predict,
        data=dataset_name,
        evaluators=[n7_metrics_evaluator],
        experiment_prefix=experiment_prefix,
        client=client,
    )


if __name__ == "__main__":
    dataset = os.getenv("N7_DATASET_NAME", "").strip()
    if not dataset:
        raise SystemExit("N7_DATASET_NAME is required.")
    exp_prefix = os.getenv("N7_EXPERIMENT_PREFIX", "n7-eval")
    run_n7_evaluation(dataset, exp_prefix)
