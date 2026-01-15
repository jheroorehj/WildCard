from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import sys

from langsmith import Client
from langsmith.evaluation import evaluate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from N6_Stock_Analyst.n6 import node6_stock_analyst
from metrics.n6_metrics import evaluate_n6_metrics


def predict(inputs: Dict[str, Any]) -> Dict[str, Any]:
    state = {
        "layer1_stock": inputs.get("layer1_stock", ""),
        "layer2_buy_date": inputs.get("layer2_buy_date", ""),
        "layer2_sell_date": inputs.get("layer2_sell_date", ""),
        "layer3_decision_basis": inputs.get("layer3_decision_basis", ""),
        "request_id": inputs.get("request_id", ""),
    }
    return node6_stock_analyst(state)


def n6_metrics_evaluator(run, example) -> Dict[str, Any]:
    output = run.outputs or {}
    analysis = output.get("n6_stock_analysis", {})
    if not isinstance(analysis, dict):
        return {
            "key": "n6_metrics",
            "score": 0,
            "comment": "missing n6_stock_analysis",
        }

    report = evaluate_n6_metrics(analysis, str(example.id) if example else None)
    summary = report.get("summary", {})
    return {
        "key": "n6_metrics",
        "score": summary.get("score", 0),
        "comment": f"passed {summary.get('passed')}/{summary.get('total')}",
    }

def n6_judge_evaluator(run, example) -> Dict[str, Any]:
    output = run.outputs or {}
    analysis = output.get("n6_stock_analysis", {})
    stock_analysis = analysis.get("stock_analysis", {}) if isinstance(analysis, dict) else {}
    judge = stock_analysis.get("judge_metrics", {}) if isinstance(stock_analysis, dict) else {}
    if not isinstance(judge, dict):
        return {
            "key": "n6_judge",
            "score": 0,
            "comment": "missing judge_metrics",
        }

    scores = [
        judge.get("consistency"),
        judge.get("indicator_coverage"),
        judge.get("trend_consistency"),
        judge.get("advice_free"),
        judge.get("clarity"),
    ]
    values = [s for s in scores if isinstance(s, (int, float))]
    avg = sum(values) / len(values) if values else 0

    return {
        "key": "n6_judge",
        "score": avg,
        "comment": "avg of judge metrics",
    }

def main() -> None:
    client = Client()
    dataset_name = "n6-eval-dataset"

    evaluate(
        predict,
        data=dataset_name,
        evaluators=[n6_metrics_evaluator, n6_judge_evaluator],
        experiment_prefix="n6-eval",
        client=client,
    )


if __name__ == "__main__":
    main()
