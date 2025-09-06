import json
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone
import core.utils.paths as path_utils
from pathlib import Path


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
        return SkillApplianceType.APPLIED if self.actual_quantity >= self.required_quantity else SkillApplianceType.MISSING
    
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
        # path_to_match_reports_dir = Path(path_utils.get_configs_dir_path()) / f"{self.company}_{self.job_title}"
        path_to_match_report_path = path_utils.get_jobscan_match_report_path(self.company, self.job_title, self.iteration)

        # path_to_match_reports_dir.mkdir(parents=True, exist_ok=True)
        path_to_match_report_path.parent.mkdir(parents=True, exist_ok=True)
        # file_path = path_to_match_reports_dir / f"match_report_{self.iteration}.json"
        with path_to_match_report_path.open("w+") as f:
            json.dump(self.model_dump(mode="json"), f)

        print(f"[write_to_file] Wrote Jobscan Match Report JSON to: {path_to_match_report_path}  (exists={path_to_match_report_path.exists()})")
