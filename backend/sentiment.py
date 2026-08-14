"""
Sentiment scoring + theme extraction, shared across all data sources
(YouTube, Reddit, ...) so every platform is scored the same way.
"""

import re
import collections
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

STOPWORDS = {
    "this", "that", "with", "from", "have", "just", "your", "about", "which",
    "would", "there", "their", "because", "really", "think", "people", "video",
    "youtube", "comment", "comments", "doesnt", "didnt", "actually", "still",
    "being", "other", "these", "those", "where", "when", "what", "watch",
    "watching", "channel", "subscribe", "reddit", "post", "thread", "upvote",
}


def score_text(text: str) -> float:
    return analyzer.polarity_scores(text)["compound"]


def label_for(score: float) -> str:
    if score > 0.15:
        return "Positive"
    if score < -0.15:
        return "Negative"
    return "Neutral"


def extract_themes(comments, top_n: int = 10):
    text = " ".join(comments).lower()
    words = re.findall(r"[a-zA-Z']+", text)
    filtered = [w for w in words if len(w) > 4 and w not in STOPWORDS]
    counts = collections.Counter(filtered).most_common(top_n)
    return [{"word": w, "count": c} for w, c in counts]
