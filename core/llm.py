"""
WildCard LLM Core (Factory)
- Upstage Solar(Pro2) Chat model + Upstage Embeddings를 프로젝트 어디서든 가져다 쓰기 위한 모듈

필수 환경변수:
- UPSTAGE_API_KEY

선택 환경변수:
- UPSTAGE_CHAT_MODEL (default: solar-pro2)
- UPSTAGE_EMBEDDING_MODEL (default: solar-embedding-1-large)

주의:
- Kubernetes 배포 환경에서는 ConfigMap/Secret으로 env가 주입되므로 .env 로드를 건너뜀
- 로컬 개발 환경에서는 .env를 읽도록 처리
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_upstage import ChatUpstage, UpstageEmbeddings


def _load_env_if_local() -> None:
    """K8s 환경이 아니면 로컬 개발 환경으로 보고 .env를 로드합니다."""
    if os.getenv("KUBERNETES_SERVICE_HOST") is None:
        load_dotenv()


class UpstageClient:
    """
    Upstage Solar Chat/Embedding 인스턴스를 재사용하기 위한 경량 싱글톤 클라이언트
    - 모델 인스턴스 생성 비용/오버헤드를 줄이기 위해 최초 1회만 생성 후 캐싱합니다.
    """

    _instance: Optional["UpstageClient"] = None

    def __new__(cls) -> "UpstageClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # __init__가 여러 번 호출될 수 있으므로, 초기화 중복 방지
        if getattr(self, "_initialized", False):
            return

        _load_env_if_local()

        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable is required")

        self.chat_model_name = os.getenv("UPSTAGE_CHAT_MODEL", "solar-pro2")
        self.embedding_model_name = os.getenv(
            "UPSTAGE_EMBEDDING_MODEL", "solar-embedding-1-large"
        )

        self._chat_instance: Optional[ChatUpstage] = None
        self._embedding_instance: Optional[UpstageEmbeddings] = None
        self._initialized = True

    def get_chat_model(self) -> ChatUpstage:
        if self._chat_instance is None:
            self._chat_instance = ChatUpstage(
                api_key=self.api_key,
                model=self.chat_model_name,
            )
        return self._chat_instance

    def get_embedding_model(self) -> UpstageEmbeddings:
        if self._embedding_instance is None:
            self._embedding_instance = UpstageEmbeddings(
                api_key=self.api_key,
                model=self.embedding_model_name,
            )
        return self._embedding_instance


# ---- Factory Functions (프로젝트 전역에서 사용) ----
_client = UpstageClient()


def get_solar_chat() -> ChatUpstage:
    """
    Upstage Solar Chat 모델을 반환합니다.
    사용처:
    - WildCard/N3/node.py 등 LLM 호출이 필요한 모든 Node
    """
    return _client.get_chat_model()


def get_upstage_embeddings() -> UpstageEmbeddings:
    """
    Upstage Embedding 모델을 반환합니다.
    사용처:
    - VectorDB 구축/검색, RAG 등
    """
    return _client.get_embedding_model()
