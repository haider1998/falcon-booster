# file: backend/services/json_service.py
import json
from typing import List

from backend.config.logging_config import configure_logging
from backend.models.Step import Step
from backend.services.interfaces import JsonServiceInterface

# Configure logging
configure_logging()


class JsonService(JsonServiceInterface):
    def steps_to_json(self, steps: List[Step], output_filename: str) -> dict:
        workflow_data = {
            "steps": []
        }

        for i, step in enumerate(steps.get_all_steps()):
            step_data = {
                "step_number": i + 1,
                "gcs_bucket_name": step.gcs_bucket_name,
                "table_name": step.table_name,
                "source_tables": step.get_all_de_tables()
            }
            workflow_data["steps"].append(step_data)

        with open(output_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(workflow_data, jsonfile, indent=4)  # Use indent for readability

        return workflow_data
