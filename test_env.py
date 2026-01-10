#!/usr/bin/env python3
"""
환경 변수 로드 테스트 스크립트
프로젝트 루트의 .env.local이 제대로 로드되는지 확인합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.llm import UpstageClient

def test_env_loading():
    """환경 변수가 제대로 로드되었는지 테스트"""
    print("=" * 60)
    print("환경 변수 로드 테스트")
    print("=" * 60)

    try:
        client = UpstageClient()

        # API 키 확인 (보안을 위해 일부만 표시)
        api_key = client.api_key
        if api_key:
            masked_key = api_key[:10] + "*" * (len(api_key) - 10)
            print(f"✅ UPSTAGE_API_KEY 로드 성공: {masked_key}")
        else:
            print("❌ UPSTAGE_API_KEY를 찾을 수 없습니다.")
            return False

        # 모델 이름 확인
        print(f"✅ Chat Model: {client.chat_model_name}")
        print(f"✅ Embedding Model: {client.embedding_model_name}")

        # Chat 모델 인스턴스 생성 테스트
        chat_model = client.get_chat_model()
        print(f"✅ Chat Model 인스턴스 생성 성공: {type(chat_model).__name__}")

        # Embedding 모델 인스턴스 생성 테스트
        embedding_model = client.get_embedding_model()
        print(f"✅ Embedding Model 인스턴스 생성 성공: {type(embedding_model).__name__}")

        print("\n" + "=" * 60)
        print("모든 테스트 통과! 🎉")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n확인 사항:")
        print("1. 프로젝트 루트에 .env.local 파일이 있는지 확인하세요")
        print("2. .env.local에 UPSTAGE_API_KEY가 설정되어 있는지 확인하세요")
        print("3. 필요한 패키지가 설치되어 있는지 확인하세요 (pip install -r requirements.txt)")
        return False

if __name__ == "__main__":
    success = test_env_loading()
    sys.exit(0 if success else 1)
