"""
Scrape r/QuantumComputing posts and save to dataset.csv.
No API credentials required — uses Reddit's public JSON endpoint.

Run in Google Colab or locally with Python 3.
"""

import requests
import pandas as pd
import time

SUBREDDIT = "QuantumComputing"
HEADERS = {"User-Agent": "ai201-takemeter-scraper/1.0"}
MIN_WORDS = 15


def fetch_posts(sort: str, after: str = None) -> tuple[list, str | None]:
    url = f"https://www.reddit.com/r/{SUBREDDIT}/{sort}.json"
    params = {"limit": 100, "raw_json": 1}
    if after:
        params["after"] = after
    resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["children"], data["data"].get("after")


def collect(sort: str, target: int = 100) -> list[dict]:
    posts, after, seen = [], None, set()
    while len(posts) < target:
        children, after = fetch_posts(sort, after=after)
        if not children:
            break
        for child in children:
            p = child["data"]
            if p["id"] in seen:
                continue
            seen.add(p["id"])
            body = p.get("selftext", "").strip()
            body = "" if body in ("[removed]", "[deleted]") else body
            text = (p["title"] + " " + body).strip()
            if len(text.split()) < MIN_WORDS:
                continue
            posts.append({
                "id": p["id"],
                "text": text,
                "label": "",
                "score": p.get("score", 0),
                "url": "https://reddit.com" + p.get("permalink", ""),
            })
        print(f"  [{sort}] {len(posts)} posts so far...")
        if not after:
            break
        time.sleep(1)
    return posts[:target]


print("Fetching posts from r/QuantumComputing...")
all_posts = []
for sort_type in ("hot", "top", "new"):
    all_posts.extend(collect(sort_type, target=100))
    time.sleep(2)

# Deduplicate
seen_ids = set()
deduped = []
for p in all_posts:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        deduped.append(p)

df = pd.DataFrame(deduped)[["text", "label", "score", "url"]]
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nTotal unique posts collected: {len(df)}")
print(df["text"].str.split().str.len().describe().to_string())

df.to_csv("dataset.csv", index=False)
print("\nSaved: dataset.csv")
print("Next step: open the CSV and fill in the 'label' column.")
print("Use labels: hype | technical | discussion")
print("Aim for ~70 of each. The 'url' column links back to the original post.")
