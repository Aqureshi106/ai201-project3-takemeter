"""Compute human vs. AI pre-label agreement (Cohen's kappa, percent agreement) and analyze corrections."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

LABEL_AGREEMENT_PATH = Path(__file__).parent / "label_agreement.csv"
RESULTS_PATH = Path(__file__).parent / "label_agreement_results.json"
LABELS = ("discussion", "technical", "hype")
REQUIRED_COLUMNS = ("ai_label", "human_label")


def validate_columns(fieldnames: list[str] | None, path: Path) -> None:
    found = set(fieldnames or [])
    missing = [column for column in REQUIRED_COLUMNS if column not in found]
    if missing:
        raise ValueError(
            f"{path.name} is missing required column(s): {', '.join(missing)}"
        )


def validate_label_values(rows: list[dict], path: Path) -> None:
    invalid = []
    for row_number, row in enumerate(rows, start=2):
        for column in REQUIRED_COLUMNS:
            label = row[column]
            if label not in LABELS:
                invalid.append((row_number, column, label or "<blank>"))

    if invalid:
        preview = "; ".join(
            f"row {row_number} {column}={label!r}"
            for row_number, column, label in invalid[:5]
        )
        if len(invalid) > 5:
            preview += f"; ... {len(invalid) - 5} more"
        raise ValueError(
            f"{path.name} contains invalid labels. Expected one of "
            f"{', '.join(LABELS)}. Found: {preview}"
        )


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        validate_columns(reader.fieldnames, path)
        rows = list(reader)
    validate_label_values(rows, path)
    if len(rows) < 30:
        raise ValueError(f"Need 30+ labeled examples, found {len(rows)}")
    return rows


def percent_agreement(rows: list[dict]) -> float:
    n = len(rows)
    agree = sum(1 for r in rows if r["ai_label"] == r["human_label"])
    return agree / n


def cohens_kappa(rows: list[dict]) -> float:
    n = len(rows)
    observed = sum(1 for r in rows if r["ai_label"] == r["human_label"]) / n

    count_ai = Counter(r["ai_label"] for r in rows)
    count_human = Counter(r["human_label"] for r in rows)
    expected = sum(
        (count_ai[label] / n) * (count_human[label] / n) for label in LABELS
    )

    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def correction_analysis(rows: list[dict]) -> dict:
    corrections = [r for r in rows if r["ai_label"] != r["human_label"]]
    pairs = Counter((r["ai_label"], r["human_label"]) for r in corrections)
    by_boundary = Counter()
    for ai, human in pairs:
        key = " ↔ ".join(sorted([ai, human]))
        by_boundary[key] += pairs[(ai, human)]

    return {
        "count": len(corrections),
        "pair_counts": {f"{ai} → {human}": c for (ai, human), c in sorted(pairs.items())},
        "boundary_counts": dict(by_boundary),
        "examples": [
            {
                "id": r["id"],
                "hn_link": r["hn_link"],
                "text_preview": r["text"][:120] + ("…" if len(r["text"]) > 120 else ""),
                "ai_label": r["ai_label"],
                "human_label": r["human_label"],
                "notes": r.get("notes", ""),
            }
            for r in corrections
        ],
    }


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else LABEL_AGREEMENT_PATH
    rows = load_rows(path)

    pct = percent_agreement(rows)
    kappa = cohens_kappa(rows)
    analysis = correction_analysis(rows)

    results = {
        "comparison": "human_final vs claude_prelabel",
        "n_examples": len(rows),
        "percent_agreement": round(pct * 100, 1),
        "cohens_kappa": round(kappa, 3),
        "agreements": len(rows) - analysis["count"],
        "corrections": analysis["count"],
        "correction_analysis": analysis,
    }

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"Examples:           {results['n_examples']}")
    print(f"Percent agreement:  {results['percent_agreement']}%")
    print(f"Cohen's kappa:      {results['cohens_kappa']}")
    print(f"Human corrections:  {results['corrections']}")
    print(f"Results written to {RESULTS_PATH.name}")


if __name__ == "__main__":
    main()
