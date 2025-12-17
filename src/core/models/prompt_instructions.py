from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum
from src.core.models.jobscan_match_report import SkillType


class KeywordStatus(str, Enum):
    MUST_KEEP = "must_keep"
    KEEP_AND_INCREASE = "keep_and_increase"
    NEEDS_INTEGRATION = "needs_integration"
    DO_NOT_ADD = "do_not_add"

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
    status: KeywordStatus
    actual_quantity: int
    required_quantity: int
    min_final_quantity: int
    quantity_to_add: int
    
    class Config:
        model_config = {"validate_assignment": True} #validate on assignment

class KeywordStatistics(BaseModel):
    keywords: Dict[SkillType, List[Keyword]]
    
    class Config:
        model_config = {"validate_assignment": True} #validate on assignment

    def get_keywords_to_integrate(self) -> List[Keyword]:
        return self._filter_keywords(KeywordStatus.NEEDS_INTEGRATION)

    def get_keywords_to_keep(self) -> List[Keyword]:
        return self._filter_keywords(KeywordStatus.MUST_KEEP)

    def get_keywords_to_ignore(self) -> List[Keyword]:
        return self._filter_keywords(KeywordStatus.DO_NOT_ADD)

    def _filter_keywords(self, target_status: KeywordStatus) -> List[Keyword]:
        return {
            skill_type: [
                keyword for keyword in self.keywords.get(skill_type, []) 
                if keyword.status == target_status
            ]
            for skill_type in (SkillType.HARD_SKILL, SkillType.SOFT_SKILL)
        }