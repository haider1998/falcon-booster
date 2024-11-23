# file: backend/services/step_service.py
from typing import List

from backend.models import Step
from backend.services.interfaces import StepServiceInterface


class StepService(StepServiceInterface):
    def __init__(self, steps: List[Step]):
        self.steps = steps

    def get_all_steps(self) -> List[Step]:
        return self.steps
