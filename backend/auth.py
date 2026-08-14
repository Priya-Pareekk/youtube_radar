"""
Auth: verifies the Supabase JWT sent by the frontend, then hands back a
Supabase client that's scoped to that user's token — so every DB query
made with it automatically respects Row Level Security. No custom
session/JWT handling needed on our end; Supabase does that part.
"""

import os
from typing import Optional
from fastapi import Header, HTTPException
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


def get_user_client(authorization: Optional[str] = Header(default=None)):
    """
    Optional auth — used on routes that work for both signed-in and
    anonymous users (e.g. /api/analyze saves history only if logged in).
    Returns (None, None) if there's no valid session.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None, None
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None, None

    token = authorization.split(" ", 1)[1]
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        user_resp = client.auth.get_user(token)
        user = user_resp.user
    except Exception:
        return None, None

    if not user:
        return None, None

    client.postgrest.auth(token)
    return client, user


def require_user_client(authorization: Optional[str] = Header(default=None)):
    """Required auth — used on routes that only make sense for a logged-in user."""
    client, user = get_user_client(authorization)
    if not client or not user:
        raise HTTPException(status_code=401, detail="Sign in required.")
    return client, user
