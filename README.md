# TakeMeter — AI201 Project 3

Fine-tuning a text classifier on a labeled Reddit dataset and comparing it to a zero-shot Groq baseline.

## Repository Structure

```
ai201-project3-takemeter/
├── planning.md               # Label definitions, annotation decisions, dataset plan
├── dataset.csv               # 200+ labeled examples (text, label)
├── evaluation_results.json   # Accuracy metrics from Colab (added after training)
├── confusion_matrix.png      # Confusion matrix from Colab (added after training)
└── README.md
```

## Dataset

- **Community:** Hacker News (quantum computing posts & comments)
- **Labels:** `hype`, `technical`, `discussion`
- **Total examples:** <!-- e.g. 210 -->
- **Label distribution:** <!-- e.g. hype: 70, technical: 70, discussion: 70 -->

## Models

| Model | Accuracy |
|---|---|
| Zero-shot baseline (Groq llama-3.3-70b-versatile) | <!-- e.g. 0.612 --> |
| Fine-tuned DistilBERT | <!-- e.g. 0.847 --> |

Results from `evaluation_results.json`.

## Setup

Training and evaluation run in the [Colab notebook](https://colab.research.google.com/drive/1YeOdVLvq1HUWaEfOUJ2iGY2cXvQTtRV7?usp=sharing). No local setup required.

## Evaluation Report

### Confusion Matrix

![Confusion Matrix](confusion_matrix.png)

### Error Analysis

<!-- After training, review the wrong predictions printed by the notebook and pick 3 to analyze here. -->

**Error 1:**
- Text: 
- True label: 
- Predicted: 
- Why it's hard: 

**Error 2:**
- Text: 
- True label: 
- Predicted: 
- Why it's hard: 

**Error 3:**
- Text: 
- True label: 
- Predicted: 
- Why it's hard: 

### Observations

<!-- What patterns do you notice? Where does the fine-tuned model outperform the baseline? Where does it still struggle? -->