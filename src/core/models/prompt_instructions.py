from pydantic import BaseModel, Field
from typing import List, Dict

class Prompt(BaseModel):
    system_instructions: List[str] = Field(default_factory=list)
    task_instructions: List[str] = Field(default_factory=list)

    class Config:
        model_config = {"validate_assignment": True} #validate on assignment

    def get_system_instructions(self) -> str:
        return self._concatenate_instructions(self.system_instructions)

    def get_task_instructions(self) -> str:
        return self._concatenate_instructions(self.task_instructions)

    def _concatenate_instructions(self, instructions: list[str]) -> str:
        return "\n".join(instructions)

class Keyword(BaseModel):
    name: str
    required: int
    actual: int

    class Config:
        model_config = {"validate_assignment": True} #validate on assignment