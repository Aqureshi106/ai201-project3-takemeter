"""Build label_agreement.csv: Claude pre-labels vs final human labels from dataset.csv."""

import csv
from pathlib import Path

ROOT = Path(__file__).parent

# Claude's original suggestion for rows where the human overrode during review.
# Keys are HN item IDs; values are Claude's pre-label before correction.
AI_OVERRIDES = {
    # hype → discussion (17): keyword-matched hype queries; human applied edge-case rules
    "955094": "hype",
    "45395121": "hype",
    "21418141": "hype",
    "28707863": "hype",
    "43319875": "hype",
    "44106327": "hype",
    "44039709": "hype",
    "24287559": "hype",
    "36034283": "hype",
    "21417173": "hype",
    "35741964": "hype",
    "46292467": "hype",
    "46724609": "hype",
    "44622144": "hype",
    "10032094": "hype",
    "43297194": "hype",
    "47679496": "hype",
    # technical → discussion (2): technical vocabulary but discursive intent
    "35912659": "technical",
    "45670953": "technical",
    # hype → technical (1): breakthrough headline on a real physics result
    "32195692": "hype",
}


def claude_label(row: dict) -> str:
    item_id = row["hn_link"].split("=")[-1]
    if item_id in AI_OVERRIDES:
        return AI_OVERRIDES[item_id]
    return row["label"]


def main() -> None:
    with (ROOT / "dataset.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    agreement = []
    for row in rows:
        item_id = row["hn_link"].split("=")[-1]
        ai = claude_label(row)
        human = row["label"]
        agreement.append({
            "id": item_id,
            "text": row["text"],
            "hn_link": row["hn_link"],
            "ai_label": ai,
            "human_label": human,
            "corrected": "1" if ai != human else "0",
            "notes": row.get("notes", ""),
        })

    out = ROOT / "label_agreement.csv"
    fields = ["id", "text", "hn_link", "ai_label", "human_label", "corrected", "notes"]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(agreement)

    agree = sum(1 for r in agreement if r["ai_label"] == r["human_label"])
    print(f"Wrote {len(agreement)} rows to {out.name} ({agree} agree, {len(agreement) - agree} corrected)")


if __name__ == "__main__":
    main()
