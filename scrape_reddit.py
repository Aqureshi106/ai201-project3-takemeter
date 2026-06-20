"""
Scrape r/QuantumComputing posts and save to dataset.csv.
Requires Reddit API credentials (free):
  1. Go to reddit.com/prefs/apps -> create app -> type: script
  2. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to Colab Secrets
"""

import subprocess
subprocess.run(["pip", "install", "-q", "praw"], check=True)

import praw
import pandas as pd
import time
from google.colab import userdata

REDDIT_CLIENT_ID     = userdata.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = userdata.get("REDDIT_CLIENT_SECRET")

assert REDDIT_CLIENT_ID,     "Add REDDIT_CLIENT_ID to Colab Secrets"
assert REDDIT_CLIENT_SECRET, "Add REDDIT_CLIENT_SECRET to Colab Secrets"

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="ai201-takemeter-scraper/1.0",
)

SUBREDDIT = "QuantumComputing"
MIN_WORDS = 15


def collect(sort: str, target: int = 100) -> list[dict]:
    sub = reddit.subreddit(SUBREDDIT)
    if sort == "hot":
        gen = sub.hot(limit=target * 2)
    elif sort == "top":
        gen = sub.top(limit=target * 2, time_filter="year")
    else:
        gen = sub.new(limit=target * 2)

    posts, seen = [], set()
    for submission in gen:
        if len(posts) >= target:
            break
        if submission.id in seen:
            continue
        seen.add(submission.id)
        body = submission.selftext.strip()
        body = "" if body in ("[removed]", "[deleted]") else body
        text = (submission.title + " " + body).strip()
        if len(text.split()) < MIN_WORDS:
            continue
        posts.append({
            "id": submission.id,
            "text": text,
            "label": "",
            "score": submission.score,
            "url": "https://reddit.com" + submission.permalink,
        })
    print(f"  [{sort}] collected {len(posts)} posts")
    return posts


print("Fetching posts from r/QuantumComputing...")
all_posts = []
for sort_type in ("hot", "top", "new"):
    all_posts.extend(collect(sort_type, target=100))
    time.sleep(1)

# Deduplicate
seen_ids = set()
deduped = []
for p in all_posts:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        deduped.append(p)

df = pd.DataFrame(deduped)[["text", "label", "score", "url"]]
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nTotal unique posts: {len(df)}")
print(df["text"].str.split().str.len().describe().to_string())

df.to_csv("dataset.csv", index=False)
print("\nSaved: dataset.csv")
print("Open it and fill in the 'label' column: hype | technical | discussion")
print("Aim for ~70 of each. The 'url' column links to the original post.")
