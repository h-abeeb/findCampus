import os

from supabase import create_client

from dotenv import load_dotenv
load_dotenv()


def get_db():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_KEY before using the API.")
    return create_client(url, key)
