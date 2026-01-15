from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .storage import ensure_metrics_dir

ALLOWED_TRENDS = {"up", "down", "sideways"}
ALLOWED_UNCERTAINTY = {"low", "medium", "high"}
REQUIRED_INDICATORS = {"rsi", "macd", "bollinger_band"}


def evaluate_n6_metrics(
    analysis_result: Dict[str, Any],
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate N6 output quality and return a metrics report.
    """
    stock_analysis = analysis_result.get("stock_analysis", {})
    metrics: List[Dict[str, Any]] = []

    metrics.append(_metric_schema_compliance(stock_analysis))
    metrics.append(_metric_price_integrity(stock_analysis))
    metrics.append(_metric_pct_change_accuracy(stock_analysis))
    metrics.append(_metric_trend_return_consistency(stock_analysis))
    metrics.append(_metric_indicator_coverage(stock_analysis))
    metrics.append(_metric_uncertainty_valid(stock_analysis))

    passed = sum(1 for metric in metrics if metric.get("passed"))
    total = len(metrics)
    score = round((passed / total) * 10, 1) if total else 0.0

    report = {
        "node": "n6",
        "request_id": request_id or "",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {"passed": passed, "total": total, "score": score},
        "metrics": metrics,
    }

    return report


def persist_n6_metrics(report: Dict[str, Any]) -> Tuple[Path, Path]:
    """
    Persist N6 metrics report to JSON and CSV in metrics/results/.
    """
    metrics_dir = ensure_metrics_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    request_id = report.get("request_id") or "n6"
    json_path = metrics_dir / f"n6_metrics_{request_id}_{timestamp}.json"
    csv_path = metrics_dir / "n6_metrics_history.csv"

    json_path.write_text(_safe_json(report), encoding="utf-8")
    _append_csv(csv_path, report)

    return json_path, csv_path


def _metric_schema_compliance(stock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    required_keys = [
        "summary",
        "price_move",
        "trend",
        "indicators",
        "risk_notes",
        "uncertainty_level",
    ]
    missing = [key for key in required_keys if key not in stock_analysis]
    passed = len(missing) == 0
    return _metric_result(
        name="schema_compliance",
        passed=passed,
        value={"missing": missing},
        reason="missing required keys" if not passed else "",
    )


def _metric_price_integrity(stock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    price_move = stock_analysis.get("price_move", {})
    start = _parse_float(price_move.get("start_price"))
    end = _parse_float(price_move.get("end_price"))
    highest = _parse_float(price_move.get("highest"))
    lowest = _parse_float(price_move.get("lowest"))

    if None in (start, end, highest, lowest):
        return _metric_result(
            name="price_integrity",
            passed=False,
            value={"start": start, "end": end, "highest": highest, "lowest": lowest},
            reason="missing price values",
        )

    passed = highest >= max(start, end) and lowest <= min(start, end)
    reason = "" if passed else "highest/lowest inconsistent with start/end"
    return _metric_result(
        name="price_integrity",
        passed=passed,
        value={"start": start, "end": end, "highest": highest, "lowest": lowest},
        reason=reason,
    )


def _metric_pct_change_accuracy(stock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    price_move = stock_analysis.get("price_move", {})
    start = _parse_float(price_move.get("start_price"))
    end = _parse_float(price_move.get("end_price"))
    pct_change = _parse_pct(price_move.get("pct_change"))
    if None in (start, end, pct_change) or start == 0:
        return _metric_result(
            name="pct_change_accuracy",
            passed=False,
            value={"start": start, "end": end, "pct_change": pct_change},
            reason="missing pct_change or price values",
        )

    computed = ((end - start) / start) * 100
    diff = abs(computed - pct_change)
    passed = diff <= 0.5
    reason = "" if passed else f"pct_change diff too large ({diff:.2f}%)"
    return _metric_result(
        name="pct_change_accuracy",
        passed=passed,
        value={"computed": round(computed, 2), "reported": pct_change, "diff": round(diff, 2)},
        reason=reason,
    )


def _metric_trend_return_consistency(stock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    trend = stock_analysis.get("trend")
    pct_change = _parse_pct(stock_analysis.get("price_move", {}).get("pct_change"))
    if trend not in ALLOWED_TRENDS or pct_change is None:
        return _metric_result(
            name="trend_return_consistency",
            passed=False,
            value={"trend": trend, "pct_change": pct_change},
            reason="missing trend or pct_change",
        )

    if trend == "up":
        passed = pct_change >= 0.3
    elif trend == "down":
        passed = pct_change <= -0.3
    else:
        passed = abs(pct_change) <= 1.0

    reason = "" if passed else "trend conflicts with pct_change"
    return _metric_result(
        name="trend_return_consistency",
        passed=passed,
        value={"trend": trend, "pct_change": pct_change},
        reason=reason,
    )


def _metric_indicator_coverage(stock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    indicators = stock_analysis.get("indicators", [])
    names = {str(item.get("name", "")).lower() for item in indicators if isinstance(item, dict)}
    missing = sorted(REQUIRED_INDICATORS - names)
    passed = len(missing) == 0
    return _metric_result(
        name="indicator_coverage",
        passed=passed,
        value={"missing": missing, "present": sorted(names)},
        reason="missing required indicators" if not passed else "",
    )


def _metric_uncertainty_valid(stock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    uncertainty = stock_analysis.get("uncertainty_level")
    passed = uncertainty in ALLOWED_UNCERTAINTY
    return _metric_result(
        name="uncertainty_valid",
        passed=passed,
        value={"uncertainty_level": uncertainty},
        reason="invalid uncertainty_level" if not passed else "",
    )


def _metric_result(name: str, passed: bool, value: Any, reason: str) -> Dict[str, Any]:
    return {"name": name, "passed": passed, "value": value, "reason": reason}


def _parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def _parse_pct(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).replace("%", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def _safe_json(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, default=str)


def _append_csv(path: Path, report: Dict[str, Any]) -> None:
    header = "timestamp,request_id,score,passed,total\n"
    line = (
        f"{report.get('timestamp')},"
        f"{report.get('request_id')},"
        f"{report.get('summary', {}).get('score')},"
        f"{report.get('summary', {}).get('passed')},"
        f"{report.get('summary', {}).get('total')}\n"
    )

    if not path.exists():
        path.write_text(header, encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
