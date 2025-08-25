from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone


class SkillApplianceType(str, Enum):
    MISSING = "missing"
    APPLIED = "applied"

class SkillType(str, Enum):
    SOFT_SKILL = "soft skill"
    HARD_SKILL = "hard skill"

class Skill(BaseModel):
    name: Optional[str] = None
    type: Optional[SkillType] = None
    is_supported: Optional[bool] = None
    required_quantity: Optional[int] = None
    actual_quantity: Optional[int] = None

    def define_appliance_type(self) -> SkillApplianceType:
        return SkillApplianceType.APPLIED if self.actual_quantity >= self.required_quantity else SkillApplianceType.MISSING
    
    class Config:
        validate_assignment = True  # validate on assignment

class JobscanMatchReport(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    iteration: Optional[int] = None
    score: Optional[int] = None
    report_url: Optional[str] = None
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_job_title_match_by_default: Optional[bool] = None
    hard_skills: Dict[SkillApplianceType, List[Skill]] = {}
    soft_skills: Dict[SkillApplianceType, List[Skill]] = {}

    class Config:
        validate_assignment = True  # validate on assignment