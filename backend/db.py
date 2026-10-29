import os
from functools import wraps

from dotenv import load_dotenv
from flask import g, jsonify, request
from supabase import create_client

load_dotenv()


def get_db():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_KEY before using the API.")
    return create_client(url, key)


def current_user():
    token = request.headers.get(
        "Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        return None
    try:
        return get_db().auth.get_user(token).user
    except Exception:
        return None


def require_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "Please sign in."}), 401
        g.user = user
        return f(*args, **kwargs)
    return wrapper
