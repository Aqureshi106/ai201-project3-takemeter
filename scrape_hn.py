"""
Scrape Hacker News posts about quantum computing and save to dataset.csv.
Uses the Algolia HN Search API — no credentials required.

Run locally:  python scrape_hn.py
Run in Colab: upload and run as a cell (works from any IP)
"""

import re
import requests
import pandas as pd
import time

QUERIES = ["quantum computing", "qubit", "quantum supremacy", "quantum error correction"]
MIN_WORDS = 15


def fetch_page(query: str, page: int, tags: str) -> list[dict]:
    url = "https://hn.algolia.com/api/v1/search"
    params = {"query": query, "tags": tags, "hitsPerPage": 50, "page": page}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("hits", [])


def collect(query: str, tags: str, target: int) -> list[dict]:
    posts, seen = [], set()
    page = 0
    while len(posts) < target:
        hits = fetch_page(query, page=page, tags=tags)
        if not hits:
            break
        for h in hits:
            oid = h.get("objectID")
            if oid in seen:
                continue
            seen.add(oid)
            if tags == "story":
                title = (h.get("title") or "").strip()
                body = (h.get("story_text") or "").strip()
                text = (title + " " + body).strip()
            else:
                raw = (h.get("comment_text") or "").strip()
                text = re.sub(r"<[^>]+>", " ", raw).strip()
            if len(text.split()) < MIN_WORDS:
                continue
            posts.append({
                "id": oid,
                "text": text,
                "label": "",
                "score": h.get("points") or 0,
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                "hn_link": f"https://news.ycombinator.com/item?id={oid}",
            })
        page += 1
        time.sleep(0.5)
    return posts[:target]


print("Fetching Hacker News posts about quantum computing...")
all_posts = []
for q in QUERIES:
    print(f"\n-- '{q}' --")
    all_posts += collect(q, tags="story", target=75)
    all_posts += collect(q, tags="comment", target=50)
    time.sleep(1)

# Deduplicate
seen_ids = set()
deduped = []
for p in all_posts:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        deduped.append(p)

df = pd.DataFrame(deduped)[["text", "label", "score", "url", "hn_link"]]
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nTotal unique posts/comments: {len(df)}")
print(df["text"].str.split().str.len().describe().to_string())

df.to_csv("dataset.csv", index=False)
print("\nSaved: dataset.csv")
print("Fill in the 'label' column: hype | technical | discussion (~70 each)")
print("Use 'hn_link' to read the full thread for context.")
