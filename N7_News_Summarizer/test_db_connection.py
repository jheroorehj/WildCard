# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

# 프로젝트 루트를 path에 추가하여 agent 모듈을 찾을 수 있게 함
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.db import get_supabase, get_chroma_client, get_chroma_collection
from repository.rdb_repo import RDBRepository
from repository.vector.vector_repo import ChromaDBRepository

def test_supabase_connection():
    print("\n--- Testing Supabase Connection ---")
    try:
        db = get_supabase()
        # 간단한 테이블 조회 시도 (데이터가 없어도 성공하면 연결은 된 것)
        response = db.table("loss_cases").select("count", count="exact").limit(1).execute()
        print(f"[OK] Supabase connected. Row count in 'loss_cases': {response.count}")
        return True
    except Exception as e:
        print(f"[ERROR] Supabase connection failed: {e}")
        return False

def test_chroma_connection():
    print("\n--- Testing ChromaDB Connection ---")
    try:
        client = get_chroma_client()
        collection = get_chroma_collection("test_collection")
        print(f"[OK] ChromaDB connected. Collection '{collection.name}' is ready.")
        
        # 간단한 데이터 쓰기/읽기 테스트
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"source": "test"}],
            ids=["test_id_001"]
        )
        print("[OK] ChromaDB Add document success.")
        
        # 데이터 삭제 (정리)
        collection.delete(ids=["test_id_001"])
        print("[OK] ChromaDB Delete document success.")
        return True
    except Exception as e:
        print(f"[ERROR] ChromaDB connection failed: {e}")
        return False

def test_repositories():
    print("\n--- Testing Repositories ---")
    try:
        rdb = RDBRepository()
        vdb = ChromaDBRepository("test_collection")
        print("[OK] RDBRepository and ChromaDBRepository initialized successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Repository initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Database Connection Tests...")
    
    s_ok = test_supabase_connection()
    c_ok = test_chroma_connection()
    r_ok = test_repositories()
    
    if s_ok and c_ok and r_ok:
        print("\n🎉 All database systems are GO!")
    else:
        print("\n❌ Some tests failed. Please check your .env settings.")
        sys.exit(1)