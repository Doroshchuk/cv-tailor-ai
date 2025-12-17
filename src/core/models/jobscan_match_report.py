import json
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone
import core.utils.paths as path_utils
from core.models.prompt_instructions import Keyword, KeywordStatus
from core.models.prompt_instructions import KeywordStatistics


class SkillApplianceType(str, Enum):
    MISSING = "missing"
    APPLIED = "applied"


class SkillType(str, Enum):
    SOFT_SKILL = "soft skill"
    HARD_SKILL = "hard skill"


class CheckStatusType(str, Enum):
    WARN = "warn"
    PASS = "pass"
    FAIL = "fail"


class Skill(BaseModel):
    name: Optional[str] = None
    type: Optional[SkillType] = None
    is_supported: Optional[bool] = None
    required_quantity: Optional[int] = None
    actual_quantity: Optional[int] = None

    def define_appliance_type(self) -> SkillApplianceType:
        return (
            SkillApplianceType.APPLIED 
            if self.actual_quantity and self.required_quantity and self.actual_quantity >= self.required_quantity 
            else SkillApplianceType.MISSING
        )

    def update_is_supported(self, whitelist) -> bool:
        """Update the is_supported field based on a whitelist and current usage."""
        if not self.name:
            self.is_supported = False
            return self.is_supported
        self.is_supported = (
            self.actual_quantity > 0 if self.actual_quantity else False
            or self.name.lower() in whitelist
        )
        return self.is_supported
    
    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment


class Check(BaseModel):
    description: Optional[str] = None
    details: List[str] = []
    status: Optional[CheckStatusType] = None

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment


class MetricFinding(BaseModel):
    title: Optional[str] = None
    is_fully_applied: Optional[bool] = None
    checks: List[Check] = []

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment
        

class JobscanMatchReport(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    iteration: Optional[int] = None
    score: Optional[int] = None
    report_url: Optional[str] = None
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_job_title_match_by_default: Optional[bool] = None
    hard_skills: Dict[SkillApplianceType, List[Skill]] = Field(default_factory=dict)
    soft_skills: Dict[SkillApplianceType, List[Skill]] = Field(default_factory=dict)
    metrics: Dict[str,List[MetricFinding]] = Field(default_factory=dict)

    class Config:
        model_config = {"validate_assignment": True}  # validate on assignment

    def write_to_file(self) -> None:
        if not self.company or not self.job_title or not self.iteration:
            raise ValueError("Missing data!")
        path_to_match_report_path = path_utils.get_jobscan_match_report_path(self.company, self.job_title, self.iteration)
        path_to_match_report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with path_to_match_report_path.open("w+") as f:
            json.dump(self.model_dump(mode="json"), f)

        print(f"[write_to_file] Wrote Jobscan Match Report JSON to: {path_to_match_report_path}  (exists={path_to_match_report_path.exists()})")

    def get_keywords_to_prompt(self) -> KeywordStatistics:
        return KeywordStatistics(
            keywords={
                SkillType.HARD_SKILL: self._transform_skills(skills=self.hard_skills),
                SkillType.SOFT_SKILL: self._transform_skills(skills=self.soft_skills)
            }
        )

    def _transform_skills(self, skills: Dict[SkillApplianceType, List[Skill]]) -> list[Keyword]:
        keywords = []
        for _, skills_for_type in skills.items():
            for skill in skills_for_type:

                if not skill.is_supported:
                    keyword_status = KeywordStatus.DO_NOT_ADD
                elif skill.actual_quantity == 0:
                    keyword_status = KeywordStatus.NEEDS_INTEGRATION
                else:
                    if skill.actual_quantity >= skill.required_quantity:
                        keyword_status = KeywordStatus.MUST_KEEP
                    else:
                        keyword_status = KeywordStatus.KEEP_AND_INCREASE

                required_quantity= 0 if keyword_status == KeywordStatus.DO_NOT_ADD else skill.required_quantity

                keyword = Keyword(
                    name=skill.name,
                    status=keyword_status,
                    actual_quantity=skill.actual_quantity,
                    required_quantity=required_quantity,
                    min_final_quantity=skill.actual_quantity,
                    quantity_to_add=max(0, required_quantity - skill.actual_quantity)
                )
                keywords.append(keyword)
        return keywords

    def get_unsupported_keywords(self) -> dict[SkillType, list[Keyword]]:
        keywords:  dict[SkillType, list[Keyword]] = {} 
        keywords[SkillType.HARD_SKILL] = self._transform_skills(supported=False, skills=self.hard_skills)
        keywords[SkillType.SOFT_SKILL] = self._transform_skills(supported=False, skills=self.soft_skills)
        return keywords

    def _update_supported_skills(self, skill_type: SkillType, whitelist: list[str]) -> None:
        skills = self.hard_skills if skill_type == SkillType.HARD_SKILL else self.soft_skills
        for appliance_type in skills:
            for skill in skills[appliance_type]:
                skill.update_is_supported(whitelist)

    def update_supported_skills(self, whitelisted_hard_skills: list[str], whitelisted_soft_skills: list[str]) -> None:
        self._update_supported_skills(SkillType.HARD_SKILL, whitelisted_hard_skills)
        self._update_supported_skills(SkillType.SOFT_SKILL, whitelisted_soft_skills)
