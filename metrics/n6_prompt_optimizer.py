from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import ensure_metrics_dir

PROMPT_PATH = Path(__file__).parent.parent / "N6_Stock_Analyst" / "prompt.py"
HISTORY_PATH = ensure_metrics_dir() / "n6_prompt_history.jsonl"

SCORE_IMPROVEMENT_THRESHOLD = 0.1
TARGET_SCORE = 8.0

RULES_BY_METRIC = {
    "schema_compliance": "출력 JSON은 누락 없이 모든 필드를 포함해야 합니다.",
    "price_integrity": "price_move의 highest/lowest는 start/end와 모순되지 않게 작성합니다.",
    "pct_change_accuracy": "pct_change는 start/end 가격으로부터 계산된 값과 크게 다르지 않아야 합니다.",
    "trend_return_consistency": "trend는 pct_change와 방향이 일치하도록 판단합니다.",
    "indicator_coverage": "RSI, MACD, Bollinger Band를 반드시 포함합니다.",
    "uncertainty_valid": "uncertainty_level은 low/medium/high 중 하나로 설정합니다.",
}


def apply_n6_prompt_optimization(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare current score with previous score and update/revert prompt if needed.
    """
    current_prompt = _read_prompt_text()
    current_hash = _hash_text(current_prompt)
    current_score = _get_score(report)

    history = _load_history()
    last_entry = history[-1] if history else None

    if last_entry and last_entry.get("prompt_hash") != current_hash:
        last_score = last_entry.get("score", 0.0)
        if _is_degradation(current_score, last_score):
            _write_prompt_text(last_entry.get("prompt_text", current_prompt))
            entry = _history_entry(
                report,
                prompt_text=last_entry.get("prompt_text", current_prompt),
                prompt_hash=_hash_text(last_entry.get("prompt_text", current_prompt)),
                action="rollback",
            )
            _append_history(entry)
            return entry

    failed = _failed_metrics(report)
    if current_score >= TARGET_SCORE or not failed:
        entry = _history_entry(report, prompt_text=current_prompt, prompt_hash=current_hash, action="keep")
        _append_history(entry)
        return entry

    new_prompt = _append_rules(current_prompt, failed)
    if new_prompt != current_prompt:
        _write_prompt_text(new_prompt)
        entry = _history_entry(report, prompt_text=new_prompt, prompt_hash=_hash_text(new_prompt), action="update")
        _append_history(entry)
        return entry

    entry = _history_entry(report, prompt_text=current_prompt, prompt_hash=current_hash, action="keep")
    _append_history(entry)
    return entry


def _append_rules(prompt_text: str, failed_metrics: List[str]) -> str:
    missing_rules = [
        RULES_BY_METRIC[name] for name in failed_metrics if RULES_BY_METRIC.get(name)
    ]
    if not missing_rules:
        return prompt_text

    missing_rules = [rule for rule in missing_rules if rule not in prompt_text]
    if not missing_rules:
        return prompt_text

    block = "\n추가 규칙(자동 최적화):\n" + "\n".join(f"- {rule}" for rule in missing_rules) + "\n"
    return _insert_into_prompt(prompt_text, block)


def _insert_into_prompt(prompt_text: str, block: str) -> str:
    match = re.search(r'NODE6_SYSTEM_PROMPT\\s*=\\s*\"\"\"(.*)\"\"\"', prompt_text, re.DOTALL)
    if not match:
        return prompt_text
    inner = match.group(1)
    updated_inner = inner.rstrip() + block
    return prompt_text[: match.start(1)] + updated_inner + prompt_text[match.end(1) :]


def _read_prompt_text() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _write_prompt_text(text: str) -> None:
    PROMPT_PATH.write_text(text, encoding="utf-8")


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _get_score(report: Dict[str, Any]) -> float:
    return float(report.get("summary", {}).get("score", 0.0))


def _failed_metrics(report: Dict[str, Any]) -> List[str]:
    metrics = report.get("metrics", [])
    failed = []
    for metric in metrics:
        if not metric.get("passed"):
            failed.append(metric.get("name", "unknown"))
    return failed


def _is_degradation(current: float, previous: float) -> bool:
    return (previous - current) >= SCORE_IMPROVEMENT_THRESHOLD


def _history_entry(
    report: Dict[str, Any],
    prompt_text: str,
    prompt_hash: str,
    action: str,
) -> Dict[str, Any]:
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": report.get("request_id", ""),
        "score": report.get("summary", {}).get("score", 0.0),
        "prompt_hash": prompt_hash,
        "prompt_text": prompt_text,
        "failed_metrics": _failed_metrics(report),
        "action": action,
    }


def _load_history() -> List[Dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    entries = []
    for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _append_history(entry: Dict[str, Any]) -> None:
    with HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
