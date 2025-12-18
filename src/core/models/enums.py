from enum import Enum


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