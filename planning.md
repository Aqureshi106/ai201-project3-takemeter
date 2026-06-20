# Planning — TakeMeter Project 3

---

## 1. Community

**Hacker News** (news.ycombinator.com) — a tech-focused link aggregator and discussion forum used heavily by software engineers, researchers, and startup founders. Quantum computing is a recurring topic there, appearing in the form of news submissions, Ask HN threads, and comment-section debates.

**Why Hacker News fits this task:**
Hacker News is a good fit for discourse classification because its quantum computing content spans a genuinely wide quality spectrum in a single place. At one end: substantive comments that walk through surface code thresholds, explain why qubit count is a misleading metric, or critique a paper's experimental setup. At the other end: breathless "this changes everything" headlines, stock-pump adjacent announcements, and speculative timeline predictions posted with no supporting reasoning. Between those extremes sits a large middle category of community debate — field comparisons, career questions, company roadmap arguments — that is neither purely technical nor purely hype. This three-way variation makes the dataset interesting: a classifier that just learns "does this mention qubits?" won't succeed. The community is also text-heavy by design; even link submissions generate long comment threads, giving rich signal for a language model.

Reddit's r/QuantumComputing was the original choice but was ruled out because Reddit has locked down their API and blocked unauthenticated JSON access. Hacker News's Algolia API is fully open, stable, and returns both story text and comment text — equivalent content for this task.

---

## 2. Labels

Three labels are used: `hype`, `technical`, and `discussion`.

**`hype`** — A post that makes claims about quantum computing's capabilities, impact, or timeline without grounding those claims in technical evidence or reasoned argument. Hype posts are typically reactive, announcement-driven, or financially motivated.

- Example 1: *"Quantum computers will make all current encryption obsolete within 3 years. Banks and governments are not ready."* — Asserts a specific, dramatic timeline with no supporting reasoning or citation.
- Example 2: *"IonQ up 60% today after announcing 1000-qubit roadmap. This is the moment quantum goes mainstream."* — Stock price reaction with no engagement with what 1000 logical vs. physical qubits actually means.

**`technical`** — A post that engages substantively with quantum computing concepts: explaining algorithms, analyzing research results, working through error correction theory, comparing qubit architectures, or asking a question that requires domain knowledge to answer. The value of the post is in its technical content, not its opinion.

- Example 1: *"I've been trying to understand why Shor's algorithm needs fault tolerance. I get the circuit diagram but I'm confused about why the error threshold has to be below ~1% rather than something higher."* — Asks a specific, answerable technical question rooted in prior reading.
- Example 2: *"IBM's new paper on error correction achieves a 0.1% physical error rate with surface codes. To put that in context: fault-tolerant quantum computing generally needs below 1%, so this is meaningful progress — but the qubit overhead to encode one logical qubit is still around 1000:1."* — Quantitative analysis that explains why a result matters.

**`discussion`** — A post that invites community debate or reflection about the field without requiring or delivering technical depth. Discussion posts are substantive opinions, comparisons, or questions about the direction, actors, or culture of quantum computing — but the core value is the exchange of views, not the technical content itself.

- Example 1: *"Is Google actually ahead of IBM in the quantum race? IBM ships more qubits but Google seems to focus more on error rates. Curious how people here think about the right metric."* — Frames a genuine debate question and invites reasoned responses.
- Example 2: *"Thinking about a PhD in quantum computing. Is the academic job market realistic, or should I aim for industry from the start? Would love to hear from people who made that choice."* — Career/field question with no technical content, but invites community knowledge.

---

## 3. Hard Edge Cases

**Edge case 1 — Hype vs. discussion:** A post that makes a strong claim about the field but backs it with some reasoning. Example: *"I think quantum computing will not be useful for optimization problems in the next decade, because variational quantum eigensolvers haven't scaled past toy problems and the hype is driven by VC money, not results."* This has a thesis and evidence, unlike pure hype, but the goal is opinion rather than technical explanation.

**Decision rule:** If the post's primary intent is to persuade or debate a position about the field (rather than explain a concept), it is `discussion` even if it uses some technical vocabulary. Hype requires the additional element of being ungrounded — no reasoning shown, just assertion or excitement.

**Edge case 2 — Technical vs. discussion:** A post comparing two companies' approaches that happens to include real numbers. Example: *"Google's Willow chip claims 105 qubits with below-threshold error rates. IBM has more qubits but higher error rates. Does this mean Google is winning?"* It cites real data but the question is ultimately about competitive standing, not technical understanding.

**Decision rule:** If the post's primary question is "who is winning" or "what should I think about X," it is `discussion`. If the primary question is "how does X work" or "what does this result mean technically," it is `technical`. When genuinely 50/50, label it `discussion` — it is the safer label for borderline cases because the technical content is present but not the point.

**Edge case 3 — Short posts:** A single-sentence submission like *"Quantum computers can now factor 2048-bit RSA keys"* could be hype (if false/exaggerated) or a news link to a real result. Without body text, the title alone is the signal.

**Decision rule:** If the title makes a dramatic capability claim with no qualifier, label it `hype`. If the title accurately describes a verifiable milestone in neutral language, label it `technical`. If still uncertain, check the HN link column to read the comments — community reaction often clarifies whether the post was treated as hype or substance.

---

## 4. Data Collection Plan

**Source:** Hacker News via the Algolia HN Search API (`hn.algolia.com/api/v1/search`). No credentials required. The scraper (`scrape_reddit.py`) queries four terms — *quantum computing*, *qubit*, *quantum supremacy*, *quantum error correction* — across both story and comment types, deduplicates by post ID, and outputs `dataset.csv` with a `text` column (title + body) and a blank `label` column.

**Volume:** 282 posts and comments were scraped. Target is to label 210 examples (~70 per label). The remaining ~72 serve as a reserve in case any label falls short.

**Per-label targets:** 70 `hype`, 70 `technical`, 70 `discussion`. Balanced classes simplify training and make accuracy a more meaningful metric. If a label falls below 60 after going through all 282 examples, the scraper will be re-run with additional queries (e.g., *"quantum startup"* for more hype, *"quantum algorithm"* for more technical) to top it up.

**If a label is underrepresented:** The most likely shortage is `hype` — Hacker News skews toward technically literate posters who call out overclaiming rather than produce it. If `hype` falls short, the query will be broadened to include terms like *"quantum breakthrough"* and *"quantum stock"* which attract more sensational framing.

**Annotation process:** Each row in `dataset.csv` will be labeled using the `hn_link` column to open the original post when the text alone is unclear. The three-class decision rules in Section 3 will be applied in order. If a post cannot be confidently assigned after reading the full thread, it will be discarded rather than guessed.

---

## 5. Evaluation Metrics

**Accuracy** will be reported because it is required by the notebook and easy to interpret: percentage of test-set examples correctly classified.

**Per-class precision, recall, and F1** are also required for this task. Accuracy alone is insufficient here for two reasons:

1. **Class imbalance is possible.** Even with a target of 70 per label, the final test distribution may not be perfectly balanced. A model that predicts `technical` for every post could achieve high accuracy if that class dominates — per-class metrics expose this.

2. **The cost of errors differs by class.** Mislabeling `hype` as `technical` is a worse error than mislabeling `discussion` as `technical`, because a community tool that surfaces hype as credible technical content is actively harmful. F1 per class lets us check whether the model is specifically weak on the hype/technical boundary, which is the most consequential one.

**Macro F1** (unweighted average of per-class F1) will be used as the primary single-number summary metric. Macro F1 treats all classes equally regardless of size, which is appropriate here because no label is inherently more important than another — they all need to work.

**Confusion matrix** will be examined to identify which specific label pairs the model confuses most. The expected hard pairs are `hype`↔`discussion` and `technical`↔`discussion`. If the confusion matrix shows the model is mostly wrong on those two pairs, that is interpretable and expected. If it is confusing `hype` and `technical` at high rates, the label boundary may need rethinking.

---

## 6. Definition of Success

**Minimum bar for this project:** Macro F1 ≥ 0.70 on the test set. This means the fine-tuned DistilBERT model correctly classifies at least 70% of each label on average, which is meaningfully above random chance (0.33) and above a baseline that just predicts the majority class (~0.33 macro F1 on balanced data).

**Bar for genuine usefulness:** Macro F1 ≥ 0.80, with no single class below F1 = 0.70. At this level, the classifier would be trustworthy enough to use as a first-pass filter in a community tool — surfacing likely-technical posts for a curator, or flagging likely-hype posts for review — with a human in the loop for borderline cases.

**Why this threshold:** A macro F1 of 0.80 means the model is wrong roughly 1 in 5 times, evenly across classes. For a triage or surfacing tool (not a gatekeeping tool), that error rate is acceptable because the cost of a false positive or false negative is low — a mislabeled post gets surfaced or filtered incorrectly, but no permanent harm is done. A gatekeeping tool (e.g., one that auto-removes hype posts) would require higher precision on the `hype` class specifically (≥ 0.90) before deployment.

**Comparison to baseline:** The zero-shot Groq baseline will be run on the same test set. If fine-tuning does not improve over the baseline by at least 5 percentage points in macro F1, that is a meaningful finding worth explaining — it would suggest the label boundaries are either too vague for a small fine-tuned model to learn, or that the 200-example dataset is too small to give DistilBERT an edge over a 70B-parameter zero-shot model.
