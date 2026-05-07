import json
import logging
from itertools import groupby

logger = logging.getLogger(__name__)


class Benchmark:
    @staticmethod
    def calculate_metrics(pqal_results_path: str, group_by_rank: bool = True):
        with open(pqal_results_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        thresholds = [1, 3, 5, 10, 25, 50, 100]
        metrics = {}

        total_questions = len(questions)
        hits = {k: 0 for k in thresholds}

        for question_pmid, ranked_results in questions.items():

            if group_by_rank:
                grouped = []
                for _, group_items in groupby(ranked_results, key=lambda x: x["rank"]):
                    pmids = list({item["pmid"] for item in group_items})
                    grouped.append(pmids)

                for k in thresholds:
                    top_k_pmids = set()

                    for group in grouped[:k]:
                        top_k_pmids.update(group)

                    if question_pmid in top_k_pmids:
                        hits[k] += 1

            else:
                result_pmids = [item["pmid"] for item in ranked_results]

                for k in thresholds:
                    top_k_pmids = set(result_pmids[:k])

                    if question_pmid in top_k_pmids:
                        hits[k] += 1

        for k in thresholds:
            recall = (hits[k] / total_questions) * 100
            metrics[f"Recall@{k}"] = recall
            logger.info(f"Recall@{k}: {recall:.2f}% ({hits[k]}/{total_questions})")

        return metrics