# -*- coding: utf-8 -*-
# 파일 상단에 추가 (agent 폴더를 루트로 인식하게 함)
import sys
from pathlib import Path

current_file = Path(__file__).resolve()
agent_root = current_file.parent.parent  # 파일 위치에 따라 parent 개수 조절
sys.path.append(str(agent_root))
from N7_News_Summarizer.n7 import node7_news_summarizer


def test_n7_flow():
    print("\n--- Testing N7 News Summarizer Flow ---")

    # 1. 가상 데이터(State) 준비
    mock_state = {
        "case_id": None,
        "layer1_stock": "삼성전자",
        "layer2_buy_date": "2024-03-15",
        "layer2_sell_date": "2024-04-10",
        "layer3_decision_basis": "유튜브에서 반도체 업황이 역대급 호재라고 해서 샀어요.",
        "n3_loss_analysis": {
            "loss_factors": [
                {
                    "type": "information_bias",
                    "evidence": {
                        "source": "news_context",
                        "detail": "유튜브 발언 기반 판단",
                        "missing_check": "실제 악재 뉴스",
                    },
                }
            ]
        },
    }

    try:
        # 2. N7 노드 실행
        print("[*] Running N7 Node...")
        result = node7_news_summarizer(mock_state)

        # 3. 결과 확인
        print("\n--- N7 Analysis Result ---")
        news_analysis = result.get("n7_news_analysis", {}).get("news_context", {})

        if "error" in news_analysis:
            print("❌ Analysis Error: {}".format(news_analysis["error"]))
            return False

        print("Summary: {}".format(news_analysis.get("summary")))
        sentiment = news_analysis.get("market_sentiment", {})
        print(
            "Sentiment: {} ({})".format(
                sentiment.get("label", "unknown"),
                sentiment.get("index", 0),
            )
        )

        fact_check = news_analysis.get("fact_check", {})

        print("\n[Fact Check]")
        print("User Belief: {}".format(fact_check.get("user_belief")))
        print("Actual Fact: {}".format(fact_check.get("actual_fact")))
        print("Verdict: {}".format(fact_check.get("verdict")))

        print("\n[Key Headlines Found]")
        for i, news in enumerate(news_analysis.get("key_headlines", []), 1):
            print("{}. {} ({})".format(i, news.get("title"), news.get("source")))

        return True

    except Exception as e:
        print("\n[ERROR] N7 flow test failed: {}".format(e))
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting N7 Agent Individual Test...")
    success = test_n7_flow()

    if success:
        print("\n🎉 N7 Agent test completed successfully!")
    else:
        print("\n❌ N7 Agent test failed.")
