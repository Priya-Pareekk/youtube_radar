"""
TubeRadar API
-------------
FastAPI backend that exposes the YouTube sentiment-scanning logic
(previously baked into a single Streamlit script) as a clean JSON API
for the React frontend to consume.
"""

import os
import re
import collections
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

app = FastAPI(title="TubeRadar API", version="1.0.0")

# In dev, allow the Vite dev server. Tighten this before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentIntensityAnalyzer()

STOPWORDS = {
    "this", "that", "with", "from", "have", "just", "your", "about", "which",
    "would", "there", "their", "because", "really", "think", "people", "video",
    "youtube", "comment", "comments", "doesnt", "didnt", "actually", "still",
    "being", "other", "these", "those", "where", "when", "what", "watch",
    "watching", "channel", "subscribe",
}


# --- Schemas -----------------------------------------------------------

class AnalyzeRequest(BaseModel):
    topic: str
    limit: int = Field(default=10, ge=1, le=50)


class CompareRequest(BaseModel):
    topic_a: str
    topic_b: str
    limit: int = Field(default=10, ge=1, le=50)


# --- YouTube + sentiment helpers ---------------------------------------

def get_youtube():
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="YOUTUBE_API_KEY is not set on the server. Add it to backend/.env",
        )
    return build("youtube", "v3", developerKey=API_KEY)


def label_for(score: float) -> str:
    if score > 0.15:
        return "Positive"
    if score < -0.15:
        return "Negative"
    return "Neutral"


def get_comments(youtube, video_id: str, limit: int = 20) -> List[str]:
    comments = []
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=min(limit, 100),
        ).execute()
        for item in response.get("items", []):
            comments.append(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
    except HttpError:
        # Comments disabled, video not found, quota issue, etc. — skip quietly.
        pass
    return comments


def extract_themes(comments: List[str], top_n: int = 10):
    text = " ".join(comments).lower()
    words = re.findall(r"[a-zA-Z']+", text)
    filtered = [w for w in words if len(w) > 4 and w not in STOPWORDS]
    counts = collections.Counter(filtered).most_common(top_n)
    return [{"word": w, "count": c} for w, c in counts]


def analyze_topic(youtube, topic: str, max_videos: int):
    search_response = youtube.search().list(
        q=topic, part="id,snippet", maxResults=max_videos, type="video"
    ).execute()

    videos = []
    all_comments = []
    all_scores = []

    for item in search_response.get("items", []):
        if "videoId" not in item["id"]:
            continue

        vid_id = item["id"]["videoId"]
        vid_title = item["snippet"]["title"]
        raw_comments = get_comments(youtube, vid_id)

        video_scores = []
        for comment in raw_comments:
            score = analyzer.polarity_scores(comment)["compound"]
            label = label_for(score)
            all_comments.append({
                "video_id": vid_id,
                "video_title": vid_title,
                "text": comment,
                "score": round(score, 3),
                "label": label,
            })
            video_scores.append(score)
            all_scores.append(score)

        if video_scores:
            videos.append({
                "video_id": vid_id,
                "title": vid_title,
                "comment_count": len(video_scores),
                "avg_score": round(sum(video_scores) / len(video_scores), 3),
            })

    if not all_scores:
        return None

    avg_score = sum(all_scores) / len(all_scores)
    pos = sum(1 for s in all_scores if s > 0.15)
    neg = sum(1 for s in all_scores if s < -0.15)
    neu = len(all_scores) - pos - neg

    return {
        "topic": topic,
        "avg_score": round(avg_score, 3),
        "total_comments": len(all_scores),
        "video_count": len(videos),
        "sentiment_split": {"positive": pos, "negative": neg, "neutral": neu},
        # Weakest-sentiment video first — usually the most interesting to look at.
        "videos": sorted(videos, key=lambda v: v["avg_score"]),
        "comments": all_comments,
        "themes": extract_themes([c["text"] for c in all_comments]),
    }


# --- Routes --------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "api_key_configured": bool(API_KEY)}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required.")
    youtube = get_youtube()
    result = analyze_topic(youtube, req.topic.strip(), req.limit)
    if result is None:
        raise HTTPException(status_code=404, detail="No comments found for this topic.")
    return result


@app.post("/api/compare")
def compare(req: CompareRequest):
    if not req.topic_a.strip() or not req.topic_b.strip():
        raise HTTPException(status_code=400, detail="Both topics are required.")
    youtube = get_youtube()
    result_a = analyze_topic(youtube, req.topic_a.strip(), req.limit)
    result_b = analyze_topic(youtube, req.topic_b.strip(), req.limit)
    if result_a is None or result_b is None:
        raise HTTPException(status_code=404, detail="No comments found for one or both topics.")

    winner = req.topic_a if result_a["avg_score"] > result_b["avg_score"] else req.topic_b
    return {
        "a": result_a,
        "b": result_b,
        "winner": winner,
        "gap": round(abs(result_a["avg_score"] - result_b["avg_score"]), 3),
    }
