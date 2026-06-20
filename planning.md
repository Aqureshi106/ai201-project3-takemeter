# Planning — TakeMeter Project 3

## Community

**r/QuantumComputing** (~170k members) — a subreddit for discussing quantum computing research, news, and education. The community spans researchers, students, and enthusiasts, which creates a wide quality spectrum: rigorous technical breakdowns sit alongside breathless hype posts and genuine beginner questions. This range makes it well-suited for discourse classification.

## Community Description

r/QuantumComputing is an active Reddit community where posts range from serious technical discussion of algorithms and error correction to sensational news headlines about quantum supremacy and stock prices. The quality distinction that matters here is whether a post engages with the actual technical substance of quantum computing or just reacts to its cultural/financial narrative. Regular members in this community are quick to call out overclaiming — the "Quantum Bullshit Detector" culture is real — which means this label boundary is meaningful to insiders.

---

## Label Definitions

**Label 1 — `hype`**
Posts that make sensational or speculative claims about quantum computing's capabilities, impact, or timeline without technical grounding. Typically news headlines, stock price discussions, "this changes everything" announcements, or predictions not backed by reasoning.

- Example 1: "Quantum computers will break all encryption within 5 years — should we be worried?"
- Example 2: "IONQ stock is up 40% after their latest qubit announcement 🚀🚀"
- Borderline: A post sharing a Google research paper titled "Quantum supremacy achieved" with no body text — it's a real paper, but the framing and lack of any technical engagement makes it lean hype.

---

**Label 2 — `technical`**
Posts that engage substantively with quantum computing concepts: explaining algorithms, analyzing research papers, discussing error correction, comparing qubit architectures, or working through implementation details. The post itself contains or invites real technical content.

- Example 1: "Can someone explain why Shor's algorithm requires a fault-tolerant quantum computer? I understand the circuit but not the error threshold requirement."
- Example 2: "IBM's new error correction paper claims a threshold of 0.1% — here's why that matters for surface codes specifically."
- Borderline: "What's the difference between gate-based and annealing quantum computers?" — it's a real question but may get one-line answers. Lean technical if the asker shows they've read something; lean discussion if it's purely open-ended.

---

**Label 3 — `discussion`**
Posts that invite community debate or reflection about the quantum computing field without requiring technical depth: comparisons between company roadmaps, career/education advice, field outlook debates, or reactions to news that go beyond the headline into reasoned opinion.

- Example 1: "Is Google or IBM actually ahead in the quantum race right now? IBM has more qubits but Google's error rates seem better."
- Example 2: "Should I pursue a PhD in quantum computing in 2025? Curious what the job market looks like for people coming out of programs."
- Borderline: A post debating whether a specific company's qubit count claims are credible — could be hype (if just venting) or discussion (if reasoning through the evidence).

---

## Mutual Exclusivity Check

The main overlap risk is between **hype** and **discussion** — both can be opinionated and non-technical. The boundary: *discussion* posts show reasoning or invite reasoned debate; *hype* posts make claims without justification or are purely reactive (stock pumping, breathless headlines).

The secondary risk is **technical** vs. **discussion** — a post can be both substantive and opinion-based. The boundary: if the post's core value is the technical content or question, it's *technical*; if the core value is community debate, it's *discussion*.

A random post can be assigned to exactly one label in the majority of cases.

---

## Dataset Collection

- **Source:** r/QuantumComputing (reddit.com/r/QuantumComputing)
- **Collection method:** Manual copy-paste from Reddit — top posts (past year) and new posts
- **Filtering:** Remove posts with no body text (image-only, link-only with no comment), mod announcements, and posts under 15 words
- **Target count:** 210 examples (~70 per label)
- **Actual count:** TBD

## CSV Format

| column | description |
|--------|-------------|
| `text` | Post title + body text concatenated |
| `label` | One of: `hype`, `technical`, `discussion` |

---

## Potential Challenges

- **Hype vs. discussion boundary:** A reasonable-sounding prediction can look like either. Rule: if there's no reasoning shown, it's hype.
- **Short posts:** Titles alone may not have enough signal — always include body text where available.
- **Technical questions from beginners:** These belong in `technical` even if superficial, because the intent is to engage with substance.
