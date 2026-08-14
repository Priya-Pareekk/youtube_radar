"""
YouTube source: search for videos on a topic, pull top-level comments.
Returns a platform-agnostic list of {platform, id, title, url, comments}
so main.py can treat every source identically.
"""

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_youtube_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return None
    return build("youtube", "v3", developerKey=api_key)


def fetch_youtube_items(topic: str, max_items: int):
    youtube = get_youtube_client()
    if youtube is None:
        return []

    try:
        search_response = youtube.search().list(
            q=topic, part="id,snippet", maxResults=max_items, type="video"
        ).execute()
    except HttpError:
        return []

    items = []
    for entry in search_response.get("items", []):
        if "videoId" not in entry["id"]:
            continue

        video_id = entry["id"]["videoId"]
        title = entry["snippet"]["title"]
        comments = []

        try:
            resp = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=20,
            ).execute()
            for c in resp.get("items", []):
                comments.append(c["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
        except HttpError:
            pass  # comments disabled, quota hit, etc — skip quietly

        items.append({
            "platform": "youtube",
            "id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "comments": comments,
        })

    return items
