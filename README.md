# Smabbler Benchmarks

A collection of benchmarks evaluating the quality and results of Smabbler Galaxia's semantic hypergraph construction, knowledge augmentation, and retrieval capabilities.

---

## Benchmarks

### [PubMedQA — Biomedical Article Retrieval](./pubmed/)

Evaluates how well the Smabbler Galaxia search/API workflow retrieves the correct PubMed article for a given biomedical question. It uses the **PubMedQA Labeled Artificial (PQAL)** test set, where each question is associated with a known PubMed ID and the system is considered successful when that ID appears in the returned results.

**Dataset:** PQAL test set from [BigBio/pubmed_qa](https://huggingface.co/datasets/bigbio/pubmed_qa) — 500 questions, each mapped to a ground-truth PubMed ID.

**Metric:** Recall@K — the percentage of questions for which the correct PubMed ID appears within the top K retrieved results. Results are calculated using rank grouping, which correctly handles tied rankings.

| Metric | Result |
|------------|-------------|
| Recall@1 | 93.00% (465/500) |
| Recall@3 | 96.20% (482/500) |
| Recall@5 | 97.20% (486/500) |
| Recall@10 | 98.20% (491/500) |
| Recall@25 | 98.80% (494/500) |
| Recall@50 | 99.00% (495/500) |
| Recall@100 | 99.00% (495/500) |

**Benchmark flow:**
1. Download and prepare the PQAL dataset into article content and question CSV files.
2. Upload content to Galaxia, build and activate a retrieval model, run all 500 questions, and save ranked results.
3. Calculate Recall@K across thresholds (1, 3, 5, 10, 25, 50, 100).
