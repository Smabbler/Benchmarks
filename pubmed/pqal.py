import requests
import zipfile
import io
import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Pqal:
    @staticmethod
    def prepare_dataset(data_dir: str, pqal_csv_contents_path: str, pqal_csv_questions_path: str):
        pqal_json_path = Path(data_dir) / "pqal.json"
        Pqal._download_pqal_test_set(pqal_json_path)
        Pqal._convert_pqal_to_csv(pqal_json_path, pqal_csv_contents_path, pqal_csv_questions_path)

    @staticmethod
    def _download_pqal_test_set(dest_path: str):
        logger.info("Downloading pqal.zip from HuggingFace...")

        if Path(dest_path).exists():
            logger.info(f"File already exists at: {dest_path}")
            return

        url = "https://huggingface.co/datasets/bigbio/pubmed_qa/resolve/main/pqal.zip"

        response = requests.get(url, timeout=120)
        response.raise_for_status()

        logger.info("Download complete. Extracting...")
        zip_data = response.content
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            all_files = z.namelist()
            target = next((f for f in all_files if "pqal_test_set.json" in f), None)
            if not target:
                raise FileNotFoundError("pqal_test_set.json not found in the zip archive.")

            with z.open(target) as source, open(dest_path, "wb") as dest:
                dest.write(source.read())
            logger.info(f"Saved to: {dest_path}")

    @staticmethod
    def _convert_pqal_to_csv(input_json: str, output_csv_contents: str, output_csv_questions: str):
        input_json = Path(input_json)
        output_csv_contents = Path(output_csv_contents)
        output_csv_questions = Path(output_csv_questions)
        logger.info(f"Converting {input_json.name} to {output_csv_contents.name} and {output_csv_questions.name}...")

        if output_csv_contents.exists() and output_csv_questions.exists():
            logger.info(f"File already exists at: {output_csv_contents} and {output_csv_questions}")
            return

        with input_json.open("r", encoding="utf-8") as f:
            data = json.load(f)

        written = 0
        with (
            output_csv_contents.open("w", encoding="utf-8", newline="") as f_contents,
            output_csv_questions.open("w", encoding="utf-8", newline="") as f_questions,
        ):
            contents_writer = csv.writer(f_contents, delimiter=";")
            questions_writer = csv.writer(f_questions, delimiter=";")
            contents_writer.writerow(["row", "pmid", "contents"])
            questions_writer.writerow(["pmid", "question"])

            for row, (pmid, payload) in enumerate(data.items(), 1):
                contents = " ".join(payload.get("CONTEXTS", [])).replace("<", " < ").replace(">", " > ")
                contents_writer.writerow([row, pmid, contents])
                questions_writer.writerow([pmid, payload.get("QUESTION")])
                written += 1

        logger.info(f"Conversion complete. Written {written} records to {output_csv_contents.name} and {output_csv_questions.name}.")
