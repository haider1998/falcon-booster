# file: backend/services/interfaces.py
from abc import ABC, abstractmethod
from typing import List

from backend.models.Step import Step


class StepServiceInterface(ABC):
    @abstractmethod
    def get_all_steps(self) -> List[Step]:
        pass


class MermaidServiceInterface(ABC):
    @abstractmethod
    def generate_mermaid_code(self, dropzone_sftp: bool, gcs_bucket: bool, steps: List[Step]) -> str:
        pass


class JsonServiceInterface(ABC):
    @abstractmethod
    def steps_to_json(self, steps: List[Step], output_filename: str) -> dict:
        pass
