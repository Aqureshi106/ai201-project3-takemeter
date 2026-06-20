"""
Scrape r/QuantumComputing posts and save to dataset.csv.
Run this in Google Colab or locally with Python 3.

Usage in Colab:
  1. Upload this file or paste the code into a cell
  2. Run it — dataset.csv will be saved to your Colab files
  3. Download dataset.csv and label the 'label' column
"""

import requests
import pandas as pd
import time

SUBREDDIT = "QuantumComputing"
HEADERS = {"User-Agent": "ai201-takemeter-scraper/1.0"}
MIN_WORDS = 15  # skip posts shorter than this


def fetch_posts(sort: str, limit: int = 100, after: str = None) -> list[dict]:
    url = f"https://www.reddit.com/r/{SUBREDDIT}/{sort}.json"
    params = {"limit": limit, "raw_json": 1}
    if after:
        params["after"] = after
    resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["children"], data["data"].get("after")


def collect(sort: str, target: int = 100) -> list[dict]:
    posts, after, seen = [], None, set()
    while len(posts) < target:
        children, after = fetch_posts(sort, limit=100, after=after)
        if not children:
            break
        for child in children:
            p = child["data"]
            if p["id"] in seen:
                continue
            seen.add(p["id"])
            # Combine title + selftext body
            body = p.get("selftext", "").strip()
            body = "" if body in ("[removed]", "[deleted]") else body
            text = (p["title"] + " " + body).strip()
            if len(text.split()) < MIN_WORDS:
                continue
            posts.append({
                "id": p["id"],
                "text": text,
                "label": "",  # fill this in manually
                "score": p.get("score", 0),
                "url": "https://reddit.com" + p.get("permalink", ""),
            })
        print(f"  [{sort}] collected {len(posts)} so far...")
        if not after:
            break
        time.sleep(1)  # be polite to Reddit's servers
    return posts[:target]


print("Fetching posts from r/QuantumComputing...")
all_posts = []
for sort in ("hot", "top", "new"):
    all_posts.extend(collect(sort, target=100))
    time.sleep(2)

# Deduplicate by id
seen_ids = set()
deduped = []
for p in all_posts:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        deduped.append(p)

df = pd.DataFrame(deduped)[["text", "label", "score", "url"]]
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

print(f"\nTotal unique posts collected: {len(df)}")
print(df["text"].str.split().str.len().describe().to_string())

df.to_csv("dataset.csv", index=False)
print("\nSaved: dataset.csv")
print("Next step: open the CSV and fill in the 'label' column.")
print("Use labels: hype | technical | discussion")
print("Aim for ~70 of each. The 'url' column links back to the original post.")
