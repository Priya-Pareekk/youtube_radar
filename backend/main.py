"""
TubeRadar API
-------------
- /api/analyze, /api/compare — scan a topic across YouTube and/or Reddit.
  If the request is authenticated (Supabase JWT), the scan is also saved
  to that user's history.
- /api/history — list a signed-in user's past scans.
- /api/watches — create/list/delete "watch this topic" alerts.
- /api/watches/run — protected endpoint a scheduled job (GitHub Actions
  cron) calls daily to re-check every active watch and email on a
  sentiment drop.
"""

import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client

from sentiment import score_text, label_for, extract_themes
from sources.youtube_source import fetch_youtube_items
from sources.reddit_source import fetch_reddit_items
from auth import get_user_client, require_user_client
from email_alerts import send_alert_email

load_dotenv()

app = FastAPI(title="TubeRadar API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CRON_SECRET = os.getenv("CRON_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

VALID_PLATFORMS = {"youtube", "reddit"}


# --- Schemas -------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    topic: str
    limit: int = Field(default=10, ge=1, le=50)
    platforms: List[str] = Field(default=["youtube"])


class CompareRequest(BaseModel):
    topic_a: str
    topic_b: str
    limit: int = Field(default=10, ge=1, le=50)
    platforms: List[str] = Field(default=["youtube"])


class WatchCreate(BaseModel):
    topic: str
    mode: str = "solo"
    platforms: List[str] = Field(default=["youtube"])
    threshold: float = Field(default=0.15, ge=0.01, le=1.0)
    email: str


# --- Core analysis, shared by /analyze, /compare, and /watches/run -------

def clean_platforms(platforms: List[str]) -> List[str]:
    cleaned = [p for p in platforms if p in VALID_PLATFORMS]
    return cleaned or ["youtube"]


def analyze_topic(topic: str, max_items: int, platforms: List[str]):
    platforms = clean_platforms(platforms)

    items = []
    if "youtube" in platforms:
        items += fetch_youtube_items(topic, max_items)
    if "reddit" in platforms:
        items += fetch_reddit_items(topic, max_items)

    all_comments = []
    all_scores = []
    item_summaries = []

    for it in items:
        item_scores = []
        for text in it["comments"]:
            score = score_text(text)
            label = label_for(score)
            all_comments.append({
                "platform": it["platform"],
                "source_title": it["title"],
                "text": text,
                "score": round(score, 3),
                "label": label,
            })
            item_scores.append(score)
            all_scores.append(score)

        if item_scores:
            item_summaries.append({
                "platform": it["platform"],
                "id": it["id"],
                "title": it["title"],
                "url": it["url"],
                "comment_count": len(item_scores),
                "avg_score": round(sum(item_scores) / len(item_scores), 3),
            })

    if not all_scores:
        return None

    avg_score = sum(all_scores) / len(all_scores)
    pos = sum(1 for s in all_scores if s > 0.15)
    neg = sum(1 for s in all_scores if s < -0.15)
    neu = len(all_scores) - pos - neg

    return {
        "topic": topic,
        "platforms": platforms,
        "avg_score": round(avg_score, 3),
        "total_comments": len(all_scores),
        "item_count": len(item_summaries),
        "sentiment_split": {"positive": pos, "negative": neg, "neutral": neu},
        "items": sorted(item_summaries, key=lambda v: v["avg_score"]),
        "comments": all_comments,
        "themes": extract_themes([c["text"] for c in all_comments]),
    }


def save_scan(client, user, mode: str, result: dict, topic_b: Optional[str] = None):
    try:
        client.table("scans").insert({
            "user_id": user.id,
            "mode": mode,
            "topic": result["topic"],
            "topic_b": topic_b,
            "avg_score": result["avg_score"],
            "total_comments": result["total_comments"],
            "item_count": result["item_count"],
            "platforms": result["platforms"],
            "result": result,
        }).execute()
    except Exception as e:
        # Saving history should never break the actual scan response.
        print(f"[history save failed] {e}")


# --- Routes ----------------------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "youtube_configured": bool(os.getenv("YOUTUBE_API_KEY")),
        "reddit_configured": bool(os.getenv("REDDIT_CLIENT_ID")),
        "supabase_configured": bool(SUPABASE_URL),
        "email_configured": bool(os.getenv("RESEND_API_KEY")),
    }


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest, authorization: Optional[str] = Header(default=None)):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required.")

    result = analyze_topic(req.topic.strip(), req.limit, req.platforms)
    if result is None:
        raise HTTPException(status_code=404, detail="No comments found for this topic.")

    client, user = get_user_client(authorization)
    if client and user:
        save_scan(client, user, "solo", result)

    return result


@app.post("/api/compare")
def compare(req: CompareRequest, authorization: Optional[str] = Header(default=None)):
    if not req.topic_a.strip() or not req.topic_b.strip():
        raise HTTPException(status_code=400, detail="Both topics are required.")

    result_a = analyze_topic(req.topic_a.strip(), req.limit, req.platforms)
    result_b = analyze_topic(req.topic_b.strip(), req.limit, req.platforms)
    if result_a is None or result_b is None:
        raise HTTPException(status_code=404, detail="No comments found for one or both topics.")

    winner = req.topic_a if result_a["avg_score"] > result_b["avg_score"] else req.topic_b
    payload = {
        "a": result_a,
        "b": result_b,
        "winner": winner,
        "gap": round(abs(result_a["avg_score"] - result_b["avg_score"]), 3),
    }

    client, user = get_user_client(authorization)
    if client and user:
        save_scan(client, user, "compare", result_a, topic_b=req.topic_b)

    return payload


@app.get("/api/history")
def history(auth_data=Depends(require_user_client)):
    client, _user = auth_data
    resp = (
        client.table("scans")
        .select("id,mode,topic,topic_b,avg_score,total_comments,item_count,platforms,created_at")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return resp.data


@app.get("/api/history/{scan_id}")
def history_detail(scan_id: str, auth_data=Depends(require_user_client)):
    client, _user = auth_data
    resp = client.table("scans").select("*").eq("id", scan_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return resp.data


@app.post("/api/watches")
def create_watch(req: WatchCreate, auth_data=Depends(require_user_client)):
    client, user = auth_data
    platforms = clean_platforms(req.platforms)

    baseline = analyze_topic(req.topic, 10, platforms)
    baseline_score = baseline["avg_score"] if baseline else None

    resp = client.table("watches").insert({
        "user_id": user.id,
        "topic": req.topic,
        "mode": req.mode,
        "platforms": platforms,
        "threshold": req.threshold,
        "email": req.email,
        "baseline_score": baseline_score,
        "last_score": baseline_score,
    }).execute()

    return resp.data[0] if resp.data else {}


@app.get("/api/watches")
def list_watches(auth_data=Depends(require_user_client)):
    client, _user = auth_data
    resp = client.table("watches").select("*").order("created_at", desc=True).execute()
    return resp.data


@app.delete("/api/watches/{watch_id}")
def delete_watch(watch_id: str, auth_data=Depends(require_user_client)):
    client, _user = auth_data
    client.table("watches").delete().eq("id", watch_id).execute()
    return {"deleted": True}


@app.post("/api/watches/run")
def run_watches(x_cron_secret: Optional[str] = Header(default=None)):
    """
    Called by a scheduled job (see .github/workflows/run-watches.yml),
    not by the frontend. Uses the service-role key to read/update across
    all users' watches, bypassing Row Level Security by design.
    """
    if not CRON_SECRET or x_cron_secret != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase service role key not configured.")

    service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    watches = service_client.table("watches").select("*").eq("active", True).execute().data or []

    checked = 0
    alerted = 0

    for w in watches:
        result = analyze_topic(w["topic"], 10, w.get("platforms") or ["youtube"])
        if result is None:
            continue

        checked += 1
        new_score = result["avg_score"]
        old_score = w["last_score"] if w.get("last_score") is not None else new_score
        drop = old_score - new_score

        if drop >= w["threshold"]:
            send_alert_email(w["email"], w["topic"], old_score, new_score, drop)
            alerted += 1

        service_client.table("watches").update({
            "last_score": new_score,
            "last_checked_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", w["id"]).execute()

    return {"checked": checked, "alerted": alerted}
