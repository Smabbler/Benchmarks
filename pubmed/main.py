import logging
import argparse
from pathlib import Path

from pqal import Pqal
from smabbler_galaxia import SmabblerGalaxia
from benchmark import Benchmark

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PubMed QA benchmark using Smabbler Galaxia API.")
    parser.add_argument("api_key", help="Smabbler API key")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M")
    logging.info("Starting PubMed QA benchmark...")

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    pqal_csv_contents_path = Path(data_dir) / "pqal_contents.csv"
    pqal_csv_questions_path = Path(data_dir) / "pqal_questions.csv"
    Pqal.prepare_dataset(data_dir, pqal_csv_contents_path, pqal_csv_questions_path)

    pqal_results_path = Path(data_dir) / "pqal_results.json"
    SmabblerGalaxia.run(args.api_key, pqal_csv_contents_path, pqal_csv_questions_path, pqal_results_path)

    Benchmark.calculate_metrics(pqal_results_path)

    logging.info("Benchmark complete.")
