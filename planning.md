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

Success is defined by two objectively checkable criteria evaluated against `evaluation_results.json` after training:

**Pass criterion (project requirement met):**
- Fine-tuned DistilBERT macro F1 ≥ 0.72 on the held-out test set
- No individual class F1 below 0.60

Both conditions must hold. A macro F1 of 0.72 with one class at 0.45 does not pass. These numbers will be read directly from the classification report printed by the notebook in Section 4 — there is no interpretation required, just comparison to the thresholds above.

**Deployment bar (classifier is genuinely useful):**
- Fine-tuned DistilBERT macro F1 ≥ 0.80
- No individual class F1 below 0.70

At this level the classifier is trustworthy as a first-pass triage tool — surfacing likely-technical posts for a curator or flagging likely-hype for review — with a human in the loop. This is not the project pass/fail; it is the bar that would justify integrating the model into a real community tool.

**Baseline comparison (secondary finding):**
Fine-tuning is expected to outperform the zero-shot Groq baseline. If the improvement is less than 5 percentage points in macro F1, that is a finding worth explaining in the evaluation report — it would suggest either that the label boundaries are too vague to learn from 200 examples, or that a 70B zero-shot model has a genuine advantage on this task. This comparison does not affect pass/fail; it is an analytical question regardless of outcome.

**Why these thresholds:** Macro F1 = 0.72 is meaningfully above both random chance (0.33) and a majority-class baseline (~0.33 on balanced data). It means the model is correct roughly 72% of the time across all classes equally — acceptable for a triage tool where errors are reviewed, not acted on automatically. The floor of 0.60 per class prevents a degenerate model that collapses one label into another from passing.

---

## 7. AI Tool Plan

### 7a. Label Stress-Testing (done before annotation)

Ten boundary posts were generated to stress-test the label definitions. Each is placed at a seam between two labels. The decision and reasoning are recorded — if a post cannot be cleanly decided, the label definition needs tightening before annotating 200 examples.

**`hype` ↔ `discussion` boundary:**

| # | Post | Decision | Reasoning |
|---|------|----------|-----------|
| 1 | "I genuinely think we're 10 years from quantum advantage in drug discovery. The error correction improvements in the last 2 years alone have moved faster than anyone predicted in 2020." | `discussion` | Has a timeline (hype signal) but the claim is grounded in a cited trend. The post invites debate rather than asserting finality. |
| 2 | "Google's Willow results are being massively oversold. Yes, 105 qubits with below-threshold error rates is real progress, but 'solving problems classical computers can't' applies to a narrow sampling task no one cares about practically." | `discussion` | Critical reaction with technical vocabulary, but the purpose is skeptical opinion, not explanation. Reasoning is visible. |
| 3 | "Quantum computing is going to be bigger than the internet. The companies positioning themselves now will dominate computing for the next 50 years." | `hype` | Grand timeline, no evidence, no mechanism. Nothing to debate — just assertion. |
| 4 | "I don't think quantum advantage for real-world problems arrives before 2040. The overhead of fault tolerance makes current hardware essentially useless outside artificial benchmarks." | `discussion` | Timeline prediction, but supported by a stated reason (fault tolerance overhead). The reasoning is present even if not fully explained. |
| 5 | "Everyone is underestimating how fast qubit quality is improving. Look at the progress curves — this is going to move faster than people think." | `hype` | Gestures at evidence ("progress curves") without providing any. The reasoning is absent; the confidence is not. |

**`technical` ↔ `discussion` boundary:**

| # | Post | Decision | Reasoning |
|---|------|----------|-----------|
| 6 | "Comparing trapped ion vs. superconducting qubits for my thesis. Trapped ion has coherence times on the order of seconds vs. microseconds for superconducting, but gate speeds are ~1000x slower. Which architecture will scale better long-term?" | `technical` | The post's value is in the quantitative framing. The closing question invites opinion but the substance is technical. |
| 7 | "Why does Shor's algorithm break RSA but not elliptic curve cryptography? I've read the Wikipedia article but I'm unclear on the difference in the hardness assumptions." | `technical` | Clear technical question, beginner-level but genuine. Unambiguous. |
| 8 | "IBM has 1000+ qubits but Google has better error rates at 105. How should we think about the right metric for measuring quantum progress? Is qubit count a red herring?" | `discussion` | Technical vocabulary used as framing for a conceptual debate about measurement. The question is about the field, not the technology. |
| 9 | "Surface codes require roughly 1000 physical qubits per logical qubit at current error rates. That means millions of physical qubits for useful fault-tolerant computation. Is there a realistic path to getting there in 20 years?" | `discussion` | Opens with a technical fact then pivots to a field-outlook question. The closing question makes the purpose `discussion`. |
| 10 | "Can someone explain the difference between NISQ algorithms and fault-tolerant algorithms? I keep seeing both terms and I'm not sure whether current hardware is capable of either." | `technical` | Genuine technical question from someone who has read enough to know the vocabulary. Clear. |

**Result of stress-test:** No definition changes needed. The decision rules from Section 3 resolved every case without ambiguity — including the two hardest (posts 4 and 6). The key boundary sharpened by this exercise: `discussion` requires that *the primary purpose of the post is debate or opinion*, even if technical content is present. A post that leads with numbers but asks "which will win" is still `technical` if the numbers carry the weight; it is `discussion` if the closing question carries the weight.

---

### 7b. Annotation Assistance

**Decision: yes, use Claude (claude.ai) to pre-label a batch of examples before human review.**

Process:
1. Copy batches of ~30 rows from `dataset.csv` into Claude with the label definitions from Section 2 and the decision rules from Section 3.
2. Ask Claude to assign one of `hype`, `technical`, `discussion` to each row and briefly state its reason.
3. Review every pre-label — accept, reject, or correct — before writing the final label to the CSV.
4. Add a `pre_labeled` column to the CSV: `1` if Claude's suggestion was the starting point, `0` if labeled from scratch.

**Why:** Pre-labeling speeds up annotation for clear cases and forces engagement with the hard cases — it is easier to disagree with a suggested label than to form one from nothing. All labels are human-verified before use.

**Disclosure:** The `pre_labeled` column provides an audit trail. The AI usage section of the README will note that Claude was used for pre-labeling assistance and that every label was human-reviewed.

---

### 7c. Failure Analysis

After training, the notebook prints up to 15 wrong predictions with the true label, predicted label, and confidence score. These will be given to Claude with the following prompt structure:

> "Here are [N] misclassified examples from a 3-class text classifier (hype / technical / discussion) trained on Hacker News quantum computing posts. For each, the true label and predicted label are shown. Identify any patterns — are there systematic confusions between specific label pairs? Are there linguistic features (sentence structure, vocabulary, hedging language) that appear repeatedly in misclassified posts? Do the errors cluster by post type (e.g., short posts, news links, beginner questions)?"

**What to look for:**
- Confusion pair frequency: are most errors `hype`→`discussion` or `technical`→`discussion`? A lopsided pattern points to a specific boundary problem.
- Length effect: are short posts (< 30 words) disproportionately wrong? This would indicate the model needs more signal than a title alone provides.
- Vocabulary leakage: does the presence of technical vocabulary (qubit, algorithm, error rate) cause `hype` posts to be mislabeled as `technical`? This would mean the model learned surface vocabulary rather than discourse structure.

**Verification step:** For any pattern Claude identifies, manually count its frequency in the error list before including it in the evaluation report. Do not report a pattern if it appears in fewer than 3 of the wrong predictions — that is noise, not a finding.
