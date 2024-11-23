from dataclasses import dataclass

from backend.models.Step import Step


@dataclass
class Steps:
    def __init__(self):
        self.steps = []

    def add_step(self, step: Step):
        self.steps.append(step)

    def remove_step(self, step: Step):
        self.steps.remove(step)

    def get_all_steps(self):
        return self.steps

    def get_size(self):
        return len(self.steps)

    def __repr__(self):
        return f"Steps(steps={self.steps})"

    def to_dict(self):
        return {
            'steps': [step.to_dict() for step in self.steps]
        }
