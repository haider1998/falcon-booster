import argparse
import logging
import os
import shutil

from backend.config.logging_config import configure_logging
from backend.repositories.data_store import DataStore
from backend.repositories.steps_cache import StepsCache
from backend.services.git_connect import GitConnect
from backend.services.json_service import JsonService
from backend.services.mermaid_service import MermaidService
from backend.services.sql_file_processor_service import SQLFileProcessor

# Configurations
clone_or_data_path = r"tmp/de"  # Replace with your desired path #Todo: Set this as Configuration

data_store = DataStore()

# Configure logging
configure_logging()


class WorkflowRunner:
    def __init__(self, git_service, sql_processor, json_service, mermaid_service):
        self.git_service = git_service
        self.sql_processor = sql_processor
        self.json_service = json_service
        self.mermaid_service = mermaid_service
        self.cache = StepsCache()

    def runflow(self, url, app_name, feed_name, initials_6char, ccpa, output_type, dropzone_gcs_bucket=False,
                dropzone_sftp=False):
        logging.info(f"Running flow for {app_name} and {feed_name} with initials {initials_6char}")

        url = url.strip()
        app_name = app_name.strip()
        feed_name = feed_name.strip().lower()
        initials_6char = initials_6char.strip().lower()

        cache_key = (app_name, feed_name, initials_6char, 'steps')

        # if self.cache.has(cache_key):  # Todo: Setup Cache
        #     steps = self.cache.get(cache_key)
        #     logging.info(f"Found steps in cache for {app_name} and {feed_name} with initials {initials_6char}")

        folder_path = self.git_service.get_local_absolute_path(url, clone_or_data_path)

        # folder_path = r'C:\Users\SRIZVI13\IdeaProjects\SQL Script repos of DE\DFA_GCP_MIGRATION\CAMPAIGN_SERVICE\OP824'

        processor = self.sql_processor(app_name, feed_name, initials_6char)
        steps = processor.process_sql_files(folder_path)

        if ccpa:
            steps = processor.add_ccpa_steps(initials_6char, steps)

        self.cache.set(cache_key, steps)

        data_store.set_data(cache_key, steps)

        if output_type == 'json':
            json_steps = self.json_service.steps_to_json(steps, f'tmp/{app_name}_{feed_name}.json')
            return json_steps

        if output_type == 'mmd':
            mermaid_code = self.mermaid_service.generate_mermaid_code(dropzone_sftp, dropzone_gcs_bucket, steps,
                                                                      f'tmp/{app_name}_{feed_name}.mmd')
            return mermaid_code

    def clear_resources(self):
        data_store.clear()
        self.cache.clear()

        # # Delete all files and folder from the path provided
        # for the_file in os.listdir("tmp"):
        #     file_path = os.path.join("tmp", the_file)
        #     try:
        #         if os.path.isfile(file_path):
        #             os.unlink(file_path)
        #         elif os.path.isdir(file_path):
        #             shutil.rmtree(file_path)
        #     except Exception as e:
        #         logging.error(f"Error deleting file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the workflow process")
    parser.add_argument("url", type=str, help="The URL of the repository")
    parser.add_argument("app_name", type=str, help="The application name")
    parser.add_argument("feed_name", type=str, help="The feed name")
    parser.add_argument("initials_6char", type=str, help="The initials (6 characters)")
    parser.add_argument("dropzone_gcs_bucket", type=bool, help="The dropzone GCS bucket")
    parser.add_argument("dropzone_sftp", type=bool, help="The dropzone SFTP")
    parser.add_argument("output_type", type=str, choices=["json", "mmd"], help="The output type (json or mmd)")

    args = parser.parse_args()

    git_service = GitConnect()
    sql_processor = SQLFileProcessor
    json_service = JsonService()
    mermaid_service = MermaidService()

    runner = WorkflowRunner(git_service, sql_processor, json_service, mermaid_service)
    result = runner.runflow(args.url, args.app_name, args.feed_name, args.initials_6char, args.output_type,
                            args.dropzone_gcs_bucket, args.dropzone_sftp)
    logging.INFO(result)
