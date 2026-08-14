"""
Reddit source: search r/all for a topic, pull top-level comments from
each matching post. Same output shape as the YouTube source.
"""

import os
import praw


def get_reddit_client():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=os.getenv("REDDIT_USER_AGENT", "tuberadar/1.0 (by /u/unknown)"),
    )


def fetch_reddit_items(topic: str, max_items: int):
    reddit = get_reddit_client()
    if reddit is None:
        return []

    try:
        submissions = list(
            reddit.subreddit("all").search(topic, limit=max_items, sort="relevance")
        )
    except Exception:
        return []

    items = []
    for submission in submissions:
        comments = []
        try:
            submission.comments.replace_more(limit=0)
            for c in submission.comments[:20]:
                if hasattr(c, "body"):
                    comments.append(c.body)
        except Exception:
            pass

        items.append({
            "platform": "reddit",
            "id": submission.id,
            "title": submission.title,
            "url": f"https://reddit.com{submission.permalink}",
            "comments": comments,
        })

    return items
