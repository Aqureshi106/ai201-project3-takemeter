"""
TakeMeter — Gradio demo for the fine-tuned QC post classifier.

Run this as a Colab cell (after training) or locally if you have
the fine-tuned model saved to ./finetuned_model.

In Colab: copy the block below into a new cell and run it.
Locally:  pip install gradio transformers torch
          python gradio_demo.py
"""

import gradio as gr
from transformers import pipeline

MODEL_PATH = "./finetuned_model"

# Label order must match the LABEL_MAP used during training
ID2LABEL = {0: "discussion", 1: "technical", 2: "hype"}

classifier = pipeline(
    "text-classification",
    model=MODEL_PATH,
    return_all_scores=True,
)


def classify_post(text: str) -> str:
    if not text.strip():
        return "Enter a post above."

    raw = classifier(text[:512])[0]

    # Normalise label keys — pipeline may return 'LABEL_0' or actual names
    scores = {}
    for item in raw:
        key = item["label"]
        if key.startswith("LABEL_"):
            key = ID2LABEL[int(key.split("_")[1])]
        scores[key] = item["score"]

    predicted = max(scores, key=scores.get)
    confidence = scores[predicted]

    lines = [
        f"Predicted:  {predicted}",
        f"Confidence: {confidence:.3f}",
        "",
        "All scores:",
    ]
    for label in ("discussion", "technical", "hype"):
        bar = "█" * int(scores.get(label, 0) * 30)
        lines.append(f"  {label:12s} {scores.get(label, 0):.3f}  {bar}")

    return "\n".join(lines)


demo = gr.Interface(
    fn=classify_post,
    inputs=gr.Textbox(
        lines=6,
        placeholder="Paste a Hacker News quantum computing post or comment here…",
        label="Post text",
    ),
    outputs=gr.Textbox(label="Classification result", lines=10),
    title="TakeMeter — Quantum Computing Post Classifier",
    description=(
        "Fine-tuned DistilBERT classifier trained on 208 labeled Hacker News posts. "
        "Labels: hype · technical · discussion"
    ),
    flagging_mode="never",
    examples=[
        "Google's new quantum chip solves in minutes what would take classical computers 10,000 years. This changes everything.",
        "The surface code threshold theorem says below ~1% physical error rate, each additional layer of concatenation exponentially suppresses logical errors. The 1000:1 overhead is the real bottleneck.",
        "Is quantum computing going to break Bitcoin? I keep seeing conflicting takes — some say 10 years, some say never. What do people here actually think?",
    ],
)

if __name__ == "__main__":
    demo.launch(share=True)
