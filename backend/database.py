from supabase import create_client, Client
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

Base = declarative_base()
engine = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        SessionLocal = supabase
        print("✅ Supabase 연결 성공")
    else:
        print("⚠️ SUPABASE_URL 또는 SUPABASE_KEY 없음 → 목업 모드")
        supabase = None
        SessionLocal = None
except Exception as e:
    print(f"⚠️ Supabase 연결 실패 → 목업 모드: {e}")
    supabase = None
    SessionLocal = None

def get_supabase():
    return supabase
