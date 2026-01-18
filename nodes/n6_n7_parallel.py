"""
N6(기술분석)과 N7(뉴스분석)을 병렬로 실행하는 통합 노드
asyncio를 사용하여 두 노드를 동시에 실행합니다.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

from N6_Stock_Analyst.n6 import node6_stock_analyst
from N7_News_Summarizer.n7 import node7_news_summarizer


def node6_n7_parallel(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    N6과 N7을 병렬로 실행하고 결과를 합칩니다.
    ThreadPoolExecutor를 사용하여 동기 함수들을 병렬 실행합니다.
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 두 노드를 동시에 실행
        future_n6 = executor.submit(node6_stock_analyst, state)
        future_n7 = executor.submit(node7_news_summarizer, state)

        # 결과 수집
        result_n6 = future_n6.result()
        result_n7 = future_n7.result()

    # 두 결과를 합쳐서 반환
    merged_result = {}
    if isinstance(result_n6, dict):
        merged_result.update(result_n6)
    if isinstance(result_n7, dict):
        merged_result.update(result_n7)

    return merged_result
