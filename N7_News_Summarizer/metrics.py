# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

from metrics.tier2_trust import parse_news_date
from metrics.storage import ensure_metrics_dir


def _clamp01(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _calc_zero_anachronism(
    news_results: List[Dict[str, Any]], buy_date: str | None, sell_date: str | None
) -> float:
    if not news_results:
        return 0.0
    start = parse_news_date(buy_date or "")
    end = parse_news_date(sell_date or "") if sell_date else None
    if not start:
        return 0.0
    valid = 0
    for item in news_results:
        parsed = parse_news_date(item.get("date", ""))
        if not parsed:
            continue
        if parsed >= start and (end is None or parsed <= end):
            valid += 1
    return round(valid / len(news_results) * 100, 1)


def _judge_n7_quality(
    llm: Any,
    ticker: str,
    user_reason: str,
    news_items: List[Dict[str, Any]],
    analysis_json: Dict[str, Any],
) -> Dict[str, Any]:
    payload = {
        "ticker": ticker,
        "user_reason": user_reason,
        "news_items": news_items,
        "summary": analysis_json.get("summary"),
        "news_summaries": analysis_json.get("news_summaries"),
        "fact_check": analysis_json.get("fact_check"),
    }
    prompt = (
        "You are a strict evaluator for financial news summaries.\n"
        "Score the following:\n"
        "1) relevance per item (0~1) to the ticker and user_reason\n"
        "2) faithfulness of the summary to snippets (0~1)\n"
        "3) signal per item (1/0): earnings, guidance, macro, regulatory, risk events\n"
        "4) coverage topics (short labels), unique_count, and score (unique_count/total)\n"
        "Return JSON exactly with keys:\n"
        "relevance.per_item, relevance.avg, faithfulness, signal.per_item, signal.ratio, "
        "coverage.topics, coverage.unique_count, coverage.score, notes\n\n"
        f"INPUT:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    try:
        response = llm.invoke(prompt)
        content = response.content if isinstance(response.content, str) else str(response.content)
        content = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Judge output is not a dict.")
    except Exception as exc:
        print(f"[WARNING] N7 judge failed: {exc}")
        parsed = {
            "relevance": {"per_item": [], "avg": 0.0},
            "faithfulness": 0.0,
            "signal": {"per_item": [], "ratio": 0.0},
            "coverage": {"topics": [], "unique_count": 0, "score": 0.0},
            "notes": "judge_failed",
        }

    total = max(1, len(news_items))
    rel = parsed.get("relevance", {})
    sig = parsed.get("signal", {})
    cov = parsed.get("coverage", {})

    rel_per = rel.get("per_item") if isinstance(rel, dict) else []
    sig_per = sig.get("per_item") if isinstance(sig, dict) else []

    rel_avg = _clamp01(rel.get("avg") if isinstance(rel, dict) else 0.0)
    faith = _clamp01(parsed.get("faithfulness", 0.0))
    sig_ratio = _clamp01(sig.get("ratio") if isinstance(sig, dict) else 0.0)
    cov_score = _clamp01(cov.get("score") if isinstance(cov, dict) else 0.0)

    if rel_per and len(rel_per) != len(news_items):
        rel_avg = _clamp01(sum(_clamp01(x) for x in rel_per) / len(rel_per))
    if sig_per and len(sig_per) != len(news_items):
        sig_ratio = _clamp01(sum(1 for x in sig_per if int(x) == 1) / len(sig_per))
    if isinstance(cov, dict) and "unique_count" in cov:
        try:
            cov_score = _clamp01(float(cov.get("unique_count", 0)) / total)
        except (TypeError, ValueError):
            cov_score = 0.0

    return {
        "relevance_rate": round(rel_avg * 100, 1),
        "faithfulness": round(faith * 100, 1),
        "signal_to_noise": round(sig_ratio * 100, 1),
        "coverage": round(cov_score * 100, 1),
        "judge_raw": parsed,
    }


def evaluate_n7_metrics(
    llm: Any,
    ticker: str,
    user_reason: str,
    news_results: List[Dict[str, Any]],
    analysis_json: Dict[str, Any],
    buy_date: str | None,
    sell_date: str | None,
) -> Dict[str, Any]:
    zero_anachronism = _calc_zero_anachronism(news_results, buy_date, sell_date)
    judge_metrics = _judge_n7_quality(llm, ticker, user_reason, news_results[:3], analysis_json)

    metrics = [
        _metric_result("zero_anachronism", zero_anachronism, 100.0),
        _metric_result("relevance_rate", judge_metrics.get("relevance_rate", 0.0), 80.0),
        _metric_result("faithfulness", judge_metrics.get("faithfulness", 0.0), 95.0),
        _metric_result("signal_to_noise", judge_metrics.get("signal_to_noise", 0.0), 70.0),
        _metric_result("coverage", judge_metrics.get("coverage", 0.0), 60.0),
    ]

    passed = sum(1 for metric in metrics if metric.get("passed"))
    total = len(metrics)
    score = round((passed / total) * 10, 1) if total else 0.0

    return {
        "node": "n7",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {"passed": passed, "total": total, "score": score},
        "metrics": metrics,
        "details": {"judge_raw": judge_metrics.get("judge_raw")},
    }


def persist_n7_metrics(report: Dict[str, Any], request_id: Optional[str] = None) -> Tuple[Path, Path]:
    metrics_dir = ensure_metrics_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_id = request_id or "n7"
    json_path = metrics_dir / f"n7_metrics_{report_id}_{timestamp}.json"
    csv_path = metrics_dir / "n7_metrics_history.csv"

    json_path.write_text(_safe_json(report), encoding="utf-8")
    _append_csv(csv_path, report, report_id)

    return json_path, csv_path


def _metric_result(name: str, value: float, target: float) -> Dict[str, Any]:
    return {
        "name": name,
        "value": value,
        "target": target,
        "passed": value >= target,
    }


def _safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _append_csv(path: Path, report: Dict[str, Any], request_id: str) -> None:
    header = "timestamp,request_id,metric_name,value,target,passed\n"
    if not path.exists():
        path.write_text(header, encoding="utf-8")

    lines = []
    for metric in report.get("metrics", []):
        lines.append(
            f"{report.get('timestamp')},{request_id},{metric.get('name')},"
            f"{metric.get('value')},{metric.get('target')},{metric.get('passed')}\n"
        )
    with path.open("a", encoding="utf-8") as handle:
        handle.writelines(lines)
