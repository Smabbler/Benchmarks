import time
import json
import csv
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


from smabbler.api.client import DefaultApi, ApiClient, Configuration
from smabbler.api.client.models import AnalyzeSourceCsvRequestSchema, BuildModelRequestSchema, InitializeOperationRequestSchema

logger = logging.getLogger(__name__)


class SmabblerGalaxia:
    def __init__(self, api_key: str):
        self._client: DefaultApi = self._create_client(api_key)

    @staticmethod
    def run(api_key: str, pqal_csv_contents_path: Path, pqal_csv_questions_path: Path, pqal_results_path: Path):
        smbb = SmabblerGalaxia(api_key)
        source_id = smbb._upload_csv(pqal_csv_contents_path)
        smbb._analyze_csv(source_id)
        model_id = smbb._build_model([source_id])
        smbb._activate_model(model_id)
        smbb._get_results(model_id, pqal_csv_questions_path, pqal_results_path)
        smbb._deactivate_model(model_id)

    def _create_client(self, api_key: str) -> DefaultApi:
        configuration = Configuration()
        configuration.api_key['ApiKeyAuth'] = api_key        
        return DefaultApi(ApiClient(configuration))

    def _poll_until(self, fetch_fn, target_status: str, *, interval: int, label: str = "", initial_delay: int = 0):
        if initial_delay:
            time.sleep(initial_delay)
        obj = fetch_fn()
        while obj.status != target_status:
            if label:
                logger.info(f"Current status for {label}: {obj.status}. Waiting...")
            time.sleep(interval)
            obj = fetch_fn()
        return obj

    def _upload_csv(self, pqal_csv_contents_path: Path):
        response = self._client.upload_source_file(str(pqal_csv_contents_path))
        return response.source_id

    def _analyze_csv(self, source_id: str, id_column: str = "pmid", text_column: str = "contents"):
        logger.info(f"Analyzing source {source_id}...")
        request = AnalyzeSourceCsvRequestSchema(
            id_column_name=id_column,
            text_column_names=[text_column]
        )
        self._client.analyze_source_csv(source_id, request)
        logger.info(f"Analysis started for source_id: {source_id}")
        self._poll_until(lambda: self._client.get_source(source_id), "Analyzed", interval=20, label=f"source_id {source_id}")
        logger.info(f"Analysis complete for source_id: {source_id}. Final status: Analyzed")

    def _build_model(self, source_ids: list[str]):
        logger.info(f"Building model for sources {source_ids}...")
        build_model_request_schema = BuildModelRequestSchema(
            sources=source_ids,
            model_name="pubmed-qa-model"
        )
        response = self._client.build_model(build_model_request_schema)
        model_id = response.model_id
        logger.info(f"Model building started, model_id: {model_id}")
        self._poll_until(lambda: self._client.get_model(model_id), "Inactive", interval=10, label=f"model_id {model_id}")
        logger.info(f"Model building complete for model_id: {model_id}. Final status: Inactive")
        return model_id

    def _activate_model(self, model_id: str):
        logger.info(f"Activating model {model_id}...")
        self._client.activate_model(model_id)
        logger.info(f"Model activation started, model_id: {model_id}")
        self._poll_until(lambda: self._client.get_model(model_id), "Active", interval=30, label=f"model_id {model_id}", initial_delay=180)
        logger.info(f"Model activation complete for model_id: {model_id}. Final status: Active")

    def _get_results(self, model_id: str, pqal_csv_questions_path: Path, pqal_results_path: Path):
        logger.info(f"Getting results for {pqal_csv_questions_path}...")
        questions = []
        with open(pqal_csv_questions_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                pmid = row.get("pmid")
                question = row.get("question")
                if pmid and question:
                    questions.append((pmid, question))

        logger.info(f"Loaded {len(questions)} questions for processing with 10 parallel workers...")
        results_dict = {}
        completed_count = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_pmid = {
                executor.submit(self._get_result_with_retry, model_id, question): pmid
                for pmid, question in questions
            }
            for future in as_completed(future_to_pmid):
                pmid = future_to_pmid[future]
                try:
                    results_dict[pmid] = future.result()
                    completed_count += 1
                    if completed_count % 100 == 0:
                        logger.info(f"Progress: Processed {completed_count}/{len(questions)} questions")
                except Exception as e:
                    logger.error(f"Error processing pmid {pmid}: {e}")

        logger.info(f"Done: Processed {len(results_dict)} questions")
        with open(pqal_results_path, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=None)
        logger.info(f"Results saved to {pqal_results_path}")

    def _get_result_with_retry(self, model_id: str, question: str, 
                                max_retries: int = 3, backoff_base: float = 2.0):
        last_exception = None
        for attempt in range(max_retries):
            try:
                return self._get_result(model_id, question)
            except Exception as e:
                last_exception = e
                wait = backoff_base ** attempt
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for question '{question}': {e}. "
                    f"Retrying in {wait:.1f}s..."
                )
                time.sleep(wait)

        raise RuntimeError(f"All {max_retries} attempts failed for question '{question}'.") from last_exception

    def _get_result(self, model_id: str, question: str):
        initialize_operation_request_schema = InitializeOperationRequestSchema(
            model_id=model_id,
            text=question
        )
        response = self._client.initialize_analysis(initialize_operation_request_schema)
        operation_id = response.operation_id
        self._poll_until(lambda: self._client.get_analysis_status(operation_id), "processed", interval=1)
        result = self._client.get_analysis_result(operation_id)
        items = result.result.result_items
        results = []
        for item in items:
            _, pmid, _ = item.group.split("*")
            results.append({"pmid": pmid, "rank": item.rank})
        return results

    def _deactivate_model(self, model_id: str):
        logger.info(f"Deactivating model {model_id}...")
        self._client.deactivate_model(model_id)
        logger.info(f"Model deactivation started, model_id: {model_id}")
